"""
Quantum Mechanics & Wave-Particle Duality Equations.
"""

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.knowledge.database import EquationKnowledgeBase


def register_quantum_equations(kb: EquationKnowledgeBase) -> None:
    # 1. Planck-Einstein Relation (Frequency)
    kb.register(PhysicalEquation.create(
        id="planck_einstein_freq",
        name="Planck-Einstein Relation (Frequency)",
        domain="Quantum",
        equation_str="E = h * f",
        bindings={"h": "PlanckConstant", "f": "Frequency", "E": "TotalEnergy"},
        assumptions=["Quantized electromagnetic radiation / Photon"],
        tags=["Photons", "Energy", "Fundamental", "Quantum Optics"],
        description="Quantized energy of a photon of frequency f."
    ))

    # 2. Planck-Einstein Relation (Angular Frequency)
    kb.register(PhysicalEquation.create(
        id="planck_einstein_angular",
        name="Planck-Einstein Relation (Angular Frequency)",
        domain="Quantum",
        equation_str="E = hbar * omega",
        bindings={"hbar": "ReducedPlanckConstant", "omega": "AngularFrequency", "E": "TotalEnergy"},
        assumptions=["Quantized electromagnetic radiation / Photon"],
        tags=["Photons", "Energy", "Fundamental"],
        description="Quantized energy of a photon with angular frequency omega."
    ))

    # 3. de Broglie Wavelength Relation
    kb.register(PhysicalEquation.create(
        id="de_broglie_wavelength",
        name="de Broglie Matter Wave Relation",
        domain="Quantum",
        equation_str="p = h / lambda_wave",
        assumptions=["Wave-particle duality for any particle with momentum p"],
        bindings={"h": "PlanckConstant", "lambda_wave": "Length", "p": "LinearMomentum"},
        tags=["Wave Mechanics", "Fundamental", "Duality"],
        description="Relates the momentum of a quantum particle to its de Broglie wavelength."
    ))

    # 4. Wave Speed Relation
    kb.register(PhysicalEquation.create(
        id="wave_speed_frequency_wavelength",
        name="Wave Speed Relation",
        domain="Quantum",
        equation_str="v = f * lambda_wave",
        assumptions=["Harmonic plane wave"],
        bindings={"lambda_wave": "Length"},
        tags=["Waves", "Kinematics"],
        description="Phase speed of a wave with frequency f and wavelength lambda."
    ))

    # 5. Angular Frequency Relation
    kb.register(PhysicalEquation.create(
        id="angular_frequency_def",
        name="Angular Frequency Definition",
        domain="Quantum",
        equation_str="omega = 2 * pi * f",
        assumptions=["Periodic oscillation or harmonic wave"],
        tags=["Waves", "Oscillations"],
        description="Relates angular frequency omega to ordinary frequency f."
    ))
