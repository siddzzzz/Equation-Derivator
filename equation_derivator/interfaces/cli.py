import sys
import argparse

# Ensure stdout uses UTF-8 where possible on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from equation_derivator.knowledge.database import GLOBAL_KNOWLEDGE_BASE
import equation_derivator.knowledge.domains
from equation_derivator.core.quantities import GLOBAL_QUANTITY_REGISTRY
from equation_derivator.core.equation import PhysicalEquation
from equation_derivator.derivation.engine import DerivationEngine
from equation_derivator.verifier.verifier import EquationVerifier
from equation_derivator.discovery.discovery_engine import DiscoveryEngine

console = Console()


def print_banner():
    banner_text = "[bold cyan]EQUATION-DERIVATOR[/bold cyan]\n[dim]Universal AI Equation Derivation, Discovery & Verification Engine[/dim]"
    console.print(Panel(banner_text, border_style="cyan", expand=False))


def handle_derive(args):
    print_banner()
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)
    
    target = args.target.strip()
    in_terms_of = [s.strip() for s in args.in_terms_of.split(",") if s.strip()]
    
    starting_eqs = None
    if args.equations:
        starting_eqs = [s.strip() for s in args.equations.split(";") if s.strip()]

    with console.status(f"[bold green]Deriving ${target}$ in terms of {in_terms_of}..."):
        try:
            result = engine.derive(
                target_variable=target,
                in_terms_of=in_terms_of,
                starting_equations=starting_eqs
            )
        except Exception as e:
            console.print(f"[bold red]Derivation Error:[/bold red] {e}")
            return

    console.print(Panel(
        f"[bold yellow]Final Result:[/bold yellow] [bold green]{result.final_equation}[/bold green]\n"
        f"[dim]LaTeX:[/dim] `{result.final_latex}`",
        title=f"🎯 Derivation for {target}",
        border_style="green"
    ))

    console.print("\n[bold cyan]Step-by-Step Derivation Chain:[/bold cyan]")
    for s in result.steps:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[bold magenta]Step " + str(s.step_number) + ":[/bold magenta]", f"[bold yellow]{s.operation}[/bold yellow]")
        table.add_row("[dim]Formula:[/dim]", f"[green]{s.expression}[/green]")
        table.add_row("[dim]LaTeX:[/dim]", f"`{s.latex}`")
        table.add_row("[dim]Reasoning:[/dim]", f"{s.explanation}")
        if s.substituted_symbol:
            table.add_row("[dim]Substituted:[/dim]", f"{s.substituted_symbol} -> {s.substitution_value}")
        console.print(Panel(table, border_style="blue"))

    if result.all_assumptions:
        console.print("\n[bold yellow]Physical Assumptions & Validity Conditions:[/bold yellow]")
        for a in result.all_assumptions:
            console.print(f"  • [dim]{a}[/dim]")

    status_color = "bold green" if result.is_verified else "bold red"
    status_icon = "✔ VERIFIED SOUND" if result.is_verified else "⚠ UNVERIFIED"
    console.print(f"\n[{status_color}]Verification Status: {status_icon}[/{status_color}]")


def handle_verify(args):
    print_banner()
    verifier = EquationVerifier()
    eq_str = args.equation.strip()

    try:
        eq = PhysicalEquation.create(
            id="cli_verify_eq",
            name="Equation to Verify",
            domain="Custom",
            equation_str=eq_str
        )
        report = verifier.verify_equation(eq)
    except Exception as e:
        console.print(f"[bold red]Verification Error:[/bold red] {e}")
        return

    table = Table(title=f"Verification Report: {eq_str}", border_style="cyan")
    table.add_column("Aspect", style="bold yellow")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")

    dim_res = report["dimensional_check"]
    table.add_row(
        "Dimensional Consistency",
        "[green]PASS[/green]" if dim_res["valid"] else "[red]FAIL[/red]",
        dim_res["message"]
    )

    sym_res = report["symbolic_check"]
    table.add_row(
        "Symbolic Equivalence",
        "[green]PASS[/green]" if sym_res["valid"] else "[yellow]INCONCLUSIVE[/yellow]",
        sym_res["message"]
    )

    num_res = report["numerical_check"]
    table.add_row(
        "Monte Carlo Random Sampling",
        "[green]PASS[/green]" if num_res["valid"] else "[red]FAIL[/red]",
        num_res["message"]
    )

    console.print(table)
    overall = report["overall_valid"]
    color = "bold green" if overall else "bold red"
    console.print(f"\n[{color}]Overall Assessment: {'EQUATION IS SOUND & CONSISTENT' if overall else 'EQUATION FAILED VALIDATION'}[/{color}]")


