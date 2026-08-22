"""
Physical and Mathematical Equation Representation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union
import sympy as sp

from equation_derivator.core.dimensions import Dimension
from equation_derivator.core.quantities import PhysicalQuantity, GLOBAL_QUANTITY_REGISTRY
from equation_derivator.core.symbols import VariableContext


@dataclass
class PhysicalEquation:
    """
    Represents a physical or mathematical law, theorem, definition, or identity.
    """
    id: str
    name: str
    domain: str
    raw_str: str
    lhs: sp.Expr
    rhs: sp.Expr
    context: VariableContext = field(default_factory=VariableContext)
    assumptions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    latex_override: Optional[str] = None
    description: str = ""

    @property
    def free_symbols(self) -> Set[sp.Symbol]:
        return self.lhs.free_symbols.union(self.rhs.free_symbols)

    @property
    def sympy_eq(self) -> sp.Equality:
        return sp.Eq(self.lhs, self.rhs)

    @property
    def relation_expr(self) -> sp.Expr:
        """LHS - RHS = 0"""
        return self.lhs - self.rhs

    @property
    def latex(self) -> str:
        if self.latex_override:
            return self.latex_override
        return f"{sp.latex(self.lhs)} = {sp.latex(self.rhs)}"

    def solve_for(self, target_sym: Union[str, sp.Symbol]) -> List[sp.Expr]:
        """
        Solves the equation algebraically for a target variable.
        Returns a list of possible symbolic solutions.
        """
        sym = target_sym if isinstance(target_sym, sp.Symbol) else self.context.get_sympy_symbol(str(target_sym))
        solutions = sp.solve(sp.Eq(self.lhs, self.rhs), sym)
        return solutions

    def is_dimensionally_valid(self) -> Tuple[bool, Optional[str]]:
        """
        Verifies that [LHS] == [RHS] and all sub-expressions have consistent dimensions.
        """
        try:
            lhs_dim = self.context.infer_dimension_of_expr(self.lhs)
            rhs_dim = self.context.infer_dimension_of_expr(self.rhs)
            if lhs_dim != rhs_dim:
                return False, f"LHS dimension {lhs_dim} does not match RHS dimension {rhs_dim}"
            return True, None
        except ValueError as e:
            return False, str(e)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "raw_str": self.raw_str,
            "latex": self.latex,
            "lhs": str(self.lhs),
            "rhs": str(self.rhs),
            "assumptions": self.assumptions,
            "tags": self.tags,
            "description": self.description,
            "variables": [
                {
                    "symbol": str(s),
                    "quantity": self.context.resolve(str(s)).name if self.context.resolve(str(s)) else "Unknown",
                    "dimension": str(self.context.get_dimension(str(s))) if self.context.get_dimension(str(s)) else "Dimensionless",
                }
                for s in self.free_symbols
            ],
        }

    @classmethod
    def create(
        cls,
        id: str,
        name: str,
        domain: str,
        equation_str: str,
        assumptions: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        bindings: Optional[Dict[str, str]] = None,
        latex_override: Optional[str] = None,
        description: str = "",
    ) -> PhysicalEquation:
        """
        Factory method to parse an equation string 'LHS = RHS' into a PhysicalEquation.
        """
        if "=" not in equation_str:
            raise ValueError(f"Equation string must contain '=': got '{equation_str}'")

        parts = equation_str.split("=")
        if len(parts) != 2:
            raise ValueError(f"Equation must have exactly one '=' sign: got '{equation_str}'")

        ctx = VariableContext()
        if bindings:
            for sym_name, qty_name in bindings.items():
                ctx.bind(sym_name, qty_name)

        lhs = ctx.parse(parts[0])
        rhs = ctx.parse(parts[1])

        return cls(
            id=id,
            name=name,
            domain=domain,
            raw_str=equation_str.strip(),
            lhs=lhs,
            rhs=rhs,
            context=ctx,
            assumptions=assumptions or [],
            tags=tags or [],
            latex_override=latex_override,
            description=description,
        )
