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


class LagrangianRequest(BaseModel):
    lagrangian: str
    coordinates: List[str]
    system_name: Optional[str] = "Variational System"


class DiffEqRequest(BaseModel):
    type: str = "damped"  # "damped" or "schrodinger"
    driving_force: Optional[str] = None


class TensorRequest(BaseModel):
    metric: str = "schwarzschild"  # "schwarzschild", "flrw", "minkowski"


class AskRequest(BaseModel):
    query: str


class DiscoverRequest(BaseModel):
    mode: str  # "dimensional" or "cross_domain"
    quantities: Optional[List[str]] = None
    target: Optional[str] = "Length"
    domain1: Optional[str] = None
    domain2: Optional[str] = None


class PaperRequest(BaseModel):
    target: str
    in_terms_of: List[str]
    title: Optional[str] = None


class SimulateRequest(BaseModel):
    accelerations: Dict[str, str]
    coordinates: List[str]
    initial_positions: Dict[str, float]
    initial_velocities: Dict[str, float]
    parameters: Optional[Dict[str, float]] = None
    t_end: Optional[float] = 10.0
    dt: Optional[float] = 0.02
    system_name: Optional[str] = "Symbolic Dynamical System"


class PhaseSpaceRequest(BaseModel):
    accel_expr: str
    coord_name: Optional[str] = "x"
    params: Optional[Dict[str, float]] = None
    q0: Optional[float] = 1.0
    v0: Optional[float] = 0.0
    t_end: Optional[float] = 8.0
    dt: Optional[float] = 0.02
    potential_expr: Optional[str] = None


class QuantumWaveRequest(BaseModel):
    barrier_type: Optional[str] = "barrier"  # "barrier", "harmonic", "step"
    barrier_height: Optional[float] = 4.0
    barrier_width: Optional[float] = 0.5
    barrier_center: Optional[float] = 0.0
    p0: Optional[float] = 3.0
    sigma: Optional[float] = 0.5


class RelativityOrbitRequest(BaseModel):
    mode: Optional[str] = "particle"  # "particle" or "photon"
    r0: Optional[float] = 12.0
    v_phi0: Optional[float] = 0.28
    impact_parameter_b: Optional[float] = 6.0


class QFTRequest(BaseModel):
    representation: Optional[str] = "dirac"  # "dirac", "weyl", "majorana"


class FeynmanRequest(BaseModel):
    process: Optional[str] = "ee_to_mumu"  # "ee_to_mumu" or "compton"


class SymmetryRequest(BaseModel):
    mode: Optional[str] = "su2"  # "su2", "su3", "yang_mills", "higgs"


class StatMechRequest(BaseModel):
    mode: Optional[str] = "ideal_gas"  # "ideal_gas", "quantum_oscillator", "distributions", "custom"
    partition_function: Optional[str] = None
    model_name: Optional[str] = "Custom Statistical Ensemble"


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


