"""
Differential Forms and Exterior Calculus Engine.
Provides symbolic wedge product, exterior derivative (d), and Hodge star (star).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import itertools
import sympy as sp


@dataclass
class DifferentialFormResult:
    degree: int
    coordinates: List[str]
    components: Dict[Tuple[int, ...], str]
    latex: str
    markdown: str

    def to_dict(self) -> dict:
        return {
            "degree": self.degree,
            "coordinates": self.coordinates,
            "components": {str(k): v for k, v in self.components.items()},
            "latex": self.latex,
            "markdown": self.markdown,
        }


class DifferentialForm:
    """
    Represents a symbolic p-form on an n-dimensional manifold:
    omega = sum_{i_1 < i_2 < ... < i_p} a_{i_1 ... i_p}(x) dx^{i_1} ^ ... ^ dx^{i_p}.
    """

    def __init__(
        self,
        degree: int,
        components: Dict[Tuple[int, ...], sp.Expr],
        coordinates: List[str]
    ):
        self.degree = degree
        self.coordinates = coordinates
        self.dim = len(coordinates)
        self.components: Dict[Tuple[int, ...], sp.Expr] = {}

        # Canonicalize component index tuples into sorted order with parity signs
        for raw_indices, coeff in components.items():
            coeff_simp = sp.simplify(coeff)
            if coeff_simp == 0 or coeff_simp.is_zero:
                continue

            sorted_idx, sign = self._canonicalize_indices(raw_indices)
            if sign != 0:
                self.components[sorted_idx] = self.components.get(sorted_idx, sp.S.Zero) + sign * coeff_simp

        # Purge any zeros that canceled out
        self.components = {k: sp.simplify(v) for k, v in self.components.items() if sp.simplify(v) != 0 and not sp.simplify(v).is_zero}

    @staticmethod
    def _canonicalize_indices(indices: Tuple[int, ...]) -> Tuple[Tuple[int, ...], int]:
        """
        Sorts indices and computes permutation parity. If duplicates exist, returns sign = 0.
        """
        idx_list = list(indices)
        if len(idx_list) != len(set(idx_list)):
            return indices, 0

        # Bubble sort count inversions
        n = len(idx_list)
        swaps = 0
        for i in range(n):
            for j in range(0, n - i - 1):
                if idx_list[j] > idx_list[j + 1]:
                    idx_list[j], idx_list[j + 1] = idx_list[j + 1], idx_list[j]
                    swaps += 1

        sign = -1 if (swaps % 2 == 1) else 1
        return tuple(idx_list), sign

    def __add__(self, other: DifferentialForm) -> DifferentialForm:
        if self.degree != other.degree or self.coordinates != other.coordinates:
            raise ValueError("Cannot add differential forms of different degrees or coordinate systems")

        new_comps = dict(self.components)
        for k, v in other.components.items():
            new_comps[k] = new_comps.get(k, sp.S.Zero) + v
        return DifferentialForm(self.degree, new_comps, self.coordinates)

    def __sub__(self, other: DifferentialForm) -> DifferentialForm:
        if self.degree != other.degree or self.coordinates != other.coordinates:
            raise ValueError("Cannot subtract differential forms of different degrees or coordinate systems")

        new_comps = dict(self.components)
        for k, v in other.components.items():
            new_comps[k] = new_comps.get(k, sp.S.Zero) - v
        return DifferentialForm(self.degree, new_comps, self.coordinates)

    def wedge(self, other: DifferentialForm) -> DifferentialForm:
        """
        Wedge product: (alpha ^ beta) of degrees p and q yielding a (p+q)-form.
        """
        if self.coordinates != other.coordinates:
            raise ValueError("Coordinate systems must match for wedge product")

        p = self.degree
        q = other.degree
        total_deg = p + q

        if total_deg > self.dim:
            # Any form of degree > dim vanishes identically
            return DifferentialForm(total_deg, {}, self.coordinates)

        new_comps: Dict[Tuple[int, ...], sp.Expr] = {}
        for idx_a, coeff_a in self.components.items():
            for idx_b, coeff_b in other.components.items():
                combined = idx_a + idx_b
                sorted_idx, sign = self._canonicalize_indices(combined)
                if sign != 0:
                    prod = sp.simplify(sign * coeff_a * coeff_b)
                    new_comps[sorted_idx] = new_comps.get(sorted_idx, sp.S.Zero) + prod

        return DifferentialForm(total_deg, new_comps, self.coordinates)

    def exterior_derivative(self) -> DifferentialForm:
        """
        Exterior derivative d(omega): d(sum a_I dx^I) = sum_mu (da_I / dx^mu) dx^mu ^ dx^I.
        Satisfies d^2 = 0.
        """
        x_syms = [sp.Symbol(c, real=True) for c in self.coordinates]
        next_deg = self.degree + 1

        if next_deg > self.dim:
            return DifferentialForm(next_deg, {}, self.coordinates)

        new_comps: Dict[Tuple[int, ...], sp.Expr] = {}
        for indices, coeff in self.components.items():
            for mu in range(self.dim):
                deriv = sp.diff(coeff, x_syms[mu])
                if deriv != 0 and not deriv.is_zero:
                    combined = (mu,) + indices
                    sorted_idx, sign = self._canonicalize_indices(combined)
                    if sign != 0:
                        term = sp.simplify(sign * deriv)
                        new_comps[sorted_idx] = new_comps.get(sorted_idx, sp.S.Zero) + term

        return DifferentialForm(next_deg, new_comps, self.coordinates)

    def hodge_star(self, metric_signature: Optional[List[int]] = None) -> DifferentialForm:
        """
        Hodge star operator star(omega): Omega^p -> Omega^(n-p).
        Default metric: Minkowski diag(-1, 1, 1, 1) if dim=4 with t, x, y, z, else Euclidean diag(1, ..., 1).
        """
        n = self.dim
        p = self.degree
        star_deg = n - p

        if metric_signature is None:
            if n == 4 and ("t" in self.coordinates[0] or "x0" in self.coordinates[0]):
                # Standard Minkowski metric (-1, 1, 1, 1)
                sig = [-1, 1, 1, 1]
            else:
                sig = [1] * n
        else:
            sig = metric_signature

        all_indices = set(range(n))
        new_comps: Dict[Tuple[int, ...], sp.Expr] = {}

        for idx_I, coeff in self.components.items():
            set_I = set(idx_I)
            set_J = all_indices - set_I
            idx_J = tuple(sorted(list(set_J)))

            # Metric factor for indices in I: product of g^{ii}
            metric_factor = 1
            for i in idx_I:
                metric_factor *= sig[i]

            # Parity of permutation (I, J) relative to (0, 1, ..., n-1)
            combined = idx_I + idx_J
            _, eps_sign = self._canonicalize_indices(combined)

            star_coeff = sp.simplify(eps_sign * metric_factor * coeff)
            if star_coeff != 0 and not star_coeff.is_zero:
                new_comps[idx_J] = new_comps.get(idx_J, sp.S.Zero) + star_coeff

        return DifferentialForm(star_deg, new_comps, self.coordinates)

    def to_latex(self) -> str:
        if not self.components:
            return "0"

        terms = []
        for indices, coeff in sorted(self.components.items()):
            coeff_latex = sp.latex(coeff)
            if self.degree == 0:
                basis_latex = ""
            elif self.degree == 1:
                basis_latex = f"d{self.coordinates[indices[0]]}"
            else:
                basis_latex = " \\wedge ".join([f"d{self.coordinates[i]}" for i in indices])

            if basis_latex:
                if coeff == 1:
                    terms.append(basis_latex)
                elif coeff == -1:
                    terms.append(f"-{basis_latex}")
                else:
                    if coeff.is_Add:
                        terms.append(f"\\left({coeff_latex}\\right) {basis_latex}")
                    else:
                        terms.append(f"{coeff_latex} {basis_latex}")
            else:
                terms.append(coeff_latex)

        return " + ".join(terms).replace("+ -", "- ")

    def to_result(self) -> DifferentialFormResult:
        latex_str = self.to_latex()
        md = f"**Degree**: {self.degree}-form\n\n$$\\omega = {latex_str}$$\n"
        return DifferentialFormResult(
            degree=self.degree,
            coordinates=self.coordinates,
            components={k: sp.latex(v) for k, v in self.components.items()},
            latex=latex_str,
            markdown=md
        )


class ExteriorCalculus:
    """
    Helper to construct standard basis forms and evaluate geometric operations.
    """

    @staticmethod
    def basis_1form(coord_idx: int, coordinates: List[str]) -> DifferentialForm:
        return DifferentialForm(1, {(coord_idx,): sp.S.One}, coordinates)

    @staticmethod
    def scalar_0form(expr: Union[str, sp.Expr], coordinates: List[str]) -> DifferentialForm:
        from equation_derivator.core.symbols import parse_expression_safely
        sym_expr = parse_expression_safely(expr) if isinstance(expr, str) else expr
        return DifferentialForm(0, {(): sym_expr}, coordinates)
