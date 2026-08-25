/**
 * Equation-Derivator: Theoretical Physics & Symbolic AI Workbench Controller
 */

// Global State
let allEquations = [];
let allQuantities = [];
let activeCatalogDomain = 'all';
let currentDerivationResult = null;
let currentSynthesisMode = 'dimensional';

document.addEventListener('DOMContentLoaded', async () => {
  if (window.lucide) lucide.createIcons();
  initNebulaBackground();
  initDockNavigation();
  initOmnibar();
  initSidecar();
  initDerivationEngine();
  initDiscoveryReactor();
  initVerifierEngine();

  // Auto-render inline KaTeX math across initial page
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ],
      throwOnError: false
    });
  }

  await fetchQuantities();
  await fetchEquations();

  initPhysicsGraph();
});

/* ================= AMBIENT NEBULA BACKGROUND ================= */
function initNebulaBackground() {
  const canvas = document.getElementById('nebula-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = [];
  for (let i = 0; i < 40; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      radius: Math.random() * 1.8 + 0.5,
      alpha: Math.random() * 0.4 + 0.1,
      color: Math.random() > 0.5 ? '#00f2fe' : '#7928ca'
    });
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    // Draw subtle particle web
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();

      // Connect close particles
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = '#00f2fe';
          ctx.globalAlpha = (1 - dist / 120) * 0.08;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    ctx.globalAlpha = 1.0;
    requestAnimationFrame(render);
  }
  render();
}

/* ================= DOCK NAVIGATION ================= */
function initDockNavigation() {
  const dockButtons = document.querySelectorAll('.dock-item[data-view]');
  dockButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const viewId = btn.getAttribute('data-view');
      switchView(viewId);
    });
  });
}

function switchView(viewId) {
  document.querySelectorAll('.dock-item[data-view]').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-view') === viewId);
  });

  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `view-${viewId}`);
  });

  lucide.createIcons();
  const activePanel = document.getElementById(`view-${viewId}`);
  if (activePanel) {
    renderMathInElement(activePanel, {
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false}
      ]
    });
  }

  if (viewId === 'graph') {
    setTimeout(renderPhysicsGraph, 100);
  }
}

/* ================= OMNIBAR LAUNCHER ================= */
function initOmnibar() {
  const input = document.getElementById('omnibar-input');
  if (!input) return;

  // Keyboard shortcut Ctrl+K
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      input.focus();
      input.select();
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const val = input.value.trim().toLowerCase();
      if (!val) return;

      if (val.startsWith('derive') || val.includes('from')) {
        switchView('derivator');
        // Parse 'derive K from p,m'
        const parts = val.replace('derive', '').split('from');
        if (parts.length === 2) {
          document.getElementById('derive-target').value = parts[0].trim();
          document.getElementById('derive-in-terms-of').value = parts[1].trim();
        }
        document.getElementById('btn-execute-derivation').click();
      } else if (val.startsWith('verify')) {
        switchView('verifier');
        document.getElementById('verify-equation-input').value = val.replace('verify', '').trim();
        document.getElementById('btn-execute-verify').click();
      } else if (val.includes('planck') || val.includes('synthesize') || val.includes('discover')) {
        switchView('discovery');
        document.getElementById('btn-execute-discovery').click();
      } else {
        // Search catalog
        switchView('catalog');
        const searchInput = document.getElementById('catalog-search-input');
        if (searchInput) {
          searchInput.value = val;
          renderCatalogCards();
        }
      }
    }
  });
}

/* ================= SIDECAR INSPECTOR ================= */
function initSidecar() {
  const toggleBtn = document.getElementById('btn-toggle-sidecar');
  const sidecar = document.getElementById('workbench-sidecar');

  if (toggleBtn && sidecar) {
    toggleBtn.addEventListener('click', () => {
      sidecar.classList.toggle('collapsed');
      toggleBtn.classList.toggle('active');
    });
  }
}

function inspectSymbol(symStr) {
  const card = document.getElementById('symbol-inspector-card');
  const nameEl = document.getElementById('insp-sym-name');
  const dimEl = document.getElementById('insp-sym-dim');
  const descEl = document.getElementById('insp-sym-desc');

  const clean = symStr.replace(/[^A-Za-z0-9_]/g, '');
  const qty = allQuantities.find(q => q.symbol === clean || q.aliases.includes(clean) || q.name.toLowerCase() === clean.toLowerCase());

  if (qty) {
    nameEl.textContent = `${qty.name} (${qty.symbol})`;
    dimEl.textContent = `SI Exponents: ${qty.dimension}`;
    descEl.textContent = `${qty.description} ${qty.is_constant ? `[Constant = ${qty.constant_value} ${qty.constant_unit}]` : ''}`;
  } else {
    nameEl.textContent = `Symbol: ${clean}`;
    dimEl.textContent = `Dimension: [Custom Variable]`;
    descEl.textContent = `Physical parameter used in active equation derivation.`;
  }
}

/* ================= SYMBOLIC DERIVATION PIPELINE ================= */
function loadDerivePreset(key) {
  const target = document.getElementById('derive-target');
  const inTermsOf = document.getElementById('derive-in-terms-of');
  const startingEqs = document.getElementById('derive-equations');

  switch (key) {
    case 'ke_momentum':
      target.value = 'K';
      inTermsOf.value = 'p, m';
      startingEqs.value = 'kinetic_energy_def; linear_momentum_def';
      break;
    case 'escape_velocity':
      target.value = 'v';
      inTermsOf.value = 'G, M, r';
      startingEqs.value = '1/2 * m * v^2 = G * M * m / r';
      break;
    case 'power_ir':
      target.value = 'P';
      inTermsOf.value = 'I, R';
      startingEqs.value = 'electric_power_iv; ohm_law';
      break;
    case 'work_energy_calculus':
      target.value = 'W';
      inTermsOf.value = 'm, v_i, v_f';
      startingEqs.value = 'work_definition_force_dist; newton_second_law';
      break;
  }
  document.getElementById('btn-execute-derivation').click();
}

function initDerivationEngine() {
  const btn = document.getElementById('btn-execute-derivation');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const target = document.getElementById('derive-target').value.trim();
    const inTermsOfRaw = document.getElementById('derive-in-terms-of').value.trim();
    const startingEqsRaw = document.getElementById('derive-equations').value.trim();

    if (!target || !inTermsOfRaw) {
      alert('Please specify a target variable and allowed terms.');
      return;
    }

    const in_terms_of = inTermsOfRaw.split(',').map(s => s.trim()).filter(Boolean);
    const starting_equations = startingEqsRaw ? startingEqsRaw.split(';').map(s => s.trim()).filter(Boolean) : null;

    const emptyState = document.getElementById('derive-empty');
    const loadingState = document.getElementById('derive-loading-state');
    const contentStage = document.getElementById('derive-content-stage');
    const copyBtns = [document.getElementById('btn-copy-latex'), document.getElementById('btn-copy-md'), document.getElementById('btn-copy-python')];

    emptyState.classList.add('hidden');
    contentStage.classList.add('hidden');
    copyBtns.forEach(b => b?.classList.add('hidden'));
    loadingState.classList.remove('hidden');

    try {
      const res = await fetch('/api/derive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, in_terms_of, starting_equations })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Derivation failed');
      }

      const data = await res.json();
      currentDerivationResult = data;
      renderDerivationPipeline(data);
      copyBtns.forEach(b => b?.classList.remove('hidden'));
    } catch (e) {
      alert(`Derivation Error: ${e.message}`);
      emptyState.classList.remove('hidden');
    } finally {
      loadingState.classList.add('hidden');
    }
  });
}

