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

    def find_path_between_quantities(self, start_qty: str, target_qty: str) -> List[List[str]]:
        """
        Finds derivation pathways (chains of equations) connecting start_qty to target_qty.
        """
        if start_qty not in self._graph or target_qty not in self._graph:
            return []
        try:
            paths = list(nx.all_shortest_paths(self._graph, source=start_qty, target=target_qty))
            # Filter path to return sequence of equation IDs
            eq_paths = []
            for p in paths:
                eq_sequence = [node for node in p if self._graph.nodes[node].get("type") == "equation"]
                if eq_sequence and eq_sequence not in eq_paths:
                    eq_paths.append(eq_sequence)
            return eq_paths
        except nx.NetworkXNoPath:
            return []


# Global Knowledge Base Singleton
GLOBAL_KNOWLEDGE_BASE = EquationKnowledgeBase()
