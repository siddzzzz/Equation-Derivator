import pytest
import sympy as sp
from equation_derivator.statmech.partition import PartitionFunctionEngine
from equation_derivator.statmech.distributions import QuantumDistributionEngine


def test_partition_function_ideal_gas():
    engine = PartitionFunctionEngine()
    res = engine.evaluate_ideal_gas()

    assert res.model_name == "Classical Monatomic Ideal Gas"
    assert "P V = N k_B T" in res.equation_of_state_latex
    assert "Sackur-Tetrode" in res.markdown
    assert "\\frac{3}{2} N k_B" in res.heat_capacity_Cv_latex


def test_partition_function_quantum_oscillator():
    engine = PartitionFunctionEngine()
    res = engine.evaluate_quantum_harmonic_oscillator()

    assert res.model_name == "Quantum Harmonic Oscillator"
    assert "\\sinh" in res.partition_function_latex
    assert "Zero-point" in res.internal_energy_U_latex


def test_custom_partition_function_derivation():
    engine = PartitionFunctionEngine()
    # 2-state system with energies 0 and epsilon: Z = 1 + exp(-epsilon / (kB * T))
    res = engine.derive_from_Z("1 + exp(-epsilon / (k_B * T))", model_name="Two-Level System", has_volume=False)

    assert res.model_name == "Two-Level System"
    assert res.pressure_P_latex is None
    assert "F =" in res.markdown
    assert "S =" in res.markdown
    assert "C_v =" in res.markdown


def test_quantum_distributions_and_planck_radiation():
    engine = QuantumDistributionEngine()
    res = engine.evaluate_distributions()

    assert "Bose-Einstein" in res.markdown
    assert "Fermi-Dirac" in res.markdown
    assert "Planck" in res.markdown
    assert "u(\\nu, T)" in res.planck_radiation_law_latex
    assert "\\sigma T^4" in res.stefan_boltzmann_law_latex
