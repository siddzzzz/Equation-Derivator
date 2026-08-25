# Equation-Derivator ⚛

> **Universal Symbolic AI Derivation, Variational Dynamics, Spacetime Tensors, Quantum Field Theory, Numerical Simulations & Verification Engine for Physics & Mathematics**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![SymPy Powered](https://img.shields.io/badge/CAS-SymPy-green.svg)](https://www.sympy.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/tests-57%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`Equation-Derivator` is an advanced computational physics and symbolic mathematics research platform. It integrates rigorous multi-step algebraic derivation, analytical variational dynamics (Euler-Lagrange, Hamiltonian, Noether symmetries), general relativistic spacetime curvature tensor evaluation, differential geometry & exterior calculus forms, quantum field theory (Dirac spinors & Feynman amplitudes), Lie algebras & gauge theory, statistical mechanics partition functions, 60fps numerical physics simulation, Buckingham $\Pi$ dimensional synthesis, and 1-click academic LaTeX paper generation.

---

## 🌟 Theoretical Domains & Capabilities

```
                                      EQUATION-DERIVATOR
   ┌───────────────────────────────────────────┬───────────────────────────────────────────┐
   │             SYMBOLIC CALCULUS             │          THEORETICAL PHYSICS              │
   ├───────────────────────────────────────────┼───────────────────────────────────────────┤
   │ • Multi-Step Algebraic Substitutions      │ • Euler-Lagrange & Hamiltonian Labs       │
   │ • 4-Layer Physical Equation Verifier      │ • Spacetime Tensors & Curvature (GR)      │
   │ • Buckingham Π Dimensional Synthesizer    │ • Quantum Field Theory & Dirac Spinors    │
   │ • Exterior Calculus Differential Forms    │ • Lie Algebras SU(2)/SU(3) & Higgs SSB    │
   │ • Geometric Maxwell Equations (dF = 0)    │ • Canonical Partition Functions Z(T,V,N)  │
   │ • 60fps Phase Space & Orbit Simulator     │ • Planck Radiation & Quantum Statistics   │
   └───────────────────────────────────────────┴───────────────────────────────────────────┘
```

### 1. 🎮 Numerical Physics Simulation & Phase Space Engine
- **Symplectic Verlet & RK4 Integrators**: Converts symbolic SymPy acceleration expressions $\ddot{q}_i(t) = f(q, \dot{q}, t)$ into high-precision numerical trajectories with energy conservation monitoring.
- **Phase Space Portraits & Streamlines**: Evaluates $(q, \dot{q})$ phase trajectories, Hamiltonian vector fields, and energy conservation drift diagnostics.
- **Quantum Wave Packet Tunneling (TDSE)**: 1D split-operator FFT wave packet solver for barrier tunneling, reflection, and transmission probabilities.
- **Relativistic Orbits & Photon Ray-Tracing**: Schwarzschild particle trajectories and photon light deflection with event horizon capture detection.

### 2. ⚛️ Quantum Field Theory (QFT) & Dirac Spinors
- **Gamma Matrix Representations**: Dirac-Pauli, Weyl (chiral), and Majorana 4x4 gamma matrices satisfying the Clifford algebra $\{\gamma^\mu, \gamma^\nu\} = 2\eta^{\mu\nu}\mathbb{I}_4$.
- **Chiral Projectors & Spinor Relations**: Left/Right chiral projectors $P_L, P_R = \frac{1 \mp \gamma^5}{2}$ and Dirac spin sums $\sum u\bar{u} = \not{p} + m$, $\sum v\bar{v} = \not{p} - m$.
- **Feynman Tree-Level Amplitudes**: Mandelstam invariants $(s, t, u)$, unpolarized squared matrix elements $|\overline{\mathcal{M}}|^2$, and differential cross sections $\frac{d\sigma}{d\Omega}$ for $e^-e^+ \to \mu^-\mu^+$ and Compton scattering.
- **Publication SVG Feynman Generator**: Vector graph generator with fermion arrows, wavy photon lines, and vertex couplings.

### 3. 🌐 Differential Forms & Geometric Electrodynamics
- **Exterior Calculus Engine**: Graded differential $p$-forms with coordinate-free wedge product $\wedge$, exterior derivative $d$ ($d^2 = 0$), and Hodge star $\star$ in 4D Minkowski spacetime.
- **Geometric Maxwell Equations**:
  - 4-Potential 1-form: $A = -\phi\, dt + A_x\, dx + A_y\, dy + A_z\, dz$
  - Field strength 2-form: $F = dA$
  - Homogeneous Maxwell (Bianchi Identity): $dF = d(dA) \equiv 0 \iff \nabla\cdot\mathbf{B} = 0, \; \nabla\times\mathbf{E} + \partial_t\mathbf{B} = 0$
  - Inhomogeneous Maxwell: $d\star F = \mu_0 \star J \iff \nabla\cdot\mathbf{E} = \rho/\varepsilon_0, \; \nabla\times\mathbf{B} - c^{-2}\partial_t\mathbf{E} = \mu_0\mathbf{J}$
  - Charge Conservation: $d\star J = 0 \iff \partial_\mu J^\mu = 0$

### 4. 🧬 Lie Algebras, Gauge Theory & Higgs Mechanism
- **$\mathfrak{su}(2)$ & $\mathfrak{su}(3)$ Lie Algebras**: Commutation relations $[T^a, T^b] = i f^{abc} T^c$, Gell-Mann matrices, and quadratic Casimir invariants ($C_2 = \frac{3}{4}\mathbb{I}_2$ for $SU(2)$, $C_2 = \frac{4}{3}\mathbb{I}_3$ for $SU(3)$).
- **Non-Abelian Yang-Mills Theory**: Gauge covariant derivative $D_\mu = \partial_\mu - i g A_\mu^a T^a$ and nonlinear field strength tensor $F_{\mu\nu}^a = \partial_\mu A_\nu^a - \partial_\nu A_\mu^a + g f^{abc} A_\mu^b A_\nu^c$.
- **Higgs Spontaneous Symmetry Breaking**: $SU(2)_L \times U(1)_Y \to U(1)_{EM}$ electroweak breaking yielding massive $W^\pm, Z^0$ bosons, unbroken massless photon ($M_\gamma = 0$), and Weinberg angle $\cos\theta_W = M_W/M_Z$.

### 5. 🌡️ Statistical Mechanics & Partition Functions
- **Thermodynamic Potentials from $\mathcal{Z}$**:
  - Helmholtz Free Energy: $F = -k_B T \ln\mathcal{Z}$
  - Entropy: $S = -\left(\frac{\partial F}{\partial T}\right)_{V, N}$
  - Internal Energy: $U = F + TS$
  - Equation of State: $P = -\left(\frac{\partial F}{\partial V}\right)_{T, N}$
  - Heat Capacity: $C_v = \left(\frac{\partial U}{\partial T}\right)_V$
- **Physical Models**: Classical Monatomic Ideal Gas (Sackur-Tetrode), Quantum Harmonic Oscillator (Einstein heat capacity), Fermi-Dirac, Bose-Einstein, and Planck Blackbody Radiation Law ($u(\nu, T) \implies I = \sigma T^4$).

### 6. 🌌 Lagrangian & Hamiltonian Variational Mechanics
- **Euler-Lagrange Equation Generator**: $\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_i} = 0 \implies \ddot{q}_i = f(q, \dot{q}, t)$
- **Conjugate Momenta & Canonical Hamiltonian**: $p_i = \frac{\partial \mathcal{L}}{\partial \dot{q}_i}, \quad \mathcal{H}(q, p) = \sum p_i \dot{q}_i - \mathcal{L}$
- **Noether's Theorem Conservation Laws**: Cyclic coordinates ($\partial\mathcal{L}/\partial q_i = 0 \implies p_i = \text{const}$) and time translation invariance ($\partial\mathcal{L}/\partial t = 0 \implies \mathcal{H} = \text{const}$).

