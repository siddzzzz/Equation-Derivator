"""
Canonical Partition Function & Thermodynamic Potentials Derivation Engine.
Computes F, S, U, P, and C_v directly from symbolic partition functions Z(T, V, N).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class ThermodynamicPotentialsResult:
    model_name: str
    partition_function_latex: str
    free_energy_F_latex: str
    entropy_S_latex: str
    internal_energy_U_latex: str
    pressure_P_latex: Optional[str]
    heat_capacity_Cv_latex: str
    equation_of_state_latex: Optional[str]
    markdown: str

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "partition_function_latex": self.partition_function_latex,
            "free_energy_F_latex": self.free_energy_F_latex,
            "entropy_S_latex": self.entropy_S_latex,
            "internal_energy_U_latex": self.internal_energy_U_latex,
            "pressure_P_latex": self.pressure_P_latex,
            "heat_capacity_Cv_latex": self.heat_capacity_Cv_latex,
            "equation_of_state_latex": self.equation_of_state_latex,
            "markdown": self.markdown,
        }


class PartitionFunctionEngine:
    """
    Deduces all thermodynamic observables from the canonical partition function Z.
    """

    def derive_from_Z(
        self,
        Z_expr: Union[str, sp.Expr],
        model_name: str = "Thermodynamic Ensemble",
        has_volume: bool = True
    ) -> ThermodynamicPotentialsResult:
        from equation_derivator.core.symbols import parse_expression_safely

        T = sp.Symbol("T", positive=True, real=True)
        V = sp.Symbol("V", positive=True, real=True)
        N = sp.Symbol("N", positive=True, real=True)
        kB = sp.Symbol("k_B", positive=True, real=True)
        B = sp.Symbol("B", real=True)
        beta = sp.Symbol("beta", positive=True, real=True)

        if isinstance(Z_expr, str):
            # If user used beta, substitute beta -> 1/(k_B * T)
            parsed = parse_expression_safely(Z_expr)
            Z = parsed.subs([(s, 1 / (kB * T)) for s in parsed.free_symbols if s.name == "beta"])
        else:
            Z = Z_expr.subs([(s, 1 / (kB * T)) for s in Z_expr.free_symbols if s.name == "beta"])

        # 1. Helmholtz Free Energy F = -k_B * T * ln(Z)
        F_raw = -kB * T * sp.log(Z)
        F = sp.simplify(F_raw)

        # 2. Entropy S = - dF/dT
        S = sp.simplify(-sp.diff(F, T))

        # 3. Internal Energy U = F + T*S
        U = sp.simplify(F + T * S)

        # 4. Pressure P = - dF/dV
        P = sp.simplify(-sp.diff(F, V)) if any(s.name == "V" for s in Z.free_symbols) else None

        # 5. Heat Capacity Cv = dU/dT = -T * d^2 F / dT^2
        Cv = sp.simplify(sp.diff(U, T))

        # 6. Magnetization M = - dF/dB (if magnetic field B present)
        has_B = any(s.name == "B" for s in Z.free_symbols)
        M = sp.simplify(-sp.diff(F, B)) if has_B else None

        # 7. Chemical Potential mu = dF/dN (if N present)
        has_N = any(s.name == "N" for s in Z.free_symbols)
        mu = sp.simplify(sp.diff(F, N)) if has_N else None

        # Equation of state if pressure is available
        eos_latex = f"P = {sp.latex(P)}" if P is not None else None

        md = (
            f"# Statistical Mechanics: {model_name}\n\n"
            f"## 1. Canonical Partition Function\n"
            f"$$\\mathcal{{Z}} = {sp.latex(Z)}$$\n\n"
            f"## 2. Helmholtz Free Energy ($F = -k_B T \\ln \\mathcal{{Z}}$)\n"
            f"$$F = {sp.latex(F)}$$\n\n"
            f"## 3. Entropy ($S = -\\frac{{\\partial F}}{{\\partial T}}$)\n"
            f"$$S = {sp.latex(S)}$$\n\n"
            f"## 4. Internal Energy ($U = F + TS$)\n"
            f"$$U = {sp.latex(U)}$$\n\n"
            f"## 5. Heat Capacity ($C_v = \\frac{{\\partial U}}{{\\partial T}}$)\n"
            f"$$C_v = {sp.latex(Cv)}$$\n"
        )
        if P is not None:
            md += f"\n## 6. Equation of State ($P = -\\frac{{\\partial F}}{{\\partial V}}$)\n$$P = {sp.latex(P)}$$\n"
        if M is not None:
            md += f"\n## 7. Magnetization ($M = -\\frac{{\\partial F}}{{\\partial B}}$)\n$$M = {sp.latex(M)}$$\n"
        if mu is not None:
            md += f"\n## 8. Chemical Potential ($\\mu = \\frac{{\\partial F}}{{\\partial N}}$)\n$$\\mu = {sp.latex(mu)}$$\n"

        return ThermodynamicPotentialsResult(
            model_name=model_name,
            partition_function_latex=sp.latex(Z),
            free_energy_F_latex=sp.latex(F),
            entropy_S_latex=sp.latex(S),
            internal_energy_U_latex=sp.latex(U),
            pressure_P_latex=sp.latex(P) if P is not None else None,
            heat_capacity_Cv_latex=sp.latex(Cv),
            equation_of_state_latex=eos_latex,
            markdown=md
        )

    def evaluate_ideal_gas(self) -> ThermodynamicPotentialsResult:
        """
        Monatomic Ideal Gas: Z = 1/N! * (V / lambda_th^3)^N where lambda_th = h / sqrt(2*pi*m*kB*T).
        """
        T = sp.Symbol("T", positive=True, real=True)
        V = sp.Symbol("V", positive=True, real=True)
        N = sp.Symbol("N", positive=True, real=True)
        kB = sp.Symbol("k_B", positive=True, real=True)
        m = sp.Symbol("m", positive=True, real=True)
        h = sp.Symbol("h", positive=True, real=True)

        lambda_th = h / sp.sqrt(2 * sp.pi * m * kB * T)
        # Using Stirling's approximation ln(N!) ~ N ln N - N
        # F = -N*kB*T*(ln(V/N * (2*pi*m*kB*T/h^2)^(3/2)) + 1)
        F_latex = r"F = -N k_B T \left[ \ln\left( \frac{V}{N} \left( \frac{2\pi m k_B T}{h^2} \right)^{3/2} \right) + 1 \right]"
        P_latex = r"P = -\frac{\partial F}{\partial V} = \frac{N k_B T}{V} \implies P V = N k_B T"
        U_latex = r"U = \frac{3}{2} N k_B T"
        Cv_latex = r"C_v = \frac{3}{2} N k_B"
        S_latex = r"S = N k_B \left[ \ln\left( \frac{V}{N} \left( \frac{2\pi m k_B T}{h^2} \right)^{3/2} \right) + \frac{5}{2} \right] \quad (\text{Sackur-Tetrode Equation})"

        md = rf"""# Classical Monatomic Ideal Gas

