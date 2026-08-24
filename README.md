# Equation-Derivator ⚛

> **Universal Symbolic AI Derivation, Variational Mechanics, Spacetime Tensors, Discovery & Verification Engine for Physics & Mathematics**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![SymPy Powered](https://img.shields.io/badge/CAS-SymPy-green.svg)](https://www.sympy.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-28%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`Equation-Derivator` is an advanced computational physics and symbolic mathematics research workbench. It automates rigorous multi-step equation derivations, analytical variational dynamics (Euler-Lagrange, Hamiltonian, Noether symmetries), general relativistic spacetime curvature tensor evaluation, differential equation solvers, Buckingham $\Pi$ dimensional synthesis, cross-domain bridge law discovery, natural language query dispatching, and 1-click academic LaTeX paper generation.

---

## 🌟 Core Theoretical Pillars

```
                                  EQUATION-DERIVATOR
   ┌───────────────────────────────────────┬───────────────────────────────────────┐
   │         SYMBOLIC ENGINES              │         ADVANCED THEORETICAL          │
   ├───────────────────────────────────────┼───────────────────────────────────────┤
   │ • Multi-Step Algebraic Substitutions  │ • Euler-Lagrange & Hamiltonian Labs   │
   │ • Work-Energy Calculus Derivation     │ • Noether's Theorem & Conservation    │
   │ • 4-Layer Equation Verifier           │ • Damped & Quantum TISE Differential  │
   │ • Buckingham Π Dimensional Synthesis  │ • Christoffel, Riemann, Ricci, & GR   │
   │ • Cross-Domain Knowledge Discovery    │ • LaTeX Paper Generator & NLP Query   │
   └───────────────────────────────────────┴───────────────────────────────────────┘
```

### 1. 🌌 Lagrangian & Hamiltonian Variational Mechanics
- **Euler-Lagrange Equation Generator**:
  $$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_i} = 0 \implies \ddot{q}_i = f(q, \dot{q}, t)$$
- **Conjugate Momenta & Canonical Hamiltonian**:
  $$p_i = \frac{\partial \mathcal{L}}{\partial \dot{q}_i}, \quad \mathcal{H}(q, p) = \sum p_i \dot{q}_i - \mathcal{L}$$
  $$\dot{q}_i = \frac{\partial \mathcal{H}}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial \mathcal{H}}{\partial q_i}$$
- **Noether's Theorem Conservation Laws**: Detects cyclic coordinates ($\partial\mathcal{L}/\partial q_i = 0 \implies p_i = \text{const}$) and temporal translational symmetry ($\partial\mathcal{L}/\partial t = 0 \implies \mathcal{H} = \text{const}$).

### 2. 🌀 Differential Equations & Quantum Systems
- **Damped-Driven Harmonic Oscillators**:
  $$\ddot{x} + 2\beta \dot{x} + \omega_0^2 x = F(t) \implies x(t) = e^{-\beta t} \left( C_1 \cos\omega_d t + C_2 \sin\omega_d t \right), \quad \omega_d = \sqrt{\omega_0^2 - \beta^2}$$
- **1D Time-Independent Schrödinger Equation (TISE)**:
  $$-\frac{\hbar^2}{2m} \frac{d^2\psi}{dx^2} = E\psi \implies E_n = \frac{n^2 \pi^2 \hbar^2}{2 m L^2}, \quad \psi_n(x) = \sqrt{\frac{2}{L}}\sin\left(\frac{n\pi x}{L}\right)$$

### 3. 📐 General Relativity & Spacetime Tensor Curvature
- Symbolic differential geometry computation:
  - **Christoffel connection coefficients:** $\Gamma^\sigma_{\mu\nu} = \frac{1}{2}g^{\sigma\rho}(\partial_\mu g_{\nu\rho} + \partial_\nu g_{\mu\rho} - \partial_\rho g_{\mu\nu})$
  - **Riemann Curvature Tensor:** $R^\rho_{\sigma\mu\nu} = \partial_\mu \Gamma^\rho_{\nu\sigma} - \partial_\nu \Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}$
  - **Ricci Tensor & Ricci Scalar:** $R_{\mu\nu} = R^\rho_{\mu\rho\nu}, \quad R = g^{\mu\nu} R_{\mu\nu}$
  - **Einstein Field Tensor:** $G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2} R g_{\mu\nu}$ (Verifies $G_{\mu\nu} \equiv 0$ in vacuum spacetimes)
  - **Geodesic Trajectory Equations:** $\ddot{x}^\mu + \Gamma^\mu_{\alpha\beta}\dot{x}^\alpha\dot{x}^\beta = 0$
  - Built-in metrics: **Schwarzschild Black Hole**, **FLRW Cosmological Expanding Metric**, and **Minkowski Spacetime**.

