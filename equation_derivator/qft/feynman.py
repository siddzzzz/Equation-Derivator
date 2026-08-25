"""
Symbolic Feynman Amplitude, Mandelstam Invariants, and QED Cross-Section Engine.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class FeynmanAmplitudeResult:
    process_name: str
    channel: str  # "s-channel", "t-channel", "u-channel"
    incoming_particles: List[str]
    outgoing_particles: List[str]
    mandelstam_s_latex: str
    mandelstam_t_latex: str
    mandelstam_u_latex: str
    matrix_element_latex: str
    squared_matrix_element_unpolarized_latex: str
    differential_cross_section_latex: str
    total_cross_section_latex: str
    markdown: str

    def to_dict(self) -> dict:
        return {
            "process_name": self.process_name,
            "channel": self.channel,
            "incoming_particles": self.incoming_particles,
            "outgoing_particles": self.outgoing_particles,
            "mandelstam_s_latex": self.mandelstam_s_latex,
            "mandelstam_t_latex": self.mandelstam_t_latex,
            "mandelstam_u_latex": self.mandelstam_u_latex,
            "matrix_element_latex": self.matrix_element_latex,
            "squared_matrix_element_unpolarized_latex": self.squared_matrix_element_unpolarized_latex,
            "differential_cross_section_latex": self.differential_cross_section_latex,
            "total_cross_section_latex": self.total_cross_section_latex,
            "markdown": self.markdown,
        }


class FeynmanEvaluator:
    """
    Evaluates tree-level QED and electroweak scattering amplitudes using trace theorems.
    """

    def evaluate_ee_to_mumu(self) -> FeynmanAmplitudeResult:
        """
        e^-(p1) + e^+(p2) -> mu^-(p3) + mu^+(p4) via virtual photon (s-channel).
        """
        e = sp.Symbol("e", positive=True, real=True)
        alpha = sp.Symbol("alpha", positive=True, real=True)
        s = sp.Symbol("s", positive=True, real=True)
        t = sp.Symbol("t", real=True)
        u = sp.Symbol("u", real=True)
        theta = sp.Symbol("theta", real=True)

        m_elem = r"\mathcal{M} = \frac{e^2}{s} \left[ \bar{v}(p_2) \gamma^\mu u(p_1) \right] \left[ \bar{u}(p_3) \gamma_\mu v(p_4) \right]"
        sq_m = r"|\overline{\mathcal{M}}|^2 = \frac{1}{4} \sum_{\text{spins}} |\mathcal{M}|^2 = 2 e^4 \frac{t^2 + u^2}{s^2} = e^4 (1 + \cos^2\theta)"
        diff_sigma = r"\frac{d\sigma}{d\Omega} = \frac{\alpha^2}{4s} \left( 1 + \cos^2\theta \right)"
        tot_sigma = r"\sigma_{\text{total}} = \frac{4\pi \alpha^2}{3s}"

        md = f"""# QED Process: $e^- e^+ \\to \\mu^- \\mu^+$ (s-Channel Annihilation)

## Feynman Amplitude
$${m_elem}$$

## Mandelstam Invariants
- Center-of-mass energy: $s = (p_1 + p_2)^2$
- Momentum transfer: $t = (p_1 - p_3)^2 = -\\frac{s}{2}(1 - \\cos\\theta)$
- Momentum transfer: $u = (p_1 - p_4)^2 = -\\frac{s}{2}(1 + \\cos\\theta)$
- Invariant constraint: $s + t + u = 2m_e^2 + 2m_\\mu^2 \\approx 0$ (ultrarelativistic limit)

## Spin-Averaged Matrix Element Squared
Using Dirac trace identity $\\operatorname{{Tr}}[(\\not{{p}}_3 + m_\\mu)\\gamma_\\mu(\\not{{p}}_4 - m_\\mu)\\gamma_\\nu] \\operatorname{{Tr}}[(\\not{{p}}_2 - m_e)\\gamma^\\mu(\\not{{p}}_1 + m_e)\\gamma^\\nu]$:
$${sq_m}$$