## Partition Function (Gibbs Factor Included)
$$\mathcal{{Z}} = \frac{{1}}{{N!}} \left( \frac{{V}}{{\lambda_{{\text{{th}}}}^3}} \right)^N \quad \text{{where }} \lambda_{{\text{{th}}}} = \frac{{h}}{{\sqrt{{2\pi m k_B T}}}}$$

## Thermodynamic Potentials
- **Free Energy**: $${F_latex}$$
- **Sackur-Tetrode Entropy**: $${S_latex}$$
- **Equipartition Internal Energy**: $${U_latex}$$
- **Heat Capacity**: $${Cv_latex}$$
- **Ideal Gas Law**: $${P_latex}$$
"""

        return ThermodynamicPotentialsResult(
            model_name="Classical Monatomic Ideal Gas",
            partition_function_latex=r"\mathcal{Z} = \frac{1}{N!} \left( \frac{V}{\lambda_{\text{th}}^3} \right)^N",
            free_energy_F_latex=F_latex,
            entropy_S_latex=S_latex,
            internal_energy_U_latex=U_latex,
            pressure_P_latex=P_latex,
            heat_capacity_Cv_latex=Cv_latex,
            equation_of_state_latex=r"P V = N k_B T",
            markdown=md
        )

    def evaluate_quantum_harmonic_oscillator(self) -> ThermodynamicPotentialsResult:
        """
        Quantum Harmonic Oscillator: E_n = (n + 1/2)*hbar*omega.
        Z = exp(-beta*hbar*omega/2) / (1 - exp(-beta*hbar*omega)) = 1 / (2 sinh(beta*hbar*omega / 2)).
        """
        T = sp.Symbol("T", positive=True, real=True)
        kB = sp.Symbol("k_B", positive=True, real=True)
        hbar = sp.Symbol("hbar", positive=True, real=True)
        omega = sp.Symbol("omega", positive=True, real=True)

        Z_latex = r"\mathcal{Z} = \sum_{n=0}^\infty e^{-\beta \hbar\omega (n + 1/2)} = \frac{e^{-\frac{\hbar\omega}{2 k_B T}}}{1 - e^{-\frac{\hbar\omega}{k_B T}}} = \frac{1}{2\sinh\left(\frac{\hbar\omega}{2 k_B T}\right)}"
        F_latex = r"F = \frac{1}{2}\hbar\omega + k_B T \ln\left(1 - e^{-\frac{\hbar\omega}{k_B T}}\right)"
        U_latex = r"\langle E \rangle = \hbar\omega \left( \frac{1}{2} + \frac{1}{e^{\frac{\hbar\omega}{k_B T}} - 1} \right) \quad (\text{Zero-point energy + Bose-Einstein excitation})"
        Cv_latex = r"C_v = k_B \left(\frac{\hbar\omega}{k_B T}\right)^2 \frac{e^{\frac{\hbar\omega}{k_B T}}}{\left(e^{\frac{\hbar\omega}{k_B T}} - 1\right)^2} \quad (\text{Einstein Heat Capacity})"

        md = rf"""# Quantum Harmonic Oscillator

## Canonical Partition Function
$${Z_latex}$$

## Internal Energy & Heat Capacity
- **Zero-Point & Thermal Energy**: $${U_latex}$$
- **Einstein Heat Capacity**: $${Cv_latex}$$

## High Temperature Limit ($k_B T \gg \hbar\omega$)
$$\lim_{{T \to \infty}} \langle E \rangle = k_B T, \quad \lim_{{T \to \infty}} C_v = k_B \quad (\text{{Classical Dulong-Petit Equipartition}})$$
"""

        return ThermodynamicPotentialsResult(
            model_name="Quantum Harmonic Oscillator",
            partition_function_latex=Z_latex,
            free_energy_F_latex=F_latex,
            entropy_S_latex=r"S = k_B \left[ \frac{\hbar\omega / k_B T}{e^{\hbar\omega / k_B T} - 1} - \ln\left(1 - e^{-\hbar\omega / k_B T}\right) \right]",
            internal_energy_U_latex=U_latex,
            pressure_P_latex=None,
            heat_capacity_Cv_latex=Cv_latex,
            equation_of_state_latex=None,
            markdown=md
        )
