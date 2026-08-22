"""
Tests for Multi-Step Derivation Engine and Calculus Derivations.
"""

import sympy as sp
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE
import equation_derivator.knowledge.domains


def test_derive_kinetic_energy_from_momentum():
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)
    
    # Derive K in terms of p and m from K = 1/2*m*v^2 and p = m*v
    result = engine.derive(
        target_variable="K",
        in_terms_of=["p", "m"],
        starting_equations=["kinetic_energy_def", "linear_momentum_def"]
    )

    assert result is not None
    assert len(result.steps) >= 3
    # Target formula: K = p^2 / (2*m)
    p, m, K = sp.symbols("p m K", real=True)
    expected_rhs = p**2 / (2 * m)
    assert sp.simplify(result.final_equation.rhs - expected_rhs) == 0
    assert result.is_verified is True


def test_derive_escape_velocity_from_custom_equations():
    engine = DerivationEngine()

    # Derive v in terms of G, M, r from kinetic energy = gravitational potential
    result = engine.derive(
        target_variable="v",
        in_terms_of=["G", "M", "r"],
        starting_equations=["1/2 * m * v^2 = G * M * m / r"]
    )

    assert result is not None
    G, M, r = sp.symbols("G M r", real=True)
    expected_sq = 2 * G * M / r
    # Final equation: v = sqrt(2*G*M/r)
    assert sp.simplify(result.final_equation.rhs**2 - expected_sq) == 0


def test_derive_electrical_power():
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)

    # Derive P in terms of I and R from P = I * V and V = I * R
    result = engine.derive(
        target_variable="P",
        in_terms_of=["I", "R"],
        starting_equations=["electric_power_iv", "ohm_law"]
    )

    assert result is not None
    I, R = sp.symbols("I R", real=True)
    expected = I**2 * R
    assert sp.simplify(result.final_equation.rhs - expected) == 0


def test_work_energy_calculus_derivation():
    engine = DerivationEngine()
    result = engine.derive_work_energy_theorem()
    assert result.is_verified is True
    assert len(result.steps) == 4
    assert "Delta K" in result.final_latex
