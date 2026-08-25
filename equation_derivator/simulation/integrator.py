"""
Numerical Integrators for Symbolic Mechanical Systems.
Provides Runge-Kutta 4th Order (RK4) and Symplectic Verlet integrators.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
import numpy as np
import sympy as sp


@dataclass
class SimulationTrajectory:
    """
    Encapsulates numerical time-series solution for generalized coordinates and velocities.
    """
    system_name: str
    coordinates: List[str]
    time: List[float]
    positions: Dict[str, List[float]]
    velocities: Dict[str, List[float]]
    total_energy: List[float] = field(default_factory=list)
    metadata: Dict[str, Union[str, float, int]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "system_name": self.system_name,
            "coordinates": self.coordinates,
            "time": self.time,
            "positions": self.positions,
            "velocities": self.velocities,
            "total_energy": self.total_energy,
            "metadata": self.metadata,
        }


class RK4Integrator:
    """
    Classic 4th-Order Runge-Kutta Integrator for systems of 2nd-order ODEs:
    d^2 q_i / dt^2 = a_i(q, \dot{q}, t).
    """

    def __init__(self, dt: float = 0.01):
        self.dt = dt

    def step(
        self,
        t: float,
        q: np.ndarray,
        v: np.ndarray,
        accel_fn: Callable[[float, np.ndarray, np.ndarray], np.ndarray]
    ) -> Tuple[float, np.ndarray, np.ndarray]:
        dt = self.dt

        # k1
        k1_q = v
        k1_v = accel_fn(t, q, v)

        # k2
        q2 = q + 0.5 * dt * k1_q
        v2 = v + 0.5 * dt * k1_v
        k2_q = v2
        k2_v = accel_fn(t + 0.5 * dt, q2, v2)

        # k3
        q3 = q + 0.5 * dt * k2_q
        v3 = v + 0.5 * dt * k2_v
        k3_q = v3
        k3_v = accel_fn(t + 0.5 * dt, q3, v3)

        # k4
        q4 = q + dt * k3_q
        v4 = v + dt * k3_v
        k4_q = v4
        k4_v = accel_fn(t + dt, q4, v4)

        # Update
        new_q = q + (dt / 6.0) * (k1_q + 2.0 * k2_q + 2.0 * k3_q + k4_q)
        new_v = v + (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)
        new_t = t + dt

        return new_t, new_q, new_v

    def integrate(
        self,
        accel_fn: Callable[[float, np.ndarray, np.ndarray], np.ndarray],
        q0: np.ndarray,
        v0: np.ndarray,
        t_span: Tuple[float, float],
        energy_fn: Optional[Callable[[np.ndarray, np.ndarray], float]] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        t_start, t_end = t_span
        n_steps = int(np.ceil((t_end - t_start) / self.dt))

        dim = len(q0)
        t_arr = np.zeros(n_steps + 1)
        q_arr = np.zeros((n_steps + 1, dim))
        v_arr = np.zeros((n_steps + 1, dim))
        e_arr = np.zeros(n_steps + 1)

        t_arr[0] = t_start
        q_arr[0] = q0
        v_arr[0] = v0
        if energy_fn:
            e_arr[0] = energy_fn(q0, v0)

        cur_t = t_start
        cur_q = np.array(q0, dtype=float)
        cur_v = np.array(v0, dtype=float)

        for i in range(1, n_steps + 1):
            cur_t, cur_q, cur_v = self.step(cur_t, cur_q, cur_v, accel_fn)
            t_arr[i] = cur_t
            q_arr[i] = cur_q
            v_arr[i] = cur_v
            if energy_fn:
                e_arr[i] = energy_fn(cur_q, cur_v)

        return t_arr, q_arr, v_arr, e_arr


class VerletIntegrator:
    """
    Velocity Verlet Symplectic Integrator for conservative systems:
    d^2 q / dt^2 = a(q). (Conserves phase space volume and total energy over long times).
    """

    def __init__(self, dt: float = 0.01):
        self.dt = dt

    def integrate(
        self,
        accel_fn: Callable[[float, np.ndarray], np.ndarray],
        q0: np.ndarray,
        v0: np.ndarray,
        t_span: Tuple[float, float],
        energy_fn: Optional[Callable[[np.ndarray, np.ndarray], float]] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        t_start, t_end = t_span
        n_steps = int(np.ceil((t_end - t_start) / self.dt))
        dt = self.dt

        dim = len(q0)
        t_arr = np.zeros(n_steps + 1)
        q_arr = np.zeros((n_steps + 1, dim))
        v_arr = np.zeros((n_steps + 1, dim))
        e_arr = np.zeros(n_steps + 1)

        t_arr[0] = t_start
        q_arr[0] = q0
        v_arr[0] = v0
        if energy_fn:
            e_arr[0] = energy_fn(q0, v0)

        cur_t = t_start
        cur_q = np.array(q0, dtype=float)
        cur_v = np.array(v0, dtype=float)
        cur_a = accel_fn(cur_t, cur_q)

        for i in range(1, n_steps + 1):
            cur_q = cur_q + cur_v * dt + 0.5 * cur_a * (dt**2)
            cur_t = cur_t + dt
            next_a = accel_fn(cur_t, cur_q)
            cur_v = cur_v + 0.5 * (cur_a + next_a) * dt
            cur_a = next_a

            t_arr[i] = cur_t
            q_arr[i] = cur_q
            v_arr[i] = cur_v
            if energy_fn:
                e_arr[i] = energy_fn(cur_q, cur_v)

        return t_arr, q_arr, v_arr, e_arr


def simulate_symbolic_system(
    accelerations: Dict[str, Union[str, sp.Expr]],
    coordinates: List[str],
    initial_positions: Dict[str, float],
    initial_velocities: Dict[str, float],
    parameters: Optional[Dict[str, float]] = None,
    t_end: float = 10.0,
    dt: float = 0.02,
    system_name: str = "Symbolic Dynamical System"
) -> SimulationTrajectory:
    """
    Compiles symbolic SymPy acceleration expressions into fast lambdified numerical functions
    and integrates them with RK4.
    """
    params = parameters or {}
    q_syms = [sp.Symbol(c, real=True) for c in coordinates]
    q_dot_syms = [sp.Symbol(f"{c}_dot", real=True) for c in coordinates]
    t_sym = sp.Symbol("t", real=True)

    # Substitute constant parameter values into acceleration expressions
    param_subs = {sp.Symbol(k): v for k, v in params.items()}

    accel_lambdas = []
    for c in coordinates:
        acc_expr = accelerations[c]
        if isinstance(acc_expr, str):
            from equation_derivator.core.symbols import parse_expression_safely
            acc_expr = parse_expression_safely(acc_expr)
        
        # Substitute numerical parameters by matching symbol name
        subs_list = [(s, params[s.name]) for s in acc_expr.free_symbols if s.name in params]
        acc_subbed = acc_expr.subs(subs_list)

        # Match coordinate and velocity symbols present in acc_subbed
        q_map = {q.name: q for q in q_syms}
        qdot_map = {qd.name: qd for qd in q_dot_syms}
        
        # Replace free symbols in acc_subbed with the canonical q_syms / q_dot_syms
        canonical_subs = []
        for s in acc_subbed.free_symbols:
            if s.name in q_map:
                canonical_subs.append((s, q_map[s.name]))
            elif s.name in qdot_map:
                canonical_subs.append((s, qdot_map[s.name]))
        acc_subbed = acc_subbed.subs(canonical_subs)

        # Create callable lambda (t, q0, q1, ..., v0, v1, ...)
        args = [t_sym] + q_syms + q_dot_syms
        f_num = sp.lambdify(args, acc_subbed, modules=["numpy"])
        accel_lambdas.append(f_num)

    def vector_accel(t: float, q: np.ndarray, v: np.ndarray) -> np.ndarray:
        args_val = [t] + list(q) + list(v)
        res = []
        for fn in accel_lambdas:
            val = fn(*args_val)
            res.append(float(val))
        return np.array(res, dtype=float)

    q0 = np.array([initial_positions.get(c, 0.0) for c in coordinates], dtype=float)
    v0 = np.array([initial_velocities.get(c, 0.0) for c in coordinates], dtype=float)

    integrator = RK4Integrator(dt=dt)
    t_arr, q_arr, v_arr, _ = integrator.integrate(vector_accel, q0, v0, (0.0, t_end))

    # Downsample if very large to prevent memory overhead in API responses
    step_skip = max(1, len(t_arr) // 500)
    t_out = t_arr[::step_skip].tolist()

    pos_dict = {c: q_arr[::step_skip, i].tolist() for i, c in enumerate(coordinates)}
    vel_dict = {c: v_arr[::step_skip, i].tolist() for i, c in enumerate(coordinates)}

    return SimulationTrajectory(
        system_name=system_name,
        coordinates=coordinates,
        time=t_out,
        positions=pos_dict,
        velocities=vel_dict,
        metadata={"dt": dt, "t_end": t_end, "parameters": params}
    )
