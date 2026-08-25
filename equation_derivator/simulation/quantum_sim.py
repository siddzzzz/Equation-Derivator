"""
1D Time-Dependent Schrödinger Equation (TDSE) Quantum Wave Packet Simulator.
Uses split-operator kinetic-potential FFT method for unitary time evolution.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np


@dataclass
class QuantumWavePacketResult:
    x_grid: List[float]
    time_points: List[float]
    potential: List[float]
    probability_density_history: List[List[float]]
    initial_norm: float
    final_norm: float
    transmission_coefficient: float
    reflection_coefficient: float

    def to_dict(self) -> dict:
        return {
            "x_grid": self.x_grid,
            "time_points": self.time_points,
            "potential": self.potential,
            "probability_density_history": self.probability_density_history,
            "initial_norm": self.initial_norm,
            "final_norm": self.final_norm,
            "transmission_coefficient": self.transmission_coefficient,
            "reflection_coefficient": self.reflection_coefficient,
        }


def _integrate_trapz(y: np.ndarray, x: np.ndarray) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


class QuantumWavePacketSim:
    r"""
    Simulates quantum wave packet dynamics and barrier tunneling:
    i \hbar \partial \psi / \partial t = [ -\frac{\hbar^2}{2m} \frac{\partial^2}{\partial x^2} + V(x) ] \psi.
    """

    def __init__(
        self,
        N: int = 512,
        x_min: float = -10.0,
        x_max: float = 10.0,
        hbar: float = 1.0,
        m: float = 1.0
    ):
        self.N = N
        self.x_min = x_min
        self.x_max = x_max
        self.hbar = hbar
        self.m = m

        self.x = np.linspace(x_min, x_max, N)
        self.dx = self.x[1] - self.x[0]
        self.p = 2.0 * np.pi * self.hbar * np.fft.fftfreq(N, self.dx)

    def create_gaussian_packet(
        self,
        x0: float = -4.0,
        p0: float = 3.0,
        sigma: float = 0.5
    ) -> np.ndarray:
        """
        Creates normalized Gaussian wave packet: psi(x) = (1 / (pi*sigma^2))^(1/4) * exp(-(x-x0)^2/(2*sigma^2) + i*p0*x/hbar)
        """
        norm_factor = (1.0 / (np.pi * sigma**2))**0.25
        psi = norm_factor * np.exp(-((self.x - x0)**2) / (2.0 * sigma**2)) * np.exp(1j * p0 * self.x / self.hbar)
        # Numerical normalization check
        norm = _integrate_trapz(np.abs(psi)**2, self.x)
        return psi / np.sqrt(norm)

    def build_potential(
        self,
        barrier_type: str = "barrier",
        barrier_height: float = 5.0,
        barrier_width: float = 0.5,
        barrier_center: float = 0.0,
        custom_potential_expr: Optional[str] = None
    ) -> np.ndarray:
        if custom_potential_expr and custom_potential_expr.strip():
            from equation_derivator.core.symbols import parse_expression_safely
            try:
                sym_expr = parse_expression_safely(custom_potential_expr)
                x_sym = [s for s in sym_expr.free_symbols if s.name == "x"]
                target_sym = x_sym[0] if x_sym else sp.Symbol("x", real=True)
                f_lamb = sp.lambdify(target_sym, sym_expr, modules=["numpy"])
                V = np.array(f_lamb(self.x), dtype=float)
                if V.ndim == 0:
                    V = np.full(self.N, float(V))
                return V
            except Exception:
                pass

        V = np.zeros(self.N)
        if barrier_type == "barrier":
            # Rectangular potential barrier
            mask = (self.x >= (barrier_center - barrier_width / 2.0)) & (self.x <= (barrier_center + barrier_width / 2.0))
            V[mask] = barrier_height
        elif barrier_type == "harmonic":
            # Harmonic trap V(x) = 1/2 k x^2
            V = 0.5 * barrier_height * (self.x**2)
        elif barrier_type == "step":
            # Potential step
            V[self.x >= barrier_center] = barrier_height
        return V

    def propagate(
        self,
        psi0: np.ndarray,
        V: np.ndarray,
        t_max: float = 3.0,
        dt: float = 0.005,
        n_frames: int = 40
    ) -> QuantumWavePacketResult:
        """
        Split-Operator time stepping: exp(-i*H*dt) ~ exp(-i*V*dt/2) exp(-i*T*dt) exp(-i*V*dt/2).
        """
        exp_V_half = np.exp(-1j * (V * dt / (2.0 * self.hbar)))
        exp_T = np.exp(-1j * ((self.p**2) / (2.0 * self.m)) * (dt / self.hbar))

        psi = np.array(psi0, dtype=complex)
        total_steps = int(t_max / dt)
        save_interval = max(1, total_steps // n_frames)

        init_norm = _integrate_trapz(np.abs(psi)**2, self.x)
        prob_history: List[List[float]] = []
        time_points: List[float] = []

        # Record initial frame
        prob_history.append((np.abs(psi)**2).tolist())
        time_points.append(0.0)

        for step in range(1, total_steps + 1):
            # 1. Half-step potential
            psi = exp_V_half * psi
            # 2. Full-step kinetic in momentum space
            psi_k = np.fft.fft(psi)
            psi_k = exp_T * psi_k
            psi = np.fft.ifft(psi_k)
            # 3. Half-step potential
            psi = exp_V_half * psi

            if step % save_interval == 0 or step == total_steps:
                prob = np.abs(psi)**2
                prob_history.append(prob.tolist())
                time_points.append(round(step * dt, 4))

        final_norm = _integrate_trapz(np.abs(psi)**2, self.x)

        # Calculate transmission (probability x > barrier_center) & reflection (x < barrier_center)
        mid_idx = self.N // 2
        prob_final = np.abs(psi)**2
        refl = float(_integrate_trapz(prob_final[:mid_idx], self.x[:mid_idx]) / final_norm)
        trans = float(_integrate_trapz(prob_final[mid_idx:], self.x[mid_idx:]) / final_norm)

        # Downsample x grid for lightweight web rendering
        skip_x = max(1, self.N // 128)

        return QuantumWavePacketResult(
            x_grid=self.x[::skip_x].tolist(),
            time_points=time_points,
            potential=V[::skip_x].tolist(),
            probability_density_history=[p[::skip_x] for p in prob_history],
            initial_norm=round(init_norm, 4),
            final_norm=round(final_norm, 4),
            transmission_coefficient=round(trans, 4),
            reflection_coefficient=round(refl, 4)
        )
