"""
Natural Language Physics Query Interpreter & Dispatcher.
Parses natural language physics requests and dispatches to the appropriate
symbolic engine (Derivation, Variational, Differential, Tensor, Verifier, or Synthesis).
"""

import re
from typing import Dict, Any, Optional

from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.calculus.variational import VariationalEngine
from equation_derivator.calculus.differential import DifferentialEquationSolver
from equation_derivator.calculus.tensors import SpacetimeTensorEngine
from equation_derivator.verifier.verifier import EquationVerifier
from equation_derivator.discovery.discovery_engine import DiscoveryEngine
from equation_derivator.core.equation import PhysicalEquation


class PhysicsQueryDispatcher:
    """
    Interprets natural language queries and executes the appropriate theoretical physics engine.
    """

    def __init__(self):
        self.deriv_engine = DerivationEngine()
        self.var_engine = VariationalEngine()
        self.diff_engine = DifferentialEquationSolver()
        self.tensor_engine = SpacetimeTensorEngine()
        self.verifier = EquationVerifier()
        self.discovery = DiscoveryEngine()

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main query processing entry point.
        """
        q = query.strip().lower()

        # 1. Variational / Euler-Lagrange / Lagrangian queries
        if any(w in q for w in ["euler", "lagrange", "lagrangian", "hamiltonian", "noether", "pendulum"]):
            if "double pendulum" in q:
                # Double pendulum Lagrangian
                L_str = "1/2*(m1+m2)*l1^2*th1_dot^2 + 1/2*m2*l2^2*th2_dot^2 + m2*l1*l2*th1_dot*th2_dot*cos(th1-th2) + (m1+m2)*g*l1*cos(th1) + m2*g*l2*cos(th2)"
                res = self.var_engine.derive(L_str, coordinates=["th1", "th2"], system_name="Double Pendulum")
            elif "pendulum" in q:
                # Simple pendulum
                L_str = "1/2 * m * L^2 * theta_dot^2 - m * g * L * (1 - cos(theta))"
                res = self.var_engine.derive(L_str, coordinates=["theta"], system_name="Simple Pendulum")
            elif "harmonic" in q or "spring" in q:
                L_str = "1/2 * m * x_dot^2 - 1/2 * k * x^2"
                res = self.var_engine.derive(L_str, coordinates=["x"], system_name="Harmonic Oscillator")
            else:
                # Default simple pendulum or extract custom
                L_str = "1/2 * m * x_dot^2 - 1/2 * k * x^2"
                res = self.var_engine.derive(L_str, coordinates=["x"], system_name="Variational System")

            return {
                "type": "variational",
                "title": f"Euler-Lagrange Derivation: {res.system_name}",
                "result": res,
                "markdown": res.to_markdown()
            }

        # 2. General Relativity & Tensor Curvature queries
        if any(w in q for w in ["tensor", "curvature", "schwarzschild", "metric", "christoffel", "riemann", "ricci", "flrw", "geodesic", "einstein tensor"]):
            if "schwarzschild" in q or "black hole" in q:
                res = self.tensor_engine.create_schwarzschild_metric()
            elif "flrw" in q or "cosmology" in q or "expanding" in q:
                res = self.tensor_engine.create_flrw_metric()
            else:
                res = self.tensor_engine.create_minkowski_metric()

            return {
                "type": "tensor",
                "title": f"Tensor Curvature: {res.metric_name}",
                "result": res,
                "markdown": res.to_markdown()
            }

        # 3. Differential Equations & Quantum Systems
        if any(w in q for w in ["schrodinger", "schrödinger", "infinite well", "potential well", "quantum well"]):
            res = self.diff_engine.solve_quantum_infinite_well()
            return {
                "type": "differential",
                "title": "Quantum Infinite Well TISE",
                "result": res,
                "markdown": res.to_markdown()
            }

        if any(w in q for w in ["damped", "oscillator", "differential equation", "ode", "harmonic"]):
            res = self.diff_engine.solve_damped_harmonic_oscillator()
            return {
                "type": "differential",
                "title": "Damped Harmonic Oscillator ODE",
                "result": res,
                "markdown": res.to_markdown()
            }

        # 4. Equation Verification queries
        if q.startswith("verify") or "verify" in q or "=" in q:
            eq_str = query.replace("verify", "", 1).strip()
            if not eq_str and "=" in query:
                eq_str = query.strip()
            if eq_str:
                eq_obj = PhysicalEquation.create(id="nlp_verify", name="Proposed Equation", domain="General Physics", equation_str=eq_str)
                report = self.verifier.verify_equation(eq_obj)
                return {
                    "type": "verifier",
                    "title": f"Equation Verification: {eq_str}",
                    "equation": eq_str,
                    "valid": report["overall_valid"],
                    "report": report,
                    "markdown": f"# Verification Report: ${sp.latex(eq_obj.sympy_eq)}$\n\n- **Overall Status:** {'✔ VALID & SOUND' if report['overall_valid'] else '⚠ FAILED'}\n- **Dimensional Check:** {report['dimensional_check']['message']}\n- **Symbolic Identity:** {report['symbolic_check']['message']}\n- **Monte Carlo Bounds:** {report['numerical_check']['message']}"
                }

        # 5. Dimensional Synthesis / Buckingham Pi Discovery
        if any(w in q for w in ["planck", "synthesize", "discover", "scaling law", "buckingham"]):
            if "length" in q:
                target = "Length"
            elif "time" in q:
                target = "Time"
            elif "mass" in q:
                target = "Mass"
            else:
                target = "Length"

            relations = self.discovery.synthesize_dimensional_relation(["G", "hbar", "c"], target_dimension_or_quantity=target)
            md_lines = [f"# Dimensional Synthesis: Scaling for {target}\n"]
            for r in relations:
                md_lines.append(f"### {r.name}")
                md_lines.append(f"$${r.latex}$$\n")
                md_lines.append(f"- **Dimension:** `{r.dimension}`")
                md_lines.append(f"- **Notes:** {r.notes}\n")

            return {
                "type": "discovery",
                "title": f"Synthesized Relations for {target}",
                "relations": [r.to_dict() for r in relations],
                "markdown": "\n".join(md_lines)
            }

        # 6. Default: Multi-Step Derivation
        # Parse patterns like "derive K from p, m" or "derive kinetic energy in terms of momentum"
        target = "K"
        in_terms_of = ["p", "m"]

        if "escape velocity" in q:
            target = "v"
            in_terms_of = ["G", "M", "r"]
        elif "power" in q and "resistance" in q:
            target = "P"
            in_terms_of = ["I", "R"]
        elif "energy" in q and "momentum" in q:
            target = "K"
            in_terms_of = ["p", "m"]
        elif "from" in q:
            parts = q.replace("derive", "").split("from")
            if len(parts) == 2:
                target = parts[0].strip()
                in_terms_of = [s.strip() for s in parts[1].split(",") if s.strip()]

        res = self.deriv_engine.derive(target_variable=target, in_terms_of=in_terms_of)
        return {
            "type": "derivation",
            "title": f"Derivation for {target}",
            "result": res.to_dict(),
            "markdown": res.to_markdown()
        }
