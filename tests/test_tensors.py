import pytest
import sympy as sp
from equation_derivator.calculus.tensors import SpacetimeTensorEngine


def test_minkowski_flat_metric():
    engine = SpacetimeTensorEngine()
    res = engine.create_minkowski_metric()

    assert res.metric_name == "Minkowski Flat Spacetime"
    # All Christoffel symbols should be zero
    assert len(res.christoffel_symbols) == 0
    # Ricci scalar should be zero
    assert res.ricci_scalar == 0
    assert res.is_vacuum_solution is True


def test_schwarzschild_vacuum_curvature():
    engine = SpacetimeTensorEngine()
    res = engine.create_schwarzschild_metric()

    assert res.metric_name == "Schwarzschild Black Hole Spacetime"
    # Non-zero Christoffel symbols
    assert len(res.christoffel_symbols) > 0
    # Vacuum solution: Ricci tensor must vanish identically (R_{mu nu} = 0)
    assert res.is_vacuum_solution is True
    assert res.ricci_scalar == 0


def test_flrw_cosmological_metric():
    engine = SpacetimeTensorEngine()
    res = engine.create_flrw_metric()

    assert "FLRW" in res.metric_name
    assert len(res.christoffel_symbols) > 0
    assert len(res.geodesic_equations) == 4
