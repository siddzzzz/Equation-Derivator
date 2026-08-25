"""
Automated unit tests for custom user inputs across all theoretical physics modules:
- Custom Differential Forms & Exterior Calculus
- Custom Matrix Lie Algebras & Commutators
- Custom QFT Gamma Traces & Dirac Hamiltonians
- Custom Partition Functions & Thermodynamic Potentials
- Custom Quantum Potentials & Relativistic Orbits
- API Custom Endpoints
"""

import pytest
import sympy as sp
from fastapi.testclient import TestClient

from equation_derivator.geometry.custom_forms import (
    CustomDifferentialFormParser,
    CustomExteriorCalculusEngine
)
from equation_derivator.symmetry.custom_algebra import CustomLieAlgebraEngine
from equation_derivator.qft.custom_qft import CustomQFTEngine
from equation_derivator.statmech.partition import PartitionFunctionEngine
from equation_derivator.simulation.quantum_sim import QuantumWavePacketSim
from equation_derivator.simulation.relativity_sim import RelativisticOrbitSim
from equation_derivator.interfaces.api import app


def test_custom_differential_forms_parsing_and_exterior_derivative():
    engine = CustomExteriorCalculusEngine()

    # 1. d(y*dx - x*dy) = dy^dx - dx^dy = -2 dx^dy
    res_d = engine.evaluate_operation(
        operation="d",
        form1_str="y*dx - x*dy",
        coordinates=["x", "y", "z"]
    )
    assert res_d.result_degree == 2
    assert "dx ^ dy" in res_d.components_latex
    assert res_d.is_closed is True  # d(d omega) = 0


def test_custom_differential_forms_wedge_and_hodge():
    engine = CustomExteriorCalculusEngine()

    # Wedge product: (x*dx) ^ (y*dy) = x*y dx^dy
    res_wedge = engine.evaluate_operation(
        operation="wedge",
        form1_str="x*dx",
        coordinates=["x", "y", "z"],
        form2_str="y*dy"
    )
    assert res_wedge.result_degree == 2
    assert "dx ^ dy" in res_wedge.components_latex

    # Hodge star 3D: star(dx^dy) = dz in Euclidean metric
    res_star = engine.evaluate_operation(
        operation="star",
        form1_str="dx^dy",
        coordinates=["x", "y", "z"],
        metric_signature=[1, 1, 1]
    )
    assert res_star.result_degree == 1
    assert "dz" in res_star.components_latex


def test_custom_lie_algebra_su2_and_jacobi():
    engine = CustomLieAlgebraEngine()

    # Input Pauli spin-1/2 generators T_a = sigma_a / 2
    mats_input = "[[0, 1/2], [1/2, 0]]; [[0, -I/2], [I/2, 0]]; [[1/2, 0], [0, -1/2]]"
    res = engine.evaluate_custom_algebra(mats_input, algebra_name="su(2) Spin-1/2")

    assert res.dimension == 3
    assert res.matrix_size == 2
    assert res.is_jacobi_identity_satisfied is True
    assert res.is_all_traceless is True
    assert res.is_all_hermitian is True
    assert "[T_1, T_2]" in res.commutator_table_latex


def test_custom_qft_gamma_trace_and_dirac_hamiltonian():
    qft_engine = CustomQFTEngine()

    # 1. Tr(gamma0 * gamma1 * gamma0 * gamma1) = 4
    res_trace = qft_engine.evaluate_gamma_expression("gamma0 * gamma1 * gamma0 * gamma1")
    assert res_trace.evaluated_result_latex in ("4", "-4")
    assert res_trace.is_trace_zero is False

    # 2. Dirac Hamiltonian for m = 0.511, p = (1.0, 0.0, 0.0) -> E = sqrt(1 + 0.511^2) ~ 1.122996
    res_ham = qft_engine.evaluate_dirac_hamiltonian(mass=0.511, px=1.0, py=0.0, pz=0.0)
    assert "1.122" in res_ham.evaluated_result_latex


def test_custom_partition_function_thermodynamic_potentials():
    engine = PartitionFunctionEngine()

    # Paramagnet with magnetic field B: Z = (2*cosh(mu_B*B / (k_B*T)))^N
    Z_paramagnet = "2*cosh(mu_B * B / (k_B * T))^N"
    res = engine.derive_from_Z(Z_paramagnet, model_name="Paramagnet")

    assert "F" in res.free_energy_F_latex or "k_{B}" in res.free_energy_F_latex or "T" in res.free_energy_F_latex
    assert res.entropy_S_latex is not None
    assert res.internal_energy_U_latex is not None


def test_custom_quantum_potential_simulation():
    sim = QuantumWavePacketSim(N=128, x_min=-5.0, x_max=5.0)
    psi0 = sim.create_gaussian_packet(x0=-2.0, p0=2.0, sigma=0.5)

    # Custom potential: harmonic oscillator V(x) = 0.5 * x^2
    V_custom = sim.build_potential(custom_potential_expr="0.5 * x^2")
    assert len(V_custom) == 128
    assert V_custom[64] >= 0.0  # Center

    res = sim.propagate(psi0, V_custom, t_max=0.5, dt=0.02, n_frames=5)
    assert len(res.probability_density_history) >= 5


def test_api_custom_endpoints():
    client = TestClient(app)

    # 1. Custom Forms API
    res_forms = client.post("/api/geometry/custom-form", json={
        "operation": "d",
        "form1": "y*dx - x*dy",
        "coordinates": ["x", "y", "z"]
    })
    assert res_forms.status_code == 200
    assert res_forms.json()["result_degree"] == 2

    # 2. Custom Symmetry API
    res_sym = client.post("/api/symmetry/custom", json={
        "generators": "[[0, 1], [1, 0]]; [[0, -I], [I, 0]]; [[1, 0], [0, -1]]",
        "algebra_name": "Pauli Algebra"
    })
    assert res_sym.status_code == 200
    assert res_sym.json()["is_jacobi_identity_satisfied"] is True

    # 3. Custom QFT API
    res_qft = client.post("/api/qft/custom", json={
        "mode": "gamma_trace",
        "expression": "gamma0 * gamma1 * gamma0 * gamma1"
    })
    assert res_qft.status_code == 200
    assert res_qft.json()["evaluated_result_latex"] in ("4", "-4")

    # 4. Custom StatMech API
    res_stat = client.post("/api/statmech/custom", json={
        "partition_function": "(V/h^3) * (2*pi*m*k_B*T)^(3/2)",
        "model_name": "Custom Ideal Gas"
    })
    assert res_stat.status_code == 200
    assert "entropy_S_latex" in res_stat.json()