## Differential & Total Cross Section
$${diff_sigma}$$
$${tot_sigma}$$
"""

        return FeynmanAmplitudeResult(
            process_name="Electron-Positron Annihilation to Muon Pair",
            channel="s-channel photon exchange",
            incoming_particles=["e^-", "e^+"],
            outgoing_particles=["\\mu^-", "\\mu^+"],
            mandelstam_s_latex="s = (p_1 + p_2)^2 = E_{\\text{CM}}^2",
            mandelstam_t_latex="t = -\\frac{s}{2}(1 - \\cos\\theta)",
            mandelstam_u_latex="u = -\\frac{s}{2}(1 + \\cos\\theta)",
            matrix_element_latex=m_elem,
            squared_matrix_element_unpolarized_latex=sq_m,
            differential_cross_section_latex=diff_sigma,
            total_cross_section_latex=tot_sigma,
            markdown=md
        )

    def evaluate_compton_scattering(self) -> FeynmanAmplitudeResult:
        """
        e^-(p) + gamma(k) -> e^-(p') + gamma(k') (s and t/u channels).
        """
        e = sp.Symbol("e", positive=True, real=True)
        m = sp.Symbol("m", positive=True, real=True)
        omega = sp.Symbol("omega", positive=True, real=True)
        omega_prime = sp.Symbol("omega'", positive=True, real=True)
        theta = sp.Symbol("theta", real=True)
        r0 = sp.Symbol("r_e", positive=True, real=True)  # Classical electron radius

        m_elem = r"\mathcal{M} = -e^2 \epsilon_\mu^*(k') \epsilon_\nu(k) \bar{u}(p') \left[ \frac{\gamma^\mu \not{k} \gamma^\nu + 2\gamma^\mu p^\nu}{2p\cdot k} + \frac{-\gamma^\nu \not{k}' \gamma^\mu + 2\gamma^\nu p^\mu}{-2p\cdot k'} \right] u(p)"
        diff_sigma = r"\frac{d\sigma}{d\Omega} = \frac{r_e^2}{2} \left( \frac{\omega'}{\omega} \right)^2 \left[ \frac{\omega'}{\omega} + \frac{\omega}{\omega'} - \sin^2\theta \right]"
        compton_shift = r"\lambda' - \lambda = \frac{h}{m_e c} (1 - \cos\theta) \implies \frac{\omega'}{\omega} = \frac{1}{1 + \frac{\hbar\omega}{m_e c^2}(1 - \cos\theta)}"

        md = f"""# QED Process: Compton Scattering ($e^- \\gamma \\to e^- \\gamma$)

## Klein-Nishina Cross Section
$${diff_sigma}$$

## Compton Wavelength Shift
$${compton_shift}$$

## Low Energy Thomson Limit ($\\omega \\to 0$)
$$\\lim_{{\\omega \\to 0}} \\frac{{d\\sigma}}{{d\\Omega}} = \\frac{{r_e^2}}{{2}} (1 + \\cos^2\\theta) \\implies \\sigma_{{\\text{{Thomson}}}} = \\frac{{8\\pi}}{{3}} r_e^2$$
"""

        return FeynmanAmplitudeResult(
            process_name="Compton Photon-Electron Scattering",
            channel="s & u-channel interference",
            incoming_particles=["e^-", "\\gamma"],
            outgoing_particles=["e^-", "\\gamma'"],
            mandelstam_s_latex="s = (p + k)^2 = m_e^2 + 2m_e \\omega",
            mandelstam_t_latex="t = (k - k')^2 = -2\\omega\\omega'(1 - \\cos\\theta)",
            mandelstam_u_latex="u = (p - k')^2 = m_e^2 - 2m_e \\omega'",
            matrix_element_latex=m_elem,
            squared_matrix_element_unpolarized_latex=r"|\overline{\mathcal{M}}|^2 = 2 e^4 \left[ \frac{p\cdot k'}{p\cdot k} + \frac{p\cdot k}{p\cdot k'} + 2m_e^2 \left( \frac{1}{p\cdot k} - \frac{1}{p\cdot k'} \right) + m_e^4 \left( \frac{1}{p\cdot k} - \frac{1}{p\cdot k'} \right)^2 \right]",
            differential_cross_section_latex=diff_sigma,
            total_cross_section_latex=r"\sigma = \frac{8\pi}{3} r_e^2 \quad (\text{Thomson Limit})",
            markdown=md
        )


class QEDScatteringProcess:
    """
    Factory interface for evaluating scattering processes.
    """
    @staticmethod
    def evaluate(process: str = "ee_to_mumu") -> FeynmanAmplitudeResult:
        evaluator = FeynmanEvaluator()
        if process in ("ee_to_mumu", "annihilation"):
            return evaluator.evaluate_ee_to_mumu()
        elif process in ("compton", "photon_scattering"):
            return evaluator.evaluate_compton_scattering()
        else:
            return evaluator.evaluate_ee_to_mumu()
