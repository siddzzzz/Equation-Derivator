import pytest
from equation_derivator.interfaces.nlp import PhysicsQueryDispatcher
from equation_derivator.interfaces.paper_generator import ScientificPaperGenerator
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE


def test_nlp_query_dispatching():
    dispatcher = PhysicsQueryDispatcher()

    # 1. Variational query
    res_var = dispatcher.process_query("euler-lagrange equation for simple pendulum")
    assert res_var["type"] == "variational"

    # 2. Tensor query
    res_tensor = dispatcher.process_query("compute christoffel symbols and curvature for schwarzschild metric")
    assert res_tensor["type"] == "tensor"

    # 3. Quantum well query
    res_diff = dispatcher.process_query("solve schrodinger equation for infinite potential well")
    assert res_diff["type"] == "differential"

    # 4. Standard derivation query
    res_deriv = dispatcher.process_query("derive kinetic energy from momentum and mass")
    assert res_deriv["type"] == "derivation"


def test_scientific_paper_generation():
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)
    deriv = engine.derive(target_variable="K", in_terms_of=["p", "m"])
    generator = ScientificPaperGenerator()
    tex_paper = generator.generate_derivation_paper(deriv.to_dict(), title="Kinetic Invariant")

    assert "\\documentclass" in tex_paper
    assert "\\begin{abstract}" in tex_paper
    assert "\\begin{equation}" in tex_paper
    assert "\\begin{thebibliography}" in tex_paper
