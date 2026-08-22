"""
Thermodynamics & Statistical Mechanics Equations.
"""

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.knowledge.database import EquationKnowledgeBase


def register_thermodynamics_equations(kb: EquationKnowledgeBase) -> None:
    # 1. Ideal Gas Law (Molar)
    kb.register(PhysicalEquation.create(
        id="ideal_gas_law_molar",
        name="Ideal Gas Law (Molar)",
        domain="Thermodynamics",
        equation_str="P * V = n * R * T",
        bindings={"P": "Pressure", "T": "Temperature", "V": "Volume", "n": "AmountOfSubstance", "R": "GasConstant"},
        assumptions=["Ideal gas (point particles, elastic collisions)", "Thermal equilibrium"],
        tags=["Gases", "State Equation", "Fundamental"],
        description="Equation of state relating pressure, volume, temperature, and moles of ideal gas."
    ))

    # 2. Average Molecular Kinetic Energy
    kb.register(PhysicalEquation.create(
        id="kinetic_theory_temp_energy",
        name="Equipartition Average Kinetic Energy (3D Monoatomic)",
        domain="Thermodynamics",
        equation_str="K = 3/2 * k_B * T",
        bindings={"T": "Temperature"},
        assumptions=["Monoatomic ideal gas", "Classical Maxwell-Boltzmann statistics"],
        tags=["Statistical Mechanics", "Kinetic Theory", "Temperature"],
        description="Average translational kinetic energy of a monoatomic gas particle at temperature T."
    ))

    # 3. First Law of Thermodynamics
    kb.register(PhysicalEquation.create(
        id="first_law_thermodynamics",
        name="First Law of Thermodynamics",
        domain="Thermodynamics",
        equation_str="U = Q - W",
        bindings={"Q": "TotalEnergy", "W": "Work", "U": "TotalEnergy"},
        assumptions=["Closed thermodynamic system", "Conservation of energy"],
        tags=["Energy Conservation", "Heat", "Work", "Fundamental"],
        description="Change in internal energy equals net heat added minus work done by the system."
    ))

    # 4. Work Done at Constant Pressure (Isobaric)
    kb.register(PhysicalEquation.create(
        id="isobaric_work",
        name="Isobaric Expansion Work",
        domain="Thermodynamics",
        equation_str="W = P * V",
        bindings={"P": "Pressure", "V": "Volume", "W": "Work"},
        assumptions=["Constant pressure process", "Quasi-static boundary displacement"],
        tags=["Work", "Processes"],
        description="Mechanical work performed by an expanding gas at constant pressure."
    ))

    # 5. Stefan-Boltzmann Radiation Law
    kb.register(PhysicalEquation.create(
        id="stefan_boltzmann_law",
        name="Stefan-Boltzmann Radiation Law",
        domain="Thermodynamics",
        equation_str="P = sigma * A * T^4",
        bindings={"P": "Power", "sigma": "StefanBoltzmannConstant", "A": "Area", "T": "Temperature"},
        assumptions=["Ideal blackbody emitter", "Thermal equilibrium radiation"],
        tags=["Radiation", "Astrophysics", "Heat Transfer"],
        description="Total radiant power emitted by a blackbody of surface area A at temperature T."
    ))
