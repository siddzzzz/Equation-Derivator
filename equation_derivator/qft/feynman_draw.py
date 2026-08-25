"""
Feynman Diagram Vector SVG Generator.
Generates publication-quality interactive SVG Feynman diagrams.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union


class FeynmanDiagramGenerator:
    """
    Renders SVG diagrams for tree-level Feynman graphs with electron arrows, wavy photon lines,
    and vertex labels.
    """

    @staticmethod
    def draw_ee_to_mumu() -> str:
        """
        Generates s-channel e- e+ -> photon -> mu- mu+ diagram in SVG format.
        """
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 320" width="100%" height="260" class="feynman-svg">
  <defs>
    <!-- Arrowhead markers -->
    <marker id="arrow-fermion" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
      <path d="M0,0 L0,6 L6,3 z" fill="#00f2fe" />
    </marker>
    <marker id="arrow-antifermion" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
      <path d="M6,0 L6,6 L0,3 z" fill="#ff416c" />
    </marker>
    <marker id="arrow-muon" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
      <path d="M0,0 L0,6 L6,3 z" fill="#7928ca" />
    </marker>
    <marker id="arrow-antimuon" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
      <path d="M6,0 L6,6 L0,3 z" fill="#ff0080" />
    </marker>
    <filter id="feynman-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    .f-line { stroke-width: 2.5; stroke-linecap: round; }
    .f-photon { stroke: #f6d365; stroke-width: 2.5; fill: none; stroke-linecap: round; }
    .f-label { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; fill: #e2e8f0; }
    .f-vertex { fill: #ffffff; stroke: #00f2fe; stroke-width: 2; filter: url(#feynman-glow); }
    .f-channel-badge { font-family: 'Inter', sans-serif; font-size: 11px; fill: #00f2fe; }
  </style>

  <!-- Background container -->
  <rect width="100%" height="100%" fill="rgba(8, 12, 24, 0.6)" rx="12" />

  <!-- Title Badge -->
  <rect x="20" y="20" width="170" height="24" rx="6" fill="rgba(0, 242, 254, 0.12)" stroke="rgba(0, 242, 254, 0.3)" />
  <text x="30" y="36" class="f-channel-badge">s-channel: e⁻ e⁺ → γ* → μ⁻ μ⁺</text>

  <!-- Incoming Electron e-(p1) -->
  <line x1="80" y1="80" x2="155" y2="125" class="f-line" stroke="#00f2fe" marker-end="url(#arrow-fermion)" />
  <line x1="155" y1="125" x2="200" y2="160" class="f-line" stroke="#00f2fe" />
  <text x="50" y="75" class="f-label" fill="#00f2fe">e⁻ (p₁)</text>

  <!-- Incoming Positron e+(p2) -->
  <line x1="80" y1="240" x2="155" y2="195" class="f-line" stroke="#ff416c" marker-start="url(#arrow-antifermion)" />
  <line x1="155" y1="195" x2="200" y2="160" class="f-line" stroke="#ff416c" />
  <text x="50" y="255" class="f-label" fill="#ff416c">e⁺ (p₂)</text>

  <!-- Intermediate Virtual Photon Propagator gamma*(q) (wavy sine line) -->
  <path d="M 200,160 Q 212.5,145 225,160 T 250,160 T 275,160 T 300,160" class="f-photon" filter="url(#feynman-glow)" />
  <text x="238" y="140" class="f-label" fill="#f6d365">γ* (q)</text>
  <text x="228" y="195" class="f-label" style="font-size: 10px;" fill="#a0aec0">q² = s</text>

  <!-- Outgoing Muon mu-(p3) -->
  <line x1="300" y1="160" x2="365" y2="115" class="f-line" stroke="#7928ca" marker-end="url(#arrow-muon)" />
  <line x1="365" y1="115" x2="420" y2="80" class="f-line" stroke="#7928ca" />
  <text x="430" y="75" class="f-label" fill="#7928ca">μ⁻ (p₃)</text>

  <!-- Outgoing Antimuon mu+(p4) -->
  <line x1="300" y1="160" x2="365" y2="205" class="f-line" stroke="#ff0080" marker-start="url(#arrow-antimuon)" />
  <line x1="365" y1="205" x2="420" y2="240" class="f-line" stroke="#ff0080" />
  <text x="430" y="255" class="f-label" fill="#ff0080">μ⁺ (p₄)</text>

  <!-- Vertices -->
  <circle cx="200" cy="160" r="4.5" class="f-vertex" />
  <text x="188" y="180" class="f-label" style="font-size: 10px;" fill="#00f2fe">-ieγᵤ</text>

  <circle cx="300" cy="160" r="4.5" class="f-vertex" />
  <text x="296" y="180" class="f-label" style="font-size: 10px;" fill="#7928ca">-ieγᵥ</text>
</svg>"""

    @staticmethod
    def draw_compton_scattering() -> str:
        """
        Generates Compton scattering e- gamma -> e- gamma diagram in SVG format.
        """
        return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 320" width="100%" height="260" class="feynman-svg">
  <defs>
    <marker id="arrow-compton" markerWidth="8" markerHeight="8" refX="5" refY="3" orient="auto">
      <path d="M0,0 L0,6 L6,3 z" fill="#00f2fe" />
    </marker>
    <filter id="feynman-glow2" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    .f-line { stroke-width: 2.5; stroke-linecap: round; }
    .f-photon { stroke: #f6d365; stroke-width: 2.5; fill: none; stroke-linecap: round; }
    .f-label { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; fill: #e2e8f0; }
    .f-vertex { fill: #ffffff; stroke: #00f2fe; stroke-width: 2; filter: url(#feynman-glow2); }
    .f-channel-badge { font-family: 'Inter', sans-serif; font-size: 11px; fill: #00f2fe; }
  </style>

  <rect width="100%" height="100%" fill="rgba(8, 12, 24, 0.6)" rx="12" />

  <rect x="20" y="20" width="160" height="24" rx="6" fill="rgba(0, 242, 254, 0.12)" stroke="rgba(0, 242, 254, 0.3)" />
  <text x="30" y="36" class="f-channel-badge">Compton: e⁻(p) + γ(k) → e⁻(p') + γ(k')</text>

  <!-- Incoming Electron -->
  <line x1="80" y1="220" x2="160" y2="180" class="f-line" stroke="#00f2fe" marker-end="url(#arrow-compton)" />
  <line x1="160" y1="180" x2="210" y2="160" class="f-line" stroke="#00f2fe" />
  <text x="50" y="235" class="f-label" fill="#00f2fe">e⁻ (p)</text>

  <!-- Incoming Photon -->
  <path d="M 80,100 Q 112.5,85 145,100 T 210,160" class="f-photon" filter="url(#feynman-glow2)" />
  <text x="50" y="95" class="f-label" fill="#f6d365">γ (k)</text>

  <!-- Virtual Propagator Electron -->
  <line x1="210" y1="160" x2="260" y2="160" class="f-line" stroke="#00f2fe" marker-end="url(#arrow-compton)" />
  <line x1="260" y1="160" x2="310" y2="160" class="f-line" stroke="#00f2fe" />
  <text x="240" y="145" class="f-label" fill="#00f2fe">e⁻ (p+k)</text>

  <!-- Outgoing Electron -->
  <line x1="310" y1="160" x2="380" y2="200" class="f-line" stroke="#00f2fe" marker-end="url(#arrow-compton)" />
  <line x1="380" y1="200" x2="430" y2="230" class="f-line" stroke="#00f2fe" />
  <text x="440" y="240" class="f-label" fill="#00f2fe">e⁻ (p')</text>

  <!-- Outgoing Photon -->
  <path d="M 310,160 Q 342.5,135 375,120 T 430,90" class="f-photon" filter="url(#feynman-glow2)" />
  <text x="440" y="90" class="f-label" fill="#f6d365">γ (k')</text>

  <!-- Vertices -->
  <circle cx="210" cy="160" r="4.5" class="f-vertex" />
  <circle cx="310" cy="160" r="4.5" class="f-vertex" />
</svg>"""
