"""
Equation Discovery & Dimensional Synthesis Engine.

Implements:
1. Buckingham Pi Dimensional Synthesis for discovering power-law scaling relations & dimensionless groups
2. Cross-domain graph composition for synthesizing new equations from known physical laws
3. Physical consistency and non-triviality filter
"""

from __future__ import annotations
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Set, Tuple, Union
import numpy as np
import sympy as sp

from equation_derivator.core.dimensions import Dimension
from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.core.quantities import GLOBAL_QUANTITY_REGISTRY, PhysicalQuantity
from equation_derivator.core.symbols import VariableContext
from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE, EquationKnowledgeBase
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.verifier.verifier import EquationVerifier


@dataclass
class DiscoveredEquation:
    """
    Represents a newly synthesized or discovered physical relation.
    """
    name: str
    discovery_method: str  # "Dimensional Synthesis (Buckingham Pi)" or "Transitive Law Composition"
    target_quantity: str
    formula: sp.Equality
    latex: str
    dimension: Dimension
    constituent_quantities: List[str]
    source_equations: List[str] = field(default_factory=list)
    is_verified: bool = True
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "discovery_method": self.discovery_method,
            "target_quantity": self.target_quantity,
            "formula": str(self.formula),
            "latex": self.latex,
            "dimension": str(self.dimension),
            "constituent_quantities": self.constituent_quantities,
            "source_equations": self.source_equations,
            "is_verified": self.is_verified,
            "notes": self.notes,
        }


