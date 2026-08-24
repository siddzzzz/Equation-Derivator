import pytest
import sympy as sp
from equation_derivator.calculus.variational import VariationalEngine


def test_harmonic_oscillator_euler_lagrange():
    engine = VariationalEngine()
    L_str = "1/2 * m * x_dot^2 - 1/2 * k * x^2"
    result = engine.derive(lagrangian=L_str, coordinates=["x"], system_name="Harmonic Oscillator")

    assert len(result.euler_lagrange_equations) == 1
    eq_info = result.euler_lagrange_equations[0]
    assert eq_info["coord"] == "x"

    # Euler-Lagrange equation should be m*x_ddot + k*x = 0 -> x_ddot = -k*x/m
    accel = eq_info["isolated_acceleration"]
    m, k, x = sp.symbols("m k x", real=True)
    assert accel.equals(-k * x / m)

    # Hamiltonian should be p_x^2 / (2m) + 1/2 k x^2
    assert result.hamiltonian is not None
    p_x = sp.Symbol("p_x", real=True)
    expected_H = p_x**2 / (2 * m) + sp.Rational(1, 2) * k * x**2
    assert result.hamiltonian["hamiltonian_expr"].equals(expected_H)


def test_simple_pendulum_euler_lagrange():
    engine = VariationalEngine()
    L_str = "1/2 * m * L^2 * theta_dot^2 - m * g * L * (1 - cos(theta))"
    result = engine.derive(lagrangian=L_str, coordinates=["theta"], system_name="Simple Pendulum")

    eq_info = result.euler_lagrange_equations[0]
    assert eq_info["coord"] == "theta"

    # Acceleration should be -g*sin(theta)/L
    accel = eq_info["isolated_acceleration"]
    g, L_sym, theta = sp.symbols("g L theta", real=True)
    assert accel.equals(-g * sp.sin(theta) / L_sym)


def test_noether_cyclic_coordinate():
    engine = VariationalEngine()
    # Free particle in 2D: L = 1/2 * m * (x_dot^2 + y_dot^2) -> x and y are cyclic
    L_str = "1/2 * m * (x_dot^2 + y_dot^2)"
    result = engine.derive(lagrangian=L_str, coordinates=["x", "y"], system_name="Free 2D Particle")

    # Should find cyclic coordinate invariants for both x and y
    assert len(result.noether_conserved_quantities) >= 2
    symbols = [cons["invariant_symbol"] for cons in result.noether_conserved_quantities]
    assert "p_{x}" in symbols
    assert "p_{y}" in symbols
