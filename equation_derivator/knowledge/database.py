"""
Universal Equation Knowledge Base and Graph Relationship Index.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
import networkx as nx
import sympy as sp

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.core.quantities import PhysicalQuantity, GLOBAL_QUANTITY_REGISTRY


class EquationKnowledgeBase:
    """
    Central repository for cataloging, indexing, and linking physical equations across all domains.
    """
    def __init__(self):
        self._equations: Dict[str, PhysicalEquation] = {}
        self._domain_index: Dict[str, List[PhysicalEquation]] = {}
        self._quantity_index: Dict[str, List[PhysicalEquation]] = {}
        self._tag_index: Dict[str, List[PhysicalEquation]] = {}
        self._graph = nx.DiGraph()

    def register(self, equation: PhysicalEquation) -> None:
        """
        Registers an equation into the knowledge base and updates graph indices.
        """
        self._equations[equation.id] = equation

        # Index by domain
        domain = equation.domain
        if domain not in self._domain_index:
            self._domain_index[domain] = []
        if equation not in self._domain_index[domain]:
            self._domain_index[domain].append(equation)

        # Index by tags
        for tag in equation.tags:
            tag_low = tag.lower()
            if tag_low not in self._tag_index:
                self._tag_index[tag_low] = []
            if equation not in self._tag_index[tag_low]:
                self._tag_index[tag_low].append(equation)

        # Index by involved quantities and build relationship graph
        symbols = [str(s) for s in equation.free_symbols]
        for sym in symbols:
            qty = equation.context.resolve(sym)
            qty_key = qty.name if qty else sym
            if qty_key not in self._quantity_index:
                self._quantity_index[qty_key] = []
            if equation not in self._quantity_index[qty_key]:
                self._quantity_index[qty_key].append(equation)

        # Add node and hyperedges to relationship graph
        self._graph.add_node(equation.id, type="equation", obj=equation)
        for s in symbols:
            self._graph.add_node(s, type="variable")
            self._graph.add_edge(equation.id, s)
            self._graph.add_edge(s, equation.id)

    def get(self, eq_id: str) -> Optional[PhysicalEquation]:
        return self._equations.get(eq_id)

    def list_all(self) -> List[PhysicalEquation]:
        return list(self._equations.values())

    def get_by_domain(self, domain: str) -> List[PhysicalEquation]:
        return self._domain_index.get(domain, [])

    def get_by_tag(self, tag: str) -> List[PhysicalEquation]:
        return self._tag_index.get(tag.lower(), [])

    def get_by_quantity(self, quantity_query: str) -> List[PhysicalEquation]:
        qty = GLOBAL_QUANTITY_REGISTRY.lookup(quantity_query)
        key = qty.name if qty else quantity_query
        return self._quantity_index.get(key, [])

    def find_connecting_equations(self, variables: List[str]) -> List[PhysicalEquation]:
        """
        Finds all equations in the knowledge base that contain at least one of the target variables.
        """
        matched: Set[PhysicalEquation] = set()
        for v in variables:
            for eq in self.get_by_quantity(v):
                matched.add(eq)
            # Also try raw symbol matching
            for eq in self._equations.values():
                if any(str(s) == v for s in eq.free_symbols):
                    matched.add(eq)
        return list(matched)

    def find_minimal_derivation_equations(self, target_var: str, in_terms_of: List[str]) -> List[PhysicalEquation]:
        """
        Finds the optimal set of equations from the knowledge base to derive target_var in terms of in_terms_of.
        Prefers fundamental definitions to perform genuine multi-step derivations.
        """
        target_qty = GLOBAL_QUANTITY_REGISTRY.lookup(target_var)
        target_name = target_qty.name if target_qty else target_var

        # 1. Candidate primary equations containing target
        primary_candidates = []
        for eq in self._equations.values():
            if any(str(s) == target_var for s in eq.free_symbols):
                primary_candidates.append(eq)

        if not primary_candidates:
            return self.find_connecting_equations([target_var] + in_terms_of)

        allowed_set = set(in_terms_of) | {target_var}

        # Separate fundamental equations from derived equations
        fund_primaries = [eq for eq in primary_candidates if "Fundamental" in eq.tags or "Definition" in eq.tags or "Law" in eq.tags]
        other_primaries = [eq for eq in primary_candidates if eq not in fund_primaries]
        ordered_primaries = fund_primaries + other_primaries

        best_multistep_chain: Optional[List[PhysicalEquation]] = None
        direct_match: Optional[PhysicalEquation] = None

        for p_eq in ordered_primaries:
            p_syms = {str(s) for s in p_eq.free_symbols}
            unresolved = p_syms - allowed_set

            if not unresolved:
                if not direct_match:
                    direct_match = p_eq
                continue

            current_chain = [p_eq]
            chain_resolved = True

            for unres_var in unresolved:
                # Find an auxiliary equation that connects unres_var to variables in in_terms_of
                # Score candidates: prefer 0 new unresolved variables, same domain, Fundamental tag
                candidate_scored_aux = []
                for aux_eq in self._equations.values():
                    if aux_eq.id == p_eq.id or aux_eq in current_chain:
                        continue
                    aux_syms = {str(s) for s in aux_eq.free_symbols}
                    if unres_var in aux_syms and any(v in in_terms_of for v in aux_syms):
                        new_unresolved = len(aux_syms - allowed_set - {unres_var})
                        same_domain_bonus = 0 if aux_eq.domain == p_eq.domain else 1
                        fund_bonus = 0 if "Fundamental" in aux_eq.tags or "Definition" in aux_eq.tags else 1
                        candidate_scored_aux.append((new_unresolved, same_domain_bonus, fund_bonus, aux_eq))

                if candidate_scored_aux:
                    candidate_scored_aux.sort(key=lambda x: (x[0], x[1], x[2]))
                    best_aux = candidate_scored_aux[0][3]
                    current_chain.append(best_aux)
                else:
                    chain_resolved = False

            if chain_resolved:
                if best_multistep_chain is None or len(current_chain) < len(best_multistep_chain):
                    best_multistep_chain = current_chain

        if best_multistep_chain and len(best_multistep_chain) > 1:
            return best_multistep_chain
        if direct_match:
            return [direct_match]
        return best_multistep_chain if best_multistep_chain else primary_candidates


# Global Knowledge Base Singleton
GLOBAL_KNOWLEDGE_BASE = EquationKnowledgeBase()
