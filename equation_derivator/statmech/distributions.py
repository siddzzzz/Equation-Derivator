"""
Quantum Statistical Distributions (Bose-Einstein, Fermi-Dirac, Maxwell-Boltzmann)
and Planck Blackbody Radiation Derivation.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class QuantumDistributionResult:
    distribution_name: str
    occupancy_formula_latex: str
    chemical_potential_condition_latex: str
    classical_limit_latex: str
    planck_radiation_law_latex: Optional[str]
    stefan_boltzmann_law_latex: Optional[str]
    markdown: str

    def to_dict(self) -> dict:
        return {
            "distribution_name": self.distribution_name,
            "occupancy_formula_latex": self.occupancy_formula_latex,
            "chemical_potential_condition_latex": self.chemical_potential_condition_latex,
            "classical_limit_latex": self.classical_limit_latex,
            "planck_radiation_law_latex": self.planck_radiation_law_latex,
            "stefan_boltzmann_law_latex": self.stefan_boltzmann_law_latex,
            "markdown": self.markdown,
        }


class QuantumDistributionEngine:
    """
    Evaluates quantum statistics and radiation laws.
    """

    def evaluate_distributions(self) -> QuantumDistributionResult:
        be_latex = r"\langle n_{\text{BE}}(\epsilon) \rangle = \frac{1}{e^{\frac{\epsilon - \mu}{k_B T}} - 1} \quad (\mu < \epsilon_{\text{ground}})"
        fd_latex = r"\langle n_{\text{FD}}(\epsilon) \rangle = \frac{1}{e^{\frac{\epsilon - \mu}{k_B T}} + 1} \quad (0 \le \langle n \rangle \le 1, \; \text{Pauli Exclusion})"
        mb_latex = r"\langle n_{\text{MB}}(\epsilon) \rangle = e^{-\frac{\epsilon - \mu}{k_B T}} \quad (\text{Classical Limit } e^{\beta(\epsilon-\mu)} \gg 1)"

        planck_latex = r"u(\nu, T) = \frac{8\pi h \nu^3}{c^3} \frac{1}{e^{\frac{h\nu}{k_B T}} - 1}"
        stefan_latex = r"u_{\text{total}}(T) = \int_0^\infty u(\nu, T)\, d\nu = a T^4 \implies I = \sigma T^4 \quad \left(\sigma = \frac{2\pi^5 k_B^4}{15 c^2 h^3}\right)"

        md = rf"""# Quantum & Classical Statistical Distributions

## 1. Bose-Einstein Distribution (Integer Spin Bosons)
$${be_latex}$$
- Identical bosons can condense into ground state (Bose-Einstein Condensation).

## 2. Fermi-Dirac Distribution (Half-Integer Spin Fermions)
$${fd_latex}$$
- Pauli exclusion principle enforces maximum single occupancy per state.
- At $T = 0$, forms a sharp Fermi surface at Fermi energy $\mu(0) = E_F$.

## 3. Classical Maxwell-Boltzmann Limit
$${mb_latex}$$
- Emerges when thermal de Broglie wavelength $\lambda_{{\text{{th}}}} \ll \text{{interparticle distance}}$.

## 4. Planck Blackbody Radiation Law
Derived by combining density of photon modes $g(\nu) = \frac{{8\pi \nu^2}}{{c^3}}$ with Bose-Einstein photon occupancy ($\mu = 0$):
$${planck_latex}$$

## 5. Stefan-Boltzmann Total Radiant Energy
$${stefan_latex}$$
"""

        return QuantumDistributionResult(
            distribution_name="Universal Quantum & Classical Statistics",
            occupancy_formula_latex=be_latex,
            chemical_potential_condition_latex=r"\mu_{\text{Boson}} < \epsilon_0, \quad \mu_{\text{Fermion}}(0) = E_F",
            classical_limit_latex=mb_latex,
            planck_radiation_law_latex=planck_latex,
            stefan_boltzmann_law_latex=stefan_latex,
            markdown=md
        )
