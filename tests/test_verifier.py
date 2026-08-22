"""
Tests for Equation and Derivation Verifier.
"""

import sympy as sp
from equation_derivator.verifier.verifier import EquationVerifier
from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.core.symbols import VariableContext


def test_verifier_dimensional_check():
    verifier = EquationVerifier()
    ctx = VariableContext()

    # Valid: F = m * a
    F, m, a = sp.symbols("F m a")
    ok, msg = verifier.verify_dimensions(F, m * a, ctx)
    assert ok is True

    # Invalid: F = m * v
    v = sp.symbols("v")
    ok_bad, msg_bad = verifier.verify_dimensions(F, m * v, ctx)
    assert ok_bad is False


def test_verifier_symbolic_and_monte_carlo():
    verifier = EquationVerifier()

    # Identity: (a + b)^2 = a^2 + 2*a*b + b^2
    a, b = sp.symbols("a b")
    lhs = (a + b)**2
    rhs = a**2 + 2 * a * b + b**2

    sym_ok, _ = verifier.verify_symbolic_identity(lhs, rhs)
    assert sym_ok is True

    mc_ok, _ = verifier.verify_numerical_monte_carlo(lhs, rhs)
    assert mc_ok is True


def test_verifier_asymptotic_limits():
    verifier = EquationVerifier()

    # Relativistic gamma as v -> 0 is 1
    v, c = sp.symbols("v c", positive=True)
    gamma = 1 / sp.sqrt(1 - (v / c)**2)

    ok, msg = verifier.verify_asymptotic_limit(gamma, v, 0, sp.Integer(1))
    assert ok is True, msg
