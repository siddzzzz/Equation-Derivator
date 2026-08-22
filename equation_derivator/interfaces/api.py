"""
FastAPI REST API & Web Application Backend.
"""

from __future__ import annotations
import os
from typing import Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE
import equation_derivator.knowledge.domains
from equation_derivator.core.quantities import GLOBAL_QUANTITY_REGISTRY, PhysicalQuantity
from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.verifier.verifier import EquationVerifier
from equation_derivator.discovery.discovery_engine import DiscoveryEngine


app = FastAPI(
    title="Equation-Derivator API",
    description="Universal AI Equation Derivation, Discovery & Verification Engine",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Models
class DeriveRequest(BaseModel):
    target: str
    in_terms_of: List[str]
    starting_equations: Optional[List[str]] = None
    bindings: Optional[Dict[str, str]] = None


class VerifyRequest(BaseModel):
    equation_str: str
    bindings: Optional[Dict[str, str]] = None


class DiscoverRequest(BaseModel):
    mode: str  # "dimensional" or "cross_domain"
    quantities: Optional[List[str]] = None
    target: Optional[str] = "Length"
    domain1: Optional[str] = None
    domain2: Optional[str] = None


# Endpoints
@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/quantities")
def get_quantities():
    qtys = GLOBAL_QUANTITY_REGISTRY.list_all()
    return [
        {
            "name": q.name,
            "symbol": q.canonical_symbol,
            "dimension": str(q.dimension),
            "description": q.description,
            "aliases": q.aliases,
            "is_constant": q.is_constant,
            "constant_value": q.constant_value,
            "constant_unit": q.constant_unit,
            "domains": q.domains,
        }
        for q in qtys
    ]


@app.get("/api/equations")
def get_equations(domain: Optional[str] = None, tag: Optional[str] = None):
    kb = GLOBAL_KNOWLEDGE_BASE
    eqs = kb.list_all()
    if domain:
        eqs = [e for e in eqs if e.domain.lower() == domain.lower()]
    if tag:
        eqs = [e for e in eqs if any(t.lower() == tag.lower() for t in e.tags)]
    return [e.to_dict() for e in eqs]


@app.post("/api/derive")
def derive_equation(req: DeriveRequest):
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)
    try:
        if req.target.lower() == "w" and any("v_f" in v or "delta k" in v.lower() for v in req.in_terms_of):
            # Special work-energy calculus template
            res = engine.derive_work_energy_theorem()
        else:
            res = engine.derive(
                target_variable=req.target,
                in_terms_of=req.in_terms_of,
                starting_equations=req.starting_equations,
            )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/verify")
def verify_equation_endpoint(req: VerifyRequest):
    verifier = EquationVerifier()
    try:
        eq = PhysicalEquation.create(
            id="api_verify_eq",
            name="Equation under verification",
            domain="Custom",
            equation_str=req.equation_str,
            bindings=req.bindings,
        )
        report = verifier.verify_equation(eq)
        report["equation"] = eq.to_dict()
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/discover")
def discover_endpoint(req: DiscoverRequest):
    engine = DiscoveryEngine(GLOBAL_KNOWLEDGE_BASE)
    try:
        if req.mode == "dimensional":
            if not req.quantities:
                raise HTTPException(status_code=400, detail="Quantities list required for dimensional synthesis")
            results = engine.synthesize_dimensional_relation(req.quantities, req.target or "Length")
            return [r.to_dict() for r in results]
        elif req.mode == "cross_domain":
            if not req.domain1 or not req.domain2:
                raise HTTPException(status_code=400, detail="domain1 and domain2 required for cross-domain discovery")
            results = engine.discover_cross_domain_relations(req.domain1, req.domain2)
            return [r.to_dict() for r in results]
        else:
            raise HTTPException(status_code=400, detail=f"Unknown discovery mode: '{req.mode}'")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Mount Static Files for Web UI
web_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="static")
