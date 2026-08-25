"""
Non-Abelian Gauge Invariance, Yang-Mills Fields, and Higgs Spontaneous Symmetry Breaking.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class GaugeSymmetryResult:
    gauge_group: str
    covariant_derivative_latex: str
    field_strength_tensor_latex: str
    yang_mills_lagrangian_latex: str
    higgs_mechanism_latex: Optional[str]
    boson_mass_eigenvalues_latex: Dict[str, str]
    weinberg_angle_latex: Optional[str]
    markdown: str

    def to_dict(self) -> dict:
        return {
            "gauge_group": self.gauge_group,
            "covariant_derivative_latex": self.covariant_derivative_latex,
            "field_strength_tensor_latex": self.field_strength_tensor_latex,
            "yang_mills_lagrangian_latex": self.yang_mills_lagrangian_latex,
            "higgs_mechanism_latex": self.higgs_mechanism_latex,
            "boson_mass_eigenvalues_latex": self.boson_mass_eigenvalues_latex,
            "weinberg_angle_latex": self.weinberg_angle_latex,
            "markdown": self.markdown,
        }


class YangMillsGaugeEngine:
    """
    Constructs non-Abelian Yang-Mills gauge covariant derivatives and field strength tensors.
    """

    def evaluate_yang_mills(self, group: str = "SU(2)") -> GaugeSymmetryResult:
        g = sp.Symbol("g", positive=True, real=True)

        if group.upper() == "SU(2)":
            cov_d = r"D_\mu \psi = \left( \partial_\mu - i g A_\mu^a \frac{\sigma^a}{2} \right) \psi \quad (a \in \{1, 2, 3\})"
            f_tensor = r"F_{\mu\nu}^a = \partial_\mu A_\nu^a - \partial_\nu A_\mu^a + g \varepsilon^{abc} A_\mu^b A_\nu^c"
            ym_lag = r"\mathcal{L}_{\text{YM}} = -\frac{1}{4} F_{\mu\nu}^a F^{a\mu\nu} = -\frac{1}{2}\operatorname{Tr}(F_{\mu\nu} F^{\mu\nu})"
        elif group.upper() == "SU(3)":
            cov_d = r"D_\mu q = \left( \partial_\mu - i g_s G_\mu^a \frac{\lambda^a}{2} \right) q \quad (a \in \{1, \dots, 8\})"
            f_tensor = r"G_{\mu\nu}^a = \partial_\mu G_\nu^a - \partial_\nu G_\mu^a + g_s f^{abc} G_\mu^b G_\nu^c"
            ym_lag = r"\mathcal{L}_{\text{QCD}} = -\frac{1}{4} G_{\mu\nu}^a G^{a\mu\nu} + \bar{q}(i\not{D} - m)q"
        else:
            cov_d = r"D_\mu \psi = (\partial_\mu - i g A_\mu^a T^a) \psi"
            f_tensor = r"F_{\mu\nu}^a = \partial_\mu A_\nu^a - \partial_\nu A_\mu^a + g f^{abc} A_\mu^b A_\nu^c"
            ym_lag = r"\mathcal{L}_{\text{YM}} = -\frac{1}{4} F_{\mu\nu}^a F^{a\mu\nu}"

        md = (
            f"# Non-Abelian {group.upper()} Gauge Theory (Yang-Mills)\n\n"
            f"## Covariant Derivative\n"
            f"$${cov_d}$$\n\n"
            f"## Non-Abelian Field Strength Tensor\n"
            f"$${f_tensor}$$\n"
            f"*Notice the nonlinear self-interaction term leading to gauge boson self-coupling and asymptotic freedom.*\n\n"
            f"## Yang-Mills Gauge Invariant Lagrangian\n"
            f"$${ym_lag}$$\n"
        )

        return GaugeSymmetryResult(
            gauge_group=group.upper(),
            covariant_derivative_latex=cov_d,
            field_strength_tensor_latex=f_tensor,
            yang_mills_lagrangian_latex=ym_lag,
            higgs_mechanism_latex=None,
            boson_mass_eigenvalues_latex={},
            weinberg_angle_latex=None,
            markdown=md
        )


class HiggsMechanismEngine:
    """
    Evaluates Electroweak Spontaneous Symmetry Breaking SU(2)_L x U(1)_Y -> U(1)_EM.
    """

    def evaluate_electroweak_breaking(self) -> GaugeSymmetryResult:
        g = sp.Symbol("g", positive=True, real=True)
        g_prime = sp.Symbol("g'", positive=True, real=True)
        v = sp.Symbol("v", positive=True, real=True)  # Vacuum Expectation Value (246 GeV)

        # Gauge boson mass formulas
        mw_latex = r"M_W = \frac{1}{2} g v \approx 80.4\text{ GeV}"
        mz_latex = r"M_Z = \frac{1}{2} \sqrt{g^2 + g'^2} v \approx 91.2\text{ GeV}"
        m_gamma_latex = r"M_\gamma = 0\text{ GeV (Unbroken } U(1)_{\text{EM}}\text{ photon)}"

        higgs_pot = r"V(\Phi) = -\mu^2 \Phi^\dagger \Phi + \lambda (\Phi^\dagger \Phi)^2 \implies \langle\Phi\rangle = \frac{1}{\sqrt{2}} \begin{pmatrix} 0 \\ v \end{pmatrix} \quad \left(v = \sqrt{\frac{\mu^2}{\lambda}} \approx 246\text{ GeV}\right)"
        weinberg = r"\cos\theta_W = \frac{g}{\sqrt{g^2 + g'^2}} = \frac{M_W}{M_Z} \approx 0.88 \implies \sin^2\theta_W \approx 0.223"
        cov_d = r"D_\mu \Phi = \left( \partial_\mu - i g A_\mu^a \frac{\sigma^a}{2} - i \frac{g'}{2} B_\mu \right) \Phi"

        md = (
            r"# Electroweak Spontaneous Symmetry Breaking (SU(2)_L x U(1)_Y -> U(1)_EM)" + "\n\n"
            r"## 1. Complex Higgs Doublet & Goldstone Potential" + "\n"
            f"$${higgs_pot}$$\n\n"
            r"## 2. Covariant Kinetic Mass Generation" + "\n"
            f"$${cov_d}$$\n\n"
            r"## 3. Gauge Boson Mass Spectrum" + "\n"
            f"- $${mw_latex}$$\n"
            f"- $${mz_latex}$$\n"
            f"- $${m_gamma_latex}$$\n\n"
            r"## 4. Weak Mixing (Weinberg) Angle" + "\n"
            f"$${weinberg}$$\n"
        )

        return GaugeSymmetryResult(
            gauge_group="SU(2)_L x U(1)_Y -> U(1)_EM",
            covariant_derivative_latex=cov_d,
            field_strength_tensor_latex=r"W_{\mu\nu}^a = \partial_\mu W_\nu^a - \partial_\nu W_\mu^a + g \varepsilon^{abc} W_\mu^b W_\nu^c, \quad B_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu",
            yang_mills_lagrangian_latex=r"\mathcal{L}_{\text{EW}} = -\frac{1}{4} W_{\mu\nu}^a W^{a\mu\nu} - \frac{1}{4} B_{\mu\nu} B^{\mu\nu} + |D_\mu \Phi|^2 - V(\Phi)",
            higgs_mechanism_latex=higgs_pot,
            boson_mass_eigenvalues_latex={
                "M_W": mw_latex,
                "M_Z": mz_latex,
                "M_\\gamma": m_gamma_latex,
            },
            weinberg_angle_latex=weinberg,
            markdown=md
        )
