"""
Lie Algebra Generators, Commutators, and Structure Constants.
Supports SU(2) (spin / weak isospin) and SU(3) (color charge / Gell-Mann matrices).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class LieAlgebraResult:
    group_name: str
    dimension: int
    generators_latex: Dict[str, str]
    structure_constants: Dict[Tuple[int, int, int], Union[int, float, str]]
    casimir_operator_latex: str
    commutation_relations_latex: List[str]
    markdown: str

    def to_dict(self) -> dict:
        return {
            "group_name": self.group_name,
            "dimension": self.dimension,
            "generators_latex": self.generators_latex,
            "structure_constants": {f"f^{{{k[0]},{k[1]},{k[2]}}}": v for k, v in self.structure_constants.items()},
            "casimir_operator_latex": self.casimir_operator_latex,
            "commutation_relations_latex": self.commutation_relations_latex,
            "markdown": self.markdown,
        }


class LieAlgebra:
    """
    Base class for matrix Lie algebra representations.
    """

    def __init__(self, name: str, generators: List[sp.Matrix]):
        self.name = name
        self.generators = generators
        self.dim = len(generators)
        self.matrix_dim = generators[0].shape[0]

    def commutator(self, Ta: sp.Matrix, Tb: sp.Matrix) -> sp.Matrix:
        """
        [Ta, Tb] = Ta * Tb - Tb * Ta.
        """
        return sp.simplify(Ta * Tb - Tb * Ta)

    def compute_casimir(self) -> sp.Matrix:
        """
        Quadratic Casimir C_2 = sum_a T^a T^a.
        """
        c2 = sp.zeros(self.matrix_dim, self.matrix_dim)
        for Ta in self.generators:
            c2 += Ta * Ta
        return sp.simplify(c2)

    def verify_generators_traceless_hermitian(self) -> Tuple[bool, bool]:
        all_traceless = all(sp.simplify(Ta.trace()) == 0 for Ta in self.generators)
        all_hermitian = all(Ta.H == Ta for Ta in self.generators)
        return all_traceless, all_hermitian


class SU2Algebra(LieAlgebra):
    """
    SU(2) Lie Algebra with spin-1/2 Pauli generators J_a = 1/2 sigma_a:
    [J_i, J_j] = i epsilon_{ijk} J_k.
    """

    def __init__(self):
        sigma_1 = sp.Matrix([[0, 1], [1, 0]])
        sigma_2 = sp.Matrix([[0, -sp.I], [sp.I, 0]])
        sigma_3 = sp.Matrix([[1, 0], [0, -1]])
        generators = [sp.Rational(1, 2) * s for s in [sigma_1, sigma_2, sigma_3]]
        super().__init__("SU(2)", generators)

    def evaluate(self) -> LieAlgebraResult:
        g_latex = {
            "J_1": sp.latex(self.generators[0]),
            "J_2": sp.latex(self.generators[1]),
            "J_3": sp.latex(self.generators[2]),
        }
        casimir = self.compute_casimir()
        casimir_latex = sp.latex(casimir)

        comm_latex = [
            r"[J_1, J_2] = i J_3",
            r"[J_2, J_3] = i J_1",
            r"[J_3, J_1] = i J_2",
        ]

        struct_consts = {
            (1, 2, 3): 1,
            (2, 3, 1): 1,
            (3, 1, 2): 1,
            (2, 1, 3): -1,
            (3, 2, 1): -1,
            (1, 3, 2): -1,
        }

        md = rf"""# $\mathfrak{{su}}(2)$ Lie Algebra (Spin & Weak Isospin)

## Generators ($J_a = \frac{{1}}{{2}}\sigma_a$)
$$J_1 = {g_latex['J_1']}, \quad J_2 = {g_latex['J_2']}, \quad J_3 = {g_latex['J_3']}$$

## Lie Commutation Relations
$$\left[ J_i, J_j \right] = i \varepsilon_{{ijk}} J_k$$

