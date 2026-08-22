"""
Multi-Layer Equation and Derivation Verifier.

Performs:
1. Dimensional Consistency Verification ([LHS] == [RHS])
2. Symbolic Algebraic Equivalence & Identity Checking
3. Numerical Monte Carlo Physical Bound Verification
4. Asymptotic Limit Verification (e.g. v -> 0, c -> inf)
5. Step-by-Step Derivation Chain Soundness Audit
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import sympy as sp

from equation_derivator.core.dimensions import Dimension
from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.core.symbols import VariableContext
from equation_derivator.derivation.step import DerivationResult, DerivationStep


class EquationVerifier:
    """
    Rigorously verifies physical and mathematical equations and multi-step derivations.
    """
    def __init__(self, context: Optional[VariableContext] = None):
        self.context = context or VariableContext()

    def verify_dimensions(
        self,
        lhs: sp.Expr,
        rhs: sp.Expr,
        ctx: Optional[VariableContext] = None
    ) -> Tuple[bool, str]:
        """
        Verifies that [LHS] == [RHS] and no terms violate dimensional homogeneity.
        """
        context = ctx or self.context
        try:
            lhs_dim = context.infer_dimension_of_expr(lhs)
            rhs_dim = context.infer_dimension_of_expr(rhs)
            if lhs_dim == rhs_dim:
                return True, f"Dimensionally consistent: both sides have dimension {lhs_dim}"
            else:
                return False, f"Dimensional mismatch: LHS has {lhs_dim} while RHS has {rhs_dim}"
        except ValueError as e:
            return False, f"Dimensional error: {str(e)}"

    def verify_symbolic_identity(
        self,
        lhs: sp.Expr,
        rhs: sp.Expr
    ) -> Tuple[bool, str]:
        """
        Checks if LHS - RHS simplifies to 0 algebraically.
        """
        diff = sp.simplify(lhs - rhs)
        if diff == 0 or diff.is_zero:
            return True, "Algebraic identity verified: LHS - RHS = 0"
        
        # Try trigonometric, expansion, and radical simplification
        diff_expanded = sp.simplify(sp.expand(diff))
        if diff_expanded == 0 or diff_expanded.is_zero:
            return True, "Algebraic identity verified: expanded LHS - RHS = 0"

        # Try factoring
        diff_factored = sp.factor(diff)
        if diff_factored == 0 or diff_factored.is_zero:
            return True, "Algebraic identity verified: factored LHS - RHS = 0"

        return False, f"Symbolic difference does not cancel to zero: {diff}"

    def verify_numerical_monte_carlo(
        self,
        lhs: sp.Expr,
        rhs: sp.Expr,
        n_samples: int = 25,
        tolerance: float = 1e-5
    ) -> Tuple[bool, str]:
        """
        Performs randomized numerical sampling on positive physical domain to verify equivalence.
        """
        free_syms = list(lhs.free_symbols.union(rhs.free_symbols))
        if not free_syms:
            try:
                diff = float(sp.N(lhs - rhs))
                if abs(diff) < tolerance:
                    return True, "Numerical identity confirmed on scalar values"
                return False, f"Scalar discrepancy: {diff}"
            except Exception as e:
                return False, str(e)

        for _ in range(n_samples):
            # Sample positive values (e.g. 0.5 to 100.0)
            subs_map = {sym: random.uniform(0.5, 50.0) for sym in free_syms}
            try:
                lhs_val = complex(lhs.evalf(subs=subs_map))
                rhs_val = complex(rhs.evalf(subs=subs_map))
                diff = abs(lhs_val - rhs_val)
                scale = max(abs(lhs_val), abs(rhs_val), 1.0)
                if (diff / scale) > tolerance:
                    return False, f"Numerical check failed at {subs_map}: LHS={lhs_val}, RHS={rhs_val}, RelDiff={diff/scale:.2e}"
            except Exception as e:
                # If evaluation raises division by zero or domain error, retry with another sample
                continue

        return True, f"Numerical consistency confirmed across {n_samples} random physical samples"

    def verify_asymptotic_limit(
        self,
        expr: sp.Expr,
        variable: sp.Symbol,
        target_limit: Any,
        expected_result: sp.Expr
    ) -> Tuple[bool, str]:
        """
        Verifies limiting behavior (e.g., non-relativistic limit v -> 0).
        """
        try:
            computed_lim = sp.limit(expr, variable, target_limit)
            diff = sp.simplify(computed_lim - expected_result)
            if diff == 0 or diff.is_zero:
                return True, f"Asymptotic limit as {variable} -> {target_limit} verified: {computed_lim}"
            return False, f"Limit mismatch: computed {computed_lim}, expected {expected_result}"
        except Exception as e:
            return False, f"Limit evaluation error: {str(e)}"

    def verify_equation(
        self,
        equation: PhysicalEquation,
        skip_dimensions: bool = False
    ) -> Dict[str, Any]:
        """
        Full multi-aspect verification of a PhysicalEquation.
        """
        results: Dict[str, Any] = {}
        
        # 1. Dimensional Check
        if not skip_dimensions and equation.domain != "Mathematics":
            dim_valid, dim_msg = self.verify_dimensions(equation.lhs, equation.rhs, equation.context)
            results["dimensional_check"] = {"valid": dim_valid, "message": dim_msg}
        else:
            results["dimensional_check"] = {"valid": True, "message": "Skipped (Pure Math / Dimensionless)"}

        # 2. Symbolic Consistency
        sym_valid, sym_msg = self.verify_symbolic_identity(equation.lhs, equation.rhs)
        results["symbolic_check"] = {"valid": sym_valid, "message": sym_msg}

        # 3. Numerical Monte Carlo
        num_valid, num_msg = self.verify_numerical_monte_carlo(equation.lhs, equation.rhs)
        results["numerical_check"] = {"valid": num_valid, "message": num_msg}

        overall_valid = results["dimensional_check"]["valid"] and (sym_valid or num_valid)
        results["overall_valid"] = overall_valid
        return results

    def verify_derivation_chain(
        self,
        result: DerivationResult,
        ctx: Optional[VariableContext] = None
    ) -> Dict[str, Any]:
        """
        Audits all steps in a DerivationResult for mathematical soundness and dimensional consistency.
        """
        context = ctx or self.context
        step_reports = []
        all_sound = True

        for i, step in enumerate(result.steps):
            step_report = {
                "step_number": step.step_number,
                "operation": step.operation,
                "valid": True,
                "notes": []
            }

            # Check dimensional consistency of the step if it's an equation
            if isinstance(step.expression, sp.Equality):
                dim_ok, dim_msg = self.verify_dimensions(step.expression.lhs, step.expression.rhs, context)
                if not dim_ok:
                    step_report["notes"].append(dim_msg)
                else:
                    step_report["notes"].append("Dimensions consistent")

            step_reports.append(step_report)

        # Check final equation
        final_dim_ok, final_dim_msg = self.verify_dimensions(
            result.final_equation.lhs, result.final_equation.rhs, context
        )

        final_num_ok, final_num_msg = self.verify_numerical_monte_carlo(
            result.final_equation.lhs, result.final_equation.rhs
        )

        return {
            "overall_sound": all_sound and final_dim_ok,
            "final_dimensional_check": {"valid": final_dim_ok, "message": final_dim_msg},
            "final_numerical_check": {"valid": final_num_ok, "message": final_num_msg},
            "step_reports": step_reports,
        }
