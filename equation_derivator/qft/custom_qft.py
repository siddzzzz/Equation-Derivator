"""
Custom QFT, Dirac Gamma Algebra Traces, and Spinor Bilinears Engine.
Allows users to enter arbitrary gamma matrix products, compute exact traces,
and evaluate relativistic Dirac Hamiltonians for custom mass and momenta.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import sympy as sp

from equation_derivator.qft.dirac import DiracAlgebra


@dataclass
class CustomQFTResult:
    query_type: str
    input_expression: str
    evaluated_result_latex: str
    eigenvalues_latex: Optional[List[str]]
    is_trace_zero: bool
    markdown: str

    def to_dict(self) -> dict:
        return {
            "query_type": self.query_type,
            "input_expression": self.input_expression,
            "evaluated_result_latex": self.evaluated_result_latex,
            "eigenvalues_latex": self.eigenvalues_latex,
            "is_trace_zero": self.is_trace_zero,
            "markdown": self.markdown,
        }


class CustomQFTEngine:
    """
    Evaluates custom gamma matrix expressions, traces, and relativistic Hamiltonians.
    """

    def __init__(self, representation: str = "dirac"):
        self.algebra = DiracAlgebra(representation=representation)

    def evaluate_gamma_expression(
        self,
        expression_str: str,
        compute_trace: bool = True
    ) -> CustomQFTResult:
        """
        Evaluates arbitrary product of gamma matrices like:
        'gamma0 * gamma1 * gamma2 * gamma3' or 'gamma5 * gamma0'
        """
        gamma_dict = {
            "g0": self.algebra.gamma0,
            "g1": self.algebra.gamma1,
            "g2": self.algebra.gamma2,
            "g3": self.algebra.gamma3,
            "g5": self.algebra.gamma5,
            "gamma0": self.algebra.gamma0,
            "gamma1": self.algebra.gamma1,
            "gamma2": self.algebra.gamma2,
            "gamma3": self.algebra.gamma3,
            "gamma5": self.algebra.gamma5,
            "I4": self.algebra.I4,
            "I": sp.I,
        }

        parsed_mat = sp.sympify(expression_str, locals=gamma_dict)
        if not isinstance(parsed_mat, (sp.Matrix, sp.MatrixBase)):
            raise ValueError(f"Expression did not evaluate to a 4x4 Dirac matrix: '{expression_str}'")

        mat_latex = sp.latex(parsed_mat)
        trace_val = sp.simplify(parsed_mat.trace())
        trace_latex = sp.latex(trace_val)
        is_trace_zero = (trace_val == 0)

        # Eigenvalues
        try:
            eigs = [sp.latex(e) for e in parsed_mat.eigenvals().keys()]
        except Exception:
            eigs = None

        md = (
            f"# Custom Dirac Matrix Expression\n\n"
            f"- **Input**: `{expression_str}`\n"
            f"- **Resulting $4 \\times 4$ Matrix**:\n"
            f"$$M = {mat_latex}$$\n\n"
            f"- **Matrix Trace ($\\operatorname{{Tr}}(M)$)**: $$\\operatorname{{Tr}}(M) = {trace_latex}$$\n"
        )
        if eigs:
            md += f"- **Eigenvalues**: ${', '.join(eigs)}$\n"

        return CustomQFTResult(
            query_type="gamma_trace",
            input_expression=expression_str,
            evaluated_result_latex=trace_latex if compute_trace else mat_latex,
            eigenvalues_latex=eigs,
            is_trace_zero=is_trace_zero,
            markdown=md
        )

    def evaluate_dirac_hamiltonian(
        self,
        mass: float = 0.511,
        px: float = 1.0,
        py: float = 0.0,
        pz: float = 0.0
    ) -> CustomQFTResult:
        """
        Dirac Hamiltonian H = alpha . p + beta * m where:
        alpha_i = gamma0 * gamma_i, beta = gamma0.
        """
        a1 = self.algebra.gamma0 * self.algebra.gamma1
        a2 = self.algebra.gamma0 * self.algebra.gamma2
        a3 = self.algebra.gamma0 * self.algebra.gamma3
        beta = self.algebra.gamma0

        H = a1 * px + a2 * py + a3 * pz + beta * mass
        H_simp = sp.simplify(H)

        p_sq = px**2 + py**2 + pz**2
        E_exact = sp.sqrt(p_sq + mass**2)
        E_val = round(float(sp.N(E_exact)), 6)

        eigs_latex = [f"+{E_val} \\text{{ (electron spin up/down)}}", f"-{E_val} \\text{{ (positron spin up/down)}}"]

        md = (
            f"# Relativistic Dirac Hamiltonian: $H = \\boldsymbol{{\\alpha}}\\cdot\\mathbf{{p}} + \\beta m$\n\n"
            f"- **Mass $m$**: `{mass}`\n"
            f"- **Momentum $\\mathbf{{p}}$**: $({px}, {py}, {pz})$\n"
            f"- **Dispersion Invariant**: $$E = \\pm\\sqrt{{|\\mathbf{{p}}|^2 + m^2}} = \\pm {E_val}$$\n\n"
            f"## $4\\times 4$ Hamiltonian Matrix\n"
            f"$$H = {sp.latex(H_simp)}$$\n"
        )

        return CustomQFTResult(
            query_type="dirac_hamiltonian",
            input_expression=f"m={mass}, p=({px},{py},{pz})",
            evaluated_result_latex=f"E = \\pm {E_val}",
            eigenvalues_latex=eigs_latex,
            is_trace_zero=True,
            markdown=md
        )
