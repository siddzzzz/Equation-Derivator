"""
Tests for Universal Knowledge Base across Mechanics, EM, Thermo, Relativity, Quantum, and Math.
"""

from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE
import equation_derivator.knowledge.domains  # Ensures all domains are loaded


def test_knowledge_base_population():
    kb = GLOBAL_KNOWLEDGE_BASE
    all_eqs = kb.list_all()
    assert len(all_eqs) >= 30, f"Expected at least 30 equations, got {len(all_eqs)}"

    # Check that each domain has registered equations
    domains = ["Mechanics", "Electromagnetism", "Thermodynamics", "Relativity", "Quantum", "Mathematics"]
    for dom in domains:
        eqs = kb.get_by_domain(dom)
        assert len(eqs) > 0, f"Domain {dom} has no registered equations"


def test_equation_dimensional_consistency():
    kb = GLOBAL_KNOWLEDGE_BASE
    for eq in kb.list_all():
        # Pure math equations might use abstract symbols without dimensions
        if eq.domain == "Mathematics":
            continue
        valid, err = eq.is_dimensionally_valid()
        assert valid is True, f"Equation '{eq.name}' ({eq.id}) failed dimensional consistency: {err}"


def test_knowledge_graph_pathfinding():
    kb = GLOBAL_KNOWLEDGE_BASE
    # Find connecting equations between 'p' (momentum) and 'K' (kinetic energy)
    eqs = kb.find_connecting_equations(["p", "K"])
    assert len(eqs) > 0
    ids = [e.id for e in eqs]
    assert "kinetic_energy_def" in ids or "kinetic_energy_momentum" in ids or "linear_momentum_def" in ids
