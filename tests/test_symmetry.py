import pytest
import sympy as sp
from equation_derivator.symmetry.lie_algebra import SU2Algebra, SU3Algebra
from equation_derivator.symmetry.gauge import YangMillsGaugeEngine, HiggsMechanismEngine


def test_su2_lie_algebra_properties():
    su2 = SU2Algebra()
    res = su2.evaluate()

    assert res.group_name == "SU(2)"
    assert res.dimension == 3
    assert "\\frac{3}{4}" in res.casimir_operator_latex

    # Verify commutator [J1, J2] == i J3
    J1, J2, J3 = su2.generators[0], su2.generators[1], su2.generators[2]
    comm = su2.commutator(J1, J2)
    assert comm == sp.I * J3


def test_su3_gell_mann_generators():
    su3 = SU3Algebra()
    res = su3.evaluate()

    assert res.group_name == "SU(3)"
    assert res.dimension == 8
    assert "\\frac{4}{3}" in res.casimir_operator_latex

    # All 8 Gell-Mann matrices must be traceless and hermitian
    traceless, hermitian = su3.verify_generators_traceless_hermitian()
    assert traceless is True
    assert hermitian is True


def test_yang_mills_gauge_engine():
    engine = YangMillsGaugeEngine()
    res_su2 = engine.evaluate_yang_mills("SU(2)")
    assert "F_{\\mu\\nu}^a" in res_su2.field_strength_tensor_latex
    assert "D_\\mu" in res_su2.covariant_derivative_latex

    res_su3 = engine.evaluate_yang_mills("SU(3)")
    assert "G_{\\mu\\nu}^a" in res_su3.field_strength_tensor_latex


def test_higgs_mechanism_spontaneous_breaking():
    higgs = HiggsMechanismEngine()
    res = higgs.evaluate_electroweak_breaking()

    assert "M_W" in res.boson_mass_eigenvalues_latex
    assert "M_Z" in res.boson_mass_eigenvalues_latex
    assert "M_\\gamma = 0" in res.boson_mass_eigenvalues_latex["M_\\gamma"]
    assert "\\cos\\theta_W" in res.weinberg_angle_latex
