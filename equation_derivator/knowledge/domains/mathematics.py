"""
Pure Mathematics, Calculus & Geometric Identities.
"""

from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.knowledge.database import EquationKnowledgeBase


def register_mathematics_equations(kb: EquationKnowledgeBase) -> None:
    # 1. Circle Area
    kb.register(PhysicalEquation.create(
        id="circle_area",
        name="Area of a Circle",
        domain="Mathematics",
        equation_str="A = pi * r^2",
        bindings={"A": "Area", "r": "Length"},
        tags=["Geometry", "Area"],
        description="Geometric area of a Euclidean circle of radius r."
    ))

    # 2. Sphere Surface Area
    kb.register(PhysicalEquation.create(
        id="sphere_surface_area",
        name="Surface Area of a Sphere",
        domain="Mathematics",
        equation_str="A = 4 * pi * r^2",
        bindings={"A": "Area", "r": "Length"},
        tags=["Geometry", "Area", "Spherical"],
        description="Surface area of a 3D Euclidean sphere of radius r."
    ))

    # 3. Sphere Volume
    kb.register(PhysicalEquation.create(
        id="sphere_volume",
        name="Volume of a Sphere",
        domain="Mathematics",
        equation_str="V = (4/3) * pi * r^3",
        bindings={"V": "Volume", "r": "Length"},
        tags=["Geometry", "Volume", "Spherical"],
        description="Volume of a 3D Euclidean sphere of radius r."
    ))

    # 4. Pythagorean Theorem
    kb.register(PhysicalEquation.create(
        id="pythagorean_theorem",
        name="Pythagorean Theorem",
        domain="Mathematics",
        equation_str="c^2 = a^2 + b^2",
        bindings={"a": "Length", "b": "Length", "c": "Length"},
        tags=["Geometry", "Trigonometry"],
        description="Relation between sides of a right Euclidean triangle."
    ))
