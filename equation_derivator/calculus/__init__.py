"""
Calculus & Advanced Theoretical Physics Package for Equation-Derivator.
Includes:
- Variational Mechanics (Euler-Lagrange, Hamiltonian, Noether's Theorem)
- Differential Equations & Dynamic Systems (ODEs, Harmonic Oscillators, Quantum Well)
- General Relativity & Spacetime Tensor Curvature (Metric, Christoffel, Riemann, Ricci, Einstein)
"""

from equation_derivator.calculus.variational import VariationalEngine, VariationalResult
from equation_derivator.calculus.differential import DifferentialEquationSolver, DifferentialResult
from equation_derivator.calculus.tensors import SpacetimeTensorEngine, TensorCurvatureResult

__all__ = [
    "VariationalEngine",
    "VariationalResult",
    "DifferentialEquationSolver",
    "DifferentialResult",
    "SpacetimeTensorEngine",
    "TensorCurvatureResult",
]
