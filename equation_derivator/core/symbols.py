"""
Symbolic parsing, variable context, and semantic alias resolution.
"""

from __future__ import annotations
import re
from typing import Dict, Optional, Set, Tuple
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

from equation_derivator.core.quantities import (
    PhysicalQuantity,
    QuantityRegistry,
    GLOBAL_QUANTITY_REGISTRY,
)
from equation_derivator.core.dimensions import Dimension


TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


class VariableContext:
    """
    Maintains a mapping between custom variable symbols used in a problem/derivation
    and their underlying PhysicalQuantity concepts.
    """
    def __init__(self, registry: Optional[QuantityRegistry] = None):
        self.registry = registry or GLOBAL_QUANTITY_REGISTRY
        self._symbol_to_quantity: Dict[str, PhysicalQuantity] = {}
        self._custom_symbols: Dict[str, sp.Symbol] = {}

    def bind(self, symbol_name: str, quantity_query: str) -> PhysicalQuantity:
        """
        Explicitly binds a variable symbol (e.g. 'u', 'M_1', 'gamma') to a PhysicalQuantity.
        """
        qty = self.registry.lookup(quantity_query)
        if not qty:
            raise ValueError(f"Unknown physical quantity or concept: '{quantity_query}'")
        self._symbol_to_quantity[symbol_name] = qty
        self._custom_symbols[symbol_name] = sp.Symbol(symbol_name, real=True)
        return qty

    def resolve(self, symbol_name: str) -> Optional[PhysicalQuantity]:
        """
        Resolves a symbol name to its PhysicalQuantity concept.
        Checks explicit bindings first, then global alias registry.
        """
        if symbol_name in self._symbol_to_quantity:
            return self._symbol_to_quantity[symbol_name]
        return self.registry.lookup(symbol_name)

    def get_dimension(self, symbol_name: str) -> Optional[Dimension]:
        qty = self.resolve(symbol_name)
        return qty.dimension if qty else None

    def get_sympy_symbol(self, symbol_name: str) -> sp.Symbol:
        if symbol_name not in self._custom_symbols:
            self._custom_symbols[symbol_name] = sp.Symbol(symbol_name, real=True)
        return self._custom_symbols[symbol_name]

    def parse(self, expr_str: str) -> sp.Expr:
        """
        Safely parses a mathematical string into a SymPy expression,
        auto-registering free symbols.
        """
        clean_str = expr_str.strip()
        # Handle Greek symbols or unicode if needed
        clean_str = clean_str.replace("π", "pi").replace("ħ", "hbar")
        
        # Pre-populate local symbol dictionary for known quantities
        symbols_found = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", clean_str)
        local_dict = {
            "pi": sp.pi,
            "E": sp.E,
            "sqrt": sp.sqrt,
            "exp": sp.exp,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "ln": sp.log,
            "log": sp.log,
        }
        for s in symbols_found:
            if s not in local_dict:
                local_dict[s] = self.get_sympy_symbol(s)
                # Auto-resolve in context if not yet bound
                if s not in self._symbol_to_quantity:
                    matched = self.registry.lookup(s)
                    if matched:
                        self._symbol_to_quantity[s] = matched

        return parse_expr(clean_str, local_dict=local_dict, transformations=TRANSFORMATIONS)

    def infer_dimension_of_expr(self, expr: sp.Expr) -> Dimension:
        """
        Calculates the physical dimension of an entire SymPy expression.
        Raises ValueError if terms with differing dimensions are added/subtracted.
        """
        if expr.is_number:
            return Dimension()

        if expr.is_Symbol:
            dim = self.get_dimension(str(expr))
            if dim is None:
                # Undefined symbol treated as dimensionless for pure math or raises warning
                return Dimension()
            return dim

        if expr.is_Mul:
            total_dim = Dimension()
            for arg in expr.args:
                total_dim = total_dim * self.infer_dimension_of_expr(arg)
            return total_dim

        if expr.is_Pow:
            base, exp = expr.args
            base_dim = self.infer_dimension_of_expr(base)
            if not exp.is_number:
                # Exponent must be dimensionless
                exp_dim = self.infer_dimension_of_expr(exp)
                if not exp_dim.is_dimensionless:
                    raise ValueError(f"Exponent {exp} must be dimensionless, got {exp_dim}")
                val = float(exp.evalf())
            else:
                val = float(exp)
            return base_dim ** val

        if expr.is_Add:
            dims = [self.infer_dimension_of_expr(arg) for arg in expr.args]
            first_dim = dims[0]
            for d in dims[1:]:
                if d != first_dim:
                    raise ValueError(
                        f"Dimensional inconsistency in addition/subtraction: cannot add {first_dim} and {d} in '{expr}'"
                    )
            return first_dim

        # For functions like sin, cos, exp, log, arguments must be dimensionless
        if isinstance(expr, (sp.sin, sp.cos, sp.tan, sp.exp, sp.log, sp.asin, sp.acos, sp.atan)):
            arg_dim = self.infer_dimension_of_expr(expr.args[0])
            if not arg_dim.is_dimensionless:
                raise ValueError(f"Argument to transcendental function {expr.func.__name__} must be dimensionless, got {arg_dim}")
            return Dimension()

        if isinstance(expr, sp.Derivative):
            func_dim = self.infer_dimension_of_expr(expr.args[0])
            wrt_dim = Dimension()
            for var in expr.args[1:]:
                v = var[0] if isinstance(var, tuple) else var
                order = var[1] if isinstance(var, tuple) else 1
                wrt_dim = wrt_dim * (self.infer_dimension_of_expr(v) ** order)
            return func_dim / wrt_dim

        if isinstance(expr, sp.Integral):
            func_dim = self.infer_dimension_of_expr(expr.args[0])
            dx_dim = Dimension()
            for lim in expr.args[1:]:
                v = lim[0] if isinstance(lim, tuple) else lim
                dx_dim = dx_dim * self.infer_dimension_of_expr(v)
            return func_dim * dx_dim

        return Dimension()
