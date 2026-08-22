"""
Classical Mechanics & Kinematics Equations.
"""

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.knowledge.database import EquationKnowledgeBase


def register_mechanics_equations(kb: EquationKnowledgeBase) -> None:
    # 1. Newton's Second Law
    kb.register(PhysicalEquation.create(
        id="newton_second_law",
        name="Newton's Second Law of Motion",
        domain="Mechanics",
        equation_str="F = m * a",
        assumptions=["Constant mass m", "Inertial reference frame", "v << c"],
        tags=["Dynamics", "Fundamental", "Force"],
        description="Relates the net force acting on a body to its mass and acceleration."
    ))

    # 2. Linear Momentum Definition
    kb.register(PhysicalEquation.create(
        id="linear_momentum_def",
        name="Linear Momentum Definition",
        domain="Mechanics",
        equation_str="p = m * v",
        assumptions=["Classical particle", "v << c"],
        tags=["Momentum", "Fundamental", "Kinematics"],
        description="Defines classical linear momentum as the product of mass and velocity."
    ))

    # 3. Kinetic Energy (Classical)
    kb.register(PhysicalEquation.create(
        id="kinetic_energy_def",
        name="Classical Kinetic Energy",
        domain="Mechanics",
        equation_str="K = 1/2 * m * v^2",
        assumptions=["v << c", "Point mass or translational motion"],
        tags=["Energy", "Work-Energy", "Fundamental"],
        description="The kinetic energy of an object of mass m moving with speed v."
    ))

    # 4. Kinetic Energy in terms of Momentum
    kb.register(PhysicalEquation.create(
        id="kinetic_energy_momentum",
        name="Kinetic Energy - Momentum Relation",
        domain="Mechanics",
        equation_str="K = p^2 / (2 * m)",
        assumptions=["v << c"],
        tags=["Energy", "Momentum", "Derived"],
        description="Expresses kinetic energy directly in terms of linear momentum and mass."
    ))

    # 5. Gravitational Potential Energy (Uniform Field)
    kb.register(PhysicalEquation.create(
        id="gravitational_potential_uniform",
        name="Gravitational Potential Energy (Uniform Field)",
        domain="Mechanics",
        equation_str="U = m * g * h",
        assumptions=["Uniform gravitational field g", "h << Earth radius"],
        tags=["Energy", "Gravity", "Potential"],
        description="Potential energy of a mass m at height h in a uniform gravitational field."
    ))

    # 6. Newton's Law of Universal Gravitation
    kb.register(PhysicalEquation.create(
        id="universal_gravitation",
        name="Newton's Law of Universal Gravitation",
        domain="Mechanics",
        equation_str="F = (G * M * m) / r^2",
        assumptions=["Point masses or spherically symmetric bodies", "Static/slowly moving masses"],
        tags=["Gravity", "Astrophysics", "Fundamental"],
        description="Gravitational attractive force between two masses separated by distance r."
    ))

    # 7. Gravitational Acceleration at Surface/Orbit
    kb.register(PhysicalEquation.create(
        id="surface_gravity",
        name="Gravitational Field / Acceleration",
        domain="Mechanics",
        equation_str="g = (G * M) / r^2",
        assumptions=["Spherically symmetric mass M", "Outside the mass radius r >= R"],
        tags=["Gravity", "Astrophysics", "Acceleration"],
        description="Gravitational acceleration produced by a mass M at distance r."
    ))

    # 8. Escape Velocity
    kb.register(PhysicalEquation.create(
        id="escape_velocity",
        name="Escape Velocity",
        domain="Mechanics",
        equation_str="v = sqrt(2 * G * M / r)",
        assumptions=["Radial launch from distance r", "Zero remaining kinetic energy at infinity", "No atmosphere"],
        tags=["Gravity", "Astrophysics", "Energy Conservation"],
        description="Minimum speed required for a body to escape a gravitational field."
    ))

    # 9. Circular Orbital Speed
    kb.register(PhysicalEquation.create(
        id="orbital_speed_circular",
        name="Circular Orbital Velocity",
        domain="Mechanics",
        equation_str="v = sqrt(G * M / r)",
        assumptions=["Circular orbit", "Central body mass M >> orbiter mass m"],
        tags=["Gravity", "Astrophysics", "Orbits"],
        description="Speed of a body in a circular gravitational orbit of radius r."
    ))

    # 10. Kepler's Third Law
    kb.register(PhysicalEquation.create(
        id="kepler_third_law",
        name="Kepler's Third Law of Planetary Motion",
        domain="Mechanics",
        equation_str="T^2 = (4 * pi^2 / (G * M)) * r^3",
        bindings={"T": "Time", "M": "Mass", "r": "Length", "G": "GravitationalConstant"},
        assumptions=["Circular/elliptical orbit", "M >> m"],
        tags=["Astrophysics", "Orbits", "Gravity"],
        description="Relates the orbital period T squared to the orbital radius r cubed."
    ))

    # 11. Work-Kinetic Energy Theorem
    kb.register(PhysicalEquation.create(
        id="work_definition_force_dist",
        name="Mechanical Work",
        domain="Mechanics",
        equation_str="W = F * d",
        bindings={"W": "Work", "F": "Force", "d": "Length"},
        assumptions=["Constant force along displacement direction"],
        tags=["Work-Energy", "Energy"],
        description="Work done by a constant force F over a displacement d."
    ))

    # 12. Mechanical Power
    kb.register(PhysicalEquation.create(
        id="power_work_time",
        name="Mechanical Power Definition",
        domain="Mechanics",
        equation_str="P = W / t",
        bindings={"P": "Power", "W": "Work", "t": "Time"},
        assumptions=["Constant work rate"],
        tags=["Power", "Work-Energy"],
        description="Rate of energy transfer or work performed over time t."
    ))

    # 13. Centripetal Acceleration
    kb.register(PhysicalEquation.create(
        id="centripetal_acceleration",
        name="Centripetal Acceleration",
        domain="Mechanics",
        equation_str="a = v^2 / r",
        bindings={"a": "Acceleration", "v": "Velocity", "r": "Length"},
        assumptions=["Uniform circular motion of radius r"],
        tags=["Kinematics", "Rotation"],
        description="Inward acceleration of an object moving in a circular path with speed v."
    ))

    # 14. Simple Harmonic Oscillator Frequency (Spring)
    kb.register(PhysicalEquation.create(
        id="spring_frequency",
        name="Spring Oscillator Angular Frequency",
        domain="Mechanics",
        equation_str="omega^2 = k / m",
        bindings={"omega": "AngularFrequency", "k": "SpringConstant", "m": "Mass"},
        assumptions=["Ideal massless spring", "Hooke's law validity"],
        tags=["Oscillations", "Waves"],
        description="Natural angular frequency of a mass-spring harmonic oscillator."
    ))

    # 15. Simple Pendulum Period
    kb.register(PhysicalEquation.create(
        id="pendulum_period",
        name="Simple Pendulum Period",
        domain="Mechanics",
        equation_str="T = 2 * pi * sqrt(L / g)",
        bindings={"T": "Time", "L": "Length", "g": "Acceleration"},
        assumptions=["Small angle approximation (sin theta ~= theta)", "Massless rigid string"],
        tags=["Oscillations", "Gravity"],
        description="Period of oscillation of a simple pendulum of length L in gravitational field g."
    ))