function renderDerivationPipeline(data) {
  const contentStage = document.getElementById('derive-content-stage');
  const mathHero = document.getElementById('math-final-hero');
  const domainTag = document.getElementById('derive-domain-tag');
  const assumptionsChips = document.getElementById('derive-assumptions-chips');
  const dagContainer = document.getElementById('derive-dag-steps');

  // Hero Formula
  katex.render(data.final_latex, mathHero, { displayMode: true, throwOnError: false });

  // Domain Tag & Assumptions
  domainTag.textContent = `Target: ${data.target_variable} | Allowed: [${data.in_terms_of.join(', ')}]`;
  if (data.all_assumptions && data.all_assumptions.length > 0) {
    assumptionsChips.innerHTML = data.all_assumptions.map(a => `<span class="assumption-badge">• ${a}</span>`).join('');
  } else {
    assumptionsChips.innerHTML = '<span class="assumption-badge">• Universal Mathematical Rigor</span>';
  }

  // Render Step DAG Nodes
  dagContainer.innerHTML = '';
  data.steps.forEach(step => {
    const node = document.createElement('div');
    node.className = 'dag-node';
    node.innerHTML = `
      <div class="dag-node-header">
        <span class="step-order-badge">Step ${step.step_number}</span>
        <span class="step-op-title">${step.operation}</span>
      </div>
      <div class="dag-reasoning">${step.explanation}</div>
      <div class="dag-formula-box" id="dag-step-math-${step.step_number}"></div>
    `;

    // Interactive symbol hover inspector
    node.addEventListener('mouseenter', () => {
      if (step.substituted_symbol) {
        inspectSymbol(step.substituted_symbol);
      } else {
        inspectSymbol(data.target_variable);
      }
    });

    dagContainer.appendChild(node);
    katex.render(step.latex, node.querySelector(`#dag-step-math-${step.step_number}`), { displayMode: true, throwOnError: false });
  });

  contentStage.classList.remove('hidden');
  lucide.createIcons();
}

/* ================= DISCOVERY REACTOR ================= */
function setDiscoveryMode(mode) {
  currentSynthesisMode = mode;
  document.querySelectorAll('.reactor-mode').forEach(el => {
    el.classList.toggle('active', el.getAttribute('data-mode') === mode);
  });

  document.getElementById('reactor-dim-controls').classList.toggle('hidden', mode !== 'dimensional');
  document.getElementById('reactor-cross-controls').classList.toggle('hidden', mode !== 'cross_domain');
}

function toggleSynthChip(btn) {
  btn.classList.toggle('active');
  const activeChips = Array.from(document.querySelectorAll('#synthesis-chips-bank .const-chip.active'))
    .map(c => c.getAttribute('data-sym'));
  document.getElementById('reactor-custom-quantities').value = activeChips.join(', ');
}

function initDiscoveryReactor() {
  const btn = document.getElementById('btn-execute-discovery');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const stage = document.getElementById('discovery-stage');
    const emptyState = document.getElementById('discovery-empty-state');
    const countBadge = document.getElementById('discovery-count-badge');

    emptyState.classList.add('hidden');
    stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Synthesizing Dimensional Null-Space Matrix...</div></div>';
    stage.classList.remove('hidden');

    try {
      let payload = { mode: currentSynthesisMode };
      if (currentSynthesisMode === 'dimensional') {
        const qRaw = document.getElementById('reactor-custom-quantities').value;
        payload.quantities = qRaw.split(',').map(s => s.trim()).filter(Boolean);
        payload.target = document.getElementById('reactor-target-dim').value;
      } else {
        payload.domain1 = document.getElementById('cross-dom-1').value;
        payload.domain2 = document.getElementById('cross-dom-2').value;
      }

      const res = await fetch('/api/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Discovery failed');
      }

      const data = await res.json();
      countBadge.textContent = `${data.length} Invariants Found`;

      if (!data || data.length === 0) {
        stage.innerHTML = '<div class="canvas-empty-state"><p>No non-trivial scaling invariants could be formed with the selected quantities.</p></div>';
        return;
      }

      stage.innerHTML = '';
      data.forEach((item, idx) => {
        const card = document.createElement('div');
        card.className = 'disc-card';
        card.innerHTML = `
          <div>
            <div class="disc-card-title">${item.name}</div>
            <div class="disc-card-dim">${item.discovery_method} • Dim: ${item.dimension}</div>
            <div class="disc-card-math" id="disc-render-${idx}"></div>
            <p style="font-size: 0.8rem; color: var(--text-secondary);">${item.notes || ''}</p>
          </div>
          <button class="btn-sm-chip" style="margin-top: 1rem;" onclick="loadEquationToDerive('${item.formula}')">
            <i data-lucide="arrow-right"></i> Send to Derivator Canvas
          </button>
        `;
        stage.appendChild(card);
        katex.render(item.latex, card.querySelector(`#disc-render-${idx}`), { displayMode: true, throwOnError: false });
      });

      lucide.createIcons();
    } catch (e) {
      stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
    }
  });
}

/* ================= VERIFIER SUITE ================= */
function setVerifyField(eqStr) {
  document.getElementById('verify-equation-input').value = eqStr;
  document.getElementById('btn-execute-verify').click();
}

function initVerifierEngine() {
  const btn = document.getElementById('btn-execute-verify');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const eqStr = document.getElementById('verify-equation-input').value.trim();
    if (!eqStr) return;

    const empty = document.getElementById('verify-empty-state');
    const hudStage = document.getElementById('verify-hud-stage');
    const badge = document.getElementById('verify-hud-badge');

    try {
      const res = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ equation_str: eqStr })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Verification error');
      }

      const data = await res.json();
      empty.classList.add('hidden');
      hudStage.classList.remove('hidden');

      const isPass = data.overall_valid;
      badge.textContent = isPass ? '✔ AUDIT PASSED' : '⚠ AUDIT FAILED';
      badge.style.color = isPass ? 'var(--plasma-emerald)' : 'var(--plasma-crimson)';
      badge.style.borderColor = isPass ? 'var(--plasma-emerald)' : 'var(--plasma-crimson)';

      const hero = document.getElementById('audit-hero-card');
      hero.className = `audit-hero-card ${isPass ? 'pass' : 'fail'}`;
      document.getElementById('audit-hero-status').textContent = isPass ?
        'PHYSICAL EQUATION PASSED HOMOGENEITY & INVARIANCE AUDIT' :
        'PHYSICAL EQUATION FAILED CONSISTENCY AUDIT';
      
      katex.render(data.equation ? data.equation.latex : eqStr, document.getElementById('audit-hero-math'), { displayMode: true, throwOnError: false });

      // Pillars
      const dimPillar = document.getElementById('pillar-dim');
      dimPillar.className = `audit-pillar ${data.dimensional_check.valid ? 'pass' : 'fail'}`;
      document.getElementById('pillar-dim-status').textContent = data.dimensional_check.valid ? 'PASSED' : 'FAILED';
      document.getElementById('pillar-dim-detail').textContent = data.dimensional_check.message;

      const symPillar = document.getElementById('pillar-sym');
      symPillar.className = `audit-pillar ${data.symbolic_check.valid ? 'pass' : 'fail'}`;
      document.getElementById('pillar-sym-status').textContent = data.symbolic_check.valid ? 'PASSED' : 'UNVERIFIED';
      document.getElementById('pillar-sym-detail').textContent = data.symbolic_check.message;

      const numPillar = document.getElementById('pillar-num');
      numPillar.className = `audit-pillar ${data.numerical_check.valid ? 'pass' : 'fail'}`;
      document.getElementById('pillar-num-status').textContent = data.numerical_check.valid ? 'PASSED' : 'FAILED';
      document.getElementById('pillar-num-detail').textContent = data.numerical_check.message;

    } catch (e) {
      alert(`Verification Error: ${e.message}`);
    }
  });
}

