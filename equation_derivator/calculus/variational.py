"""
Lagrangian & Hamiltonian Variational Mechanics Engine.
Derives Euler-Lagrange equations of motion, Hamilton's canonical equations,
and Noether's theorem conservation laws.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
import sympy as sp

from equation_derivator.core.symbols import VariableContext, parse_expression_safely
from equation_derivator.derivation.step import DerivationStep


@dataclass
class VariationalResult:
    """
    Encapsulates the complete derivation of a variational physical system.
    """
    system_name: str
    coordinates: List[str]
    lagrangian: sp.Expr
    lagrangian_latex: str
    euler_lagrange_equations: List[Dict[str, Any]]
    hamiltonian: Optional[Dict[str, Any]] = None
    noether_conserved_quantities: List[Dict[str, Any]] = field(default_factory=list)
    steps: List[DerivationStep] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# Variational Mechanics Derivation: {self.system_name}\n",
            f"**Generalized Coordinates:** ${', '.join(self.coordinates)}$\n",
            f"**Lagrangian:**",
            f"$$\\mathcal{{L}} = {self.lagrangian_latex}$$\n",
            "## 1. Euler-Lagrange Equations of Motion\n"
        ]

        for eq_info in self.euler_lagrange_equations:
            q = eq_info["coord"]
            lines.append(f"### Coordinate ${q}$:")
            lines.append(f"- **Partial Derivative wrt Position:** $\\frac{{\\partial \\mathcal{{L}}}}{{\\partial {q}}} = {sp.latex(eq_info['dL_dq'])}$")
            lines.append(f"- **Conjugate Momentum:** $p_{{{q}}} = \\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{q}}}}} = {sp.latex(eq_info['dL_dqdot'])}$")
            lines.append(f"- **Time Derivative of Momentum:** $\\frac{{d}}{{dt}}\\left(\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{q}}}}}\\right) = {sp.latex(eq_info['d_dt_dL_dqdot'])}$")
            lines.append(f"- **Euler-Lagrange Relation:**")
            lines.append(f"  $$\\frac{{d}}{{dt}}\\left(\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{q}}}}}\\right) - \\frac{{\\partial \\mathcal{{L}}}}{{\\partial {q}}} = 0 \\implies {eq_info['equation_latex']}$$")
            if eq_info.get("acceleration_latex"):
                lines.append(f"- **Isolated Acceleration (Equation of Motion):**")
                lines.append(f"  $$\\ddot{{{q}}} = {eq_info['acceleration_latex']}$$\n")

        if self.hamiltonian:
            lines.append("## 2. Hamiltonian Formulation & Canonical Equations\n")
            lines.append(f"**Hamiltonian:**")
            lines.append(f"$$\\mathcal{{H}} = {self.hamiltonian['hamiltonian_latex']}$$\n")
            lines.append("**Hamilton's Canonical Equations:**")
            for h_eq in self.hamiltonian.get("hamiltons_equations", []):
                lines.append(f"- $\\dot{{{h_eq['coord']}}} = \\frac{{\\partial \\mathcal{{H}}}}{{\\partial p_{{{h_eq['coord']}}}}} = {sp.latex(h_eq['dq_dt'])}$")
                lines.append(f"- $\\dot{{p}}_{{{h_eq['coord']}}} = -\\frac{{\\partial \\mathcal{{H}}}}{{\\partial {h_eq['coord']}}} = {sp.latex(h_eq['dp_dt'])}$")
            lines.append("")

        if self.noether_conserved_quantities:
            lines.append("## 3. Noether's Theorem & Conserved Invariants\n")
            for cons in self.noether_conserved_quantities:
                lines.append(f"- **{cons['symmetry']}:** {cons['description']} $\\implies$ **${cons['invariant_symbol']} = {sp.latex(cons['expression'])}$ is Constant**")
            lines.append("")

        return "\n".join(lines)


class VariationalEngine:
    """
    Symbolic engine for variational calculus, Euler-Lagrange derivations,
    Hamiltonian mechanics, and Noether symmetries.
    """

    def __init__(self, context: Optional[VariableContext] = None):
        self.context = context or VariableContext()

    def derive(
        self,
        lagrangian: Union[str, sp.Expr],
        coordinates: List[str],
        time_var: str = "t",
        system_name: str = "Physical System",
        derive_hamiltonian: bool = True
    ) -> VariationalResult:
        """
        Performs full multi-step Euler-Lagrange, Hamiltonian, and Noether derivation.
        """
        t = sp.Symbol(time_var, real=True)
        q_syms = [sp.Symbol(q, real=True) for q in coordinates]
        q_dot_syms = [sp.Symbol(f"{q}_dot", real=True) for q in coordinates]
        q_ddot_syms = [sp.Symbol(f"{q}_ddot", real=True) for q in coordinates]

        # Parse Lagrangian expression
        if isinstance(lagrangian, str):
            L_expr = parse_expression_safely(lagrangian, self.context)
        else:
            L_expr = lagrangian

        steps: List[DerivationStep] = []
        step_num = 1

        # Step 1: Lagrangian Definition
        steps.append(DerivationStep(
            step_number=step_num,
            operation=f"Lagrangian Definition: {system_name}",
            expression=sp.Eq(sp.Symbol("L"), L_expr),
            latex=f"\\mathcal{{L}} = {sp.latex(L_expr)}",
            explanation=f"System Lagrangian defined in terms of generalized coordinates ({', '.join(coordinates)}) and generalized velocities."
        ))
        step_num += 1

        el_equations = []
        for q, q_dot, q_ddot in zip(q_syms, q_dot_syms, q_ddot_syms):
            # 1. Partial wrt q
            dL_dq = sp.diff(L_expr, q)

            # 2. Partial wrt q_dot (generalized momentum)
            dL_dqdot = sp.diff(L_expr, q_dot)

            # 3. Total time derivative d/dt(dL/dqdot)
            # d/dt f(q, q_dot, t) = df/dt + sum (df/dq * q_dot + df/dq_dot * q_ddot)
            d_dt_dL_dqdot = sp.diff(dL_dqdot, t)
            for qi, qi_dot, qi_ddot in zip(q_syms, q_dot_syms, q_ddot_syms):
                d_dt_dL_dqdot += sp.diff(dL_dqdot, qi) * qi_dot + sp.diff(dL_dqdot, qi_dot) * qi_ddot

            d_dt_dL_dqdot = sp.simplify(d_dt_dL_dqdot)

            # 4. Euler-Lagrange equation: d/dt(dL/dqdot) - dL/dq = 0
            el_raw = sp.simplify(d_dt_dL_dqdot - dL_dq)
            el_equation = sp.Eq(el_raw, 0)

            # 5. Isolate acceleration q_ddot if linear in q_ddot
            accel_expr = None
            accel_latex = None
            try:
                accel_sols = sp.solve(el_raw, q_ddot)
                if accel_sols:
                    accel_expr = sp.simplify(accel_sols[0])
                    accel_latex = sp.latex(accel_expr)
            except Exception:
                pass

            el_info = {
                "coord": str(q),
                "dL_dq": dL_dq,
                "dL_dqdot": dL_dqdot,
                "d_dt_dL_dqdot": d_dt_dL_dqdot,
                "raw_equation": el_equation,
                "equation_latex": f"{sp.latex(d_dt_dL_dqdot)} - \\left({sp.latex(dL_dq)}\\right) = 0",
                "isolated_acceleration": accel_expr,
                "acceleration_latex": accel_latex
            }
            el_equations.append(el_info)

            # Record step for this coordinate
            steps.append(DerivationStep(
                step_number=step_num,
                operation=f"Euler-Lagrange Equation for ${q}$",
                expression=el_equation,
                latex=f"\\frac{{d}}{{dt}}\\left(\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{q}}}}}\\right) - \\frac{{\\partial \\mathcal{{L}}}}{{\\partial {q}}} = 0 \\implies {sp.latex(el_raw)} = 0",
                explanation=f"Compute partial derivatives with respect to generalized coordinate ${q}$ and velocity $\\dot{{{q}}}$, then evaluate total time derivative."
            ))
            step_num += 1

            if accel_expr is not None:
                steps.append(DerivationStep(
                    step_number=step_num,
                    operation=f"Equation of Motion for $\\ddot{{{q}}}$",
                    expression=sp.Eq(q_ddot, accel_expr),
                    latex=f"\\ddot{{{q}}} = {accel_latex}",
                    explanation=f"Algebraically isolate generalized acceleration $\\ddot{{{q}}}$."
                ))
                step_num += 1

        # 6. Hamiltonian Formulation
        hamiltonian_info = None
        if derive_hamiltonian:
            try:
                p_syms = [sp.Symbol(f"p_{q}", real=True) for q in coordinates]
                p_eqs = [sp.Eq(p, el["dL_dqdot"]) for p, el in zip(p_syms, el_equations)]

                # Invert q_dot in terms of p
                qdot_solutions = sp.solve(p_eqs, q_dot_syms, dict=True)
                if qdot_solutions:
                    sol_map = qdot_solutions[0]
                    # H = sum(p_i * q_dot_i) - L
                    H_raw = sum(p * sol_map.get(q_dot, q_dot) for p, q_dot in zip(p_syms, q_dot_syms)) - L_expr.subs(sol_map)
                    H_expr = sp.simplify(H_raw)

                    # Compute Hamilton's canonical equations: dq/dt = dH/dp, dp/dt = -dH/dq
                    hamiltons_equations = []
                    for q, p in zip(q_syms, p_syms):
                        dq_dt = sp.simplify(sp.diff(H_expr, p))
                        dp_dt = sp.simplify(-sp.diff(H_expr, q))
                        hamiltons_equations.append({
                            "coord": str(q),
                            "momentum": str(p),
                            "dq_dt": dq_dt,
                            "dp_dt": dp_dt
                        })

                    hamiltonian_info = {
                        "hamiltonian_expr": H_expr,
                        "hamiltonian_latex": sp.latex(H_expr),
                        "conjugate_momenta": {str(q): el["dL_dqdot"] for q, el in zip(q_syms, el_equations)},
                        "hamiltons_equations": hamiltons_equations
                    }

                    steps.append(DerivationStep(
                        step_number=step_num,
                        operation="Hamiltonian Legendre Transformation",
                        expression=sp.Eq(sp.Symbol("H"), H_expr),
                        latex=f"\\mathcal{{H}} = \\sum p_i \\dot{{q}}_i - \\mathcal{{L}} = {sp.latex(H_expr)}",
                        explanation="Perform Legendre transformation to express total energy in terms of generalized coordinates and conjugate momenta."
                    ))
                    step_num += 1
            except Exception:
                pass

        # 7. Noether's Theorem Conserved Quantities
        noether_invariants = []
        # Check cyclic coordinates (dL/dq == 0)
        for q, el in zip(q_syms, el_equations):
            if el["dL_dq"] == 0 or el["dL_dq"].is_zero:
                noether_invariants.append({
                    "symmetry": f"Spatial Invariance / Cyclic Coordinate in ${q}$",
                    "description": f"Lagrangian does not explicitly depend on coordinate ${q}$ ($\\frac{{\\partial \\mathcal{{L}}}}{{\\partial {q}}} = 0$)",
                    "invariant_symbol": f"p_{{{q}}}",
                    "expression": el["dL_dqdot"]
                })

        # Check time invariance (dL/dt == 0)
        dL_dt = sp.diff(L_expr, t)
        if dL_dt == 0 or dL_dt.is_zero:
            noether_invariants.append({
                "symmetry": "Time Translation Invariance",
                "description": f"Lagrangian does not explicitly depend on time $t$ ($\\frac{{\\partial \\mathcal{{L}}}}{{\\partial t}} = 0$)",
                "invariant_symbol": "E \\equiv \\mathcal{H}",
                "expression": hamiltonian_info["hamiltonian_expr"] if hamiltonian_info else sum(q_dot * el["dL_dqdot"] for q_dot, el in zip(q_dot_syms, el_equations)) - L_expr
            })

        return VariationalResult(
            system_name=system_name,
            coordinates=coordinates,
            lagrangian=L_expr,
            lagrangian_latex=sp.latex(L_expr),
            euler_lagrange_equations=el_equations,
            hamiltonian=hamiltonian_info,
            noether_conserved_quantities=noether_invariants,
            steps=steps
        )