### 4. 🧮 Multi-Step Algebraic & Calculus Derivation
- Multi-step substitution solver with forward/backward chaining.
- Fundamental physical law prioritization and intermediate elimination.
- Step-by-step mathematical reasoning with LaTeX formatting.

### 5. 🛡️ 4-Layer Equation Verifier
- **Dimensional Homogeneity**: Confirms $[LHS] \equiv [RHS]$ across 7 SI base dimensions ($[M, L, T, I, \Theta, N, J]$).
- **Symbolic Identity**: Verifies analytical zero-cancellation $LHS - RHS \equiv 0$.
- **Monte Carlo Sampling**: Random sampling over positive physical parameter spaces.
- **Asymptotic Limiting Checks**: Tests boundary conditions ($v \to 0$, $c \to \infty$, $T \to 0$).

### 6. ⚛️ Buckingham $\Pi$ Discovery & Synthesis Lab
- Synthesizes power-law scaling relations from dimensional null-spaces (e.g. Planck Length $\ell_P = \sqrt{\frac{\hbar G}{c^3}}$, Pendulum Period $T \sim \sqrt{L/g}$).
- Cross-domain bridge laws linking Quantum Mechanics, Thermodynamics, and Gravitation.

### 7. 🤖 Natural Language Query Dispatcher & 📄 LaTeX Paper Generator
- Interprets plain English queries (*"derive pendulum equation of motion"*, *"calculate curvature for schwarzschild metric"*) and routes them to the correct calculus engine.
- Generates publication-ready `.tex` academic manuscripts with abstract, methodology, derivation steps, dimensional tables, and BibTeX citations.

---

## 🚀 Quickstart & Usage

### 1. Launching the Theoretical Physics Web Workbench
```bash
python -m equation_derivator.interfaces.cli serve --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to access the obsidian dark-mode cyber workbench with live KaTeX rendering, interactive DAG canvas, and graph explorer.

---

### 2. Command Line Interface (CLI)

#### **Variational Mechanics (Euler-Lagrange & Hamiltonian)**
```bash
# Simple Pendulum
python -m equation_derivator.interfaces.cli lagrangian -L "1/2 * m * L^2 * theta_dot^2 - m * g * L * (1 - cos(theta))" -q "theta" --name "Simple Pendulum"

# Harmonic Oscillator
python -m equation_derivator.interfaces.cli lagrangian -L "1/2 * m * x_dot^2 - 1/2 * k * x^2" -q "x" --name "Harmonic Oscillator"

# Free 2D Particle (Noether Invariants)
python -m equation_derivator.interfaces.cli lagrangian -L "1/2 * m * (x_dot^2 + y_dot^2)" -q "x, y"
```

#### **General Relativity & Spacetime Tensors**
```bash
# Schwarzschild Black Hole Curvature (Ricci tensor & Geodesics)
python -m equation_derivator.interfaces.cli tensor --metric "schwarzschild"

# FLRW Cosmological Metric
python -m equation_derivator.interfaces.cli tensor --metric "flrw"

# Minkowski Flat Spacetime
python -m equation_derivator.interfaces.cli tensor --metric "minkowski"
```

#### **Differential Equations & Quantum Solvers**
```bash
# Damped Harmonic Oscillator
python -m equation_derivator.interfaces.cli diff-eq --type "damped"

# 1D Quantum Infinite Potential Well
python -m equation_derivator.interfaces.cli diff-eq --type "schrodinger"
```

#### **Natural Language Physics Assistant**
```bash
python -m equation_derivator.interfaces.cli ask "derive kinetic energy from momentum and mass"
python -m equation_derivator.interfaces.cli ask "derive euler-lagrange equation for simple pendulum"
python -m equation_derivator.interfaces.cli ask "compute curvature for schwarzschild metric"
```

#### **1-Click Academic LaTeX Paper Generator**
```bash
# Export full .tex paper to file
python -m equation_derivator.interfaces.cli paper --target "K" --in-terms-of "p, m" --output paper_kinetic.tex
```

#### **Algebraic Derivations & Verification**
```bash
# Derive Kinetic Energy
python -m equation_derivator.interfaces.cli derive --target "K" --in-terms-of "p, m"

