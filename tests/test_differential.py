import pytest
import sympy as sp
from equation_derivator.calculus.differential import DifferentialEquationSolver


def test_damped_harmonic_oscillator_solver():
    solver = DifferentialEquationSolver()
    result = solver.solve_damped_harmonic_oscillator(m="m", gamma="gamma", k="k")

    assert result.name == "Damped Harmonic Oscillator"
    assert result.characteristic_equation is not None
    assert len(result.roots) == 2
    assert len(result.steps) >= 4


def test_quantum_infinite_well_solver():
    solver = DifferentialEquationSolver()
    result = solver.solve_quantum_infinite_well(L_str="L", m_str="m")

    assert "Infinite Potential Well" in result.name
    assert result.eigenvalues_and_states is not None
    assert len(result.eigenvalues_and_states) == 3

    # Check E1, E2, E3 levels
    e1 = result.eigenvalues_and_states[0]
    assert e1["n"] == 1
    assert "pi^2" in e1["energy_latex"]