/* ================= INTERACTIVE PHYSICS KNOWLEDGE GRAPH ================= */
function initPhysicsGraph() {
  renderPhysicsGraph();
}

function renderPhysicsGraph() {
  const svg = document.getElementById('physics-svg-graph');
  if (!svg || allEquations.length === 0) return;

  const width = svg.clientWidth || 800;
  const height = svg.clientHeight || 550;
  svg.innerHTML = '';

  // Core physics nodes
  const nodes = [
    { id: 'Energy', label: 'Energy (E, K, U)', x: width * 0.5, y: height * 0.35, color: '#00f2fe', r: 24 },
    { id: 'Momentum', label: 'Momentum (p)', x: width * 0.3, y: height * 0.55, color: '#4facfe', r: 20 },
    { id: 'Mass', label: 'Mass (m)', x: width * 0.35, y: height * 0.2, color: '#00df89', r: 18 },
    { id: 'Velocity', label: 'Velocity (v)', x: width * 0.2, y: height * 0.35, color: '#00f2fe', r: 18 },
    { id: 'Force', label: 'Force (F)', x: width * 0.15, y: height * 0.65, color: '#ffb703', r: 18 },
    { id: 'Spacetime', label: 'Light Speed (c)', x: width * 0.65, y: height * 0.25, color: '#a855f7', r: 20 },
    { id: 'Quantum', label: 'Planck (hbar)', x: width * 0.7, y: height * 0.5, color: '#a855f7', r: 20 },
    { id: 'Charge', label: 'Charge (q)', x: width * 0.5, y: height * 0.75, color: '#ffb703', r: 18 },
    { id: 'Thermodynamics', label: 'Temperature (T)', x: width * 0.8, y: height * 0.7, color: '#ff007a', r: 20 },
  ];

  const links = [
    { source: 'Mass', target: 'Momentum' },
    { source: 'Velocity', target: 'Momentum' },
    { source: 'Mass', target: 'Energy' },
    { source: 'Velocity', target: 'Energy' },
    { source: 'Momentum', target: 'Energy' },
    { source: 'Spacetime', target: 'Energy' },
    { source: 'Quantum', target: 'Energy' },
    { source: 'Force', target: 'Momentum' },
    { source: 'Charge', target: 'Force' },
    { source: 'Thermodynamics', target: 'Energy' },
  ];

  // Draw links
  links.forEach(l => {
    const s = nodes.find(n => n.id === l.source);
    const t = nodes.find(n => n.id === l.target);
    if (!s || !t) return;

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', s.x);
    line.setAttribute('y1', s.y);
    line.setAttribute('x2', t.x);
    line.setAttribute('y2', t.y);
    line.setAttribute('stroke', 'rgba(99, 102, 241, 0.35)');
    line.setAttribute('stroke-width', '1.8');
    svg.appendChild(line);
  });

  // Draw Nodes
  nodes.forEach(n => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.style.cursor = 'pointer';

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', n.x);
    circle.setAttribute('cy', n.y);
    circle.setAttribute('r', n.r);
    circle.setAttribute('fill', n.color);
    circle.setAttribute('fill-opacity', '0.2');
    circle.setAttribute('stroke', n.color);
    circle.setAttribute('stroke-width', '2');
    circle.style.filter = `drop-shadow(0 0 8px ${n.color})`;

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', n.x);
    text.setAttribute('y', n.y + n.r + 14);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('fill', '#f1f5f9');
    text.setAttribute('font-size', '11');
    text.setAttribute('font-family', 'Space Grotesk');
    text.textContent = n.label;

    g.appendChild(circle);
    g.appendChild(text);

    g.addEventListener('click', () => {
      inspectSymbol(n.id);
      switchView('catalog');
      const searchInput = document.getElementById('catalog-search-input');
      if (searchInput) {
        searchInput.value = n.id;
        renderCatalogCards();
      }
    });

    svg.appendChild(g);
  });
}

/* ================= CATALOG & ONTOLOGY ================= */
async function fetchEquations() {
  try {
    const res = await fetch('/api/equations');
    allEquations = await res.json();
    document.getElementById('stat-eq-count').textContent = allEquations.length;
    renderCatalogCards();
  } catch (e) {
    console.error('Failed to load equations:', e);
  }
}

function filterCatalogDomain(dom) {
  activeCatalogDomain = dom;
  document.querySelectorAll('#catalog-domain-pills .dom-pill').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-dom') === dom);
  });
  renderCatalogCards();
}

function onCatalogSearch() {
  renderCatalogCards();
}

function renderCatalogCards() {
  const query = (document.getElementById('catalog-search-input')?.value || '').toLowerCase();
  const grid = document.getElementById('catalog-cards-grid');
  if (!grid) return;

  const filtered = allEquations.filter(eq => {
    const matchesDomain = activeCatalogDomain === 'all' || eq.domain.toLowerCase() === activeCatalogDomain.toLowerCase();
    const matchesQuery = !query ||
      eq.name.toLowerCase().includes(query) ||
      eq.raw_str.toLowerCase().includes(query) ||
      eq.id.toLowerCase().includes(query) ||
      (eq.tags && eq.tags.some(t => t.toLowerCase().includes(query)));
    return matchesDomain && matchesQuery;
  });

  grid.innerHTML = '';
  filtered.forEach(eq => {
    const card = document.createElement('div');
    card.className = 'catalog-item-card';
    card.innerHTML = `
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
          <span class="pod-badge">${eq.domain}</span>
          <span style="font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono);">${eq.id}</span>
        </div>
        <h4 style="font-size: 1rem; color: #fff; margin-bottom: 0.6rem;">${eq.name}</h4>
        <div style="background: rgba(6, 9, 18, 0.85); padding: 0.75rem; border-radius: var(--radius-sm); margin-bottom: 0.8rem; text-align: center; font-size: 1.1rem;" id="cat-math-${eq.id}"></div>
        <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4;">${eq.description || ''}</p>
      </div>
      <button class="btn-sm-chip" style="margin-top: 1rem;" onclick="loadEquationToDerive('${eq.id}')">
        <i data-lucide="play"></i> Use in Derivation Canvas
      </button>
    `;
    grid.appendChild(card);
    katex.render(eq.latex, card.querySelector(`#cat-math-${eq.id}`), { displayMode: true, throwOnError: false });
  });

  lucide.createIcons();
}

function loadEquationToDerive(eqIdOrFormula) {
  switchView('derivator');
  document.getElementById('derive-equations').value = eqIdOrFormula;
}

async function fetchQuantities() {
  try {
    const res = await fetch('/api/quantities');
    allQuantities = await res.json();
    renderOntologyTable();
  } catch (e) {
    console.error('Failed to load quantities:', e);
  }
}

function onOntologySearch() {
  renderOntologyTable();
}