@app.post("/api/lagrangian")
def lagrangian_endpoint(req: LagrangianRequest):
    from equation_derivator.calculus.variational import VariationalEngine
    engine = VariationalEngine()
    try:
        res = engine.derive(
            lagrangian=req.lagrangian,
            coordinates=req.coordinates,
            system_name=req.system_name or "Variational System"
        )
        return {
            "system_name": res.system_name,
            "coordinates": res.coordinates,
            "lagrangian_latex": res.lagrangian_latex,
            "euler_lagrange_equations": [
                {
                    "coord": eq["coord"],
                    "equation_latex": eq["equation_latex"],
                    "acceleration_latex": eq.get("acceleration_latex")
                }
                for eq in res.euler_lagrange_equations
            ],
            "hamiltonian": res.hamiltonian,
            "noether_conserved_quantities": res.noether_conserved_quantities,
            "markdown": res.to_markdown()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/diff-eq")
def diff_eq_endpoint(req: DiffEqRequest):
    from equation_derivator.calculus.differential import DifferentialEquationSolver
    solver = DifferentialEquationSolver()
    try:
        if req.type == "schrodinger":
            res = solver.solve_quantum_infinite_well()
        else:
            res = solver.solve_damped_harmonic_oscillator(driving_force=req.driving_force)
        return {
            "name": res.name,
            "ode_type": res.ode_type,
            "differential_equation_latex": res.differential_equation_latex,
            "general_solution_latex": res.general_solution_latex,
            "eigenvalues_and_states": res.eigenvalues_and_states,
            "markdown": res.to_markdown()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tensors")
def tensor_endpoint(req: TensorRequest):
    from equation_derivator.calculus.tensors import SpacetimeTensorEngine
    import sympy as sp
    engine = SpacetimeTensorEngine()
    try:
        if req.metric == "schwarzschild":
            res = engine.create_schwarzschild_metric()
        elif req.metric == "flrw":
            res = engine.create_flrw_metric()
        else:
            res = engine.create_minkowski_metric()
        return {
            "metric_name": res.metric_name,
            "coordinates": res.coordinates,
            "metric_latex": sp.latex(res.metric_matrix),
            "ricci_scalar_latex": sp.latex(res.ricci_scalar),
            "einstein_tensor_latex": sp.latex(res.einstein_tensor),
            "is_vacuum_solution": res.is_vacuum_solution,
            "geodesic_equations": res.geodesic_equations,
            "markdown": res.to_markdown()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sim/simulate")
def simulate_endpoint(req: SimulateRequest):
    from equation_derivator.simulation.integrator import simulate_symbolic_system
    try:
        traj = simulate_symbolic_system(
            accelerations=req.accelerations,
            coordinates=req.coordinates,
            initial_positions=req.initial_positions,
            initial_velocities=req.initial_velocities,
            parameters=req.parameters,
            t_end=req.t_end or 10.0,
            dt=req.dt or 0.02,
            system_name=req.system_name or "Symbolic Dynamical System"
        )
        return traj.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sim/phase-portrait")
def phase_portrait_endpoint(req: PhaseSpaceRequest):
    from equation_derivator.simulation.phase_space import PhaseSpaceEngine
    engine = PhaseSpaceEngine()
    try:
        res = engine.generate_phase_portrait(
            accel_expr_str=req.accel_expr,
            coord_name=req.coord_name or "x",
            params=req.params,
            q0=req.q0 if req.q0 is not None else 1.0,
            v0=req.v0 if req.v0 is not None else 0.0,
            t_end=req.t_end or 8.0,
            dt=req.dt or 0.02,
            potential_expr_str=req.potential_expr
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sim/quantum-wave")
def quantum_wave_endpoint(req: QuantumWaveRequest):
    from equation_derivator.simulation.quantum_sim import QuantumWavePacketSim
    sim = QuantumWavePacketSim(N=256, x_min=-8.0, x_max=8.0)
    try:
        psi0 = sim.create_gaussian_packet(
            x0=-3.0,
            p0=req.p0 or 3.0,
            sigma=req.sigma or 0.5
        )
        V = sim.build_potential(
            barrier_type=req.barrier_type or "barrier",
            barrier_height=req.barrier_height if req.barrier_height is not None else 4.0,
            barrier_width=req.barrier_width or 0.5,
            barrier_center=req.barrier_center or 0.0
        )
        res = sim.propagate(psi0, V, t_max=1.5, dt=0.01, n_frames=25)
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sim/relativity-orbit")
def relativity_orbit_endpoint(req: RelativityOrbitRequest):
    from equation_derivator.simulation.relativity_sim import RelativisticOrbitSim
    sim = RelativisticOrbitSim(M=1.0, G=1.0, c=1.0)
    try:
        if req.mode == "photon":
            res = sim.simulate_photon_deflection(
                impact_parameter_b=req.impact_parameter_b or 6.0,
                x_start=-20.0,
                y_start=req.impact_parameter_b or 6.0
            )
        else:
            res = sim.simulate_particle_orbit(
                r0=req.r0 or 12.0,
                v_phi0=req.v_phi0 or 0.28
            )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/qft/dirac")
def qft_dirac_endpoint(req: QFTRequest):
    from equation_derivator.qft.dirac import evaluate_dirac_equation
    try:
        res = evaluate_dirac_equation(representation=req.representation or "dirac")
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/qft/feynman")
def qft_feynman_endpoint(req: FeynmanRequest):
    from equation_derivator.qft.feynman import QEDScatteringProcess
    from equation_derivator.qft.feynman_draw import FeynmanDiagramGenerator
    try:
        res = QEDScatteringProcess.evaluate(req.process or "ee_to_mumu")
        data = res.to_dict()
        if req.process in ("compton", "photon_scattering"):
            data["svg_diagram"] = FeynmanDiagramGenerator.draw_compton_scattering()
        else:
            data["svg_diagram"] = FeynmanDiagramGenerator.draw_ee_to_mumu()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/geometry/maxwell")
def geometry_maxwell_endpoint():
    from equation_derivator.geometry.maxwell_forms import GeometricMaxwellEngine
    engine = GeometricMaxwellEngine()
    try:
        res = engine.build_electrodynamics()
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/symmetry/eval")
def symmetry_endpoint(req: SymmetryRequest):
    from equation_derivator.symmetry.lie_algebra import SU2Algebra, SU3Algebra
    from equation_derivator.symmetry.gauge import YangMillsGaugeEngine, HiggsMechanismEngine
    try:
        mode = (req.mode or "su2").lower()
        if mode == "su2":
            res = SU2Algebra().evaluate()
            return res.to_dict()
        elif mode == "su3":
            res = SU3Algebra().evaluate()
            return res.to_dict()
        elif mode == "higgs":
            res = HiggsMechanismEngine().evaluate_electroweak_breaking()
            return res.to_dict()
        else:
            res = YangMillsGaugeEngine().evaluate_yang_mills("SU(2)")
            return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/statmech/eval")
def statmech_endpoint(req: StatMechRequest):
    from equation_derivator.statmech.partition import PartitionFunctionEngine
    from equation_derivator.statmech.distributions import QuantumDistributionEngine
    engine = PartitionFunctionEngine()
    try:
        mode = (req.mode or "ideal_gas").lower()
        if mode == "ideal_gas":
            res = engine.evaluate_ideal_gas()
            return res.to_dict()
        elif mode == "quantum_oscillator":
            res = engine.evaluate_quantum_harmonic_oscillator()
            return res.to_dict()
        elif mode == "distributions":
            res = QuantumDistributionEngine().evaluate_distributions()
            return res.to_dict()
        elif mode == "custom" and req.partition_function:
            res = engine.derive_from_Z(req.partition_function, model_name=req.model_name or "Custom Ensemble")
            return res.to_dict()
        else:
            res = engine.evaluate_ideal_gas()
            return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ask")
def ask_endpoint(req: AskRequest):
    from equation_derivator.interfaces.nlp import PhysicsQueryDispatcher
    dispatcher = PhysicsQueryDispatcher()
    try:
        res = dispatcher.process_query(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/paper")
def paper_endpoint(req: PaperRequest):
    from equation_derivator.derivation.engine import DerivationEngine
    from equation_derivator.interfaces.paper_generator import ScientificPaperGenerator
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)
    generator = ScientificPaperGenerator()
    try:
        deriv = engine.derive(target_variable=req.target, in_terms_of=req.in_terms_of)
        tex_code = generator.generate_derivation_paper(deriv.to_dict(), title=req.title)
        return {"latex_source": tex_code, "target": req.target}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Mount Static Files for Web UI
web_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="static")

