"""
Electromagnetism & Circuit Equations.
"""

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.knowledge.database import EquationKnowledgeBase


def register_electromagnetism_equations(kb: EquationKnowledgeBase) -> None:
    # 1. Coulomb's Law
    kb.register(PhysicalEquation.create(
        id="coulomb_law",
        name="Coulomb's Electrostatic Law",
        domain="Electromagnetism",
        equation_str="F = (q1 * q2) / (4 * pi * epsilon_0 * r^2)",
        bindings={"q1": "ElectricCharge", "q2": "ElectricCharge", "r": "Length", "F": "Force", "epsilon_0": "VacuumPermittivity"},
        assumptions=["Point charges at rest in vacuum"],
        tags=["Electrostatics", "Fundamental", "Force"],
        description="Electrostatic force between two stationary electric charges."
    ))

    # 2. Electric Field Definition
    kb.register(PhysicalEquation.create(
        id="electric_field_def",
        name="Electric Field Definition",
        domain="Electromagnetism",
        equation_str="F = q * E",
        bindings={"F": "Force", "q": "ElectricCharge", "E": "ElectricField"},
        assumptions=["Test charge q in electric field E"],
        tags=["Electrostatics", "Field", "Force"],
        description="Force exerted on a charge q by an electric field E."
    ))

    # 3. Electric Potential Energy
    kb.register(PhysicalEquation.create(
        id="electric_potential_energy",
        name="Electric Potential Energy",
        domain="Electromagnetism",
        equation_str="U = q * V",
        bindings={"U": "PotentialEnergy", "q": "ElectricCharge", "V": "ElectricPotential"},
        assumptions=["Electrostatic potential V"],
        tags=["Electrostatics", "Energy"],
        description="Potential energy of a charge q at electric potential V."
    ))

    # 4. Ohm's Law
    kb.register(PhysicalEquation.create(
        id="ohm_law",
        name="Ohm's Law",
        domain="Electromagnetism",
        equation_str="V = I * R",
        bindings={"V": "ElectricPotential", "I": "ElectricCurrent", "R": "Resistance"},
        assumptions=["Ohmic conductor", "Constant temperature"],
        tags=["Circuits", "Current", "Resistance"],
        description="Linear relation between voltage, current, and resistance."
    ))

    # 5. Electrical Power (Joule Heating)
    kb.register(PhysicalEquation.create(
        id="electric_power_iv",
        name="Electrical Power (IV)",
        domain="Electromagnetism",
        equation_str="P = I * V",
        bindings={"P": "Power", "I": "ElectricCurrent", "V": "ElectricPotential"},
        assumptions=["Steady state DC or RMS AC in phase"],
        tags=["Circuits", "Power", "Energy"],
        description="Power dissipated or supplied in an electrical element with current I and voltage V."
    ))

    # 6. Electrical Power (I^2 R)
    kb.register(PhysicalEquation.create(
        id="electric_power_i2r",
        name="Joule Heating (I^2 R)",
        domain="Electromagnetism",
        equation_str="P = I^2 * R",
        bindings={"P": "Power", "I": "ElectricCurrent", "R": "Resistance"},
        assumptions=["Ohmic resistor"],
        tags=["Circuits", "Power", "Heating"],
        description="Thermal power dissipated in a resistor R with current I."
    ))

    # 7. Capacitance Definition
    kb.register(PhysicalEquation.create(
        id="capacitance_def",
        name="Capacitor Charge-Voltage Relation",
        domain="Electromagnetism",
        equation_str="q = C * V",
        bindings={"q": "ElectricCharge", "C": "Capacitance", "V": "ElectricPotential"},
        assumptions=["Linear dielectric or vacuum capacitor"],
        tags=["Electrostatics", "Capacitance", "Circuits"],
        description="Charge q stored on a capacitor C at voltage V."
    ))

    # 8. Capacitor Stored Energy
    kb.register(PhysicalEquation.create(
        id="capacitor_energy",
        name="Energy Stored in a Capacitor",
        domain="Electromagnetism",
        equation_str="U = 1/2 * C * V^2",
        bindings={"U": "PotentialEnergy", "C": "Capacitance", "V": "ElectricPotential"},
        assumptions=["Linear dielectric"],
        tags=["Electrostatics", "Energy", "Capacitance"],
        description="Total electrical potential energy stored in an electrostatic field of a capacitor."
    ))

    # 9. Magnetic Lorentz Force (Magnitude)
    kb.register(PhysicalEquation.create(
        id="magnetic_lorentz_force",
        name="Magnetic Lorentz Force (Perpendicular)",
        domain="Electromagnetism",
        equation_str="F = q * v * B",
        bindings={"F": "Force", "q": "ElectricCharge", "v": "Velocity", "B": "MagneticField"},
        assumptions=["Velocity v perpendicular to magnetic field B"],
        tags=["Magnetism", "Force", "Particles"],
        description="Magnetic force on a charge q moving with velocity v perpendicular to field B."
    ))

    # 10. Electromagnetic Wave Speed in Vacuum
    kb.register(PhysicalEquation.create(
        id="speed_of_light_em",
        name="Speed of Light from EM Constants",
        domain="Electromagnetism",
        equation_str="c^2 = 1 / (epsilon_0 * mu_0)",
        bindings={"c": "SpeedOfLight", "epsilon_0": "VacuumPermittivity", "mu_0": "VacuumPermeability"},
        assumptions=["Vacuum propagation", "Maxwell equations derivation"],
        tags=["EM Waves", "Constants", "Fundamental"],
        description="Relation linking speed of light to vacuum permittivity and permeability."
    ))