function renderOntologyTable() {
  const query = (document.getElementById('ontology-search')?.value || '').toLowerCase();
  const tbody = document.getElementById('ontology-table-body');
  if (!tbody) return;

  const filtered = allQuantities.filter(q =>
    !query ||
    q.name.toLowerCase().includes(query) ||
    q.symbol.toLowerCase().includes(query) ||
    q.dimension.toLowerCase().includes(query) ||
    (q.aliases && q.aliases.some(a => a.toLowerCase().includes(query)))
  );

  tbody.innerHTML = filtered.map(q => `
    <tr style="cursor: pointer;" onclick="inspectSymbol('${q.symbol}')">
      <td><strong>${q.name}</strong><br><small style="color: var(--text-muted);">${q.description}</small></td>
      <td><span class="pod-badge" style="background: rgba(0, 242, 254, 0.12); color: var(--plasma-cyan);">${q.symbol}</span></td>
      <td><code style="color: var(--plasma-violet);">${q.dimension}</code></td>
      <td style="color: var(--text-secondary);">${q.aliases.join(', ') || '—'}</td>
      <td style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--plasma-amber);">${q.is_constant ? `${q.constant_value.toExponential(3)} ${q.constant_unit || ''}` : '—'}</td>
      <td><span class="assumption-badge">${q.domains[0] || 'Physics'}</span></td>
    </tr>
  `).join('');
}

/* ================= VARIATIONAL MECHANICS & TENSORS ================= */
let selectedTensorMetric = 'schwarzschild';

function loadVariationalPreset(key) {
  const lagInput = document.getElementById('var-lagrangian-input');
  const coordsInput = document.getElementById('var-coords-input');
  if (key === 'pendulum') {
    lagInput.value = '1/2 * m * L^2 * theta_dot^2 - m * g * L * (1 - cos(theta))';
    coordsInput.value = 'theta';
  } else if (key === 'harmonic') {
    lagInput.value = '1/2 * m * x_dot^2 - 1/2 * k * x^2';
    coordsInput.value = 'x';
  } else if (key === 'free_2d') {
    lagInput.value = '1/2 * m * (x_dot^2 + y_dot^2)';
    coordsInput.value = 'x, y';
  }
  executeVariationalDerivation();
}

