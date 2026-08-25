"""
Custom Differential Forms Parser and Exterior Calculus Operator.
Allows users to define arbitrary differential forms on arbitrary manifolds
and compute d(omega), omega_1 ^ omega_2, star(omega), and gauge field strengths.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import re
import sympy as sp

from equation_derivator.geometry.differential_forms import DifferentialForm
from equation_derivator.core.symbols import parse_expression_safely


@dataclass
class CustomFormEvaluationResult:
    operation: str
    coordinates: List[str]
    input_form_latex: str
    result_form_latex: str
    result_degree: int
    components_latex: Dict[str, str]
    is_closed: Optional[bool]
    is_exact_candidate: Optional[bool]
    markdown: str

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "coordinates": self.coordinates,
            "input_form_latex": self.input_form_latex,
            "result_form_latex": self.result_form_latex,
            "result_degree": self.result_degree,
            "components_latex": self.components_latex,
            "is_closed": self.is_closed,
            "is_exact_candidate": self.is_exact_candidate,
            "markdown": self.markdown,
        }


class CustomDifferentialFormParser:
    """
    Parses user-entered differential form string into a DifferentialForm object.
    Example string: "y*dx - x*dy + z^2*dz" or "f(x,y)*dx^dy + g(x,y)*dt^dx"
    """

    @staticmethod
    def parse_form(
        form_str: str,
        coordinates: List[str]
    ) -> DifferentialForm:
        """
        Parses a differential form string like:
        'y*dx - x*dy' or 'cos(theta)*dr^dtheta'
        """
        clean_str = form_str.strip()
        if not clean_str or clean_str == "0":
            return DifferentialForm(0, {}, coordinates)

        coord_indices = {c.strip(): i for i, c in enumerate(coordinates)}

        # Split form into additive terms by + and - outside parentheses
        terms = CustomDifferentialFormParser._split_additive_terms(clean_str)

        detected_degree = None
        components_map: Dict[Tuple[int, ...], sp.Expr] = {}

        for term in terms:
            term = term.strip()
            if not term:
                continue

            # Extract basis wedge part: e.g. dx^dy or dx or dt^dx^dy
            # Look for d<coord> patterns
            wedge_match = re.findall(r'd([a-zA-Z0-9_]+)', term)
            if not wedge_match:
                # 0-form scalar term
                deg = 0
                coeff_expr = parse_expression_safely(term)
                idx_tuple = ()
            else:
                deg = len(wedge_match)
                # Verify all coords are in coordinates
                idx_list = []
                for c in wedge_match:
                    if c not in coord_indices:
                        raise ValueError(f"Coordinate 'd{c}' in term '{term}' not found in coordinate list {coordinates}")
                    idx_list.append(coord_indices[c])
                idx_tuple = tuple(idx_list)

                # Strip out the d<coord> and ^ parts from term to get the coefficient
                coeff_str = re.sub(r'(\^|\*|\s)*d[a-zA-Z0-9_]+', '', term).strip()
                if coeff_str in ("", "+"):
                    coeff_expr = sp.S.One
                elif coeff_str == "-":
                    coeff_expr = -sp.S.One
                else:
                    coeff_expr = parse_expression_safely(coeff_str)

            if detected_degree is None:
                detected_degree = deg
            elif detected_degree != deg:
                raise ValueError(f"Mixed degree differential form detected: found both {detected_degree}-form and {deg}-form terms in '{form_str}'")

            components_map[idx_tuple] = components_map.get(idx_tuple, sp.S.Zero) + coeff_expr

        return DifferentialForm(detected_degree if detected_degree is not None else 0, components_map, coordinates)

    @staticmethod
    def _split_additive_terms(s: str) -> List[str]:
        terms = []
        current = []
        paren_depth = 0
        i = 0
        while i < len(s):
            char = s[i]
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif (char == '+' or char == '-') and paren_depth == 0 and i > 0:
                terms.append("".join(current).strip())
                current = [char]
            else:
                current.append(char)
            i += 1
        if current:
            terms.append("".join(current).strip())
        return [t for t in terms if t]


class CustomExteriorCalculusEngine:
    """
    Evaluates arbitrary user exterior calculus expressions.
    """

    def evaluate_operation(
        self,
        operation: str,  # "exterior_derivative", "hodge_star", "wedge_product", "field_strength"
        form1_str: str,
        coordinates: Optional[List[str]] = None,
        form2_str: Optional[str] = None,
        metric_signature: Optional[List[int]] = None
    ) -> CustomFormEvaluationResult:
        coords = coordinates or ["x", "y", "z"]
        sig = metric_signature or ([ -1, 1, 1, 1 ] if len(coords) == 4 and "t" in coords[0] else [1] * len(coords))

        parser = CustomDifferentialFormParser()
        omega1 = parser.parse_form(form1_str, coords)

        is_closed = None
        is_exact = None

        if operation in ("d", "exterior_derivative", "diff"):
            res_form = omega1.exterior_derivative()
            # Test closure d(res_form) == 0
            d_res = res_form.exterior_derivative()
            is_closed = (len(d_res.components) == 0)
            op_title = "Exterior Derivative $d\\omega$"

        elif operation in ("star", "hodge_star", "hodge"):
            res_form = omega1.hodge_star(metric_signature=sig)
            op_title = "Hodge Dual $\\star \\omega$"

        elif operation in ("wedge", "wedge_product"):
            if not form2_str:
                raise ValueError("Second differential form (form2) required for wedge product")
            omega2 = parser.parse_form(form2_str, coords)
            res_form = omega1.wedge(omega2)
            op_title = "Wedge Product $\\omega_1 \\wedge \\omega_2$"

        elif operation in ("field_strength", "gauge"):
            # Treating form1 as gauge potential 1-form A
            res_form = omega1.exterior_derivative()
            d_F = res_form.exterior_derivative()
            is_closed = (len(d_F.components) == 0)  # Bianchi identity dF = 0
            op_title = "Gauge Field Strength $F = dA$"

        else:
            res_form = omega1.exterior_derivative()
            op_title = f"Operation {operation}"

        res_latex = res_form.to_latex()
        in_latex = omega1.to_latex()

        comps_dict = {}
        for idx, val in res_form.components.items():
            if res_form.degree == 0:
                basis_label = "scalar"
            elif res_form.degree == 1:
                basis_label = f"d{coords[idx[0]]}"
            else:
                basis_label = " ^ ".join([f"d{coords[i]}" for i in idx])
            comps_dict[basis_label] = sp.latex(val)

        md = (
            f"# Custom Exterior Calculus: {op_title}\n\n"
            f"- **Manifold Coordinates**: $({', '.join(coords)})$\n"
            f"- **Input Differential Form**: $\\omega = {in_latex}$\n"
            f"- **Resulting {res_form.degree}-Form**: $$\\Omega = {res_latex}$$\n"
        )
        if is_closed is not None:
            md += f"- **Is Closed ($d\\Omega = 0$)**: `{is_closed}`\n"

        return CustomFormEvaluationResult(
            operation=operation,
            coordinates=coords,
            input_form_latex=in_latex,
            result_form_latex=res_latex,
            result_degree=res_form.degree,
            components_latex=comps_dict,
            is_closed=is_closed,
            is_exact_candidate=is_exact,
            markdown=md
        )
