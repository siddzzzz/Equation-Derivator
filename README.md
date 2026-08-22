# Equation-Derivator ⚛

> **Universal AI Equation Derivation, Discovery & Verification Engine for Physics & Mathematics**

`Equation-Derivator` is an advanced symbolic and physics-informed computational system designed for physicists, mathematicians, and researchers. It automates rigorous multi-step equation derivations, synthesizes new physical scaling laws through dimensional analysis (Buckingham $\Pi$), discovers cross-domain bridges between physical disciplines, and verifies mathematical and physical consistency.

---

## 🌟 Key Features

1. **Universal Physical Quantity Ontology & Dimensional Engine**:
   - Exact 7-dimensional SI base representation ($[M, L, T, I, \Theta, N, J]$).
   - Canonical physical concept registry with semantic variable aliasing ($v, u, \dot{x}, \beta c \to \text{Velocity}$; $m, M, m_0, \mu \to \text{Mass}$).

2. **Universal Equation Knowledge Base**:
   - Comprehensive repository spanning **Classical Mechanics**, **Electromagnetism**, **Thermodynamics & Statistical Mechanics**, **Special & General Relativity**, **Quantum Mechanics & Wave Physics**, and **Pure Mathematics**.
   - Includes physical assumptions, boundary conditions, and domain validity constraints.

3. **Multi-Step Symbolic Derivation Solver**:
   - Forward & backward chaining symbolic search over equation graphs.
   - Step-by-step algebraic isolation, substitution, expansion, and factorization with LaTeX typesetting.
   - Built-in calculus derivations (e.g. Work-Energy Theorem $\int F dx \implies \Delta K$).

4. **Multi-Aspect Equation & Derivation Verifier**:
   - **Dimensional Homogeneity**: Confirms $[LHS] \equiv [RHS]$.
   - **Symbolic Equivalence**: Confirms algebraic cancellation $LHS - RHS \equiv 0$.
   - **Numerical Monte Carlo Sampling**: Validates equations over random positive physical parameter spaces.
   - **Asymptotic Limiting Checks**: Tests boundary conditions ($v \to 0$, $c \to \infty$, $T \to 0$).

5. **Equation Discovery & Synthesis Lab**:
   - **Buckingham $\Pi$ Dimensional Synthesizer**: Discovers power-law scaling relations (e.g. synthesizing Planck Length $\ell_P = \sqrt{\frac{\hbar G}{c^3}}$, Pendulum Period $T \sim \sqrt{L/g}$).
   - **Cross-Domain Bridge Composition**: Chains shared variables across disparate domains to discover novel relation bridges.

6. **Interactive Interfaces**:
   - **Rich Terminal CLI** with colored step-by-step panels.
   - **Glassmorphic Web Dashboard** with live KaTeX math rendering, preset derivations, and interactive ontology inspector.

---

## 🚀 Quickstart & Usage

### 1. Launching the Web Interface
```bash
python -m equation_derivator.interfaces.cli serve --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

### 2. Command Line Interface (CLI)

#### **Derive a Formula**
```bash
# Derive Kinetic Energy (K) in terms of Momentum (p) and Mass (m)
python -m equation_derivator.interfaces.cli derive --target "K" --in-terms-of "p,m"

# Derive with explicit starting equations
python -m equation_derivator.interfaces.cli derive --target "K" --in-terms-of "p,m" --equations "kinetic_energy_def; linear_momentum_def"
```

#### **Verify an Equation**
```bash
# Verify relativistic energy-momentum invariant
python -m equation_derivator.interfaces.cli verify --equation "E^2 = (p*c)^2 + (m*c^2)^2"

# Test dimensionally invalid formula
python -m equation_derivator.interfaces.cli verify --equation "F = m * v"
```

#### **Discover New Equations (Buckingham $\Pi$)**
```bash
# Discover Planck length scaling from fundamental constants
python -m equation_derivator.interfaces.cli discover --quantities "G, hbar, c" --target "Length"

# Discover cross-domain bridges between Quantum and Relativity
python -m equation_derivator.interfaces.cli discover --cross-domain "Quantum,Relativity"
```

#### **Browse Equation Knowledge Base & Ontology**
```bash
# Browse Mechanics equations
python -m equation_derivator.interfaces.cli browse --domain Mechanics

# View physical quantity ontology and SI dimensions
python -m equation_derivator.interfaces.cli quantities
```

---

### 3. Python API Usage

```python
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.verifier.verifier import EquationVerifier
from equation_derivator.discovery.discovery_engine import DiscoveryEngine
from equation_derivator.core.equation import PhysicalEquation

# 1. Multi-Step Derivation
engine = DerivationEngine()
result = engine.derive(
    target_variable="K",
    in_terms_of=["p", "m"],
    starting_equations=["kinetic_energy_def", "linear_momentum_def"]
)

print(result.to_markdown())

# 2. Equation Verification
verifier = EquationVerifier()
eq = PhysicalEquation.create(
    id="test_eq",
    name="Energy-Momentum",
    domain="Relativity",
    equation_str="E^2 = (p*c)^2 + (m*c^2)^2"
)
report = verifier.verify_equation(eq)
print("Is Valid:", report["overall_valid"])

# 3. Buckingham Pi Discovery
discovery = DiscoveryEngine()
relations = discovery.synthesize_dimensional_relation(
    quantities=["G", "hbar", "c"],
    target_dimension_or_quantity="Length"
)
for r in relations:
    print(r.name, ":", r.formula)
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 📜 License
MIT License.