import pytest
import sympy as sp
from equation_derivator.geometry.differential_forms import DifferentialForm, ExteriorCalculus
from equation_derivator.geometry.maxwell_forms import GeometricMaxwellEngine


def test_wedge_product_antisymmetry():
    coords = ["x", "y", "z"]
    dx = DifferentialForm(1, {(0,): sp.S.One}, coords)
    dy = DifferentialForm(1, {(1,): sp.S.One}, coords)

    dx_wedge_dy = dx.wedge(dy)
    dy_wedge_dx = dy.wedge(dx)

    # dx ^ dy = - dy ^ dx
    sum_form = dx_wedge_dy + dy_wedge_dx
    assert len(sum_form.components) == 0

    # dx ^ dx = 0
    dx_wedge_dx = dx.wedge(dx)
    assert len(dx_wedge_dx.components) == 0


def test_exterior_derivative_nilpotency_d_squared():
    # For an arbitrary 0-form f(x, y, z) = x^2 * y * sin(z), d(d(f)) == 0
    coords = ["x", "y", "z"]
    x, y, z = sp.symbols("x y z", real=True)
    f = x**2 * y * sp.sin(z)

    f_0form = DifferentialForm(0, {(): f}, coords)
    df = f_0form.exterior_derivative()
    assert df.degree == 1

    d_df = df.exterior_derivative()
    assert d_df.degree == 2
    # All components of d^2(f) must vanish identically
    assert len(d_df.components) == 0


def test_hodge_star_operator():
    coords = ["t", "x", "y", "z"]
    dt = DifferentialForm(1, {(0,): sp.S.One}, coords)
    star_dt = dt.hodge_star(metric_signature=[-1, 1, 1, 1])

    # star(dt) in (-1,1,1,1) should be a 3-form dx ^ dy ^ dz with negative sign from g^{00}=-1
    assert star_dt.degree == 3
    assert (1, 2, 3) in star_dt.components


def test_geometric_maxwell_equations():
    engine = GeometricMaxwellEngine()
    result = engine.build_electrodynamics()

    assert result.is_dF_zero is True
    assert result.is_charge_conserved is True
    assert "dF = d(dA)" in result.homogeneous_maxwell_latex
    assert "d\\star F = \\mu_0" in result.inhomogeneous_maxwell_latex
