"""
Tests for Core Physical Ontology, Dimensions, Quantities, and Equations.
"""

import pytest
from fractions import Fraction
import sympy as sp

from equation_derivator.core.dimensions import (
    Dimension,
    DIM_FORCE,
    DIM_ENERGY,
    DIM_MOMENTUM,
    DIM_VELOCITY,
    DIM_MASS,
    DIM_ACCELERATION,
    DIM_LENGTH,
    DIM_TIME,
)
from equation_derivator.core.quantities import GLOBAL_QUANTITY_REGISTRY, PhysicalQuantity
from equation_derivator.core.symbols import VariableContext
from equation_derivator.core.equation import PhysicalEquation


def test_dimension_arithmetic():
    # Force = Mass * Acceleration = M * (L / T^2)
    calc_force = DIM_MASS * (DIM_LENGTH / (DIM_TIME ** 2))
    assert calc_force == DIM_FORCE
    assert calc_force.to_dict() == {"M": 1, "L": 1, "T": -2}

    # Energy = Force * Length = M L^2 T^-2
    calc_energy = DIM_FORCE * DIM_LENGTH
    assert calc_energy == DIM_ENERGY

    # Momentum = Mass * Velocity
    assert DIM_MASS * DIM_VELOCITY == DIM_MOMENTUM

    # Power = Energy / Time
    dim_power = DIM_ENERGY / DIM_TIME
    assert str(dim_power) == "[M L^2 T^-3]"


def test_dimension_from_string():
    d = Dimension.from_string("[M L^2 T^-2]")
    assert d == DIM_ENERGY

    d_dimless = Dimension.from_string("1 (dimensionless)")
    assert d_dimless.is_dimensionless


def test_quantity_registry_lookup():
    reg = GLOBAL_QUANTITY_REGISTRY
    # By canonical symbol
    v = reg.get_by_symbol("v")
    assert v is not None
    assert v.name == "Velocity"

    # By alias
    u = reg.lookup("u")
    assert u is not None
    assert u.name == "Velocity"

    # Rest mass alias
    m0 = reg.lookup("m_0")
    assert m0 is not None
    assert m0.name == "Mass"

    # Planck constant
    hbar = reg.lookup("hbar")
    assert hbar is not None
    assert hbar.is_constant is True


def test_variable_context_parsing_and_dimensions():
    ctx = VariableContext()
    # Kinetic energy expression: 0.5 * m * v^2
    expr = ctx.parse("0.5 * m * v^2")
    dim = ctx.infer_dimension_of_expr(expr)
    assert dim == DIM_ENERGY

    # Force expression: m * a
    expr_f = ctx.parse("m * a")
    dim_f = ctx.infer_dimension_of_expr(expr_f)
    assert dim_f == DIM_FORCE

    # Inconsistent addition should raise error
    with pytest.raises(ValueError, match="Dimensional inconsistency"):
        ctx.infer_dimension_of_expr(ctx.parse("m * v + m * a"))


def test_physical_equation_creation_and_solving():
    eq = PhysicalEquation.create(
        id="kinetic_energy",
        name="Kinetic Energy Formula",
        domain="Mechanics",
        equation_str="K = 1/2 * m * v^2",
        assumptions=["v << c"],
    )

    valid, err = eq.is_dimensionally_valid()
    assert valid is True, err

    # Solve for v
    v_sols = eq.solve_for("v")
    assert len(v_sols) == 2  # +/- sqrt(2*K/m)
    assert any(str(sol).endswith("sqrt(2)*sqrt(K/m)") or "sqrt(2*K/m)" in str(sol) or "sqrt(K/m)" in str(sol) for sol in v_sols)
