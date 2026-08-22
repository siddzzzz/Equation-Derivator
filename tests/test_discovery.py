"""
Tests for Equation Discovery & Dimensional Synthesis Engine.
"""

import sympy as sp
from equation_derivator.discovery.discovery_engine import DiscoveryEngine
from equation_derivator.core.dimensions import DIM_LENGTH, DIM_TIME, DIM_MASS
from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE
import equation_derivator.knowledge.domains


def test_planck_units_synthesis():
    engine = DiscoveryEngine(GLOBAL_KNOWLEDGE_BASE)

    # Synthesize Planck Length from G, hbar, c
    results = engine.synthesize_dimensional_relation(
        quantities=["G", "hbar", "c"],
        target_dimension_or_quantity="Length"
    )

    assert len(results) >= 1
    # Check that Planck length formula: sqrt(hbar * G / c^3) is synthesized
    # Dimension should be Length
    assert results[0].dimension == DIM_LENGTH
    latex = results[0].latex
    assert "hbar" in latex and "G" in latex and "c" in latex


def test_pendulum_period_synthesis():
    engine = DiscoveryEngine(GLOBAL_KNOWLEDGE_BASE)

    # Synthesize time / period from pendulum length (x) and acceleration (a)
    results = engine.synthesize_dimensional_relation(
        quantities=["Length", "Acceleration"],
        target_dimension_or_quantity="Time"
    )

    assert len(results) >= 1
    assert results[0].dimension == DIM_TIME


def test_cross_domain_discovery():
    engine = DiscoveryEngine(GLOBAL_KNOWLEDGE_BASE)

    # Discover relations bridging Mechanics and Quantum
    bridges = engine.discover_cross_domain_relations(
        domain1="Quantum",
        domain2="Relativity",
        max_results=3
    )

    assert len(bridges) > 0
    assert any("Composed" in b.notes for b in bridges)
