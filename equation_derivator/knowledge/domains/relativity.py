"""
Special & General Relativity Equations.
"""

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.knowledge.database import EquationKnowledgeBase


def register_relativity_equations(kb: EquationKnowledgeBase) -> None:
    # 1. Lorentz Factor
    kb.register(PhysicalEquation.create(
        id="lorentz_factor",
        name="Lorentz Factor Definition",
        domain="Relativity",
        equation_str="gamma^2 = 1 / (1 - v^2 / c^2)",
        assumptions=["v < c", "Flat spacetime (Special Relativity)"],
        tags=["Kinematics", "Fundamental", "Spacetime"],
        description="Lorentz factor quantifying relativistic time dilation and length contraction."
    ))

    # 2. Relativistic Energy-Momentum Invariant Relation
    kb.register(PhysicalEquation.create(
        id="relativistic_energy_momentum",
        name="Relativistic Energy-Momentum Invariant Relation",
        domain="Relativity",
        equation_str="E^2 = (p * c)^2 + (m * c^2)^2",
        assumptions=["Free relativistic particle", "m is rest mass"],
        tags=["Energy", "Momentum", "Fundamental", "Mass-Energy"],
        description="Fundamental relativistic relationship between total energy E, momentum p, and rest mass m."
    ))

    # 3. Mass-Energy Equivalence (Rest Mass)
    kb.register(PhysicalEquation.create(
        id="rest_mass_energy",
        name="Einstein Mass-Energy Equivalence",
        domain="Relativity",
        equation_str="E = m * c^2",
        assumptions=["Particle at rest (p = 0)"],
        tags=["Mass-Energy", "Fundamental", "Nuclear"],
        description="Rest energy of an object of mass m at rest."
    ))

    # 4. Photon Energy-Momentum Relation (Massless)
    kb.register(PhysicalEquation.create(
        id="photon_energy_momentum",
        name="Massless Particle Energy-Momentum Relation",
        domain="Relativity",
        equation_str="E = p * c",
        assumptions=["Zero rest mass (m = 0), e.g. photon or gluon"],
        tags=["Photons", "Massless", "Quantum-Relativity"],
        description="Total energy of a massless particle traveling at the speed of light."
    ))

    # 5. Relativistic Momentum
    kb.register(PhysicalEquation.create(
        id="relativistic_momentum",
        name="Relativistic Momentum",
        domain="Relativity",
        equation_str="p = gamma * m * v",
        assumptions=["Special Relativity", "m is rest mass"],
        tags=["Momentum", "Dynamics"],
        description="Linear momentum of a relativistic particle with Lorentz factor gamma."
    ))

    # 6. Relativistic Total Energy
    kb.register(PhysicalEquation.create(
        id="relativistic_total_energy",
        name="Relativistic Total Energy",
        domain="Relativity",
        equation_str="E = gamma * m * c^2",
        assumptions=["Special Relativity", "m is rest mass"],
        tags=["Energy", "Mass-Energy"],
        description="Total relativistic energy of a moving particle."
    ))

    # 7. Schwarzschild Radius (General Relativity)
    kb.register(PhysicalEquation.create(
        id="schwarzschild_radius",
        name="Schwarzschild Black Hole Event Horizon Radius",
        domain="Relativity",
        equation_str="r = (2 * G * M) / c^2",
        assumptions=["Static spherically symmetric non-rotating uncharged black hole (Schwarzschild metric)"],
        tags=["General Relativity", "Black Holes", "Astrophysics"],
        description="Radius defining the event horizon of a Schwarzschild black hole of mass M."
    ))
