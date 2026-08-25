"""
Phase Space Dynamics, Vector Fields & Poincaré Invariants.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
import numpy as np
import sympy as sp


@dataclass
class PhaseSpaceTrajectory:
    system_name: str
    coordinate: str
    q_values: List[float]
    p_values: List[float]
    energy_values: List[float]
    vector_field_grid: Dict[str, List[List[float]]] = field(default_factory=dict)
    is_conservative: bool = True
    energy_drift_percent: float = 0.0

    def to_dict(self) -> dict:
        return {
            "system_name": self.system_name,
            "coordinate": self.coordinate,
            "q_values": self.q_values,
            "p_values": self.p_values,
            "energy_values": self.energy_values,
            "vector_field_grid": self.vector_field_grid,
            "is_conservative": self.is_conservative,
            "energy_drift_percent": self.energy_drift_percent,
        }


class PhaseSpaceEngine:
    """
    Computes phase space portraits, streamlines, and energy drift diagnostics.
    """

    def generate_phase_portrait(
        self,
        accel_expr_str: str,
        coord_name: str = "x",
        params: Optional[Dict[str, float]] = None,
        q_range: Tuple[float, float] = (-3.0, 3.0),
        v_range: Tuple[float, float] = (-3.0, 3.0),
        grid_resolution: int = 15,
        q0: float = 1.0,
        v0: float = 0.0,
        t_end: float = 10.0,
        dt: float = 0.01,
        potential_expr_str: Optional[str] = None
    ) -> PhaseSpaceTrajectory:
        from equation_derivator.simulation.integrator import RK4Integrator
        from equation_derivator.core.symbols import parse_expression_safely

        parameters = params or {}
        q_sym = sp.Symbol(coord_name, real=True)
        v_sym = sp.Symbol(f"{coord_name}_dot", real=True)
        t_sym = sp.Symbol("t", real=True)

        acc_parsed = parse_expression_safely(accel_expr_str)
        subs_list = [(s, parameters[s.name]) for s in acc_parsed.free_symbols if s.name in parameters]
        acc_subbed = acc_parsed.subs(subs_list)

        # Replace any residual symbol with q_sym or v_sym if matching name
        coord_subs = []
        for s in acc_subbed.free_symbols:
            if s.name == coord_name:
                coord_subs.append((s, q_sym))
            elif s.name in (f"{coord_name}_dot", "v"):
                coord_subs.append((s, v_sym))
        acc_subbed = acc_subbed.subs(coord_subs)

        acc_fn = sp.lambdify([t_sym, q_sym, v_sym], acc_subbed, modules=["numpy"])

        # 1. Generate 2D Vector Field Grid
        q_min, q_max = q_range
        v_min, v_max = v_range
        q_grid = np.linspace(q_min, q_max, grid_resolution)
        v_grid = np.linspace(v_min, v_max, grid_resolution)
        Q, V = np.meshgrid(q_grid, v_grid)

        # dq/dt = v, dv/dt = a(q, v)
        U_flow = V
        W_flow = np.zeros_like(Q)
        for i in range(grid_resolution):
            for j in range(grid_resolution):
                W_flow[i, j] = float(acc_fn(0.0, Q[i, j], V[i, j]))

        # Normalize vector magnitudes for clean plotting
        speed = np.sqrt(U_flow**2 + W_flow**2) + 1e-12
        U_norm = U_flow / speed
        W_norm = W_flow / speed

        # 2. Integrate user trajectory in phase space
        def single_accel(t: float, q_vec: np.ndarray, v_vec: np.ndarray) -> np.ndarray:
            return np.array([float(acc_fn(t, q_vec[0], v_vec[0]))])

        integrator = RK4Integrator(dt=dt)
        t_arr, q_arr, v_arr, _ = integrator.integrate(
            single_accel,
            np.array([q0]),
            np.array([v0]),
            (0.0, t_end)
        )

        q_traj = q_arr[:, 0]
        v_traj = v_arr[:, 0]

        # 3. Energy evaluation if potential available
        energies = []
        if potential_expr_str:
            m_val = parameters.get("m", 1.0)
            v_pot_parsed = parse_expression_safely(potential_expr_str)
            v_pot_subbed = v_pot_parsed.subs([(s, parameters[s.name]) for s in v_pot_parsed.free_symbols if s.name in parameters])
            v_pot_subbed = v_pot_subbed.subs([(s, q_sym) for s in v_pot_subbed.free_symbols if s.name == coord_name])
            pot_fn = sp.lambdify([q_sym], v_pot_subbed, modules=["numpy"])
            for q_val, v_val in zip(q_traj, v_traj):
                e = 0.5 * m_val * (v_val**2) + float(pot_fn(q_val))
                energies.append(e)
        else:
            energies = [0.5 * (v**2) for v in v_traj]

        # Calculate energy drift
        initial_e = energies[0] if energies else 1.0
        final_e = energies[-1] if energies else 1.0
        drift = abs((final_e - initial_e) / (abs(initial_e) + 1e-12)) * 100.0

        skip = max(1, len(q_traj) // 300)

        return PhaseSpaceTrajectory(
            system_name=f"Phase Portrait ({coord_name})",
            coordinate=coord_name,
            q_values=q_traj[::skip].tolist(),
            p_values=v_traj[::skip].tolist(),
            energy_values=[float(e) for e in energies[::skip]],
            vector_field_grid={
                "q": Q.tolist(),
                "v": V.tolist(),
                "u": U_norm.tolist(),
                "w": W_norm.tolist()
            },
            is_conservative=bool(drift < 1.0),
            energy_drift_percent=float(round(drift, 4))
        )