def handle_discover(args):
    print_banner()
    engine = DiscoveryEngine(GLOBAL_KNOWLEDGE_BASE)

    if args.quantities:
        q_list = [q.strip() for q in args.quantities.split(",") if q.strip()]
        target = args.target.strip()
        with console.status(f"[bold green]Synthesizing dimensional relations for {target}..."):
            results = engine.synthesize_dimensional_relation(q_list, target)

        if not results:
            console.print("[yellow]No power-law relations could be formed with the given quantities.[/yellow]")
            return

        console.print(f"\n[bold cyan]Discovered Dimensional Scaling Relations for {target}:[/bold cyan]\n")
        for i, res in enumerate(results, 1):
            console.print(Panel(
                f"[bold green]{res.formula}[/bold green]\n"
                f"[dim]LaTeX:[/dim] `{res.latex}`\n"
                f"[dim]Dimension:[/dim] {res.dimension}\n"
                f"[dim]Notes:[/dim] {res.notes}",
                title=f"Candidate {i}: {res.name}",
                border_style="green"
            ))

    elif args.cross_domain:
        domains = [d.strip() for d in args.cross_domain.split(",") if d.strip()]
        if len(domains) != 2:
            console.print("[red]Please specify two domains separated by comma, e.g. --cross-domain 'Quantum,Relativity'[/red]")
            return
        with console.status(f"[bold green]Discovering bridge equations between {domains[0]} and {domains[1]}..."):
            bridges = engine.discover_cross_domain_relations(domains[0], domains[1])

        console.print(f"\n[bold cyan]Discovered Cross-Domain Bridge Relations:[/bold cyan]\n")
        for i, b in enumerate(bridges, 1):
            console.print(Panel(
                f"[bold green]{b.formula}[/bold green]\n"
                f"[dim]LaTeX:[/dim] `{b.latex}`\n"
                f"[dim]Source Laws:[/dim] {', '.join(b.source_equations)}\n"
                f"[dim]Notes:[/dim] {b.notes}",
                title=f"Bridge {i}: {b.name}",
                border_style="magenta"
            ))


def handle_browse(args):
    print_banner()
    eqs = GLOBAL_KNOWLEDGE_BASE.list_all()
    if args.domain:
        eqs = [e for e in eqs if e.domain.lower() == args.domain.lower()]

    table = Table(title="Universal Equation Knowledge Base", border_style="cyan")
    table.add_column("ID", style="bold cyan")
    table.add_column("Name", style="bold white")
    table.add_column("Domain", style="magenta")
    table.add_column("Formula", style="green")
    table.add_column("Tags", style="dim")

    for e in eqs:
        table.add_row(e.id, e.name, e.domain, e.raw_str, ", ".join(e.tags[:3]))

    console.print(table)
    console.print(f"[dim]Total Equations in Catalog: {len(eqs)}[/dim]")


def handle_quantities(args):
    print_banner()
    qtys = GLOBAL_QUANTITY_REGISTRY.list_all()
    table = Table(title="Universal Physical Quantities Registry", border_style="cyan")
    table.add_column("Quantity Name", style="bold cyan")
    table.add_column("Symbol", style="bold green")
    table.add_column("Dimension", style="yellow")
    table.add_column("Aliases", style="dim")
    table.add_column("Constant?", style="magenta")

    for q in qtys:
        table.add_row(
            q.name,
            q.canonical_symbol,
            str(q.dimension),
            ", ".join(q.aliases[:4]),
            f"Yes ({q.constant_value:.3e} {q.constant_unit})" if q.is_constant else "No"
        )

    console.print(table)


def handle_lagrangian(args):
    print_banner()
    from equation_derivator.calculus.variational import VariationalEngine
    engine = VariationalEngine()
    coords = [c.strip() for c in args.coords.split(",") if c.strip()]

    with console.status("[bold green]Solving Euler-Lagrange & Hamiltonian Mechanics..."):
        try:
            res = engine.derive(
                lagrangian=args.lagrangian,
                coordinates=coords,
                system_name=args.name or "Variational System"
            )
        except Exception as e:
            console.print(f"[bold red]Variational Error:[/bold red] {e}")
            return

    console.print(Markdown(res.to_markdown()))


