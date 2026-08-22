"""
Domains loader for Equation Knowledge Base.
"""

from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE, EquationKnowledgeBase
from equation_derivator.knowledge.domains.mechanics import register_mechanics_equations
from equation_derivator.knowledge.domains.electromagnetism import register_electromagnetism_equations
from equation_derivator.knowledge.domains.thermodynamics import register_thermodynamics_equations
from equation_derivator.knowledge.domains.relativity import register_relativity_equations
from equation_derivator.knowledge.domains.quantum import register_quantum_equations
from equation_derivator.knowledge.domains.mathematics import register_mathematics_equations


def load_all_domains(kb: EquationKnowledgeBase = GLOBAL_KNOWLEDGE_BASE) -> None:
    register_mechanics_equations(kb)
    register_electromagnetism_equations(kb)
    register_thermodynamics_equations(kb)
    register_relativity_equations(kb)
    register_quantum_equations(kb)
    register_mathematics_equations(kb)


# Auto-populate the global knowledge base on module import
load_all_domains(GLOBAL_KNOWLEDGE_BASE)
