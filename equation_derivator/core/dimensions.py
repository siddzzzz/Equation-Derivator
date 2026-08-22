"""
Physical Dimensions Engine.

Provides exact representation and arithmetic for the 7 SI base dimensions:
- M: Mass (kg)
- L: Length (m)
- T: Time (s)
- I: Electric Current (A)
- Theta: Temperature (K)
- N: Amount of Substance (mol)
- J: Luminous Intensity (cd)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Union, Tuple
from fractions import Fraction
import sympy as sp


@dataclass(frozen=True)
class Dimension:
    """
    Represents physical dimensions as a vector of rational exponents over base SI units.
    """
    M: Fraction = Fraction(0)
    L: Fraction = Fraction(0)
    T: Fraction = Fraction(0)
    I: Fraction = Fraction(0)
    Theta: Fraction = Fraction(0)
    N: Fraction = Fraction(0)
    J: Fraction = Fraction(0)

    def __post_init__(self):
        # Ensure all fields are Fractions
        for field in ("M", "L", "T", "I", "Theta", "N", "J"):
            val = getattr(self, field)
            if not isinstance(val, Fraction):
                object.__setattr__(self, field, Fraction(val))

    @property
    def is_dimensionless(self) -> bool:
        return all(
            getattr(self, k) == 0
            for k in ("M", "L", "T", "I", "Theta", "N", "J")
        )

    def to_vector(self) -> Tuple[Fraction, ...]:
        return (self.M, self.L, self.T, self.I, self.Theta, self.N, self.J)

    def to_dict(self) -> Dict[str, Union[int, float]]:
        return {
            k: (int(v) if v.denominator == 1 else float(v))
            for k in ("M", "L", "T", "I", "Theta", "N", "J")
            if (v := getattr(self, k)) != 0
        }

    def __mul__(self, other: Dimension) -> Dimension:
        if not isinstance(other, Dimension):
            raise TypeError(f"Cannot multiply Dimension by {type(other)}")
        return Dimension(
            M=self.M + other.M,
            L=self.L + other.L,
            T=self.T + other.T,
            I=self.I + other.I,
            Theta=self.Theta + other.Theta,
            N=self.N + other.N,
            J=self.J + other.J,
        )

    def __truediv__(self, other: Dimension) -> Dimension:
        if not isinstance(other, Dimension):
            raise TypeError(f"Cannot divide Dimension by {type(other)}")
        return Dimension(
            M=self.M - other.M,
            L=self.L - other.L,
            T=self.T - other.T,
            I=self.I - other.I,
            Theta=self.Theta - other.Theta,
            N=self.N - other.N,
            J=self.J - other.J,
        )

    def __pow__(self, power: Union[int, float, Fraction, sp.Rational]) -> Dimension:
        p = Fraction(str(power)) if not isinstance(power, (int, Fraction)) else Fraction(power)
        return Dimension(
            M=self.M * p,
            L=self.L * p,
            T=self.T * p,
            I=self.I * p,
            Theta=self.Theta * p,
            N=self.N * p,
            J=self.J * p,
        )

    def __str__(self) -> str:
        if self.is_dimensionless:
            return "1 (dimensionless)"
        parts = []
        for name in ("M", "L", "T", "I", "Theta", "N", "J"):
            val = getattr(self, name)
            if val != 0:
                if val == 1:
                    parts.append(name)
                elif val.denominator == 1:
                    parts.append(f"{name}^{val.numerator}")
                else:
                    parts.append(f"{name}^({val.numerator}/{val.denominator})")
        return f"[{' '.join(parts)}]"

    def __repr__(self) -> str:
        return f"Dimension({str(self)})"

    def to_latex(self) -> str:
        if self.is_dimensionless:
            return r"\text{dimensionless}"
        parts = []
        for name in ("M", "L", "T", "I", r"\Theta", "N", "J"):
            attr = "Theta" if name == r"\Theta" else name
            val = getattr(self, attr)
            if val != 0:
                if val == 1:
                    parts.append(name)
                elif val.denominator == 1:
                    parts.append(f"{name}^{{{val.numerator}}}")
                else:
                    parts.append(f"{name}^{{{val.numerator}/{val.denominator}}}")
        return r"\left[" + r"\,".join(parts) + r"\right]"

    @classmethod
    def from_string(cls, dim_str: str) -> Dimension:
        """
        Parses strings like '[M L^2 T^-2]', 'M*L/T^2', or '[M L^2 T^(-2)]' into a Dimension.
        """
        cleaned = dim_str.strip().strip("[]").strip()
        if not cleaned or cleaned in ("1", "dimensionless"):
            return cls.dimensionless()

        import re
        # Find all tokens: e.g. M, L^2, T^-2, T^(-2), Theta^1, etc.
        pattern = r"([A-Za-z]+)(?:\^?\(([-\d/]+)\)|\^([-\d/]+))?"
        tokens = re.findall(pattern, cleaned)
        
        powers: Dict[str, Fraction] = {
            "M": Fraction(0), "L": Fraction(0), "T": Fraction(0),
            "I": Fraction(0), "Theta": Fraction(0), "N": Fraction(0), "J": Fraction(0)
        }

        for base, exp1, exp2 in tokens:
            exp_str = exp1 or exp2
            if base in powers:
                p = Fraction(exp_str) if exp_str else Fraction(1)
                powers[base] += p

        return cls(**powers)

    @classmethod
    def dimensionless(cls) -> Dimension:
        return cls()


# Standard Pre-defined Dimensions
DIM_DIMENSIONLESS = Dimension()
DIM_MASS = Dimension(M=1)
DIM_LENGTH = Dimension(L=1)
DIM_TIME = Dimension(T=1)
DIM_CURRENT = Dimension(I=1)
DIM_TEMPERATURE = Dimension(Theta=1)
DIM_AMOUNT = Dimension(N=1)
DIM_LUMINOUS_INTENSITY = Dimension(J=1)

# Derived Kinematics & Mechanics
DIM_AREA = DIM_LENGTH ** 2
DIM_VOLUME = DIM_LENGTH ** 3
DIM_VELOCITY = DIM_LENGTH / DIM_TIME
DIM_ACCELERATION = DIM_LENGTH / (DIM_TIME ** 2)
DIM_JERK = DIM_LENGTH / (DIM_TIME ** 3)
DIM_FORCE = DIM_MASS * DIM_ACCELERATION
DIM_MOMENTUM = DIM_MASS * DIM_VELOCITY
DIM_ENERGY = DIM_FORCE * DIM_LENGTH
DIM_WORK = DIM_ENERGY
DIM_POWER = DIM_ENERGY / DIM_TIME
DIM_PRESSURE = DIM_FORCE / DIM_AREA
DIM_DENSITY = DIM_MASS / DIM_VOLUME
DIM_ACTION = DIM_ENERGY * DIM_TIME
DIM_ANGULAR_MOMENTUM = DIM_ACTION
DIM_TORQUE = DIM_ENERGY
DIM_FREQUENCY = DIM_TIME ** -1
DIM_ANGULAR_VELOCITY = DIM_FREQUENCY
DIM_ANGULAR_ACCELERATION = DIM_TIME ** -2
DIM_MOMENT_OF_INERTIA = DIM_MASS * (DIM_LENGTH ** 2)

# Derived Electromagnetism
DIM_CHARGE = DIM_CURRENT * DIM_TIME
DIM_VOLTAGE = DIM_ENERGY / DIM_CHARGE
DIM_ELECTRIC_FIELD = DIM_FORCE / DIM_CHARGE
DIM_MAGNETIC_FIELD = DIM_FORCE / (DIM_CHARGE * DIM_VELOCITY)
DIM_MAGNETIC_FLUX = DIM_MAGNETIC_FIELD * DIM_AREA
DIM_RESISTANCE = DIM_VOLTAGE / DIM_CURRENT
DIM_CAPACITANCE = DIM_CHARGE / DIM_VOLTAGE
DIM_INDUCTANCE = (DIM_VOLTAGE * DIM_TIME) / DIM_CURRENT
DIM_PERMITTIVITY = DIM_CAPACITANCE / DIM_LENGTH
DIM_PERMEABILITY = DIM_INDUCTANCE / DIM_LENGTH

# Derived Thermodynamics & Astrophysics
DIM_ENTROPY = DIM_ENERGY / DIM_TEMPERATURE
DIM_HEAT_CAPACITY = DIM_ENTROPY
DIM_SPECIFIC_HEAT = DIM_HEAT_CAPACITY / DIM_MASS
DIM_GRAVITATIONAL_CONSTANT = (DIM_LENGTH ** 3) / (DIM_MASS * (DIM_TIME ** 2))
DIM_PLANCK_CONSTANT = DIM_ACTION
DIM_BOLTZMANN_CONSTANT = DIM_ENTROPY