## Quadratic Casimir Invariant
$$C_2 = \sum_{{a=1}}^3 J_a^2 = {casimir_latex} = \frac{{3}}{{4}} \mathbb{{I}}_2 \implies j(j+1)\hbar^2 \quad \left(j = \frac{{1}}{{2}}\right)$$
"""

        return LieAlgebraResult(
            group_name="SU(2)",
            dimension=3,
            generators_latex=g_latex,
            structure_constants=struct_consts,
            casimir_operator_latex=casimir_latex,
            commutation_relations_latex=comm_latex,
            markdown=md
        )


class SU3Algebra(LieAlgebra):
    """
    SU(3) Lie Algebra with 8 Gell-Mann generators T_a = 1/2 lambda_a:
    [T_a, T_b] = i f^{abc} T_c.
    """

    def __init__(self):
        # 8 Gell-Mann matrices lambda_1 ... lambda_8
        l1 = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
        l2 = sp.Matrix([[0, -sp.I, 0], [sp.I, 0, 0], [0, 0, 0]])
        l3 = sp.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]])
        l4 = sp.Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]])
        l5 = sp.Matrix([[0, 0, -sp.I], [0, 0, 0], [sp.I, 0, 0]])
        l6 = sp.Matrix([[0, 0, 0], [0, 0, 1], [0, 1, 0]])
        l7 = sp.Matrix([[0, 0, 0], [0, 0, -sp.I], [0, sp.I, 0]])
        l8 = sp.Rational(1, 1) * sp.Matrix([[1, 0, 0], [0, 1, 0], [0, 0, -2]]) / sp.sqrt(3)

        generators = [sp.Rational(1, 2) * l for l in [l1, l2, l3, l4, l5, l6, l7, l8]]
        super().__init__("SU(3)", generators)

    def evaluate(self) -> LieAlgebraResult:
        g_latex = {f"T_{i+1}": sp.latex(Ta) for i, Ta in enumerate(self.generators)}
        casimir = self.compute_casimir()
        casimir_latex = sp.latex(casimir)

        comm_latex = [
            r"[T_a, T_b] = i f^{abc} T_c",
            r"\text{Totally antisymmetric structure constants } f^{abc}:",
            r"f^{123}=1, \quad f^{147}=f^{246}=f^{257}=f^{345}=f^{516}=f^{637}=\frac{1}{2}, \quad f^{458}=f^{678}=\frac{\sqrt{3}}{2}"
        ]

        struct_consts = {
            (1, 2, 3): 1.0,
            (1, 4, 7): 0.5,
            (2, 4, 6): 0.5,
            (2, 5, 7): 0.5,
            (3, 4, 5): 0.5,
            (5, 1, 6): 0.5,
            (6, 3, 7): 0.5,
            (4, 5, 8): round(float(sp.sqrt(3)/2), 4),
            (6, 7, 8): round(float(sp.sqrt(3)/2), 4),
        }

        md = rf"""# $\mathfrak{{su}}(3)$ Lie Algebra (Color Charge & Quantum Chromodynamics)

## 8 Gell-Mann Generators ($T_a = \frac{{1}}{{2}}\lambda_a$)
- Dimension: $N^2 - 1 = 8$ gluons
- Traceless & Hermitian: $\operatorname{{Tr}}(T_a) = 0, \; T_a^\dagger = T_a$

## Quadratic Casimir Operator
$$C_2 = \sum_{{a=1}}^8 T_a^2 = {casimir_latex} = \frac{{4}}{{3}} \mathbb{{I}}_3$$
"""

        return LieAlgebraResult(
            group_name="SU(3)",
            dimension=8,
            generators_latex=g_latex,
            structure_constants=struct_consts,
            casimir_operator_latex=casimir_latex,
            commutation_relations_latex=comm_latex,
            markdown=md
        )