# Verify Relativistic Energy-Momentum Equation
python -m equation_derivator.interfaces.cli verify --equation "E^2 = (p*c)^2 + (m*c^2)^2"

# Buckingham Pi Synthesis
python -m equation_derivator.interfaces.cli discover --quantities "G, hbar, c" --target "Length"
```

---

### 3. Python API Usage

```python
from equation_derivator.calculus.variational import VariationalEngine
from equation_derivator.calculus.tensors import SpacetimeTensorEngine
from equation_derivator.calculus.differential import DifferentialEquationSolver
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.interfaces.paper_generator import ScientificPaperGenerator

# 1. Variational Mechanics: Euler-Lagrange & Hamiltonian
var_engine = VariationalEngine()
var_res = var_engine.derive(
    lagrangian="1/2 * m * L^2 * theta_dot^2 - m * g * L * (1 - cos(theta))",
    coordinates=["theta"],
    system_name="Simple Pendulum"
)
print(var_res.to_markdown())

# 2. Spacetime Tensors: Schwarzschild Curvature
tensor_engine = SpacetimeTensorEngine()
curv_res = tensor_engine.create_schwarzschild_metric()
print("Is Vacuum Solution:", curv_res.is_vacuum_solution)
print("Ricci Scalar:", curv_res.ricci_scalar)

# 3. Quantum Infinite Well TISE Solver
diff_solver = DifferentialEquationSolver()
quant_res = diff_solver.solve_quantum_infinite_well()
print("Quantized Energy Levels:", quant_res.eigenvalues_and_states)

# 4. Multi-Step Algebraic Derivation & Academic Paper Export
deriv_engine = DerivationEngine()
deriv_res = deriv_engine.derive(target_variable="K", in_terms_of=["p", "m"])

paper_gen = ScientificPaperGenerator()
tex_code = paper_gen.generate_derivation_paper(deriv_res.to_dict(), title="Kinetic Invariant")
with open("paper.tex", "w") as f:
    f.write(tex_code)
```

---

## 🧪 Automated Test Suite

The project includes an extensive test suite verifying mathematical correctness, dimensions, variational equations, tensor contractions, differential equations, and paper generation:

```bash
python -m pytest tests/ -v
```

```
tests/test_core.py .......... PASSED
tests/test_derivation.py .... PASSED
tests/test_differential.py .. PASSED
tests/test_discovery.py ..... PASSED
tests/test_knowledge.py ..... PASSED
tests/test_nlp_paper.py ..... PASSED
tests/test_tensors.py ....... PASSED
tests/test_variational.py ... PASSED
tests/test_verifier.py ...... PASSED

======================= 28 passed in 9.67s =======================
```

---

## 📁 Repository Structure

```
Equation-Derivator/
├── equation_derivator/
│   ├── calculus/               # Variational dynamics, ODEs, and spacetime tensors
│   │   ├── variational.py      # Euler-Lagrange, Hamiltonian, Noether invariants
│   │   ├── differential.py     # Damped oscillator, Quantum TISE well
│   │   └── tensors.py          # Metric, Christoffel, Riemann, Ricci, Einstein
│   ├── core/                   # 7D SI base dimensions, quantities registry, symbol parsing
│   ├── knowledge/              # Universal physical equation database & graph
│   ├── derivation/             # Multi-step substitution derivation engine & steps
│   ├── verifier/               # 4-layer equation verifier (dimensions, Monte Carlo, limits)
│   ├── discovery/              # Buckingham Pi dimensional synthesis & cross-domain bridges
│   └── interfaces/             # User interfaces & tools
│       ├── nlp.py              # Natural language physics query dispatcher
│       ├── paper_generator.py  # LaTeX academic paper compiler
│       ├── cli.py              # Rich terminal CLI
│       ├── api.py              # FastAPI REST backend
│       └── web/                # Glassmorphic cyber-workbench UI (HTML, CSS, JS, KaTeX)
├── tests/                      # 28 test cases across 9 test modules
├── README.md                   # System documentation
└── requirements.txt            # Python dependencies
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).