def handle_diff_eq(args):
    print_banner()
    from equation_derivator.calculus.differential import DifferentialEquationSolver
    solver = DifferentialEquationSolver()

    if args.type == "schrodinger":
        res = solver.solve_quantum_infinite_well()
    else:
        res = solver.solve_damped_harmonic_oscillator(driving_force=args.driving)

    console.print(Markdown(res.to_markdown()))


def handle_tensor(args):
    print_banner()
    from equation_derivator.calculus.tensors import SpacetimeTensorEngine
    engine = SpacetimeTensorEngine()

    if args.metric == "schwarzschild":
        res = engine.create_schwarzschild_metric()
    elif args.metric == "flrw":
        res = engine.create_flrw_metric()
    else:
        res = engine.create_minkowski_metric()

    console.print(Markdown(res.to_markdown()))


def handle_ask(args):
    print_banner()
    from equation_derivator.interfaces.nlp import PhysicsQueryDispatcher
    dispatcher = PhysicsQueryDispatcher()

    with console.status(f"[bold green]Processing physics query: '{args.query}'..."):
        try:
            res = dispatcher.process_query(args.query)
        except Exception as e:
            console.print(f"[bold red]Query Error:[/bold red] {e}")
            return

    console.print(Markdown(res.get("markdown", str(res))))


