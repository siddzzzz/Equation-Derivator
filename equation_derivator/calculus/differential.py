"""
Differential Equations & Dynamic Systems Solver.
Symbolically solves physical ODEs, damped-driven harmonic oscillators,
and quantum eigenvalue problems (Schrödinger infinite well).
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
import sympy as sp

from equation_derivator.core.symbols import VariableContext, parse_expression_safely
from equation_derivator.derivation.step import DerivationStep


@dataclass
class DifferentialResult:
    """
    Encapsulates the complete step-by-step solution of a physical differential equation.
    """
    name: str
    ode_type: str
    differential_equation: sp.Eq
    differential_equation_latex: str
    general_solution: sp.Eq
    general_solution_latex: str
    characteristic_equation: Optional[sp.Eq] = None
    roots: Optional[List[Any]] = None
    particular_solution: Optional[sp.Eq] = None
    eigenvalues_and_states: Optional[List[Dict[str, Any]]] = None
    steps: List[DerivationStep] = field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [
            f"# Differential Equation Solution: {self.name}\n",
            f"**Classification:** {self.ode_type}\n",
            f"**Differential Equation:**",
            f"$${self.differential_equation_latex}$$\n",
            "## Step-by-Step Derivation Chain\n"
        ]

        for step in self.steps:
            lines.append(f"### Step {step.step_number}: {step.operation}")
            lines.append(f"{step.explanation}")
            lines.append(f"$${step.latex}$$\n")

        lines.append("## Final Solution\n")
        lines.append(f"$${self.general_solution_latex}$$\n")

        if self.eigenvalues_and_states:
            lines.append("### Quantum Eigenstates & Energy Spectrum:\n")
            for state in self.eigenvalues_and_states:
                lines.append(f"- **Level $n={state['n']}$:** Energy $E_{state['n']} = {state['energy_latex']}$, Wavefunction $\\psi_{state['n']}(x) = {state['psi_latex']}$")
            lines.append("")

        return "\n".join(lines)


class DifferentialEquationSolver:
    """
    Solver for physical ordinary differential equations and boundary-value eigenvalue problems.
    """

    def __init__(self, context: Optional[VariableContext] = None):
        self.context = context or VariableContext()

    def solve_damped_harmonic_oscillator(
        self,
        m: str = "m",
        gamma: str = "gamma",
        k: str = "k",
        driving_force: Optional[str] = None
    ) -> DifferentialResult:
        """
        Solves the damped harmonic oscillator m*x''(t) + gamma*x'(t) + k*x(t) = F(t).
        """
        t = sp.Symbol("t", real=True)
        m_s = sp.Symbol(m, positive=True, real=True)
        gamma_s = sp.Symbol(gamma, positive=True, real=True)
        k_s = sp.Symbol(k, positive=True, real=True)
        x = sp.Function("x")(t)

        steps: List[DerivationStep] = []
        step_num = 1

        # 1. State ODE
        lhs_ode = m_s * x.diff(t, 2) + gamma_s * x.diff(t, 1) + k_s * x
        if driving_force:
            F_expr = parse_expression_safely(driving_force, self.context)
            ode = sp.Eq(lhs_ode, F_expr)
            ode_type = "2nd-Order Inhomogeneous Linear ODE (Driven Damped Oscillator)"
        else:
            ode = sp.Eq(lhs_ode, 0)
            ode_type = "2nd-Order Homogeneous Linear ODE (Damped Oscillator)"

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Formulate Equation of Motion",
            expression=ode,
            latex=f"m \\ddot{{x}} + \\gamma \\dot{{x}} + k x = {sp.latex(ode.rhs)}",
            explanation="State the dynamic balance of inertia, viscous damping, and Hooke's restoring force."
        ))
        step_num += 1

        # 2. Standard Form
        omega_0_sq = k_s / m_s
        two_beta = gamma_s / m_s
        std_ode = sp.Eq(x.diff(t, 2) + two_beta * x.diff(t, 1) + omega_0_sq * x, ode.rhs / m_s)

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Normalize to Standard Form",
            expression=std_ode,
            latex=f"\\ddot{{x}} + 2\\beta \\dot{{x}} + \\omega_0^2 x = 0 \\quad \\text{{where }} \\omega_0 = \\sqrt{{\\frac{{k}}{{m}}}}, \\; \\beta = \\frac{{\\gamma}}{{2m}}",
            explanation="Divide by mass $m$ to identify natural frequency $\\omega_0$ and damping coefficient $\\beta$."
        ))
        step_num += 1

        # 3. Characteristic Equation
        r = sp.Symbol("r")
        char_eq = sp.Eq(r**2 + two_beta * r + omega_0_sq, 0)
        discriminant = two_beta**2 - 4 * omega_0_sq

        # Characteristic Roots
        r1 = -gamma_s / (2 * m_s) + sp.sqrt((gamma_s / (2 * m_s))**2 - k_s / m_s)
        r2 = -gamma_s / (2 * m_s) - sp.sqrt((gamma_s / (2 * m_s))**2 - k_s / m_s)

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Characteristic Polynomial & Roots",
            expression=char_eq,
            latex=f"r^2 + 2\\beta r + \\omega_0^2 = 0 \\implies r_{{1,2}} = -\\beta \\pm \\sqrt{{\\beta^2 - \\omega_0^2}}",
            explanation="Assume trial exponential solution $x(t) = e^{rt}$ and solve the characteristic quadratic."
        ))
        step_num += 1

        # 4. Underdamped Physical Regime Solution
        omega_d = sp.Symbol("omega_d", real=True, positive=True)
        C1 = sp.Symbol("C_1", real=True)
        C2 = sp.Symbol("C_2", real=True)
        beta_sym = sp.Symbol("beta", real=True, positive=True)

        underdamped_sol = sp.Eq(
            x,
            sp.exp(-beta_sym * t) * (C1 * sp.cos(omega_d * t) + C2 * sp.sin(omega_d * t))
        )

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Underdamped Oscillation Solution (\\beta < \\omega_0)",
            expression=underdamped_sol,
            latex=f"x(t) = e^{{-\\beta t}} \\left( C_1 \\cos(\\omega_d t) + C_2 \\sin(\\omega_d t) \\right) \\quad \\text{{where }} \\omega_d = \\sqrt{{\\omega_0^2 - \\beta^2}}",
            explanation="In the underdamped regime ($\\gamma^2 < 4mk$), the roots are complex conjugates, yielding exponentially decaying sinusoidal oscillations with damped frequency $\\omega_d$."
        ))

        return DifferentialResult(
            name="Damped Harmonic Oscillator",
            ode_type=ode_type,
            differential_equation=ode,
            differential_equation_latex=sp.latex(ode),
            characteristic_equation=char_eq,
            roots=[r1, r2],
            general_solution=underdamped_sol,
            general_solution_latex=f"x(t) = e^{{-\\frac{{\\gamma}}{{2m}} t}} \\left( C_1 \\cos(\\omega_d t) + C_2 \\sin(\\omega_d t) \\right), \\quad \\omega_d = \\sqrt{{\\frac{{k}}{{m}} - \\frac{{\\gamma^2}}{{4m^2}}}}",
            steps=steps
        )

    def solve_quantum_infinite_well(
        self,
        L_str: str = "L",
        m_str: str = "m"
    ) -> DifferentialResult:
        """
        Solves the 1D Time-Independent Schrödinger Equation for an infinite potential well [0, L].
        """
        x_sym = sp.Symbol("x", real=True)
        L = sp.Symbol(L_str, positive=True, real=True)
        m = sp.Symbol(m_str, positive=True, real=True)
        hbar = sp.Symbol("hbar", positive=True, real=True)
        E = sp.Symbol("E", positive=True, real=True)
        psi = sp.Function("psi")(x_sym)

        steps: List[DerivationStep] = []
        step_num = 1

        # 1. State TISE
        tise_lhs = -(hbar**2 / (2 * m)) * psi.diff(x_sym, 2)
        tise = sp.Eq(tise_lhs, E * psi)

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Time-Independent Schrödinger Equation (TISE)",
            expression=tise,
            latex="-\\frac{\\hbar^2}{2m} \\frac{d^2\\psi}{dx^2} = E \\psi",
            explanation="Inside the well ($0 < x < L$), potential energy $V(x) = 0$."
        ))
        step_num += 1

        # 2. Wavevector substitution
        k_sq = 2 * m * E / hbar**2
        k_sym = sp.Symbol("k", positive=True, real=True)
        helmholtz = sp.Eq(psi.diff(x_sym, 2) + k_sym**2 * psi, 0)

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Wavenumber Formulation",
            expression=helmholtz,
            latex="\\frac{d^2\\psi}{dx^2} + k^2 \\psi = 0 \\quad \\text{where } k = \\frac{\\sqrt{2mE}}{\\hbar}",
            explanation="Transform TISE into standard Helmholtz harmonic differential equation."
        ))
        step_num += 1

        # 3. Boundary Conditions
        steps.append(DerivationStep(
            step_number=step_num,
            operation="Apply Dirichlet Boundary Conditions",
            expression=sp.Eq(sp.Symbol("psi(0)"), 0),
            latex="\\psi(0) = 0 \\implies A = 0, \\quad \\psi(L) = B \\sin(kL) = 0 \\implies k_n L = n\\pi, \\; n \\in \\{1, 2, 3, \\dots\\}",
            explanation="The wavefunction must vanish at the infinitely high potential walls $x=0$ and $x=L$."
        ))
        step_num += 1

        # 4. Energy Quantization
        E_n_expr = (sp.Symbol("n")**2 * sp.pi**2 * hbar**2) / (2 * m * L**2)

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Quantized Energy Eigenvalues",
            expression=sp.Eq(sp.Symbol("E_n"), E_n_expr),
            latex="E_n = \\frac{n^2 \\pi^2 \\hbar^2}{2 m L^2} \\quad (n = 1, 2, 3, \\dots)",
            explanation="Equating $k_n = \\frac{n\\pi}{L} = \\frac{\\sqrt{2mE_n}}{\\hbar}$ proves discrete energy level quantization."
        ))
        step_num += 1

        # 5. Normalization
        psi_n_expr = sp.sqrt(2 / L) * sp.sin(sp.Symbol("n") * sp.pi * x_sym / L)

        steps.append(DerivationStep(
            step_number=step_num,
            operation="Wavefunction Normalization",
            expression=sp.Eq(sp.Symbol("psi_n(x)"), psi_n_expr),
            latex="\\int_0^L |\\psi(x)|^2 dx = 1 \\implies \\psi_n(x) = \\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{n\\pi x}{L}\\right)",
            explanation="Enforce unitary total probability condition over the domain $[0, L]$."
        ))

        eigenstates = [
            {
                "n": 1,
                "energy_latex": "\\frac{\\pi^2 \\hbar^2}{2mL^2}",
                "psi_latex": "\\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{\\pi x}{L}\\right)"
            },
            {
                "n": 2,
                "energy_latex": "\\frac{4\\pi^2 \\hbar^2}{2mL^2} = \\frac{2\\pi^2 \\hbar^2}{mL^2}",
                "psi_latex": "\\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{2\\pi x}{L}\\right)"
            },
            {
                "n": 3,
                "energy_latex": "\\frac{9\\pi^2 \\hbar^2}{2mL^2}",
                "psi_latex": "\\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{3\\pi x}{L}\\right)"
            }
        ]

        return DifferentialResult(
            name="1D Quantum Infinite Potential Well",
            ode_type="Boundary-Value Quantum Eigenvalue Problem (TISE)",
            differential_equation=tise,
            differential_equation_latex="-\\frac{\\hbar^2}{2m} \\frac{d^2\\psi}{dx^2} = E \\psi",
            general_solution=sp.Eq(sp.Symbol("psi_n(x)"), psi_n_expr),
            general_solution_latex="\\psi_n(x) = \\sqrt{\\frac{2}{L}} \\sin\\left(\\frac{n\\pi x}{L}\\right), \\quad E_n = \\frac{n^2 \\pi^2 \\hbar^2}{2 m L^2}",
            eigenvalues_and_states=eigenstates,
            steps=steps
        )