### 7. 📐 General Relativity & Spacetime Tensor Curvature
- Exact Christoffel connection symbols $\Gamma^\sigma_{\mu\nu}$, Riemann Curvature Tensor $R^\rho_{\sigma\mu\nu}$, Ricci Tensor $R_{\mu\nu}$, Ricci Scalar $R$, Einstein Field Tensor $G_{\mu\nu}$, and Geodesic Equations.
- Built-in metrics: **Schwarzschild Black Hole**, **FLRW Expanding Cosmological Universe**, and **Minkowski Spacetime**.

---

## 🚀 Quickstart & Usage

### 1. Launching the Theoretical Physics Web Workbench
```bash
python -m equation_derivator.interfaces.cli serve --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to access the obsidian dark-mode cyber workbench with live KaTeX rendering, 60fps simulation canvases, interactive DAG workflows, and SVG diagram viewers.

---

### 2. Command Line Interface (CLI)

#### **Numerical Physics Simulation**
```bash
# Simulate nonlinear pendulum with RK4
python -m equation_derivator.interfaces.cli sim --accel "-9.81*sin(theta)" --coords "theta" --q0 "1.5" --v0 "0.0" --t-end 5.0
```

#### **Quantum Field Theory & Dirac Spinors**
```bash
# Evaluate Dirac gamma algebra & chiral projectors
python -m equation_derivator.interfaces.cli qft --representation dirac

