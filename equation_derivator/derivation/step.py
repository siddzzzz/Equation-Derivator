"""
Derivation Step and Result Data Structures.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import sympy as sp


@dataclass
class DerivationStep:
    """
    Represents an atomic mathematical or physical transformation step in a derivation.
    """
    step_number: int
    operation: str
    expression: Union[sp.Expr, sp.Equality]
    latex: str
    explanation: str
    source_equation_id: Optional[str] = None
    substituted_symbol: Optional[str] = None
    substitution_value: Optional[str] = None
    assumptions_used: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "operation": self.operation,
            "expression": str(self.expression),
            "latex": self.latex,
            "explanation": self.explanation,
            "source_equation_id": self.source_equation_id,
            "substituted_symbol": self.substituted_symbol,
            "substitution_value": self.substitution_value,
            "assumptions_used": self.assumptions_used,
        }


@dataclass
class DerivationResult:
    """
    Encapsulates the complete multi-step derivation chain, reasoning, and verification status.
    """
    target_variable: str
    in_terms_of: List[str]
    final_equation: sp.Equality
    final_latex: str
    steps: List[DerivationStep] = field(default_factory=list)
    source_equation_ids: List[str] = field(default_factory=list)
    all_assumptions: List[str] = field(default_factory=list)
    is_verified: bool = False
    verification_details: Dict[str, Union[bool, str, dict]] = field(default_factory=dict)

    def to_markdown(self) -> str:
        md = []
        md.append(f"# Derivation: Expressing ${self.target_variable}$ in terms of ${', '.join(self.in_terms_of)}$\n")
        md.append(f"**Final Result:** $${self.final_latex}$$\n")
        
        if self.all_assumptions:
            md.append("### Key Physical Assumptions & Constraints:")
            for a in self.all_assumptions:
                md.append(f"- {a}")
            md.append("")

        md.append("### Step-by-Step Mathematical Derivation:")
        for s in self.steps:
            md.append(f"#### Step {s.step_number}: {s.operation}")
            md.append(f"{s.explanation}\n")
            md.append(f"$${s.latex}$$\n")

        if self.verification_details:
            md.append("### Verification Status:")
            md.append(f"- **Overall Soundness:** {'Verified Sound' if self.is_verified else 'Verification Incomplete'}")
            for k, v in self.verification_details.items():
                md.append(f"- **{k}:** {v}")
            md.append("")

        return "\n".join(md)

    def to_latex_document(self) -> str:
        lines = [
            r"\begin{align*}",
        ]
        for s in self.steps:
            lines.append(f"& \\text{{Step {s.step_number}: {s.operation}}} \\\\")
            lines.append(f"& {s.latex} \\quad \\text{{({s.explanation})}} \\\\[1em]")
        lines.append(r"\end{align*}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "target_variable": self.target_variable,
            "in_terms_of": self.in_terms_of,
            "final_equation": str(self.final_equation),
            "final_latex": self.final_latex,
            "steps": [s.to_dict() for s in self.steps],
            "source_equation_ids": self.source_equation_ids,
            "all_assumptions": self.all_assumptions,
            "is_verified": self.is_verified,
            "verification_details": self.verification_details,
        }
