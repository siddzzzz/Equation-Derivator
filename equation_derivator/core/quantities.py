"""
Physical Quantities Registry & Universal Physical Ontology.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import sympy as sp

from equation_derivator.core.dimensions import (
    Dimension,
    DIM_DIMENSIONLESS,
    DIM_MASS,
    DIM_LENGTH,
    DIM_TIME,
    DIM_CURRENT,
    DIM_TEMPERATURE,
    DIM_AMOUNT,
    DIM_AREA,
    DIM_VOLUME,
    DIM_VELOCITY,
    DIM_ACCELERATION,
    DIM_FORCE,
    DIM_MOMENTUM,
    DIM_ENERGY,
    DIM_WORK,
    DIM_POWER,
    DIM_PRESSURE,
    DIM_DENSITY,
    DIM_ACTION,
    DIM_ANGULAR_MOMENTUM,
    DIM_TORQUE,
    DIM_FREQUENCY,
    DIM_ANGULAR_VELOCITY,
    DIM_MOMENT_OF_INERTIA,
    DIM_CHARGE,
    DIM_VOLTAGE,
    DIM_ELECTRIC_FIELD,
    DIM_MAGNETIC_FIELD,
    DIM_MAGNETIC_FLUX,
    DIM_RESISTANCE,
    DIM_CAPACITANCE,
    DIM_INDUCTANCE,
    DIM_PERMITTIVITY,
    DIM_PERMEABILITY,
    DIM_ENTROPY,
    DIM_GRAVITATIONAL_CONSTANT,
    DIM_PLANCK_CONSTANT,
    DIM_BOLTZMANN_CONSTANT,
)


@dataclass
class PhysicalQuantity:
    """
    Represents an invariant physical concept (e.g. Mass, Velocity, Electric Field)
    independent of the particular variable name used in a given paper or equation.
    """
    name: str
    canonical_symbol: str
    dimension: Dimension
    description: str
    aliases: List[str] = field(default_factory=list)
    latex_symbol: Optional[str] = None
    is_constant: bool = False
    constant_value: Optional[float] = None
    constant_unit: Optional[str] = None
    domains: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.latex_symbol:
            self.latex_symbol = self.canonical_symbol

    def to_sympy_symbol(self) -> sp.Symbol:
        return sp.Symbol(self.canonical_symbol, real=True)

    def matches_alias(self, sym_str: str) -> bool:
        sym_clean = sym_str.strip()
        if sym_clean == self.canonical_symbol or sym_clean == self.name:
            return True
        return sym_clean in self.aliases


class QuantityRegistry:
    """
    Universal Registry of Physical Quantities and Fundamental Constants.
    """
    def __init__(self):
        self._quantities_by_name: Dict[str, PhysicalQuantity] = {}
        self._exact_symbol_map: Dict[str, PhysicalQuantity] = {}
        self._ci_map: Dict[str, PhysicalQuantity] = {}
        self._dimension_index: Dict[Dimension, List[PhysicalQuantity]] = {}
        self._load_standard_quantities()

    def register(self, quantity: PhysicalQuantity) -> None:
        self._quantities_by_name[quantity.name.lower()] = quantity
        
        # Exact case indexing
        self._exact_symbol_map[quantity.canonical_symbol] = quantity
        for alias in quantity.aliases:
            # Don't let an alias overwrite an existing canonical symbol
            if alias not in self._exact_symbol_map:
                self._exact_symbol_map[alias] = quantity

        # Case-insensitive fallback
        if quantity.canonical_symbol.lower() not in self._ci_map:
            self._ci_map[quantity.canonical_symbol.lower()] = quantity
        if quantity.name.lower() not in self._ci_map:
            self._ci_map[quantity.name.lower()] = quantity
        for alias in quantity.aliases:
            if alias.lower() not in self._ci_map:
                self._ci_map[alias.lower()] = quantity

        # Index by dimension
        dim = quantity.dimension
        if dim not in self._dimension_index:
            self._dimension_index[dim] = []
        if quantity not in self._dimension_index[dim]:
            self._dimension_index[dim].append(quantity)

    def get_by_name(self, name: str) -> Optional[PhysicalQuantity]:
        return self._quantities_by_name.get(name.lower())

    def get_by_symbol(self, symbol: str) -> Optional[PhysicalQuantity]:
        return self._exact_symbol_map.get(symbol) or self._ci_map.get(symbol.lower())

    def lookup(self, query: str) -> Optional[PhysicalQuantity]:
        q = query.strip()
        # 1. Try exact symbol/alias
        if q in self._exact_symbol_map:
            return self._exact_symbol_map[q]
        # 2. Try exact name (case-insensitive)
        q_low = q.lower()
        if q_low in self._quantities_by_name:
            return self._quantities_by_name[q_low]
        # 3. Try case-insensitive symbol/alias
        if q_low in self._ci_map:
            return self._ci_map[q_low]
        return None

    def get_by_dimension(self, dimension: Dimension) -> List[PhysicalQuantity]:
        return self._dimension_index.get(dimension, [])

    def list_all(self) -> List[PhysicalQuantity]:
        return list(self._quantities_by_name.values())

    def _load_standard_quantities(self) -> None:
        # Base Dimensions
        self.register(PhysicalQuantity(
            name="Mass", canonical_symbol="m", dimension=DIM_MASS,
            description="Measure of inertia and matter content",
            aliases=["M", "m_0", "m1", "m2", "mu", "mass", "m_e", "m_p"],
            domains=["Mechanics", "Relativity", "Quantum", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="Length", canonical_symbol="x", dimension=DIM_LENGTH,
            description="Spatial displacement or distance",
            aliases=["r", "d", "L", "s", "h", "y", "z", "R", "x_0", "dx", "dr"],
            domains=["Mechanics", "Electromagnetism", "Relativity", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="Time", canonical_symbol="t", dimension=DIM_TIME,
            description="Duration or temporal coordinate",
            aliases=["T", "t_0", "tau", "dt", "time"],
            domains=["Mechanics", "Relativity", "Electromagnetism", "Quantum"]
        ))
        self.register(PhysicalQuantity(
            name="ElectricCurrent", canonical_symbol="I", dimension=DIM_CURRENT,
            description="Flow of electric charge",
            aliases=["i", "I_0", "current"],
            domains=["Electromagnetism", "Circuits"]
        ))
        self.register(PhysicalQuantity(
            name="Temperature", canonical_symbol="T_abs", dimension=DIM_TEMPERATURE,
            description="Absolute thermodynamic temperature",
            aliases=["T", "Theta", "temp", "temperature", "T_k"],
            latex_symbol="T",
            domains=["Thermodynamics", "Statistical Mechanics", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="AmountOfSubstance", canonical_symbol="n_mol", dimension=DIM_AMOUNT,
            description="Number of elementary entities in moles",
            aliases=["n", "mol", "moles"],
            latex_symbol="n",
            domains=["Thermodynamics", "Chemistry"]
        ))

        # Kinematics & Mechanics
        self.register(PhysicalQuantity(
            name="Velocity", canonical_symbol="v", dimension=DIM_VELOCITY,
            description="Rate of change of position",
            aliases=["u", "v_0", "v_f", "v_x", "v_y", "v_z", "v_avg", "v_esc", "c_s", "x_dot"],
            domains=["Mechanics", "Relativity", "Fluid Dynamics"]
        ))
        self.register(PhysicalQuantity(
            name="Acceleration", canonical_symbol="a", dimension=DIM_ACCELERATION,
            description="Rate of change of velocity",
            aliases=["g", "a_x", "a_y", "a_c", "a_t", "x_ddot"],
            domains=["Mechanics", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="Force", canonical_symbol="F", dimension=DIM_FORCE,
            description="Interaction causing acceleration",
            aliases=["f", "F_net", "F_g", "F_e", "F_b", "N_force", "T_tension"],
            domains=["Mechanics", "Electromagnetism", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="LinearMomentum", canonical_symbol="p", dimension=DIM_MOMENTUM,
            description="Product of mass and velocity",
            aliases=["P", "p_0", "p_x", "p_y", "momentum"],
            domains=["Mechanics", "Relativity", "Quantum"]
        ))
        self.register(PhysicalQuantity(
            name="KineticEnergy", canonical_symbol="K", dimension=DIM_ENERGY,
            description="Energy possessed by an object due to motion",
            aliases=["E_k", "KE", "T_kin", "kinetic_energy"],
            latex_symbol="K",
            domains=["Mechanics", "Relativity", "Quantum"]
        ))
        self.register(PhysicalQuantity(
            name="PotentialEnergy", canonical_symbol="U", dimension=DIM_ENERGY,
            description="Energy stored due to position or configuration",
            aliases=["V", "PE", "E_p", "U_g", "U_e", "potential_energy"],
            latex_symbol="U",
            domains=["Mechanics", "Electromagnetism", "Quantum"]
        ))
        self.register(PhysicalQuantity(
            name="TotalEnergy", canonical_symbol="E", dimension=DIM_ENERGY,
            description="Total energy of a system",
            aliases=["E_tot", "H", "energy"],
            domains=["Mechanics", "Thermodynamics", "Relativity", "Quantum"]
        ))
        self.register(PhysicalQuantity(
            name="Work", canonical_symbol="W", dimension=DIM_WORK,
            description="Energy transferred by a force acting through distance",
            aliases=["w", "work"],
            domains=["Mechanics", "Thermodynamics"]
        ))
        self.register(PhysicalQuantity(
            name="Power", canonical_symbol="P_pow", dimension=DIM_POWER,
            description="Rate of doing work or transferring energy",
            aliases=["P", "power"],
            latex_symbol="P",
            domains=["Mechanics", "Electromagnetism", "Thermodynamics"]
        ))
        self.register(PhysicalQuantity(
            name="Pressure", canonical_symbol="P_press", dimension=DIM_PRESSURE,
            description="Force applied perpendicular to surface per unit area",
            aliases=["p", "P", "pressure", "P_0"],
            latex_symbol="P",
            domains=["Thermodynamics", "Fluid Dynamics", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="Volume", canonical_symbol="V_vol", dimension=DIM_VOLUME,
            description="Three-dimensional space enclosed by a boundary",
            aliases=["V", "volume", "vol"],
            latex_symbol="V",
            domains=["Thermodynamics", "Mechanics", "Fluid Dynamics"]
        ))
        self.register(PhysicalQuantity(
            name="Area", canonical_symbol="A_area", dimension=DIM_AREA,
            description="Two-dimensional surface extent",
            aliases=["A", "S", "area"],
            latex_symbol="A",
            domains=["Mechanics", "Electromagnetism", "Thermodynamics"]
        ))
        self.register(PhysicalQuantity(
            name="Density", canonical_symbol="rho", dimension=DIM_DENSITY,
            description="Mass per unit volume",
            aliases=["d_dens", "density"],
            latex_symbol=r"\rho",
            domains=["Mechanics", "Fluid Dynamics", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="AngularMomentum", canonical_symbol="L_ang", dimension=DIM_ANGULAR_MOMENTUM,
            description="Rotational analog of linear momentum",
            aliases=["L", "J_ang"],
            latex_symbol="L",
            domains=["Mechanics", "Quantum", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="Torque", canonical_symbol="tau_torq", dimension=DIM_TORQUE,
            description="Rotational force or moment",
            aliases=["tau", "Torque"],
            latex_symbol=r"\tau",
            domains=["Mechanics"]
        ))
        self.register(PhysicalQuantity(
            name="Frequency", canonical_symbol="f", dimension=DIM_FREQUENCY,
            description="Number of occurrences of a repeating event per unit time",
            aliases=["nu", "freq"],
            latex_symbol="f",
            domains=["Mechanics", "Waves", "Quantum", "Electromagnetism"]
        ))
        self.register(PhysicalQuantity(
            name="AngularFrequency", canonical_symbol="omega", dimension=DIM_ANGULAR_VELOCITY,
            description="Scalar measure of rotation rate",
            aliases=["w", "ang_freq"],
            latex_symbol=r"\omega",
            domains=["Mechanics", "Waves", "Quantum", "Electromagnetism"]
        ))

        # Electromagnetism
        self.register(PhysicalQuantity(
            name="ElectricCharge", canonical_symbol="q", dimension=DIM_CHARGE,
            description="Physical property of matter causing electrostatic force",
            aliases=["Q", "e_charge", "q1", "q2", "charge"],
            domains=["Electromagnetism", "Quantum", "Circuits"]
        ))
        self.register(PhysicalQuantity(
            name="ElectricField", canonical_symbol="E_field", dimension=DIM_ELECTRIC_FIELD,
            description="Physical field exerting force on electric charges",
            aliases=["E", "E_x", "E_y", "E_z"],
            latex_symbol=r"\mathbf{E}",
            domains=["Electromagnetism"]
        ))
        self.register(PhysicalQuantity(
            name="MagneticField", canonical_symbol="B_field", dimension=DIM_MAGNETIC_FIELD,
            description="Physical field exerting force on moving electric charges",
            aliases=["B", "B_x", "B_y", "B_z"],
            latex_symbol=r"\mathbf{B}",
            domains=["Electromagnetism"]
        ))
        self.register(PhysicalQuantity(
            name="ElectricPotential", canonical_symbol="V_volt", dimension=DIM_VOLTAGE,
            description="Electric potential energy per unit charge",
            aliases=["V", "phi", "voltage", "emf"],
            latex_symbol="V",
            domains=["Electromagnetism", "Circuits"]
        ))
        self.register(PhysicalQuantity(
            name="Resistance", canonical_symbol="R_res", dimension=DIM_RESISTANCE,
            description="Measure of opposition to electric current",
            aliases=["R", "resistance"],
            latex_symbol="R",
            domains=["Electromagnetism", "Circuits"]
        ))
        self.register(PhysicalQuantity(
            name="Capacitance", canonical_symbol="C_cap", dimension=DIM_CAPACITANCE,
            description="Ratio of change in electric charge to change in electric potential",
            aliases=["C", "capacitance"],
            latex_symbol="C",
            domains=["Electromagnetism", "Circuits"]
        ))
        self.register(PhysicalQuantity(
            name="Inductance", canonical_symbol="L_ind", dimension=DIM_INDUCTANCE,
            description="Tendency of an electrical conductor to oppose change in electric current",
            aliases=["L", "inductance"],
            latex_symbol="L",
            domains=["Electromagnetism", "Circuits"]
        ))

        # Fundamental Constants
        self.register(PhysicalQuantity(
            name="SpeedOfLight", canonical_symbol="c", dimension=DIM_VELOCITY,
            description="Universal speed of light in vacuum",
            aliases=["c_0", "light_speed"],
            is_constant=True, constant_value=299792458.0, constant_unit="m/s",
            domains=["Relativity", "Electromagnetism", "Quantum", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="GravitationalConstant", canonical_symbol="G", dimension=DIM_GRAVITATIONAL_CONSTANT,
            description="Newtonian universal constant of gravitation",
            aliases=["G_grav", "grav_const"],
            is_constant=True, constant_value=6.67430e-11, constant_unit="m^3/(kg s^2)",
            domains=["Mechanics", "Relativity", "Astrophysics"]
        ))
        self.register(PhysicalQuantity(
            name="PlanckConstant", canonical_symbol="h_planck", dimension=DIM_PLANCK_CONSTANT,
            description="Planck constant relating photon energy to frequency",
            aliases=["h", "planck"],
            latex_symbol="h",
            is_constant=True, constant_value=6.62607015e-34, constant_unit="J s",
            domains=["Quantum", "Statistical Mechanics"]
        ))
        self.register(PhysicalQuantity(
            name="ReducedPlanckConstant", canonical_symbol="hbar", dimension=DIM_PLANCK_CONSTANT,
            description="Reduced Planck constant (h / 2pi)",
            aliases=["h_bar", "dirac_constant"],
            latex_symbol=r"\hbar",
            is_constant=True, constant_value=1.054571817e-34, constant_unit="J s",
            domains=["Quantum", "Relativity"]
        ))
        self.register(PhysicalQuantity(
            name="BoltzmannConstant", canonical_symbol="k_B", dimension=DIM_BOLTZMANN_CONSTANT,
            description="Relates average kinetic energy of particles in a gas with temperature",
            aliases=["k", "k_b", "boltzmann"],
            latex_symbol="k_B",
            is_constant=True, constant_value=1.380649e-23, constant_unit="J/K",
            domains=["Thermodynamics", "Statistical Mechanics"]
        ))
        self.register(PhysicalQuantity(
            name="GasConstant", canonical_symbol="R_gas", dimension=DIM_ENTROPY / DIM_AMOUNT,
            description="Universal molar gas constant",
            aliases=["R", "gas_constant"],
            latex_symbol="R",
            is_constant=True, constant_value=8.314462618, constant_unit="J/(mol K)",
            domains=["Thermodynamics"]
        ))
        self.register(PhysicalQuantity(
            name="VacuumPermittivity", canonical_symbol="epsilon_0", dimension=DIM_PERMITTIVITY,
            description="Electric permittivity of free space",
            aliases=["eps_0", "eps0", "permittivity"],
            latex_symbol=r"\varepsilon_0",
            is_constant=True, constant_value=8.8541878128e-12, constant_unit="F/m",
            domains=["Electromagnetism"]
        ))
        self.register(PhysicalQuantity(
            name="VacuumPermeability", canonical_symbol="mu_0", dimension=DIM_PERMEABILITY,
            description="Magnetic permeability of free space",
            aliases=["mu0", "permeability"],
            latex_symbol=r"\mu_0",
            is_constant=True, constant_value=1.25663706212e-6, constant_unit="N/A^2",
            domains=["Electromagnetism"]
        ))


# Singleton Global Registry
GLOBAL_QUANTITY_REGISTRY = QuantityRegistry()