# Evaluate electron-positron annihilation amplitude & cross section
python -m equation_derivator.interfaces.cli qft --process ee_to_mumu
```

#### **Differential Forms & Geometric Electrodynamics**
```bash
# Derive coordinate-free geometric Maxwell equations
python -m equation_derivator.interfaces.cli forms
```

#### **Lie Algebras & Gauge Symmetries**
```bash
# Evaluate SU(2) Pauli algebra & Casimir invariant
python -m equation_derivator.interfaces.cli symmetry --group su2

# Evaluate SU(3) Gell-Mann color algebra for QCD
python -m equation_derivator.interfaces.cli symmetry --group su3

# Evaluate Electroweak Higgs spontaneous symmetry breaking
python -m equation_derivator.interfaces.cli symmetry --group higgs
```

#### **Statistical Mechanics & Partition Functions**
```bash
# Derive Sackur-Tetrode equation of state for Ideal Gas
python -m equation_derivator.interfaces.cli statmech --model ideal_gas

# Derive Einstein heat capacity for Quantum Harmonic Oscillator
python -m equation_derivator.interfaces.cli statmech --model quantum_oscillator

# Universal Bose-Einstein, Fermi-Dirac, and Planck Blackbody Law
python -m equation_derivator.interfaces.cli statmech --model distributions
```

#### **Variational Mechanics (Euler-Lagrange & Hamiltonian)**
```bash
# Simple Pendulum
python -m equation_derivator.interfaces.cli lagrangian -l "1/2 * m * L^2 * theta_dot^2 - m * g * L * (1 - cos(theta))" -c "theta" --name "Simple Pendulum"

# Harmonic Oscillator
python -m equation_derivator.interfaces.cli lagrangian -l "1/2 * m * x_dot^2 - 1/2 * k * x^2" -c "x" --name "Harmonic Oscillator"
```

#### **General Relativity & Spacetime Tensors**
```bash
# Schwarzschild Black Hole Curvature (Ricci tensor & Geodesics)
python -m equation_derivator.interfaces.cli tensor --metric schwarzschild

# Expanding FLRW Universe
python -m equation_derivator.interfaces.cli tensor --metric flrw
```

#### **Multi-Step Equation Derivation**
```bash
# Derive Kinetic Energy (K) in terms of momentum (p) and mass (m)
python -m equation_derivator.interfaces.cli derive -t K -i "p,m"

# Derive Escape Velocity
python -m equation_derivator.interfaces.cli derive -t v -i "G,M,R"
```

#### **Natural Language Physics Query & Paper Generation**
```bash
# Ask questions in natural language
python -m equation_derivator.interfaces.cli ask -q "derive simple pendulum equation of motion"

# Generate publication LaTeX paper (.tex)
python -m equation_derivator.interfaces.cli paper -t K -i "p,m" -o "paper_kinetic_energy.tex"
```

---

## 🧪 Comprehensive Automated Test Suite

Run the full test suite covering all 57 automated unit tests across algebraic derivation, variational dynamics, differential forms, QFT, simulations, symmetries, and statistical mechanics:

```bash
python -m pytest tests/ -v
```

```
============================= 57 passed in 20.79s =============================
```

---

## 🏛️ System Architecture

```
equation_derivator/
├── core/                  # Physical dimensions ([M,L,T,I,Theta,N,J]), SI unit arithmetic
├── knowledge/             # Universal physical equation ontology & graph pathfinder
├── derivation/            # Symbolic multi-step substitution solver & work-energy theorem
├── verifier/              # 4-Layer Verifier (Dimensional, Symbolic, Monte Carlo, Asymptotic)
├── discovery/             # Buckingham Pi dimensional synthesizer & cross-domain discovery
├── calculus/              # Variational Euler-Lagrange, Hamiltonian, Differential, Tensors
├── simulation/            # RK4/Verlet integrator, Phase portraits, TDSE wave packet, Schwarzschild orbits
├── qft/                   # Dirac gamma algebra, Spinor completeness, Feynman amplitudes, SVG drawer
├── geometry/              # Differential forms (wedge, d, Hodge star), Geometric Maxwell
├── symmetry/              # Lie algebras SU(2)/SU(3), Yang-Mills fields, Higgs mechanism
├── statmech/              # Partition function derivation Z -> (F, S, U, P, Cv), Quantum distributions
└── interfaces/            # FastAPI backend, Rich CLI, Cyber HTML5/Canvas workbench UI
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.