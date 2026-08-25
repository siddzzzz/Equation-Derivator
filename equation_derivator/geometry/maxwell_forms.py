"""
Geometric Electrodynamics & Maxwell Differential Forms Formulation.
Expresses Maxwell's equations as dF = 0 and d*F = mu_0 *J.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp

from equation_derivator.geometry.differential_forms import DifferentialForm, ExteriorCalculus


@dataclass
class MaxwellFormResult:
    coordinates: List[str]
    potential_1form_latex: str
    field_strength_2form_latex: str
    homogeneous_maxwell_latex: str
    dual_field_strength_2form_latex: str
    inhomogeneous_maxwell_latex: str
    current_conservation_latex: str
    is_dF_zero: bool
    is_charge_conserved: bool
    markdown: str

    def to_dict(self) -> dict:
        return {
            "coordinates": self.coordinates,
            "potential_1form_latex": self.potential_1form_latex,
            "field_strength_2form_latex": self.field_strength_2form_latex,
            "homogeneous_maxwell_latex": self.homogeneous_maxwell_latex,
            "dual_field_strength_2form_latex": self.dual_field_strength_2form_latex,
            "inhomogeneous_maxwell_latex": self.inhomogeneous_maxwell_latex,
            "current_conservation_latex": self.current_conservation_latex,
            "is_dF_zero": self.is_dF_zero,
            "is_charge_conserved": self.is_charge_conserved,
            "markdown": self.markdown,
        }


class GeometricMaxwellEngine:
    """
    Constructs electromagnetic forms on 4D Minkowski spacetime (t, x, y, z).
    """

    def __init__(self, coordinates: Optional[List[str]] = None):
        self.coordinates = coordinates or ["t", "x", "y", "z"]

    def build_electrodynamics(self) -> MaxwellFormResult:
        """
        Derives F = dA, dF = 0, star(F), and d(star(F)) = mu_0 star(J).
        """
        t, x, y, z = [sp.Symbol(c, real=True) for c in self.coordinates]

        # Potentials: phi(t,x,y,z), Ax(t,x,y,z), Ay, Az
        phi = sp.Function("phi")(t, x, y, z)
        Ax = sp.Function("A_x")(t, x, y, z)
        Ay = sp.Function("A_y")(t, x, y, z)
        Az = sp.Function("A_z")(t, x, y, z)

        # 1. 4-Potential 1-form A = -phi dt + Ax dx + Ay dy + Az dz
        A_form = DifferentialForm(
            degree=1,
            components={
                (0,): -phi,
                (1,): Ax,
                (2,): Ay,
                (3,): Az,
            },
            coordinates=self.coordinates
        )

        # 2. Field Strength 2-form F = dA
        F_form = A_form.exterior_derivative()

        # 3. Homogeneous Maxwell Equation: dF = d(dA) = 0
        dF = F_form.exterior_derivative()
        is_dF_zero = len(dF.components) == 0

        # 4. Hodge Dual 2-form *F in Minkowski metric (-1, 1, 1, 1)
        star_F = F_form.hodge_star(metric_signature=[-1, 1, 1, 1])

        # 5. Inhomogeneous Maxwell: d(*F) = mu_0 *J
        d_star_F = star_F.exterior_derivative()

        # 6. Current Conservation: d(*J) = 1/mu_0 d(d(*F)) = 0
        d_d_star_F = d_star_F.exterior_derivative()
        is_charge_conserved = len(d_d_star_F.components) == 0

        # Build clean LaTeX formulas
        A_latex = r"A = -\phi\, dt + A_x\, dx + A_y\, dy + A_z\, dz"
        F_latex = r"F = dA = -E_x\, dt\wedge dx - E_y\, dt\wedge dy - E_z\, dt\wedge dz + B_z\, dx\wedge dy - B_y\, dx\wedge dz + B_x\, dy\wedge dz"
        dF_latex = r"dF = d(dA) \equiv 0 \iff \begin{cases} \nabla\cdot \mathbf{B} = 0 \\ \nabla\times \mathbf{E} + \frac{\partial \mathbf{B}}{\partial t} = 0 \end{cases}"
        star_F_latex = r"\star F = B_x\, dt\wedge dx + B_y\, dt\wedge dy + B_z\, dt\wedge dz + E_z\, dx\wedge dy - E_y\, dx\wedge dz + E_x\, dy\wedge dz"
        inhom_latex = r"d\star F = \mu_0 \star J \iff \begin{cases} \nabla\cdot \mathbf{E} = \frac{\rho}{\varepsilon_0} \\ \nabla\times \mathbf{B} - \frac{1}{c^2}\frac{\partial \mathbf{E}}{\partial t} = \mu_0 \mathbf{J} \end{cases}"
        cons_latex = r"d\star J = 0 \iff \frac{\partial \rho}{\partial t} + \nabla\cdot \mathbf{J} = 0"

        md = rf"""# Geometric Electrodynamics in Differential Forms

## 1. Gauge Potential 1-Form
$${A_latex}$$

## 2. Field Strength 2-Form ($F = dA$)
$${F_latex}$$

## 3. Homogeneous Maxwell Equations (Bianchi Identity)
$${dF_latex}$$
*Exact topological guarantee: $d^2 = 0 \implies dF = 0$ everywhere.*

## 4. Dual Field 2-Form ($\star F$)
$${star_F_latex}$$

## 5. Inhomogeneous Maxwell Equations & Charge Conservation
$${inhom_latex}$$
$${cons_latex}$$
"""

        return MaxwellFormResult(
            coordinates=self.coordinates,
            potential_1form_latex=A_latex,
            field_strength_2form_latex=F_latex,
            homogeneous_maxwell_latex=dF_latex,
            dual_field_strength_2form_latex=star_F_latex,
            inhomogeneous_maxwell_latex=inhom_latex,
            current_conservation_latex=cons_latex,
            is_dF_zero=is_dF_zero,
            is_charge_conserved=is_charge_conserved,
            markdown=md
        )
