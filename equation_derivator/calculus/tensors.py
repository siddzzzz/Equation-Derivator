"""
General Relativity & Spacetime Tensor Curvature Engine.
Computes symbolic Metric inverses, Christoffel connection symbols,
Riemann curvature tensor, Ricci tensor/scalar, Einstein tensor, and Geodesic equations.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import sympy as sp


@dataclass
class TensorCurvatureResult:
    """
    Encapsulates the exact symbolic differential geometry of a spacetime metric.
    """
    metric_name: str
    coordinates: List[str]
    metric_matrix: sp.Matrix
    inverse_metric: sp.Matrix
    christoffel_symbols: Dict[Tuple[int, int, int], sp.Expr]  # (sigma, mu, nu) -> Gamma^sigma_{mu, nu}
    ricci_tensor: sp.Matrix
    ricci_scalar: sp.Expr
    einstein_tensor: sp.Matrix
    geodesic_equations: List[Dict[str, Any]]
    is_vacuum_solution: bool = False

    def to_markdown(self) -> str:
        lines = [
            f"# General Relativity Tensor Curvature: {self.metric_name}\n",
            f"**Spacetime Coordinates:** $x^\\mu = ({', '.join(self.coordinates)})$\n",
            "## 1. Metric Tensor $g_{\\mu\\nu}$ & Inverse $g^{\\mu\\nu}$\n",
            f"$$g_{{\\mu\\nu}} = {sp.latex(self.metric_matrix)}$$\n",
            f"$$g^{{\\mu\\nu}} = {sp.latex(self.inverse_metric)}$$\n",
            "## 2. Non-Zero Christoffel Connection Symbols $\\Gamma^\\sigma_{\\mu\\nu}$\n"
        ]

        if not self.christoffel_symbols:
            lines.append("- All Christoffel connection coefficients vanish identically (Flat spacetime).\n")
        else:
            # Group by upper index sigma
            for s_idx, s_coord in enumerate(self.coordinates):
                s_gammas = {
                    (m, n): val for (s, m, n), val in self.christoffel_symbols.items()
                    if s == s_idx and m <= n
                }
                if s_gammas:
                    lines.append(f"### Upper index $\\sigma = {s_coord}$:")
                    for (m, n), val in s_gammas.items():
                        m_coord = self.coordinates[m]
                        n_coord = self.coordinates[n]
                        lines.append(f"- $\\Gamma^{{{s_coord}}}_{{{m_coord} {n_coord}}} = {sp.latex(val)}$")
            lines.append("")

        lines.append("## 3. Spacetime Curvature Tensors\n")
        lines.append(f"- **Ricci Curvature Tensor $R_{{\\mu\\nu}}$:**")
        lines.append(f"  $$R_{{\\mu\\nu}} = {sp.latex(self.ricci_tensor)}$$")
        lines.append(f"- **Ricci Curvature Scalar $R$:**")
        lines.append(f"  $$R = g^{{\\mu\\nu}} R_{{\\mu\\nu}} = {sp.latex(self.ricci_scalar)}$$")
        lines.append(f"- **Einstein Tensor $G_{{\\mu\\nu}} = R_{{\\mu\\nu}} - \\frac{{1}}{{2}} R g_{{\\mu\\nu}}$:**")
        lines.append(f"  $$G_{{\\mu\\nu}} = {sp.latex(self.einstein_tensor)}$$\n")

        if self.is_vacuum_solution:
            lines.append("> [!NOTE]\n> **Vacuum Solution Verified:** $R_{\\mu\\nu} = 0 \\implies G_{\\mu\\nu} = 0$ (Satisfies Einstein vacuum field equations $G_{\\mu\\nu} = 0$).\n")

        lines.append("## 4. Geodesic Equations of Motion\n")
        lines.append("$$\\frac{d^2 x^\\mu}{d\\lambda^2} + \\Gamma^\\mu_{\\alpha\\beta} \\frac{dx^\\alpha}{d\\lambda} \\frac{dx^\\beta}{d\\lambda} = 0$$\n")
        for geo in self.geodesic_equations:
            lines.append(f"- **Coordinate ${geo['coord']}$:**")
            lines.append(f"  $${geo['equation_latex']}$$")
        lines.append("")

        return "\n".join(lines)


class SpacetimeTensorEngine:
    """
    Symbolic tensor engine for differential geometry and General Relativity.
    """

    def compute_curvature(
        self,
        metric: sp.Matrix,
        coordinates: List[Union[str, sp.Symbol]],
        metric_name: str = "Spacetime Metric"
    ) -> TensorCurvatureResult:
        """
        Computes all connection coefficients and curvature tensors for a given spacetime metric.
        """
        dim = len(coordinates)
        x_syms = [c if isinstance(c, sp.Symbol) else sp.Symbol(c, real=True) for c in coordinates]
        coord_names = [str(c) for c in coordinates]

        # 1. Inverse metric g^{mu nu}
        g_inv = metric.inv()

        # 2. Christoffel symbols of the 2nd kind:
        # Gamma^sigma_{mu nu} = 1/2 * sum_rho g^{sigma rho} ( d_mu g_{nu rho} + d_nu g_{mu rho} - d_rho g_{mu nu} )
        christoffel: Dict[Tuple[int, int, int], sp.Expr] = {}

        for sigma in range(dim):
            for mu in range(dim):
                for nu in range(dim):
                    gamma_val = sp.S.Zero
                    for rho in range(dim):
                        term = (
                            metric[nu, rho].diff(x_syms[mu]) +
                            metric[mu, rho].diff(x_syms[nu]) -
                            metric[mu, nu].diff(x_syms[rho])
                        )
                        gamma_val += sp.Rational(1, 2) * g_inv[sigma, rho] * term
                    gamma_val = sp.simplify(gamma_val)
                    if gamma_val != 0 and not gamma_val.is_zero:
                        christoffel[(sigma, mu, nu)] = gamma_val

        # 3. Riemann Curvature Tensor R^rho_{sigma mu nu}
        # R^rho_{sigma mu nu} = d_mu Gamma^rho_{nu sigma} - d_nu Gamma^rho_{mu sigma}
        #                     + sum_lambda (Gamma^rho_{mu lambda} Gamma^lambda_{nu sigma} - Gamma^rho_{nu lambda} Gamma^lambda_{mu sigma})
        riemann: Dict[Tuple[int, int, int, int], sp.Expr] = {}

        def get_gamma(s, m, n):
            return christoffel.get((s, m, n), sp.S.Zero)

        for rho in range(dim):
            for sigma in range(dim):
                for mu in range(dim):
                    for nu in range(dim):
                        g_nu_sig = get_gamma(rho, nu, sigma)
                        g_mu_sig = get_gamma(rho, mu, sigma)

                        term1 = g_nu_sig.diff(x_syms[mu]) if g_nu_sig != 0 else sp.S.Zero
                        term2 = g_mu_sig.diff(x_syms[nu]) if g_mu_sig != 0 else sp.S.Zero

                        term3 = sp.S.Zero
                        for lam in range(dim):
                            g1 = get_gamma(rho, mu, lam)
                            g2 = get_gamma(lam, nu, sigma)
                            g3 = get_gamma(rho, nu, lam)
                            g4 = get_gamma(lam, mu, sigma)
                            if g1 != 0 and g2 != 0:
                                term3 += g1 * g2
                            if g3 != 0 and g4 != 0:
                                term3 -= g3 * g4

                        r_val = sp.simplify(term1 - term2 + term3)
                        if r_val != 0 and not r_val.is_zero:
                            riemann[(rho, sigma, mu, nu)] = r_val

        # 4. Ricci Tensor R_{mu nu} = sum_rho R^rho_{mu rho nu}
        ricci_mat = sp.zeros(dim, dim)
        for mu in range(dim):
            for nu in range(dim):
                r_val = sp.S.Zero
                for rho in range(dim):
                    r_val += riemann.get((rho, mu, rho, nu), sp.S.Zero)
                ricci_mat[mu, nu] = sp.simplify(r_val)

        # 5. Ricci Scalar R = sum_{mu, nu} g^{mu nu} R_{mu nu}
        ricci_scalar = sp.S.Zero
        for mu in range(dim):
            for nu in range(dim):
                if ricci_mat[mu, nu] != 0:
                    ricci_scalar += g_inv[mu, nu] * ricci_mat[mu, nu]
        ricci_scalar = sp.simplify(ricci_scalar)

        # 6. Einstein Tensor G_{mu nu} = R_{mu nu} - 1/2 * R * g_{mu nu}
        einstein_mat = sp.zeros(dim, dim)
        for mu in range(dim):
            for nu in range(dim):
                einstein_mat[mu, nu] = sp.simplify(ricci_mat[mu, nu] - sp.Rational(1, 2) * ricci_scalar * metric[mu, nu])

        # 7. Geodesic Equations: d^2 x^sigma / dlambda^2 + Gamma^sigma_{mu nu} (dx^mu/dlambda) (dx^nu/dlambda) = 0
        geodesic_eqs = []
        for sigma in range(dim):
            s_coord = coord_names[sigma]
            geo_sum = sp.S.Zero
            for mu in range(dim):
                for nu in range(dim):
                    g_val = get_gamma(sigma, mu, nu)
                    if g_val != 0:
                        u_mu = sp.Symbol(f"\\dot{{{coord_names[mu]}}}")
                        u_nu = sp.Symbol(f"\\dot{{{coord_names[nu]}}}")
                        geo_sum += g_val * u_mu * u_nu

            geo_sum = sp.simplify(geo_sum)
            geo_eq_latex = f"\\ddot{{{s_coord}}} + {sp.latex(geo_sum)} = 0" if geo_sum != 0 else f"\\ddot{{{s_coord}}} = 0"
            geodesic_eqs.append({
                "coord": s_coord,
                "connection_sum": geo_sum,
                "equation_latex": geo_eq_latex
            })

        is_vacuum = all(ricci_mat[i, j] == 0 for i in range(dim) for j in range(dim))

        return TensorCurvatureResult(
            metric_name=metric_name,
            coordinates=coord_names,
            metric_matrix=metric,
            inverse_metric=g_inv,
            christoffel_symbols=christoffel,
            ricci_tensor=ricci_mat,
            ricci_scalar=ricci_scalar,
            einstein_tensor=einstein_mat,
            geodesic_equations=geodesic_eqs,
            is_vacuum_solution=is_vacuum
        )

    def create_schwarzschild_metric(self) -> TensorCurvatureResult:
        """
        Constructs the static, spherically symmetric vacuum Schwarzschild black hole spacetime.
        Coordinates: (t, r, theta, phi)
        """
        t = sp.Symbol("t", real=True)
        r = sp.Symbol("r", positive=True, real=True)
        theta = sp.Symbol("theta", real=True)
        phi = sp.Symbol("phi", real=True)
        G = sp.Symbol("G", positive=True, real=True)
        M = sp.Symbol("M", positive=True, real=True)
        c = sp.Symbol("c", positive=True, real=True)

        r_s = 2 * G * M / c**2
        f_r = 1 - r_s / r

        # g_{mu nu} = diag( -f_r * c^2, 1/f_r, r^2, r^2 * sin^2(theta) )
        metric = sp.diag(
            -f_r * c**2,
            1 / f_r,
            r**2,
            r**2 * sp.sin(theta)**2
        )

        return self.compute_curvature(
            metric=metric,
            coordinates=[t, r, theta, phi],
            metric_name="Schwarzschild Black Hole Spacetime"
        )

    def create_minkowski_metric(self) -> TensorCurvatureResult:
        """
        Constructs flat Minkowski spacetime in Cartesian coordinates (t, x, y, z).
        """
        c = sp.Symbol("c", positive=True, real=True)
        metric = sp.diag(-c**2, 1, 1, 1)
        return self.compute_curvature(
            metric=metric,
            coordinates=["t", "x", "y", "z"],
            metric_name="Minkowski Flat Spacetime"
        )

    def create_flrw_metric(self) -> TensorCurvatureResult:
        """
        Constructs the spatially flat (k=0) Friedmann-Lemaître-Robertson-Walker expanding cosmological spacetime.
        Coordinates: (t, r, theta, phi)
        """
        t = sp.Symbol("t", real=True)
        r = sp.Symbol("r", positive=True, real=True)
        theta = sp.Symbol("theta", real=True)
        c = sp.Symbol("c", positive=True, real=True)
        a = sp.Function("a")(t)  # Cosmological scale factor

        metric = sp.diag(
            -c**2,
            a**2,
            a**2 * r**2,
            a**2 * r**2 * sp.sin(theta)**2
        )

        return self.compute_curvature(
            metric=metric,
            coordinates=["t", "r", "theta", "phi"],
            metric_name="FLRW Cosmological Metric (Spatially Flat k=0)"
        )
