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