def handle_paper(args):
    print_banner()
    from equation_derivator.derivation.engine import DerivationEngine
    from equation_derivator.interfaces.paper_generator import ScientificPaperGenerator
    
    engine = DerivationEngine(GLOBAL_KNOWLEDGE_BASE)
    target = args.target.strip()
    in_terms_of = [s.strip() for s in args.in_terms_of.split(",") if s.strip()]
    
    try:
        deriv = engine.derive(target_variable=target, in_terms_of=in_terms_of)
        generator = ScientificPaperGenerator()
        tex_code = generator.generate_derivation_paper(deriv.to_dict(), title=args.title)
        
        out_file = args.output or f"paper_{target}.tex"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(tex_code)
            
        console.print(Panel(
            f"[bold green]Academic LaTeX Paper Successfully Generated![/bold green]\n"
            f"[bold cyan]Saved to:[/bold cyan] {out_file}\n"
            f"[dim]Compile with: pdflatex {out_file}[/dim]",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[bold red]Paper Generation Error:[/bold red] {e}")


def handle_sim(args):
    print_banner()
    from equation_derivator.simulation.integrator import simulate_symbolic_system
    coords = [c.strip() for c in args.coords.split(",") if c.strip()]
    q0_vals = [float(x.strip()) for x in args.q0.split(",") if x.strip()]
    v0_vals = [float(x.strip()) for x in args.v0.split(",") if x.strip()]
    accels = {c: a.strip() for c, a in zip(coords, args.accel.split(";"))}
    pos0 = {c: q0_vals[i] if i < len(q0_vals) else 0.0 for i, c in enumerate(coords)}
    vel0 = {c: v0_vals[i] if i < len(v0_vals) else 0.0 for i, c in enumerate(coords)}

    console.print(f"[bold cyan]Integrating Dynamical System: {args.name}...[/bold cyan]")
    traj = simulate_symbolic_system(
        accelerations=accels,
        coordinates=coords,
        initial_positions=pos0,
        initial_velocities=vel0,
        t_end=args.t_end,
        dt=args.dt,
        system_name=args.name
    )

    table = Table(title=f"Numerical Trajectory (First 8 Steps): {args.name}", border_style="cyan")
    table.add_column("Time t (s)", style="bold yellow")
    for c in coords:
        table.add_column(f"q: {c}", style="green")
        table.add_column(f"v: {c}_dot", style="magenta")

    for i in range(min(8, len(traj.time))):
        row = [f"{traj.time[i]:.3f}"]
        for c in coords:
            row.append(f"{traj.positions[c][i]:.4f}")
            row.append(f"{traj.velocities[c][i]:.4f}")
        table.add_row(*row)

    console.print(table)
    console.print(f"[dim]Total simulated points: {len(traj.time)} across [0, {args.t_end}] s[/dim]")


def handle_qft(args):
    print_banner()
    if args.representation:
        from equation_derivator.qft.dirac import evaluate_dirac_equation
        res = evaluate_dirac_equation(representation=args.representation)
        console.print(Markdown(res.markdown))
    else:
        from equation_derivator.qft.feynman import QEDScatteringProcess
        res = QEDScatteringProcess.evaluate(args.process)
        console.print(Markdown(res.markdown))


def handle_forms(args):
    print_banner()
    from equation_derivator.geometry.maxwell_forms import GeometricMaxwellEngine
    engine = GeometricMaxwellEngine()
    res = engine.build_electrodynamics()
    console.print(Markdown(res.markdown))


def handle_symmetry(args):
    print_banner()
    mode = args.group.lower()
    if mode == "su2":
        from equation_derivator.symmetry.lie_algebra import SU2Algebra
        res = SU2Algebra().evaluate()
        console.print(Markdown(res.markdown))
    elif mode == "su3":
        from equation_derivator.symmetry.lie_algebra import SU3Algebra
        res = SU3Algebra().evaluate()
        console.print(Markdown(res.markdown))
    elif mode == "higgs":
        from equation_derivator.symmetry.gauge import HiggsMechanismEngine
        res = HiggsMechanismEngine().evaluate_electroweak_breaking()
        console.print(Markdown(res.markdown))
    else:
        from equation_derivator.symmetry.gauge import YangMillsGaugeEngine
        res = YangMillsGaugeEngine().evaluate_yang_mills("SU(2)")
        console.print(Markdown(res.markdown))


def handle_statmech(args):
    print_banner()
    from equation_derivator.statmech.partition import PartitionFunctionEngine
    from equation_derivator.statmech.distributions import QuantumDistributionEngine
    engine = PartitionFunctionEngine()
    if args.model == "ideal_gas":
        res = engine.evaluate_ideal_gas()
        console.print(Markdown(res.markdown))
    elif args.model == "quantum_oscillator":
        res = engine.evaluate_quantum_harmonic_oscillator()
        console.print(Markdown(res.markdown))
    elif args.model == "distributions":
        res = QuantumDistributionEngine().evaluate_distributions()
        console.print(Markdown(res.markdown))
    elif args.partition:
        res = engine.derive_from_Z(args.partition, model_name=args.name or "Custom Ensemble")
        console.print(Markdown(res.markdown))


def handle_serve(args):
    print_banner()
    import uvicorn
    console.print(f"[bold green]Starting Equation Derivator Web Interface on http://localhost:{args.port}...[/bold green]")
    uvicorn.run("equation_derivator.interfaces.api:app", host=args.host, port=args.port, reload=False)


def main():
    parser = argparse.ArgumentParser(
        description="Equation-Derivator: Universal AI Equation Derivation, Discovery & Verification Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # derive
    p_derive = subparsers.add_parser("derive", help="Derive formula for target variable")
    p_derive.add_argument("--target", "-t", required=True, help="Target variable (e.g. K, v, P, E)")
    p_derive.add_argument("--in-terms-of", "-i", required=True, help="Comma-separated allowed variables (e.g. p,m)")
    p_derive.add_argument("--equations", "-e", help="Semicolon-separated equation IDs or formulas")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify physical/dimensional consistency of equation")
    p_verify.add_argument("--equation", "-e", required=True, help="Equation string (e.g. 'F = m*a')")

    # discover
    p_discover = subparsers.add_parser("discover", help="Discover new relations or scaling laws")
    p_discover.add_argument("--quantities", "-q", help="Comma-separated input quantities (e.g. 'G,hbar,c')")
    p_discover.add_argument("--target", "-t", default="Length", help="Target quantity or dimension")
    p_discover.add_argument("--cross-domain", "-cd", help="Comma-separated domains (e.g. 'Quantum,Relativity')")

    # lagrangian
    p_lag = subparsers.add_parser("lagrangian", help="Derive Euler-Lagrange, Hamiltonian & Noether invariants")
    p_lag.add_argument("--lagrangian", "-l", required=True, help="Lagrangian formula (e.g. '1/2*m*x_dot^2 - 1/2*k*x^2')")
    p_lag.add_argument("--coords", "-c", required=True, help="Comma-separated generalized coordinates (e.g. 'x' or 'th1,th2')")
    p_lag.add_argument("--name", "-n", default="Physical System", help="System name")

    # diff-eq
    p_diff = subparsers.add_parser("diff-eq", help="Solve physical differential equations & eigenvalue problems")
    p_diff.add_argument("--type", choices=["damped", "schrodinger"], default="damped", help="ODE type")
    p_diff.add_argument("--driving", help="Driving force function F(t)")

    # tensor
    p_tens = subparsers.add_parser("tensor", help="Compute General Relativity spacetime curvature tensors")
    p_tens.add_argument("--metric", choices=["schwarzschild", "flrw", "minkowski"], default="schwarzschild", help="Spacetime metric")

    # sim
    p_sim = subparsers.add_parser("sim", help="Run numerical RK4 trajectory simulation on symbolic equations")
    p_sim.add_argument("--accel", "-a", required=True, help="Symbolic acceleration (e.g. '-g/L*sin(theta)')")
    p_sim.add_argument("--coords", "-c", default="theta", help="Comma-separated coordinates")
    p_sim.add_argument("--q0", default="0.5", help="Initial positions (e.g. '0.5')")
    p_sim.add_argument("--v0", default="0.0", help="Initial velocities (e.g. '0.0')")
    p_sim.add_argument("--t-end", type=float, default=5.0, help="Simulation duration (s)")
    p_sim.add_argument("--dt", type=float, default=0.01, help="Time step dt")
    p_sim.add_argument("--name", default="Dynamical System", help="System title")

    # qft
    p_qft = subparsers.add_parser("qft", help="Evaluate Dirac spinors, gamma matrices, and Feynman QED scattering")
    p_qft.add_argument("--representation", "-r", choices=["dirac", "weyl", "majorana"], help="Dirac matrix representation")
    p_qft.add_argument("--process", "-p", choices=["ee_to_mumu", "compton"], default="ee_to_mumu", help="QED scattering process")

    # forms
    p_forms = subparsers.add_parser("forms", help="Evaluate differential forms and geometric Maxwell electrodynamics")

    # symmetry
    p_sym = subparsers.add_parser("symmetry", help="Evaluate Lie algebras, Yang-Mills fields, and Higgs mechanism")
    p_sym.add_argument("--group", "-g", choices=["su2", "su3", "yang_mills", "higgs"], default="su2", help="Symmetry group / model")

    # statmech
    p_stat = subparsers.add_parser("statmech", help="Derive thermodynamic potentials from partition functions")
    p_stat.add_argument("--model", "-m", choices=["ideal_gas", "quantum_oscillator", "distributions"], default="ideal_gas", help="Ensemble model")
    p_stat.add_argument("--partition", "-z", help="Custom partition function Z(T, V, N)")
    p_stat.add_argument("--name", default="Custom Statistical Ensemble", help="Model name")

    # ask
    p_ask = subparsers.add_parser("ask", help="Natural language physics query dispatcher")
    p_ask.add_argument("--query", "-q", required=True, help="Natural language physics question")

    # paper
    p_paper = subparsers.add_parser("paper", help="Generate academic LaTeX paper (.tex)")
    p_paper.add_argument("--target", "-t", required=True, help="Target variable (e.g. K)")
    p_paper.add_argument("--in-terms-of", "-i", required=True, help="Allowed variables (e.g. p,m)")
    p_paper.add_argument("--title", help="Paper title")
    p_paper.add_argument("--output", "-o", help="Output .tex file path")

    # browse
    p_browse = subparsers.add_parser("browse", help="Browse catalog of equations")
    p_browse.add_argument("--domain", "-d", help="Filter by domain")

    # quantities
    subparsers.add_parser("quantities", help="List physical quantities and dimensions")

    # serve
    p_serve = subparsers.add_parser("serve", help="Launch interactive web server")
    p_serve.add_argument("--host", default="127.0.0.1", help="Host address")
    p_serve.add_argument("--port", type=int, default=8000, help="Port")

    args = parser.parse_args()

    if args.command == "derive":
        handle_derive(args)
    elif args.command == "verify":
        handle_verify(args)
    elif args.command == "discover":
        handle_discover(args)
    elif args.command == "lagrangian":
        handle_lagrangian(args)
    elif args.command == "diff-eq":
        handle_diff_eq(args)
    elif args.command == "tensor":
        handle_tensor(args)
    elif args.command == "sim":
        handle_sim(args)
    elif args.command == "qft":
        handle_qft(args)
    elif args.command == "forms":
        handle_forms(args)
    elif args.command == "symmetry":
        handle_symmetry(args)
    elif args.command == "statmech":
        handle_statmech(args)
    elif args.command == "ask":
        handle_ask(args)
    elif args.command == "paper":
        handle_paper(args)
    elif args.command == "browse":
        handle_browse(args)
    elif args.command == "quantities":
        handle_quantities(args)
    elif args.command == "serve":
        handle_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

