"""
Custom Lie Algebra, Commutator Matrix Table & Gauge Symmetry Engine.
Allows users to enter arbitrary matrix generators T_1, ..., T_k, compute all commutators,
extract structure constants f^{abc}, verify Jacobi identities, and compute Casimir invariants.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import sympy as sp

from equation_derivator.symmetry.lie_algebra import LieAlgebra, LieAlgebraResult


@dataclass
class CustomLieAlgebraResult:
    algebra_name: str
    dimension: int
    matrix_size: int
    generators_latex: Dict[str, str]
    commutator_table_latex: Dict[str, str]
    structure_constants_latex: Dict[str, str]
    casimir_operator_latex: str
    is_jacobi_identity_satisfied: bool
    is_all_traceless: bool
    is_all_hermitian: bool
    markdown: str

    def to_dict(self) -> dict:
        return {
            "algebra_name": self.algebra_name,
            "dimension": self.dimension,
            "matrix_size": self.matrix_size,
            "generators_latex": self.generators_latex,
            "commutator_table_latex": self.commutator_table_latex,
            "structure_constants_latex": self.structure_constants_latex,
            "casimir_operator_latex": self.casimir_operator_latex,
            "is_jacobi_identity_satisfied": self.is_jacobi_identity_satisfied,
            "is_all_traceless": self.is_all_traceless,
            "is_all_hermitian": self.is_all_hermitian,
            "markdown": self.markdown,
        }


class CustomLieAlgebraEngine:
    """
    Evaluates custom user-defined matrix Lie algebras.
    """

    @staticmethod
    def parse_matrices(input_data: Union[str, List[List[List[Any]]]]) -> List[sp.Matrix]:
        """
        Parses list of matrices from JSON string, semicolon string, or raw list.
        Example: '[[0, 1], [1, 0]]; [[0, -I], [I, 0]]; [[1, 0], [0, -1]]'
        """
        if isinstance(input_data, str):
            clean_str = input_data.strip()
            # Try JSON first
            if clean_str.startswith("[") and clean_str.endswith("]"):
                try:
                    raw_list = json.loads(clean_str)
                    if isinstance(raw_list[0][0], list):
                        # List of matrices
                        return [sp.Matrix(m) for m in raw_list]
                    else:
                        # Single matrix
                        return [sp.Matrix(raw_list)]
                except Exception:
                    pass

            # Semicolon separated matrices
            parts = [p.strip() for p in clean_str.split(";") if p.strip()]
            matrices = []
            for p in parts:
                mat_expr = sp.sympify(p)
                if isinstance(mat_expr, (list, tuple)):
                    matrices.append(sp.Matrix(mat_expr))
                elif isinstance(mat_expr, sp.Matrix):
                    matrices.append(mat_expr)
                else:
                    raise ValueError(f"Could not parse matrix generator: '{p}'")
            return matrices
        elif isinstance(input_data, list):
            return [sp.Matrix(m) for m in input_data]
        else:
            raise ValueError(f"Unsupported matrix input format: {type(input_data)}")

    def evaluate_custom_algebra(
        self,
        generators_input: Union[str, List[Any]],
        algebra_name: str = "Custom Lie Algebra"
    ) -> CustomLieAlgebraResult:
        generators = self.parse_matrices(generators_input)
        if not generators:
            raise ValueError("No matrix generators provided")

        dim = len(generators)
        matrix_size = generators[0].shape[0]

        # Verify all matrices have matching square dimensions
        for i, g in enumerate(generators):
            if g.shape[0] != matrix_size or g.shape[1] != matrix_size:
                raise ValueError(f"Generator T_{i+1} has invalid shape {g.shape}, expected ({matrix_size}, {matrix_size})")

        # 1. Tracelessness & Hermiticity
        all_traceless = all(sp.simplify(g.trace()) == 0 for g in generators)
        all_hermitian = all(g.H == g for g in generators)

        # 2. Commutator Table & Structure Constants
        comm_table = {}
        struct_consts = {}
        for a in range(dim):
            for b in range(a + 1, dim):
                Ta, Tb = generators[a], generators[b]
                comm = sp.simplify(Ta * Tb - Tb * Ta)
                comm_key = f"[T_{a+1}, T_{b+1}]"
                comm_table[comm_key] = sp.latex(comm)

                # Try projecting onto generators to find f^{abc}
                # If basis is orthogonal with respect to trace: Tr(Ta Tb)
                for c in range(dim):
                    Tc = generators[c]
                    norm = sp.simplify((Tc * Tc).trace())
                    if norm != 0:
                        proj = sp.simplify((comm * Tc).trace() / norm)
                        if proj != 0:
                            struct_consts[f"f^{{{a+1},{b+1},{c+1}}}"] = sp.latex(proj)

        # 3. Jacobi Identity Verification [[Ta, Tb], Tc] + [[Tb, Tc], Ta] + [[Tc, Ta], Tb] == 0
        jacobi_valid = True
        for a in range(dim):
            for b in range(dim):
                for c in range(dim):
                    Ta, Tb, Tc = generators[a], generators[b], generators[c]
                    c_ab = Ta * Tb - Tb * Ta
                    c_bc = Tb * Tc - Tc * Tb
                    c_ca = Tc * Ta - Ta * Tc
                    jacobi = (c_ab * Tc - Tc * c_ab) + (c_bc * Ta - Ta * c_bc) + (c_ca * Tb - Tb * c_ca)
                    if sp.simplify(jacobi) != sp.zeros(matrix_size, matrix_size):
                        jacobi_valid = False
                        break

        # 4. Quadratic Casimir C_2 = sum Ta^2
        casimir = sp.zeros(matrix_size, matrix_size)
        for g in generators:
            casimir += g * g
        casimir = sp.simplify(casimir)
        casimir_latex = sp.latex(casimir)

        gen_latex = {f"T_{i+1}": sp.latex(g) for i, g in enumerate(generators)}

        md = (
            f"# {algebra_name} Analysis\n\n"
            f"- **Dimension (Number of Generators)**: {dim}\n"
            f"- **Matrix Representation Size**: ${matrix_size} \\times {matrix_size}$\n"
            f"- **Jacobi Identity Satisfied**: `{jacobi_valid}`\n"
            f"- **All Traceless ($\\operatorname{{Tr}}(T)=0$)**: `{all_traceless}`\n"
            f"- **All Hermitian ($T^\\dagger = T$)**: `{all_hermitian}`\n\n"
            f"## Quadratic Casimir Operator\n"
            f"$$C_2 = \\sum_{{a=1}}^{{{dim}}} T_a^2 = {casimir_latex}$$\n"
        )

        return CustomLieAlgebraResult(
            algebra_name=algebra_name,
            dimension=dim,
            matrix_size=matrix_size,
            generators_latex=gen_latex,
            commutator_table_latex=comm_table,
            structure_constants_latex=struct_consts,
            casimir_operator_latex=casimir_latex,
            is_jacobi_identity_satisfied=jacobi_valid,
            is_all_traceless=all_traceless,
            is_all_hermitian=all_hermitian,
            markdown=md
        )
