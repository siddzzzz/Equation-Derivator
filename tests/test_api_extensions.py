import pytest
from fastapi.testclient import TestClient
from equation_derivator.interfaces.api import app

client = TestClient(app)


def test_api_simulate_endpoint():
    payload = {
        "accelerations": {"theta": "-9.81 * sin(theta)"},
        "coordinates": ["theta"],
        "initial_positions": {"theta": 0.5},
        "initial_velocities": {"theta": 0.0},
        "t_end": 1.0,
        "dt": 0.05
    }
    response = client.post("/api/sim/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "time" in data
    assert "positions" in data
    assert len(data["time"]) > 10


def test_api_phase_portrait_endpoint():
    payload = {
        "accel_expr": "-4.0 * x",
        "coord_name": "x",
        "q0": 1.0,
        "v0": 0.0,
        "t_end": 2.0,
        "dt": 0.05
    }
    response = client.post("/api/sim/phase-portrait", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "vector_field_grid" in data
    assert "q_values" in data
    assert "p_values" in data


def test_api_quantum_wave_endpoint():
    payload = {
        "barrier_type": "barrier",
        "barrier_height": 4.0,
        "p0": 3.0
    }
    response = client.post("/api/sim/quantum-wave", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transmission_coefficient" in data
    assert "probability_density_history" in data


def test_api_relativity_orbit_endpoint():
    payload = {
        "mode": "particle",
        "r0": 12.0,
        "v_phi0": 0.28
    }
    response = client.post("/api/sim/relativity-orbit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "r_coords" in data
    assert "schwarzschild_radius" in data


def test_api_qft_endpoints():
    res_dirac = client.post("/api/qft/dirac", json={"representation": "dirac"})
    assert res_dirac.status_code == 200
    assert res_dirac.json()["clifford_anticommutators_valid"] is True

    res_feynman = client.post("/api/qft/feynman", json={"process": "ee_to_mumu"})
    assert res_feynman.status_code == 200
    assert "svg_diagram" in res_feynman.json()


def test_api_geometry_and_symmetry_and_statmech_endpoints():
    res_geom = client.post("/api/geometry/maxwell")
    assert res_geom.status_code == 200
    assert res_geom.json()["is_dF_zero"] is True

    res_sym = client.post("/api/symmetry/eval", json={"mode": "higgs"})
    assert res_sym.status_code == 200
    assert "M_W" in res_sym.json()["boson_mass_eigenvalues_latex"]

    res_stat = client.post("/api/statmech/eval", json={"mode": "ideal_gas"})
    assert res_stat.status_code == 200
    assert "P V = N k_B T" in res_stat.json()["equation_of_state_latex"]
