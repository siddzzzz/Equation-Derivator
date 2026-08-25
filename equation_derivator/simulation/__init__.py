"""
Numerical Simulation & Phase Space Dynamics Module.
Bridges symbolic derivations to live numerical physics engines.
"""

from equation_derivator.simulation.integrator import (
    RK4Integrator,
    VerletIntegrator,
    SimulationTrajectory,
    simulate_symbolic_system
)
from equation_derivator.simulation.phase_space import (
    PhaseSpaceEngine,
    PhaseSpaceTrajectory
)
from equation_derivator.simulation.quantum_sim import (
    QuantumWavePacketSim,
    QuantumWavePacketResult
)
from equation_derivator.simulation.relativity_sim import (
    RelativisticOrbitSim,
    RelativisticOrbitResult
)

__all__ = [
    "RK4Integrator",
    "VerletIntegrator",
    "SimulationTrajectory",
    "simulate_symbolic_system",
    "PhaseSpaceEngine",
    "PhaseSpaceTrajectory",
    "QuantumWavePacketSim",
    "QuantumWavePacketResult",
    "RelativisticOrbitSim",
    "RelativisticOrbitResult",
]
