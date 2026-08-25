"""
Dirac Gamma Matrix Algebra, Spinors, and Relativistic Wave Equations.
Supports Dirac-Pauli, Weyl (Chiral), and Majorana matrix representations.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class DiracSpinorResult:
    representation: str
    gamma_matrices_latex: Dict[str, str]
    gamma5_latex: str
    clifford_anticommutators_valid: bool
    spinors_latex: Dict[str, str]
    spin_sum_u_latex: str
    spin_sum_v_latex: str
    chiral_projectors_valid: bool
    markdown: str

    def to_dict(self) -> dict:
        return {
            "representation": self.representation,
            "gamma_matrices_latex": self.gamma_matrices_latex,
            "gamma5_latex": self.gamma5_latex,
            "clifford_anticommutators_valid": self.clifford_anticommutators_valid,
            "spinors_latex": self.spinors_latex,
            "spin_sum_u_latex": self.spin_sum_u_latex,
            "spin_sum_v_latex": self.spin_sum_v_latex,
            "chiral_projectors_valid": self.chiral_projectors_valid,
            "markdown": self.markdown,
        }


class DiracAlgebra:
    """
    Symbolic 4x4 Dirac matrix and Clifford algebra engine.
    """

    def __init__(self, representation: str = "dirac"):
        self.representation = representation.lower()
        self.gamma0, self.gamma1, self.gamma2, self.gamma3, self.gamma5 = self._build_gamma_matrices()
        self.gammas = [self.gamma0, self.gamma1, self.gamma2, self.gamma3]
        self.eta = sp.diag(1, -1, -1, -1)
        self.I4 = sp.eye(4)

    def _build_gamma_matrices(self) -> Tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
        # Pauli matrices sigma_i
        sigma_0 = sp.eye(2)
        sigma_1 = sp.Matrix([[0, 1], [1, 0]])
        sigma_2 = sp.Matrix([[0, -sp.I], [sp.I, 0]])
        sigma_3 = sp.Matrix([[1, 0], [0, -1]])
        zero_2 = sp.zeros(2, 2)

        if self.representation in ("dirac", "dirac-pauli", "standard"):
            # Standard Dirac-Pauli Representation
            g0 = sp.BlockMatrix([[sigma_0, zero_2], [zero_2, -sigma_0]]).as_explicit()
            g1 = sp.BlockMatrix([[zero_2, sigma_1], [-sigma_1, zero_2]]).as_explicit()
            g2 = sp.BlockMatrix([[zero_2, sigma_2], [-sigma_2, zero_2]]).as_explicit()
            g3 = sp.BlockMatrix([[zero_2, sigma_3], [-sigma_3, zero_2]]).as_explicit()
            g5 = sp.BlockMatrix([[zero_2, sigma_0], [sigma_0, zero_2]]).as_explicit()
        elif self.representation in ("weyl", "chiral"):
            # Chiral / Weyl Representation (gamma5 is diagonal)
            g0 = sp.BlockMatrix([[zero_2, sigma_0], [sigma_0, zero_2]]).as_explicit()
            g1 = sp.BlockMatrix([[zero_2, sigma_1], [-sigma_1, zero_2]]).as_explicit()
            g2 = sp.BlockMatrix([[zero_2, sigma_2], [-sigma_2, zero_2]]).as_explicit()
            g3 = sp.BlockMatrix([[zero_2, sigma_3], [-sigma_3, zero_2]]).as_explicit()
            g5 = sp.BlockMatrix([[-sigma_0, zero_2], [zero_2, sigma_0]]).as_explicit()
        elif self.representation == "majorana":
            # Majorana Representation (all gammas are purely imaginary)
            g0 = sp.BlockMatrix([[zero_2, sigma_2], [sigma_2, zero_2]]).as_explicit()
            g1 = sp.BlockMatrix([[sp.I * sigma_3, zero_2], [zero_2, sp.I * sigma_3]]).as_explicit()
            g2 = sp.BlockMatrix([[zero_2, -sigma_2], [sigma_2, zero_2]]).as_explicit()
            g3 = sp.BlockMatrix([[-sp.I * sigma_1, zero_2], [zero_2, -sp.I * sigma_1]]).as_explicit()
            g5 = sp.BlockMatrix([[sigma_2, zero_2], [zero_2, -sigma_2]]).as_explicit()
        else:
            raise ValueError(f"Unknown Dirac representation: '{self.representation}'")

        return g0, g1, g2, g3, g5

    def verify_clifford_algebra(self) -> bool:
        """
        Verifies that {gamma^mu, gamma^nu} = gamma^mu gamma^nu + gamma^nu gamma^mu == 2 eta^{mu nu} I_4.
        """
        for mu in range(4):
            for nu in range(4):
                anticomm = self.gammas[mu] * self.gammas[nu] + self.gammas[nu] * self.gammas[mu]
                expected = 2 * self.eta[mu, nu] * self.I4
                if anticomm != expected:
                    return False
        return True

    def get_chiral_projectors(self) -> Tuple[sp.Matrix, sp.Matrix]:
        """
        P_L = 1/2 (I - gamma^5), P_R = 1/2 (I + gamma^5)
        """
        P_L = sp.Rational(1, 2) * (self.I4 - self.gamma5)
        P_R = sp.Rational(1, 2) * (self.I4 + self.gamma5)
        return P_L, P_R

    def slash(self, p_vec: Union[List[sp.Expr], sp.Matrix]) -> sp.Matrix:
        """
        Feynman slash notation: p_slash = gamma^mu p_mu = gamma^0 p_0 - gamma^1 p_1 - gamma^2 p_2 - gamma^3 p_3.
        """
        p0, p1, p2, p3 = p_vec[0], p_vec[1], p_vec[2], p_vec[3]
        return self.gamma0 * p0 - self.gamma1 * p1 - self.gamma2 * p2 - self.gamma3 * p3

    def compute_trace(self, matrix_expr: sp.Matrix) -> sp.Expr:
        """
        Computes the trace of a 4x4 matrix expression: Tr(M).
        """
        return sp.simplify(matrix_expr.trace())


def evaluate_dirac_equation(representation: str = "dirac") -> DiracSpinorResult:
    algebra = DiracAlgebra(representation=representation)
    is_clifford = algebra.verify_clifford_algebra()

    P_L, P_R = algebra.get_chiral_projectors()
    # Check projection idempotency: P_L^2 = P_L, P_R^2 = P_R, P_L P_R = 0
    chiral_valid = (
        (P_L * P_L == P_L) and
        (P_R * P_R == P_R) and
        (P_L * P_R == sp.zeros(4, 4))
    )

    g_latex = {
        "\\gamma^0": sp.latex(algebra.gamma0),
        "\\gamma^1": sp.latex(algebra.gamma1),
        "\\gamma^2": sp.latex(algebra.gamma2),
        "\\gamma^3": sp.latex(algebra.gamma3),
    }
    g5_latex = sp.latex(algebra.gamma5)

    # Rest frame spinors u^(1), u^(2), v^(1), v^(2)
    m = sp.Symbol("m", positive=True, real=True)
    spinors = {
        "u^{(1)}(0)": "\\sqrt{2m} \\begin{pmatrix} 1 \\\\ 0 \\\\ 0 \\\\ 0 \\end{pmatrix}",
        "u^{(2)}(0)": "\\sqrt{2m} \\begin{pmatrix} 0 \\\\ 1 \\\\ 0 \\\\ 0 \\end{pmatrix}",
        "v^{(1)}(0)": "\\sqrt{2m} \\begin{pmatrix} 0 \\\\ 0 \\\\ 1 \\\\ 0 \\end{pmatrix}",
        "v^{(2)}(0)": "\\sqrt{2m} \\begin{pmatrix} 0 \\\\ 0 \\\\ 0 \\\\ 1 \\end{pmatrix}",
    }

    spin_u = "\\sum_{s=1}^2 u^{(s)}(p) \\bar{u}^{(s)}(p) = \\not{p} + m"
    spin_v = "\\sum_{s=1}^2 v^{(s)}(p) \\bar{v}^{(s)}(p) = \\not{p} - m"

    md = (
        f"# Dirac Spinor & Clifford Algebra: {representation.capitalize()} Representation\n\n"
        f"## Gamma Matrices\n"
        f"$$\\gamma^0 = {g_latex['\\gamma^0']}, \\quad \\gamma^1 = {g_latex['\\gamma^1']}$$\n"
        f"$$\\gamma^2 = {g_latex['\\gamma^2']}, \\quad \\gamma^3 = {g_latex['\\gamma^3']}$$\n"
        f"$$\\gamma^5 = i\\gamma^0\\gamma^1\\gamma^2\\gamma^3 = {g5_latex}$$\n\n"
        f"## Clifford Algebra Verification\n"
        f"$$\\{{\\gamma^\\mu, \\gamma^\\nu\\}} = 2\\eta^{{\\mu\\nu}} \\mathbb{{I}}_4 \\quad \\text{{[Valid: {is_clifford}]}}$$\n\n"
        f"## Completeness Relations (Spin Sums)\n"
        f"$${spin_u}$$\n"
        f"$${spin_v}$$\n\n"
        f"## Chiral Projectors\n"
        f"$$P_L = \\frac{{1 - \\gamma^5}}{{2}}, \\quad P_R = \\frac{{1 + \\gamma^5}}{{2}} \\quad \\text{{[Idempotent: {chiral_valid}]}}$$\n"
    )

    return DiracSpinorResult(
        representation=representation,
        gamma_matrices_latex=g_latex,
        gamma5_latex=g5_latex,
        clifford_anticommutators_valid=is_clifford,
        spinors_latex=spinors,
        spin_sum_u_latex=spin_u,
        spin_sum_v_latex=spin_v,
        chiral_projectors_valid=chiral_valid,
        markdown=md
    )