class DiscoveryEngine:
    """
    Discovers new physical relations, scaling laws, and cross-domain bridges.
    """
    def __init__(self, kb: Optional[EquationKnowledgeBase] = None):
        self.kb = kb or GLOBAL_KNOWLEDGE_BASE
        self.derivation_engine = DerivationEngine(self.kb)
        self.verifier = EquationVerifier()

    def synthesize_dimensional_relation(
        self,
        quantities: List[Union[str, PhysicalQuantity]],
        target_dimension_or_quantity: Union[str, Dimension, PhysicalQuantity],
    ) -> List[DiscoveredEquation]:
        """
        Uses Buckingham Pi Theorem / Dimensional Linear Algebra to discover all power-law combinations
        of `quantities` that produce `target_dimension_or_quantity`.
        """
        # Resolve input quantities
        resolved_quantities: List[PhysicalQuantity] = []
        for q in quantities:
            if isinstance(q, PhysicalQuantity):
                resolved_quantities.append(q)
            else:
                found = GLOBAL_QUANTITY_REGISTRY.lookup(q)
                if not found:
                    raise ValueError(f"Unknown quantity for dimensional synthesis: '{q}'")
                resolved_quantities.append(found)

        # Resolve target dimension
        target_name = "Target"
        target_dim: Dimension
        if isinstance(target_dimension_or_quantity, Dimension):
            target_dim = target_dimension_or_quantity
            target_name = str(target_dim)
        elif isinstance(target_dimension_or_quantity, PhysicalQuantity):
            target_dim = target_dimension_or_quantity.dimension
            target_name = target_dimension_or_quantity.name
        elif isinstance(target_dimension_or_quantity, str):
            # Check if query is a quantity name or symbol
            found_qty = GLOBAL_QUANTITY_REGISTRY.lookup(target_dimension_or_quantity)
            if found_qty:
                target_dim = found_qty.dimension
                target_name = found_qty.name
            else:
                target_dim = Dimension.from_string(target_dimension_or_quantity)
                target_name = str(target_dim)

        # Build dimensional matrix (7 SI base dimensions x k input quantities)
        # Dimensions order: [M, L, T, I, Theta, N, J]
        k = len(resolved_quantities)
        dim_matrix = np.zeros((7, k), dtype=float)
        symbols = []

        for j, q in enumerate(resolved_quantities):
            symbols.append(sp.Symbol(q.canonical_symbol, positive=True))
            v = q.dimension.to_vector()
            for i in range(7):
                dim_matrix[i, j] = float(v[i])

        target_vec = np.array([float(x) for x in target_dim.to_vector()], dtype=float)

        # Solve dim_matrix @ exponents = target_vec using SymPy exact rational linear algebra
        # Build augmented SymPy Matrix
        sympy_mat = []
        for i in range(7):
            row = [sp.Rational(Fraction(str(dim_matrix[i, j]))) for j in range(k)]
            row.append(sp.Rational(Fraction(str(target_vec[i]))))
            sympy_mat.append(row)

        M = sp.Matrix(sympy_mat)
        system_vars = [sp.Symbol(f"alpha_{j}") for j in range(k)]
        solutions = sp.linsolve((M[:, :-1], M[:, -1]), system_vars)

        discovered = []
        if not solutions:
            return discovered

        sol_tuple = list(solutions)[0]
        # Check if free symbols exist in the solution (under-determined system)
        free_symbols = set()
        for term in sol_tuple:
            if hasattr(term, "free_symbols"):
                free_symbols.update(term.free_symbols)

        # Generate candidate integer/fraction combinations for free variables
        param_assignments = [{}]
        if free_symbols:
            # Sample small rational combinations (-2, -1, 0, 1, 2)
            param_assignments = []
            for val in [sp.Integer(1), sp.Integer(0), sp.Integer(-1)]:
                param_assignments.append({fs: val for fs in free_symbols})

        target_sym = sp.Symbol(target_name.lower())

        for assign in param_assignments:
            evaluated_exponents = [term.subs(assign) if hasattr(term, "subs") else term for term in sol_tuple]
            # Check if all exponents are numbers
            if not all(e.is_number for e in evaluated_exponents):
                continue

            # Build power-law expression: Product(q_j ^ alpha_j)
            formula_rhs = sp.Integer(1)
            for j, exp in enumerate(evaluated_exponents):
                sym = symbols[j]
                formula_rhs *= sym ** exp

            formula_rhs = sp.simplify(formula_rhs)
            if formula_rhs == 1 and not target_dim.is_dimensionless:
                continue

            formula_eq = sp.Eq(target_sym, formula_rhs)
            latex_str = f"{sp.latex(target_sym)} \\propto {sp.latex(formula_rhs)}"

            discovered.append(DiscoveredEquation(
                name=f"Synthesized Scaling for {target_name}",
                discovery_method="Dimensional Synthesis (Buckingham Pi)",
                target_quantity=target_name,
                formula=formula_eq,
                latex=latex_str,
                dimension=target_dim,
                constituent_quantities=[q.name for q in resolved_quantities],
                notes=f"Derived from dimensional homogeneity across {', '.join(q.canonical_symbol for q in resolved_quantities)}",
            ))

        return discovered

    def discover_cross_domain_relations(
        self,
        domain1: str,
        domain2: str,
        max_results: int = 5,
    ) -> List[DiscoveredEquation]:
        """
        Synthesizes novel cross-domain bridge relations between two different physics disciplines
        (e.g., Quantum Mechanics and Relativity, or Mechanics and Electromagnetism).
        """
        eqs1 = self.kb.get_by_domain(domain1)
        eqs2 = self.kb.get_by_domain(domain2)

        discovered = []
        seen_formulas = set()

        for eq1 in eqs1:
            for eq2 in eqs2:
                # Find shared variables
                syms1 = {str(s) for s in eq1.free_symbols}
                syms2 = {str(s) for s in eq2.free_symbols}
                shared = syms1.intersection(syms2)

                if not shared:
                    continue

                for bridge_var in shared:
                    # Try deriving non-shared target in terms of remaining variables
                    non_shared_1 = [s for s in syms1 if s != bridge_var]
                    non_shared_2 = [s for s in syms2 if s != bridge_var]

                    if not non_shared_1 or not non_shared_2:
                        continue

                    target = non_shared_1[0]
                    in_terms_of = non_shared_2 + [s for s in non_shared_1 if s != target]

                    try:
                        res = self.derivation_engine.derive(
                            target_variable=target,
                            in_terms_of=in_terms_of,
                            starting_equations=[eq1, eq2],
                        )
                        formula_str = str(res.final_equation)
                        if formula_str not in seen_formulas and res.is_verified:
                            seen_formulas.add(formula_str)
                            qty = GLOBAL_QUANTITY_REGISTRY.lookup(target)
                            target_name = qty.name if qty else target

                            discovered.append(DiscoveredEquation(
                                name=f"Cross-Domain Bridge: {domain1} <-> {domain2}",
                                discovery_method="Transitive Law Composition",
                                target_quantity=target_name,
                                formula=res.final_equation,
                                latex=res.final_latex,
                                dimension=qty.dimension if qty else Dimension(),
                                constituent_quantities=[s for s in in_terms_of],
                                source_equations=[eq1.name, eq2.name],
                                notes=f"Composed through shared bridge variable '{bridge_var}' via {eq1.id} and {eq2.id}",
                            ))

                        if len(discovered) >= max_results:
                            return discovered
                    except Exception:
                        continue

        return discovered