async function executeVariationalDerivation() {
  const lag = document.getElementById('var-lagrangian-input').value.trim();
  const coordsRaw = document.getElementById('var-coords-input').value.trim();
  if (!lag || !coordsRaw) return;

  const coordinates = coordsRaw.split(',').map(s => s.trim()).filter(Boolean);
  const emptyState = document.getElementById('var-empty-state');
  const stage = document.getElementById('var-content-stage');

  emptyState.classList.add('hidden');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Euler-Lagrange & Hamiltonian Mechanics...</div></div>';
  stage.classList.remove('hidden');

  try {
    const res = await fetch('/api/lagrangian', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lagrangian: lag, coordinates, system_name: 'Variational System' })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
    const data = await res.json();

    let html = `
      <div class="derived-banner">
        <div class="derived-banner-header">
          <div class="verified-tag"><i data-lucide="orbit"></i> EULER-LAGRANGE EQUATIONS OF MOTION</div>
          <div class="tag-domain">${data.system_name}</div>
        </div>
        <div class="math-hero" id="var-hero-lag"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
    `;

    data.euler_lagrange_equations.forEach((eq, idx) => {
      html += `
        <div class="dag-node">
          <div class="dag-node-header">
            <span class="step-order-badge">Coordinate $${eq.coord}$</span>
            <span class="step-op-title">Equation of Motion & Acceleration</span>
          </div>
          <div class="dag-formula-box" id="var-el-eq-${idx}"></div>
          ${eq.acceleration_latex ? `<div class="dag-formula-box" style="margin-top: 0.5rem; border-left-color: var(--plasma-violet);" id="var-accel-${idx}"></div>` : ''}
        </div>
      `;
    });

    if (data.hamiltonian) {
      html += `
        <div class="dag-node">
          <div class="dag-node-header">
            <span class="step-order-badge">Hamiltonian</span>
            <span class="step-op-title">Legendre Invariant $\\mathcal{H}$</span>
          </div>
          <div class="dag-formula-box" id="var-ham-math"></div>
        </div>
      `;
    }

    if (data.noether_conserved_quantities && data.noether_conserved_quantities.length > 0) {
      html += `
        <div class="assumptions-chip-box">
          <div class="box-title"><i data-lucide="shield-check"></i> Noether Conserved Invariants:</div>
          <div class="chips-flex">
            ${data.noether_conserved_quantities.map(c => `<span class="assumption-badge">✔ ${c.symmetry} &implies; <strong>$${c.invariant_symbol}$ is Constant</strong></span>`).join('')}
          </div>
        </div>
      `;
    }

    html += '</div></div>';
    stage.innerHTML = html;

    katex.render(`\\mathcal{L} = ${data.lagrangian_latex}`, document.getElementById('var-hero-lag'), { displayMode: true, throwOnError: false });
    data.euler_lagrange_equations.forEach((eq, idx) => {
      katex.render(eq.equation_latex, document.getElementById(`var-el-eq-${idx}`), { displayMode: true, throwOnError: false });
      if (eq.acceleration_latex) {
        katex.render(`\\ddot{${eq.coord}} = ${eq.acceleration_latex}`, document.getElementById(`var-accel-${idx}`), { displayMode: true, throwOnError: false });
      }
    });
    if (data.hamiltonian) {
      katex.render(`\\mathcal{H} = ${data.hamiltonian.hamiltonian_latex}`, document.getElementById('var-ham-math'), { displayMode: true, throwOnError: false });
    }

    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

function selectTensorMetric(metricKey) {
  selectedTensorMetric = metricKey;
  document.querySelectorAll('#view-tensors .reactor-mode').forEach(m => {
    m.classList.toggle('active', m.getAttribute('data-metric') === metricKey);
  });
  executeTensorCurvature();
}

async function executeTensorCurvature() {
  const emptyState = document.getElementById('tensor-empty-state');
  const stage = document.getElementById('tensor-content-stage');

  emptyState.classList.add('hidden');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Riemann, Ricci & Einstein Spacetime Tensors...</div></div>';
  stage.classList.remove('hidden');

  try {
    const res = await fetch('/api/tensors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metric: selectedTensorMetric })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
    const data = await res.json();

    let html = `
      <div class="derived-banner">
        <div class="derived-banner-header">
          <div class="verified-tag"><i data-lucide="disc"></i> ${data.is_vacuum_solution ? 'EINSTEIN VACUUM SOLUTION (G_{\\mu\\nu} = 0)' : 'CURVED SPACETIME METRIC'}</div>
          <div class="tag-domain">${data.metric_name}</div>
        </div>
        <div class="math-hero" id="tensor-hero-metric"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
        <div class="dag-node">
          <div class="dag-node-header">
            <span class="step-order-badge">Curvature</span>
            <span class="step-op-title">Ricci Scalar Invariant $R$</span>
          </div>
          <div class="dag-formula-box" id="tensor-ricci-scalar"></div>
        </div>
        <div class="dag-node">
          <div class="dag-node-header">
            <span class="step-order-badge">Einstein Tensor</span>
            <span class="step-op-title">Field Equation Tensor $G_{\\mu\\nu}$</span>
          </div>
          <div class="dag-formula-box" id="tensor-einstein-mat"></div>
        </div>
      </div></div>
    `;

    stage.innerHTML = html;
    katex.render(`g_{\\mu\\nu} = ${data.metric_latex}`, document.getElementById('tensor-hero-metric'), { displayMode: true, throwOnError: false });
    katex.render(`R = ${data.ricci_scalar_latex}`, document.getElementById('tensor-ricci-scalar'), { displayMode: true, throwOnError: false });
    katex.render(`G_{\\mu\\nu} = ${data.einstein_tensor_latex}`, document.getElementById('tensor-einstein-mat'), { displayMode: true, throwOnError: false });

    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

/* ================= NUMERICAL SIMULATION & CANVASES ================= */
let simAnimationId = null;
let simIsPlaying = true;
let simCurrentFrame = 0;
let simTrajectoryData = null;

function onSimModeChange() {
  const mode = document.getElementById('sim-mode-select').value;
  document.getElementById('sim-block-classical').classList.toggle('hidden', mode !== 'phase_portrait');
  document.getElementById('sim-block-quantum').classList.toggle('hidden', mode !== 'quantum');
  document.getElementById('sim-block-relativity').classList.toggle('hidden', mode !== 'relativity');
}

function loadSimPreset(presetKey) {
  const modeSelect = document.getElementById('sim-mode-select');
  if (presetKey === 'pendulum') {
    modeSelect.value = 'phase_portrait';
    document.getElementById('sim-accel-input').value = '-9.81 * sin(theta)';
    document.getElementById('sim-q0-input').value = '1.5';
    document.getElementById('sim-v0-input').value = '0.0';
  } else if (presetKey === 'harmonic') {
    modeSelect.value = 'phase_portrait';
    document.getElementById('sim-accel-input').value = '-4.0 * x';
    document.getElementById('sim-q0-input').value = '1.0';
    document.getElementById('sim-v0-input').value = '0.0';
  } else if (presetKey === 'duffing') {
    modeSelect.value = 'phase_portrait';
    document.getElementById('sim-accel-input').value = '-0.2*v - 1.0*x - 1.0*x^3 + 2.0*cos(1.2*t)';
    document.getElementById('sim-q0-input').value = '1.0';
    document.getElementById('sim-v0-input').value = '0.0';
  } else if (presetKey === 'quantum_barrier') {
    modeSelect.value = 'quantum';
    document.getElementById('sim-quantum-potential-input').value = '4.0 * (abs(x) < 0.5)';
    document.getElementById('sim-quantum-p0').value = '3.0';
    document.getElementById('sim-quantum-sigma').value = '0.5';
  } else if (presetKey === 'quantum_well') {
    modeSelect.value = 'quantum';
    document.getElementById('sim-quantum-potential-input').value = '0.5 * x^2';
    document.getElementById('sim-quantum-p0').value = '0.0';
    document.getElementById('sim-quantum-sigma').value = '0.7';
  } else if (presetKey === 'orbit_bound') {
    modeSelect.value = 'relativity';
    document.getElementById('sim-rel-M').value = '1.0';
    document.getElementById('sim-rel-r0').value = '12.0';
    document.getElementById('sim-rel-vphi').value = '0.28';
  } else if (presetKey === 'orbit_photon') {
    modeSelect.value = 'relativity';
    document.getElementById('sim-rel-M').value = '1.0';
    document.getElementById('sim-rel-r0').value = '20.0';
    document.getElementById('sim-rel-vphi').value = '6.0';
  }
  onSimModeChange();
  executeSimulation();
}

async function executeSimulation() {
  if (simAnimationId) cancelAnimationFrame(simAnimationId);

  const canvas = document.getElementById('sim-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const mode = document.getElementById('sim-mode-select').value;

  if (mode === 'quantum') {
    const pot = document.getElementById('sim-quantum-potential-input').value;
    const p0 = parseFloat(document.getElementById('sim-quantum-p0').value) || 3.0;
    const sig = parseFloat(document.getElementById('sim-quantum-sigma').value) || 0.5;

    try {
      const res = await fetch('/api/sim/quantum-wave', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          custom_potential_expr: pot,
          p0: p0,
          sigma: sig
        })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Quantum simulation error');
      const data = await res.json();
      renderQuantumWaveFrames(data);
    } catch (e) {
      alert('Quantum Sim Error: ' + e.message);
    }
    return;
  }

  if (mode === 'relativity') {
    const M = parseFloat(document.getElementById('sim-rel-M').value) || 1.0;
    const r0 = parseFloat(document.getElementById('sim-rel-r0').value) || 12.0;
    const vphi = parseFloat(document.getElementById('sim-rel-vphi').value) || 0.28;
    const isPhoton = r0 > 15.0;

    try {
      const res = await fetch('/api/sim/relativity-orbit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: isPhoton ? 'photon' : 'particle',
          M: M,
          r0: r0,
          v_phi0: vphi,
          impact_parameter_b: vphi
        })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Relativity simulation error');
      const data = await res.json();
      renderOrbitTrajectory(data);
    } catch (e) {
      alert('Relativistic Orbit Error: ' + e.message);
    }
    return;
  }

  // Standard numerical simulation & phase portrait
  const accel = document.getElementById('sim-accel-input').value;
  const q0 = parseFloat(document.getElementById('sim-q0-input').value) || 1.0;
  const v0 = parseFloat(document.getElementById('sim-v0-input').value) || 0.0;

  try {
    const res = await fetch('/api/sim/phase-portrait', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        accel_expr: accel,
        coord_name: accel.includes('x') ? 'x' : 'theta',
        q0: q0,
        v0: v0,
        t_end: 10.0,
        dt: 0.02
      })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
    const data = await res.json();
    simTrajectoryData = data;
    simCurrentFrame = 0;
    simIsPlaying = true;
    animatePhaseSpace(data);
  } catch (e) {
    alert('Simulation Error: ' + e.message);
  }
}

function animatePhaseSpace(data) {
  const canvas = document.getElementById('sim-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  const trajQ = data.q_values || [];
  const trajV = data.p_values || [];
  const totalPoints = trajQ.length;

  function draw() {
    ctx.fillStyle = 'rgba(6, 9, 18, 0.25)';
    ctx.fillRect(0, 0, w, h);

    // Draw Vector Field arrows
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.2)';
    ctx.lineWidth = 1;
    if (data.grid_q && data.grid_p) {
      const qGrid = data.grid_q;
      const vGrid = data.grid_p;
      const dq = data.grid_dq;
      const dv = data.grid_dp;

      for (let i = 0; i < qGrid.length; i += 2) {
        for (let j = 0; j < vGrid.length; j += 2) {
          const cx = w / 2 + qGrid[i] * 50;
          const cy = h / 2 - vGrid[j] * 35;
          const u = (dq[j] ? dq[j][i] : 0) * 0.08;
          const v = (dv[j] ? dv[j][i] : 0) * 0.08;
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(cx + u, cy - v);
          ctx.stroke();
        }
      }
    }

    // Draw full trajectory path
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(0, 242, 254, 0.4)';
    ctx.lineWidth = 2;
    for (let i = 0; i <= simCurrentFrame && i < trajQ.length; i++) {
      const px = w / 2 + trajQ[i] * 65;
      const py = h / 2 - trajV[i] * 40;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    // Draw current particle head
    if (simCurrentFrame < trajQ.length) {
      const px = w / 2 + trajQ[simCurrentFrame] * 65;
      const py = h / 2 - trajV[simCurrentFrame] * 40;
      ctx.beginPath();
      ctx.arc(px, py, 6, 0, 2 * Math.PI);
      ctx.fillStyle = '#00f2fe';
      ctx.shadowColor = '#00f2fe';
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Update HUD
      document.getElementById('sim-hud-time').textContent = `Step ${simCurrentFrame + 1}/${totalPoints}`;
      document.getElementById('sim-hud-pos').textContent = trajQ[simCurrentFrame].toFixed(3);
      document.getElementById('sim-hud-vel').textContent = trajV[simCurrentFrame].toFixed(3);
    }

    if (simIsPlaying) {
      simCurrentFrame = (simCurrentFrame + 1) % trajQ.length;
    }
    simAnimationId = requestAnimationFrame(draw);
  }

  draw();
}

function renderQuantumWaveFrames(data) {
  const canvas = document.getElementById('sim-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const xVals = data.x;
  const probFrames = data.probability_density_history;
  let frameIdx = 0;

  function drawWave() {
    ctx.fillStyle = 'rgba(6, 9, 18, 0.2)';
    ctx.fillRect(0, 0, w, h);

    // Draw Potential Barrier
    ctx.fillStyle = 'rgba(255, 65, 108, 0.25)';
    ctx.fillRect(w / 2 - 15, h / 2 - 80, 30, 80);

    const probs = probFrames[frameIdx];
    ctx.beginPath();
    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 2.5;
    for (let i = 0; i < xVals.length; i++) {
      const cx = (xVals[i] + 8) / 16 * w;
      const cy = h / 2 + 50 - probs[i] * 120;
      if (i === 0) ctx.moveTo(cx, cy);
      else ctx.lineTo(cx, cy);
    }
    ctx.stroke();

    document.getElementById('sim-hud-time').textContent = `Frame ${frameIdx + 1}/${probFrames.length}`;
    document.getElementById('sim-hud-pos').textContent = `T = ${(data.transmission_coefficient * 100).toFixed(1)}%`;
    document.getElementById('sim-hud-vel').textContent = `R = ${(data.reflection_coefficient * 100).toFixed(1)}%`;

    if (simIsPlaying) {
      frameIdx = (frameIdx + 1) % probFrames.length;
    }
    simAnimationId = requestAnimationFrame(drawWave);
  }

  drawWave();
}

function renderOrbitTrajectory(data) {
  const canvas = document.getElementById('sim-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const xs = data.x_cartesian || [];
  const ys = data.y_cartesian || [];
  let idx = 0;

  function drawOrbit() {
    ctx.fillStyle = 'rgba(6, 9, 18, 0.2)';
    ctx.fillRect(0, 0, w, h);

    // Black Hole Event Horizon r = 2M
    ctx.beginPath();
    ctx.arc(w / 2, h / 2, 16, 0, 2 * Math.PI);
    ctx.fillStyle = '#000000';
    ctx.strokeStyle = '#ffb703';
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    // Orbit path
    ctx.beginPath();
    ctx.strokeStyle = '#a855f7';
    ctx.lineWidth = 2;
    for (let i = 0; i <= idx && i < xs.length; i++) {
      const px = w / 2 + xs[i] * 12;
      const py = h / 2 - ys[i] * 12;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.stroke();

    if (idx < xs.length) {
      const px = w / 2 + xs[idx] * 12;
      const py = h / 2 - ys[idx] * 12;
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, 2 * Math.PI);
      ctx.fillStyle = '#00f2fe';
      ctx.fill();
    }

    if (simIsPlaying) {
      idx = (idx + 1) % xs.length;
    }
    simAnimationId = requestAnimationFrame(drawOrbit);
  }

  drawOrbit();
}

function toggleSimPlayPause() {
  simIsPlaying = !simIsPlaying;
  const btn = document.getElementById('btn-sim-play-pause');
  btn.innerHTML = simIsPlaying ? '<i data-lucide="pause"></i> Pause' : '<i data-lucide="play"></i> Play';
  lucide.createIcons();
}

function resetSimCanvas() {
  simCurrentFrame = 0;
}

/* ================= QFT & FEYNMAN LAB ================= */
function onQFTModeChange() {
  const mode = document.getElementById('qft-mode-select').value;
  document.getElementById('qft-block-trace').classList.toggle('hidden', mode !== 'custom_trace');
  document.getElementById('qft-block-hamiltonian').classList.toggle('hidden', mode !== 'dirac_hamiltonian');
  document.getElementById('qft-block-scattering').classList.toggle('hidden', mode !== 'scattering');
}

function loadQFTPreset(presetKey) {
  const modeSelect = document.getElementById('qft-mode-select');
  if (presetKey === 'trace_4g') {
    modeSelect.value = 'custom_trace';
    document.getElementById('qft-custom-expr').value = 'gamma0 * gamma1 * gamma0 * gamma1';
  } else if (presetKey === 'trace_g5') {
    modeSelect.value = 'custom_trace';
    document.getElementById('qft-custom-expr').value = 'gamma5 * gamma0 * gamma1 * gamma2 * gamma3';
  } else if (presetKey === 'dirac_hamiltonian') {
    modeSelect.value = 'dirac_hamiltonian';
    document.getElementById('qft-mass-input').value = '0.511';
    document.getElementById('qft-momentum-input').value = '1.0, 0.0, 0.0';
  } else if (presetKey === 'ee_to_mumu') {
    modeSelect.value = 'scattering';
    document.getElementById('qft-scattering-select').value = 'ee_to_mumu';
  } else if (presetKey === 'compton') {
    modeSelect.value = 'scattering';
    document.getElementById('qft-scattering-select').value = 'compton';
  }
  onQFTModeChange();
  executeQFTEval();
}

async function executeQFTEval() {
  const emptyState = document.getElementById('qft-empty-state');
  const stage = document.getElementById('qft-content-stage');
  emptyState.classList.add('hidden');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Exact Quantum Field Theory Invariants & Traces...</div></div>';
  stage.classList.remove('hidden');

  const mode = document.getElementById('qft-mode-select').value;

  try {
    if (mode === 'custom_trace') {
      const expr = document.getElementById('qft-custom-expr').value;
      const res = await fetch('/api/qft/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'gamma_trace', expression: expr, compute_trace: true })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
      const data = await res.json();
      stage.innerHTML = `
        <div class="derived-banner">
          <div class="verified-tag"><i data-lucide="shield"></i> DIRAC MATRIX TRACE EVALUATOR</div>
          <div class="tag-domain">Input: ${data.input_expression}</div>
        </div>
        <div class="dag-container"><div class="dag-steps">
          <div class="dag-node">
            <div class="dag-node-header"><span class="step-op-title">Exact Trace $\\operatorname{Tr}(M)$</span></div>
            <div class="dag-formula-box" id="qft-res-trace"></div>
          </div>
        </div></div>
      `;
      katex.render(`\\operatorname{Tr}\\left(${data.input_expression}\\right) = ${data.evaluated_result_latex}`, document.getElementById('qft-res-trace'), { displayMode: true, throwOnError: false });
    } else if (mode === 'dirac_hamiltonian') {
      const m = parseFloat(document.getElementById('qft-mass-input').value) || 0.511;
      const pParts = document.getElementById('qft-momentum-input').value.split(',').map(x => parseFloat(x.trim()) || 0);
      const res = await fetch('/api/qft/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: 'dirac_hamiltonian',
          mass: m,
          px: pParts[0] || 1.0,
          py: pParts[1] || 0.0,
          pz: pParts[2] || 0.0
        })
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
      const data = await res.json();
      stage.innerHTML = `
        <div class="derived-banner">
          <div class="verified-tag"><i data-lucide="activity"></i> RELATIVISTIC DISPERSION $E = \\pm\\sqrt{p^2 + m^2}$</div>
          <div class="tag-domain">Mass: ${m} | Momenta: (${pParts.join(', ')})</div>
        </div>
        <div class="dag-container"><div class="dag-steps">
          <div class="dag-node">
            <div class="dag-node-header"><span class="step-op-title">Energy Eigenvalues</span></div>
            <div class="dag-formula-box" id="qft-res-eigs"></div>
          </div>
        </div></div>
      `;
      katex.render(data.evaluated_result_latex, document.getElementById('qft-res-eigs'), { displayMode: true, throwOnError: false });
    } else {
      const proc = document.getElementById('qft-scattering-select').value;
      const res = await fetch('/api/qft/feynman', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ process: proc })
      });
      const data = await res.json();
      stage.innerHTML = `
        <div class="derived-banner">
          <div class="derived-banner-header">
            <div class="verified-tag"><i data-lucide="sparkles"></i> ${data.process_name}</div>
            <div class="tag-domain">${data.channel}</div>
          </div>
          <div style="margin-top: 1rem;">${data.svg_diagram || ''}</div>
        </div>
        <div class="dag-container"><div class="dag-steps">
          <div class="dag-node">
            <div class="dag-node-header"><span class="step-order-badge">Amplitude</span><span class="step-op-title">Feynman Matrix Element $\\mathcal{M}$</span></div>
            <div class="dag-formula-box" id="qft-matrix-elem"></div>
          </div>
          <div class="dag-node">
            <div class="dag-node-header"><span class="step-order-badge">Cross Section</span><span class="step-op-title">Unpolarized Squared Amplitude $|\\overline{\\mathcal{M}}|^2$</span></div>
            <div class="dag-formula-box" id="qft-sq-matrix"></div>
          </div>
          <div class="dag-node">
            <div class="dag-node-header"><span class="step-order-badge">Differential</span><span class="step-op-title">Differential Cross Section $\\frac{d\\sigma}{d\\Omega}$</span></div>
            <div class="dag-formula-box" id="qft-diff-sigma"></div>
          </div>
        </div></div>
      `;
      katex.render(data.matrix_element_latex, document.getElementById('qft-matrix-elem'), { displayMode: true, throwOnError: false });
      katex.render(data.squared_matrix_element_unpolarized_latex, document.getElementById('qft-sq-matrix'), { displayMode: true, throwOnError: false });
      katex.render(data.differential_cross_section_latex, document.getElementById('qft-diff-sigma'), { displayMode: true, throwOnError: false });
    }
    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

/* ================= DIFFERENTIAL FORMS ================= */
function onFormsOpChange() {
  const op = document.getElementById('forms-op-select').value;
  document.getElementById('forms-form2-container').style.display = (op === 'wedge') ? 'block' : 'none';
}

function loadFormsPreset(presetKey) {
  const coords = document.getElementById('forms-coords-input');
  const f1 = document.getElementById('forms-form1-input');
  const op = document.getElementById('forms-op-select');
  const f2 = document.getElementById('forms-form2-input');

  if (presetKey === 'maxwell_d') {
    coords.value = 't, x, y, z';
    f1.value = '-phi*dt + Ax*dx + Ay*dy + Az*dz';
    op.value = 'd';
  } else if (presetKey === 'curl_form') {
    coords.value = 'x, y, z';
    f1.value = 'y*dx - x*dy';
    op.value = 'd';
  } else if (presetKey === 'symplectic') {
    coords.value = 'q, p';
    f1.value = 'dp';
    op.value = 'wedge';
    f2.value = 'dq';
  } else if (presetKey === 'hodge_3d') {
    coords.value = 'x, y, z';
    f1.value = 'dx^dy';
    op.value = 'star';
  }
  onFormsOpChange();
  executeCustomFormEval();
}

async function executeCustomFormEval() {
  const stage = document.getElementById('forms-content-stage');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Exterior Derivatives & Hodge Duals...</div></div>';

  const coords = document.getElementById('forms-coords-input').value.split(',').map(x => x.trim()).filter(x => x);
  const f1 = document.getElementById('forms-form1-input').value;
  const op = document.getElementById('forms-op-select').value;
  const f2 = document.getElementById('forms-form2-input').value;

  try {
    const res = await fetch('/api/geometry/custom-form', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operation: op,
        form1: f1,
        coordinates: coords,
        form2: op === 'wedge' ? f2 : null
      })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
    const data = await res.json();

    stage.innerHTML = `
      <div class="derived-banner">
        <div class="verified-tag"><i data-lucide="triangle"></i> RESULT: ${data.result_degree}-FORM</div>
        <div class="math-hero" id="forms-hero-math"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-op-title">Operation Result $\\Omega$</span></div>
          <div class="dag-formula-box" id="forms-box-res"></div>
        </div>
      </div></div>
    `;
    katex.render(`\\Omega = ${data.result_form_latex}`, document.getElementById('forms-hero-math'), { displayMode: true, throwOnError: false });
    katex.render(`\\text{Input: } \\omega = ${data.input_form_latex} \\implies \\Omega = ${data.result_form_latex}`, document.getElementById('forms-box-res'), { displayMode: true, throwOnError: false });
    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

/* ================= SYMMETRIES & LIE ALGEBRAS ================= */
function loadSymPreset(presetKey) {
  const mats = document.getElementById('sym-matrices-input');
  const title = document.getElementById('sym-name-input');

  if (presetKey === 'su2') {
    mats.value = '[[0, 1/2], [1/2, 0]]; [[0, -I/2], [I/2, 0]]; [[1/2, 0], [0, -1/2]]';
    title.value = 'SU(2) Pauli Spin-1/2 Algebra';
  } else if (presetKey === 'so3') {
    mats.value = '[[0, 0, 0], [0, 0, -1], [0, 1, 0]]; [[0, 0, 1], [0, 0, 0], [-1, 0, 0]]; [[0, -1, 0], [1, 0, 0], [0, 0, 0]]';
    title.value = 'SO(3) 3D Rotational Generators';
  } else if (presetKey === 'su3') {
    mats.value = '[[0, 1, 0], [1, 0, 0], [0, 0, 0]]; [[0, -I, 0], [I, 0, 0], [0, 0, 0]]; [[1, 0, 0], [0, -1, 0], [0, 0, 0]]; [[0, 0, 1], [0, 0, 0], [1, 0, 0]]';
    title.value = 'SU(3) Color Gell-Mann Generators';
  } else if (presetKey === 'higgs') {
    selectSymmetryPresetStandard('higgs');
    return;
  }
  executeCustomSymmetryEval();
}

async function selectSymmetryPresetStandard(modeKey) {
  const stage = document.getElementById('sym-content-stage');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Gauge Group SSB & Masses...</div></div>';
  try {
    const res = await fetch('/api/symmetry/eval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: modeKey })
    });
    const data = await res.json();
    stage.innerHTML = `
      <div class="derived-banner">
        <div class="verified-tag"><i data-lucide="shield-check"></i> HIGGS SSB: SU(2) x U(1) -> U(1)</div>
        <div class="math-hero" id="sym-hero-math"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-op-title">Gauge Boson Mass Spectrum</span></div>
          <div class="dag-formula-box" id="sym-box-1"></div>
        </div>
      </div></div>
    `;
    katex.render(data.covariant_derivative_latex || 'D_\\mu', document.getElementById('sym-hero-math'), { displayMode: true, throwOnError: false });
    katex.render(`M_W = \\frac{1}{2} g v, \\quad M_Z = \\frac{1}{2}\\sqrt{g^2+g'^2} v, \\quad M_\\gamma = 0`, document.getElementById('sym-box-1'), { displayMode: true, throwOnError: false });
    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

async function executeCustomSymmetryEval() {
  const stage = document.getElementById('sym-content-stage');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Lie Commutator Tables & Casimir Invariants...</div></div>';

  const mats = document.getElementById('sym-matrices-input').value;
  const name = document.getElementById('sym-name-input').value;

  try {
    const res = await fetch('/api/symmetry/custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ generators: mats, algebra_name: name })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
    const data = await res.json();

    stage.innerHTML = `
      <div class="derived-banner">
        <div class="verified-tag"><i data-lucide="network"></i> ${data.algebra_name} (Dim ${data.dimension})</div>
        <div class="math-hero" id="sym-hero-math"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-op-title">Quadratic Casimir Invariant $C_2 = \\sum T_a^2$</span></div>
          <div class="dag-formula-box" id="sym-box-casimir"></div>
        </div>
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-op-title">Commutators & Jacobi Identity Check</span></div>
          <div class="dag-formula-box" id="sym-box-comm"></div>
        </div>
      </div></div>
    `;
    katex.render(`C_2 = ${data.casimir_operator_latex}`, document.getElementById('sym-hero-math'), { displayMode: true, throwOnError: false });
    katex.render(`C_2 = ${data.casimir_operator_latex}`, document.getElementById('sym-box-casimir'), { displayMode: true, throwOnError: false });

    const firstComm = Object.entries(data.commutator_table_latex)[0];
    const commStr = firstComm ? `${firstComm[0]} = ${firstComm[1]}` : '\\text{Commutators Verified}';
    katex.render(`\\text{Jacobi Identity: } ${data.is_jacobi_identity_satisfied ? '\\text{True}' : '\\text{False}'} \\quad | \\quad ${commStr}`, document.getElementById('sym-box-comm'), { displayMode: true, throwOnError: false });
    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

/* ================= STATISTICAL MECHANICS ================= */
function loadStatPreset(presetKey) {
  const partInput = document.getElementById('stat-partition-input');
  const titleInput = document.getElementById('stat-name-input');

  if (presetKey === 'ideal_gas') {
    partInput.value = '(V / h^3) * (2*pi*m*k_B*T)^(3/2)';
    titleInput.value = 'Classical Monatomic Ideal Gas (Sackur-Tetrode)';
  } else if (presetKey === 'paramagnet') {
    partInput.value = '2 * cosh(mu_B * B / (k_B * T))^N';
    titleInput.value = 'Paramagnet in Magnetic Field (Curie Law)';
  } else if (presetKey === 'quantum_oscillator') {
    partInput.value = 'exp(-hbar*omega / (2*k_B*T)) / (1 - exp(-hbar*omega / (k_B*T)))';
    titleInput.value = 'Quantum Harmonic Oscillator (Einstein Solid)';
  } else if (presetKey === 'two_level') {
    partInput.value = '1 + exp(-epsilon / (k_B * T))';
    titleInput.value = 'Two-Level Quantum System';
  } else if (presetKey === 'distributions') {
    selectStatPresetStandard('distributions');
    return;
  }
  executeCustomStatMechEval();
}

async function selectStatPresetStandard(modeKey) {
  const stage = document.getElementById('stat-content-stage');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Evaluating Quantum Distributions & Planck Law...</div></div>';
  try {
    const res = await fetch('/api/statmech/eval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: modeKey })
    });
    const data = await res.json();
    stage.innerHTML = `
      <div class="derived-banner">
        <div class="verified-tag"><i data-lucide="bar-chart-2"></i> ${data.distribution_name}</div>
        <div class="math-hero" id="stat-hero-math"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-op-title">Planck Blackbody Radiation Spectrum</span></div>
          <div class="dag-formula-box" id="stat-box-planck"></div>
        </div>
      </div></div>
    `;
    katex.render(data.occupancy_formula_latex, document.getElementById('stat-hero-math'), { displayMode: true, throwOnError: false });
    katex.render(data.planck_radiation_law_latex || '', document.getElementById('stat-box-planck'), { displayMode: true, throwOnError: false });
    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

async function executeCustomStatMechEval() {
  const stage = document.getElementById('stat-content-stage');
  stage.innerHTML = '<div class="canvas-loading-state"><div class="reactor-spinner"><div class="reactor-core"></div></div><div class="loading-label">Deducing Exact Thermodynamic Potentials F, S, U, P, Cv, M...</div></div>';

  const part = document.getElementById('stat-partition-input').value;
  const name = document.getElementById('stat-name-input').value;

  try {
    const res = await fetch('/api/statmech/custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ partition_function: part, model_name: name })
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed');
    const data = await res.json();

    stage.innerHTML = `
      <div class="derived-banner">
        <div class="verified-tag"><i data-lucide="flame"></i> ${data.model_name}</div>
        <div class="math-hero" id="stat-hero-math"></div>
      </div>
      <div class="dag-container"><div class="dag-steps">
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-order-badge">Free Energy</span><span class="step-op-title">Helmholtz Potential $F = -k_B T \\ln\\mathcal{Z}$</span></div>
          <div class="dag-formula-box" id="stat-box-F"></div>
        </div>
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-order-badge">Entropy</span><span class="step-op-title">Entropy $S = -\\partial F / \\partial T$</span></div>
          <div class="dag-formula-box" id="stat-box-S"></div>
        </div>
        <div class="dag-node">
          <div class="dag-node-header"><span class="step-order-badge">Energy</span><span class="step-op-title">Internal Energy $U$ & Heat Capacity $C_v$</span></div>
          <div class="dag-formula-box" id="stat-box-U"></div>
        </div>
      </div></div>
    `;
    katex.render(`\\mathcal{Z} = ${data.partition_function_latex}`, document.getElementById('stat-hero-math'), { displayMode: true, throwOnError: false });
    katex.render(`F = ${data.free_energy_F_latex}`, document.getElementById('stat-box-F'), { displayMode: true, throwOnError: false });
    katex.render(`S = ${data.entropy_S_latex}`, document.getElementById('stat-box-S'), { displayMode: true, throwOnError: false });
    katex.render(`U = ${data.internal_energy_U_latex}, \\quad C_v = ${data.heat_capacity_Cv_latex}`, document.getElementById('stat-box-U'), { displayMode: true, throwOnError: false });
    lucide.createIcons();
  } catch (e) {
    stage.innerHTML = `<div class="canvas-empty-state"><p style="color: var(--plasma-crimson)">${e.message}</p></div>`;
  }
}

/* ================= EXPORT HELPERS ================= */
async function downloadAcademicPaper() {
  if (!currentDerivationResult) {
    alert('Please execute a derivation first before generating an academic paper.');
    return;
  }

  try {
    const res = await fetch('/api/paper', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target: currentDerivationResult.target_variable,
        in_terms_of: currentDerivationResult.in_terms_of
      })
    });
    if (!res.ok) throw new Error('Paper generation failed');
    const data = await res.json();

    const blob = new Blob([data.latex_source], { type: 'text/x-tex' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `paper_${data.target}.tex`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (e) {
    alert(`Error: ${e.message}`);
  }
}

function copyLatexProof() {
  if (!currentDerivationResult) return;
  const latex = `\\begin{align*}\n${currentDerivationResult.steps.map(s => `  & \\text{Step ${s.step_number}: ${s.operation}} \\\\\n  & ${s.latex} \\quad \\text{(${s.explanation})} \\\\[0.8em]`).join('\n')}\n\\end{align*}`;
  navigator.clipboard.writeText(latex).then(() => alert('LaTeX derivation code copied to clipboard!'));
}

function copyMarkdownProof() {
  if (!currentDerivationResult) return;
  const md = `# Derivation: ${currentDerivationResult.target_variable}\n\n$$\n${currentDerivationResult.final_latex}\n$$\n\n## Steps:\n` +
    currentDerivationResult.steps.map(s => `### Step ${s.step_number}: ${s.operation}\n${s.explanation}\n$$\n${s.latex}\n$$\n`).join('\n');
  navigator.clipboard.writeText(md).then(() => alert('Markdown derivation copied to clipboard!'));
}

function copyPythonProof() {
  if (!currentDerivationResult) return;
  const code = `import sympy as sp\n\n# Target: ${currentDerivationResult.target_variable}\n# Final Formula: ${currentDerivationResult.final_equation}\nprint("Derived:", "${currentDerivationResult.final_equation}")`;
  navigator.clipboard.writeText(code).then(() => alert('Python SymPy snippet copied to clipboard!'));
}


