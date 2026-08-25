import pytest
import numpy as np
from equation_derivator.simulation.integrator import RK4Integrator, VerletIntegrator, simulate_symbolic_system
from equation_derivator.simulation.phase_space import PhaseSpaceEngine
from equation_derivator.simulation.quantum_sim import QuantumWavePacketSim
from equation_derivator.simulation.relativity_sim import RelativisticOrbitSim


def test_rk4_harmonic_oscillator_energy_conservation():
    # d^2 x / dt^2 = -k/m * x
    k, m = 4.0, 1.0
    omega_sq = k / m

    def accel(t, q, v):
        return np.array([-omega_sq * q[0]])

    def energy(q, v):
        return 0.5 * m * (v[0]**2) + 0.5 * k * (q[0]**2)

    integrator = RK4Integrator(dt=0.01)
    t, q, v, e = integrator.integrate(accel, np.array([2.0]), np.array([0.0]), (0.0, 10.0), energy_fn=energy)

    # Energy should be conserved within 0.05%
    initial_e = e[0]
    max_e_error = np.max(np.abs(e - initial_e)) / initial_e
    assert max_e_error < 0.001


def test_simulate_symbolic_system_pendulum():
    # Simple Pendulum acceleration theta_ddot = -g/L * sin(theta)
    traj = simulate_symbolic_system(
        accelerations={"theta": "-g/L * sin(theta)"},
        coordinates=["theta"],
        initial_positions={"theta": 0.5},
        initial_velocities={"theta": 0.0},
        parameters={"g": 9.81, "L": 1.0},
        t_end=2.0,
        dt=0.01
    )
    assert traj.system_name == "Symbolic Dynamical System"
    assert "theta" in traj.positions
    assert len(traj.time) > 10
    # Position should oscillate
    assert traj.positions["theta"][0] == 0.5


def test_phase_space_engine_generation():
    engine = PhaseSpaceEngine()
    result = engine.generate_phase_portrait(
        accel_expr_str="-k/m * x",
        coord_name="x",
        params={"k": 2.0, "m": 1.0},
        q0=1.5,
        v0=0.0,
        t_end=5.0,
        dt=0.02,
        potential_expr_str="1/2 * k * x^2"
    )
    assert result.is_conservative is True
    assert len(result.q_values) > 0
    assert "u" in result.vector_field_grid


def test_quantum_wave_packet_tunneling():
    sim = QuantumWavePacketSim(N=256, x_min=-8.0, x_max=8.0)
    psi0 = sim.create_gaussian_packet(x0=-3.0, p0=2.5, sigma=0.6)
    V = sim.build_potential(barrier_type="barrier", barrier_height=4.0, barrier_width=0.4, barrier_center=0.0)

    res = sim.propagate(psi0, V, t_max=1.5, dt=0.01, n_frames=10)
    assert len(res.time_points) >= 10
    # Total probability should remain conserved ~ 1.0
    assert abs(res.final_norm - 1.0) < 0.01
    # Both transmission and reflection should be physical probabilities [0, 1]
    assert 0.0 <= res.transmission_coefficient <= 1.0
    assert 0.0 <= res.reflection_coefficient <= 1.0


def test_relativistic_schwarzschild_orbit():
    sim = RelativisticOrbitSim(M=1.0, G=1.0, c=1.0)
    orbit = sim.simulate_particle_orbit(r0=12.0, v_phi0=0.28, n_steps=500, dt=0.05)

    assert orbit.schwarzschild_radius == 2.0
    assert orbit.photon_sphere_radius == 3.0
    assert orbit.isco_radius == 6.0
    assert len(orbit.x_cartesian) > 0
    assert orbit.is_captured_by_horizon is False
