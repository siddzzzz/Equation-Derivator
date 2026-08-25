"""
General Relativistic Orbit & Photon Geodesic Ray-Tracing Simulator.
Solves the Schwarzschild equatorial geodesic equation:
(dr/dphi)^2 = (E^2 - (1 - r_s/r)(1 + L^2/r^2)) / (L^2/r^4).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np


@dataclass
class RelativisticOrbitResult:
    r_coords: List[float]
    phi_coords: List[float]
    x_cartesian: List[float]
    y_cartesian: List[float]
    schwarzschild_radius: float
    photon_sphere_radius: float
    isco_radius: float
    perihelion_advance_rad: float
    is_captured_by_horizon: bool

    def to_dict(self) -> dict:
        return {
            "r_coords": self.r_coords,
            "phi_coords": self.phi_coords,
            "x_cartesian": self.x_cartesian,
            "y_cartesian": self.y_cartesian,
            "schwarzschild_radius": self.schwarzschild_radius,
            "photon_sphere_radius": self.photon_sphere_radius,
            "isco_radius": self.isco_radius,
            "perihelion_advance_rad": self.perihelion_advance_rad,
            "is_captured_by_horizon": self.is_captured_by_horizon,
        }


class RelativisticOrbitSim:
    """
    Simulates test particle orbits and photon null-geodesics around Schwarzschild black holes.
    """

    def __init__(self, M: float = 1.0, G: float = 1.0, c: float = 1.0):
        self.M = M
        self.G = G
        self.c = c
        self.r_s = 2.0 * G * M / (c**2)
        self.r_photon = 1.5 * self.r_s      # 3 GM / c^2
        self.r_isco = 3.0 * self.r_s        # 6 GM / c^2

    def simulate_particle_orbit(
        self,
        r0: float = 15.0,
        v_phi0: float = 0.28,
        v_r0: float = 0.0,
        n_steps: int = 1500,
        dt: float = 0.05
    ) -> RelativisticOrbitResult:
        """
        Integrates equatorial geodesic:
        d^2 r / dtau^2 = -GM/r^2 + L^2/r^3 - 3GM L^2 / (c^2 r^4)
        dphi / dtau = L / r^2
        """
        r = float(r0)
        phi = 0.0
        vr = float(v_r0)
        L = r0 * float(v_phi0)  # Specific angular momentum

        r_hist = [r]
        phi_hist = [phi]
        x_hist = [r * np.cos(phi)]
        y_hist = [r * np.sin(phi)]
        captured = False

        GM = self.G * self.M
        c_sq = self.c**2

        for _ in range(n_steps):
            if r <= self.r_s * 1.01:
                captured = True
                break

            # 1. Acceleration with relativistic correction -3GM L^2 / (c^2 r^4)
            a_newton = -GM / (r**2) + (L**2) / (r**3)
            a_gr = -3.0 * GM * (L**2) / (c_sq * (r**4))
            ar = a_newton + a_gr

            # 2. Verlet / Euler-Cromer update
            vr += ar * dt
            r += vr * dt
            dphi = (L / (r**2)) * dt
            phi += dphi

            r_hist.append(r)
            phi_hist.append(phi)
            x_hist.append(r * np.cos(phi))
            y_hist.append(r * np.sin(phi))

        # Estimate perihelion precession per revolution: delta_phi = 6*pi*G*M / (c^2 * a * (1 - e^2))
        perihelion_shift = float(6.0 * np.pi * GM / (c_sq * r0))

        skip = max(1, len(r_hist) // 400)

        return RelativisticOrbitResult(
            r_coords=r_hist[::skip],
            phi_coords=phi_hist[::skip],
            x_cartesian=x_hist[::skip],
            y_cartesian=y_hist[::skip],
            schwarzschild_radius=round(self.r_s, 4),
            photon_sphere_radius=round(self.r_photon, 4),
            isco_radius=round(self.r_isco, 4),
            perihelion_advance_rad=round(perihelion_shift, 6),
            is_captured_by_horizon=captured
        )

    def simulate_photon_deflection(
        self,
        impact_parameter_b: float = 6.0,
        x_start: float = -20.0,
        y_start: float = 6.0,
        n_steps: int = 1000,
        dt: float = 0.05
    ) -> RelativisticOrbitResult:
        """
        Simulates null geodesic trajectory of a light ray passing near a black hole.
        """
        x = float(x_start)
        y = float(y_start)
        vx = self.c
        vy = 0.0

        r_hist = []
        phi_hist = []
        x_hist = [x]
        y_hist = [y]
        captured = False

        GM = self.G * self.M
        c_sq = self.c**2

        for _ in range(n_steps):
            r = np.sqrt(x**2 + y**2)
            if r <= self.r_s * 1.01:
                captured = True
                break

            r_hist.append(r)
            phi_hist.append(np.arctan2(y, x))

            # GR photon deflection effective acceleration: a = -3GM / (c^2 r^5) * (x, y) * L^2 ...
            # Standard light ray acceleration toward center: a_vec = - 2 * GM / r^3 * r_vec
            a_mag = -2.0 * GM / (r**3)
            ax = a_mag * x
            ay = a_mag * y

            vx += ax * dt
            vy += ay * dt

            # Enforce speed of light normalization
            v_mag = np.sqrt(vx**2 + vy**2)
            vx = (vx / v_mag) * self.c
            vy = (vy / v_mag) * self.c

            x += vx * dt
            y += vy * dt

            x_hist.append(x)
            y_hist.append(y)

            if x > abs(x_start) + 5.0:
                break

        skip = max(1, len(x_hist) // 300)

        # Einstein's deflection angle: theta = 4GM / (c^2 b)
        deflection = 4.0 * GM / (c_sq * impact_parameter_b)

        return RelativisticOrbitResult(
            r_coords=r_hist[::skip],
            phi_coords=phi_hist[::skip],
            x_cartesian=x_hist[::skip],
            y_cartesian=y_hist[::skip],
            schwarzschild_radius=round(self.r_s, 4),
            photon_sphere_radius=round(self.r_photon, 4),
            isco_radius=round(self.r_isco, 4),
            perihelion_advance_rad=round(deflection, 6),
            is_captured_by_horizon=captured
        )
