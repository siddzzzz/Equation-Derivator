import pytest
import sympy as sp
from equation_derivator.qft.dirac import DiracAlgebra, evaluate_dirac_equation
from equation_derivator.qft.feynman import FeynmanEvaluator, QEDScatteringProcess
from equation_derivator.qft.feynman_draw import FeynmanDiagramGenerator


def test_dirac_clifford_algebra_representations():
    # Test standard Dirac-Pauli, Weyl, and Majorana representations
    for rep in ["dirac", "weyl", "majorana"]:
        algebra = DiracAlgebra(representation=rep)
        assert algebra.verify_clifford_algebra() is True


def test_chiral_projectors_properties():
    algebra = DiracAlgebra(representation="weyl")
    P_L, P_R = algebra.get_chiral_projectors()

    # P_L + P_R = I
    assert P_L + P_R == algebra.I4
    # P_L^2 = P_L
    assert P_L * P_L == P_L
    # P_R^2 = P_R
    assert P_R * P_R == P_R
    # P_L * P_R = 0
    assert P_L * P_R == sp.zeros(4, 4)


def test_dirac_equation_evaluation():
    res = evaluate_dirac_equation(representation="dirac")
    assert res.clifford_anticommutators_valid is True
    assert res.chiral_projectors_valid is True
    assert "\\gamma^0" in res.gamma_matrices_latex
    assert "u^{(1)}(0)" in res.spinors_latex


def test_feynman_evaluator_ee_to_mumu():
    evaluator = FeynmanEvaluator()
    res = evaluator.evaluate_ee_to_mumu()

    assert res.process_name == "Electron-Positron Annihilation to Muon Pair"
    assert res.channel == "s-channel photon exchange"
    assert "\\mathcal{M}" in res.matrix_element_latex
    assert "1 + \\cos^2\\theta" in res.squared_matrix_element_unpolarized_latex
    assert "\\sigma_{\\text{total}}" in res.total_cross_section_latex


def test_feynman_evaluator_compton():
    evaluator = FeynmanEvaluator()
    res = evaluator.evaluate_compton_scattering()

    assert "Compton" in res.process_name
    assert "\\frac{\\omega'}{\\omega}" in res.differential_cross_section_latex


def test_feynman_diagram_svg_generation():
    svg_ee = FeynmanDiagramGenerator.draw_ee_to_mumu()
    assert "<svg" in svg_ee
    assert "s-channel" in svg_ee

    svg_compton = FeynmanDiagramGenerator.draw_compton_scattering()
    assert "<svg" in svg_compton
    assert "Compton" in svg_compton
