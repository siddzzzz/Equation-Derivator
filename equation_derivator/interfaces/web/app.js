/**
 * Equation-Derivator: Client-side Application Controller
 */

// Global State
let allEquations = [];
let allQuantities = [];
let activeCatalogDomain = 'all';
let currentDerivationResult = null;

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', async () => {
  lucide.createIcons();
  initNavigation();
  initDeriveHandler();
  initVerifyHandler();
  initDiscoverHandler();

  await fetchQuantities();
  await fetchEquations();
});

// Navigation Tabs
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const targetTabId = `tab-${tab.getAttribute('data-tab')}`;
      document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
      });

      const activePanel = document.getElementById(targetTabId);
      if (activePanel) {
        activePanel.classList.add('active');
        lucide.createIcons();
        renderMathInElement(activePanel, {
          delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
          ]
        });
      }
    });
  });
}

// Preset Loader for Derivations
function loadPreset(presetKey) {
  const targetInput = document.getElementById('target-var');
  const inTermsOfInput = document.getElementById('in-terms-of');
  const startingEqsInput = document.getElementById('starting-eqs');

  switch (presetKey) {
    case 'ke_momentum':
      targetInput.value = 'K';
      inTermsOfInput.value = 'p, m';
      startingEqsInput.value = 'kinetic_energy_def; linear_momentum_def';
      break;
    case 'escape_velocity':
      targetInput.value = 'v';
      inTermsOfInput.value = 'G, M, r';
      startingEqsInput.value = '1/2 * m * v^2 = G * M * m / r';
      break;
    case 'power_ir':
      targetInput.value = 'P';
      inTermsOfInput.value = 'I, R';
      startingEqsInput.value = 'electric_power_iv; ohm_law';
      break;
    case 'work_energy_calculus':
      targetInput.value = 'W';
      inTermsOfInput.value = 'm, v_i, v_f';
      startingEqsInput.value = 'work_definition_force_dist; newton_second_law';
      break;
  }
  document.getElementById('btn-run-derive').click();
}

// Derivation Execution Handler
function initDeriveHandler() {
  const btn = document.getElementById('btn-run-derive');
  btn.addEventListener('click', async () => {
    const target = document.getElementById('target-var').value.trim();
    const inTermsOfRaw = document.getElementById('in-terms-of').value.trim();
    const startingEqsRaw = document.getElementById('starting-eqs').value.trim();

    if (!target || !inTermsOfRaw) {
      alert('Please provide a target variable and allowed terms.');
      return;
    }

    const in_terms_of = inTermsOfRaw.split(',').map(s => s.trim()).filter(Boolean);
    const starting_equations = startingEqsRaw ? startingEqsRaw.split(';').map(s => s.trim()).filter(Boolean) : null;

    const placeholder = document.getElementById('derive-placeholder');
    const loader = document.getElementById('derive-loading');
    const resultContainer = document.getElementById('derive-result-container');
    const actions = document.getElementById('derive-actions');

    placeholder.classList.add('hidden');
    resultContainer.classList.add('hidden');
    actions.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
      const response = await fetch('/api/derive', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          target,
          in_terms_of,
          starting_equations
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Derivation failed');
      }

      const data = await response.json();
      currentDerivationResult = data;
      renderDerivationResult(data);
    } catch (e) {
      alert(`Derivation Error: ${e.message}`);
      placeholder.classList.remove('hidden');
    } finally {
      loader.classList.add('hidden');
    }
  });
}

function renderDerivationResult(data) {
  const resultContainer = document.getElementById('derive-result-container');
  const actions = document.getElementById('derive-actions');
  const finalDisplay = document.getElementById('final-math-display');
  const stepsChain = document.getElementById('steps-chain');
  const assumptionsBox = document.getElementById('assumptions-box');
  const assumptionsList = document.getElementById('assumptions-list');

  // Render Final Result
  katex.render(data.final_latex, finalDisplay, { displayMode: true, throwOnError: false });

  // Render Assumptions
  if (data.all_assumptions && data.all_assumptions.length > 0) {
    assumptionsList.innerHTML = data.all_assumptions.map(a => `<li>${a}</li>`).join('');
    assumptionsBox.classList.remove('hidden');
  } else {
    assumptionsBox.classList.add('hidden');
  }

  // Render Step Cards
  stepsChain.innerHTML = '';
  data.steps.forEach(step => {
    const card = document.createElement('div');
    card.className = 'step-card';
    card.innerHTML = `
      <div class="step-header">
        <span class="step-badge">Step ${step.step_number}</span>
        <span class="step-op">${step.operation}</span>
      </div>
      <div class="step-explanation">${step.explanation}</div>
      <div class="step-formula" id="step-katex-${step.step_number}"></div>
    `;
    stepsChain.appendChild(card);

    const stepFormulaEl = card.querySelector(`#step-katex-${step.step_number}`);
    katex.render(step.latex, stepFormulaEl, { displayMode: true, throwOnError: false });
  });

  resultContainer.classList.remove('hidden');
  actions.classList.remove('hidden');
  lucide.createIcons();
}

function copyDeriveMarkdown() {
  if (!currentDerivationResult) return;
  const md = [
    `# Derivation: ${currentDerivationResult.target_variable}`,
    `$$${currentDerivationResult.final_latex}$$`,
    '\n## Step-by-Step Derivation:',
    ...currentDerivationResult.steps.map(s => `### Step ${s.step_number}: ${s.operation}\n${s.explanation}\n$$${s.latex}$$\n`)
  ].join('\n');

  navigator.clipboard.writeText(md).then(() => {
    alert('Derivation markdown copied to clipboard!');
  });
}

// Verifier Handler
function setVerifyInput(eq) {
  document.getElementById('verify-input').value = eq;
  document.getElementById('btn-run-verify').click();
}

function initVerifyHandler() {
  const btn = document.getElementById('btn-run-verify');
  btn.addEventListener('click', async () => {
    const eqStr = document.getElementById('verify-input').value.trim();
    if (!eqStr) return;

    const placeholder = document.getElementById('verify-placeholder');
    const container = document.getElementById('verify-report-container');

    try {
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ equation_str: eqStr })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Verification error');
      }

      const data = await response.json();
      placeholder.classList.add('hidden');
      container.classList.remove('hidden');

      const badge = document.getElementById('verify-overall-badge');
      const isPass = data.overall_valid;
      badge.className = `overall-badge ${isPass ? 'pass' : 'fail'}`;
      badge.innerHTML = isPass ? '✔ EQUATION PASSED PHYSICAL & MATHEMATICAL VERIFICATION' : '⚠ EQUATION FAILED CONSISTENCY AUDIT';

      const grid = document.getElementById('audit-grid');
      grid.innerHTML = `
        <div class="audit-item ${data.dimensional_check.valid ? 'pass' : 'fail'}">
          <div>
            <div class="audit-name">Dimensional Homogeneity [LHS = RHS]</div>
            <div class="audit-msg">${data.dimensional_check.message}</div>
          </div>
          <span class="step-badge">${data.dimensional_check.valid ? 'PASS' : 'FAIL'}</span>
        </div>

        <div class="audit-item ${data.symbolic_check.valid ? 'pass' : 'fail'}">
          <div>
            <div class="audit-name">Symbolic Equivalence & Identity</div>
            <div class="audit-msg">${data.symbolic_check.message}</div>
          </div>
          <span class="step-badge">${data.symbolic_check.valid ? 'PASS' : 'UNVERIFIED'}</span>
        </div>

        <div class="audit-item ${data.numerical_check.valid ? 'pass' : 'fail'}">
          <div>
            <div class="audit-name">Monte Carlo Random Domain Sampling</div>
            <div class="audit-msg">${data.numerical_check.message}</div>
          </div>
          <span class="step-badge">${data.numerical_check.valid ? 'PASS' : 'FAIL'}</span>
        </div>
      `;
    } catch (e) {
      alert(`Verification Error: ${e.message}`);
    }
  });
}

// Discovery Handler
function toggleDiscoveryMode() {
  const mode = document.querySelector('input[name="disc-mode"]:checked').value;
  const dimInputs = document.getElementById('dim-synth-inputs');
  const crossInputs = document.getElementById('cross-domain-inputs');

  if (mode === 'dimensional') {
    dimInputs.classList.remove('hidden');
    crossInputs.classList.add('hidden');
  } else {
    dimInputs.classList.add('hidden');
    crossInputs.classList.remove('hidden');
  }
}

function initDiscoverHandler() {
  const btn = document.getElementById('btn-run-discover');
  btn.addEventListener('click', async () => {
    const mode = document.querySelector('input[name="disc-mode"]:checked').value;
    const resultsContainer = document.getElementById('discovery-results');

    resultsContainer.innerHTML = `
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Synthesizing candidate relations and filtering through verification...</p>
      </div>
    `;

    try {
      let payload = { mode };
      if (mode === 'dimensional') {
        payload.quantities = document.getElementById('synth-quantities').value.split(',').map(s => s.trim()).filter(Boolean);
        payload.target = document.getElementById('synth-target').value.trim();
      } else {
        payload.domain1 = document.getElementById('disc-domain-1').value;
        payload.domain2 = document.getElementById('disc-domain-2').value;
      }

      const response = await fetch('/api/discover', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Discovery failed');
      }

      const data = await response.json();
      if (!data || data.length === 0) {
        resultsContainer.innerHTML = '<div class="empty-state"><p>No non-trivial scaling relations discovered for given parameters.</p></div>';
        return;
      }

      resultsContainer.innerHTML = '';
      data.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'step-card';
        card.style.marginBottom = '1.25rem';
        card.innerHTML = `
          <div class="step-header">
            <span class="step-badge">Candidate ${index + 1}</span>
            <span class="step-op">${item.name}</span>
          </div>
          <div class="step-explanation">${item.notes || ''}</div>
          <div class="step-formula" id="disc-math-${index}"></div>
        `;
        resultsContainer.appendChild(card);
        katex.render(item.latex, card.querySelector(`#disc-math-${index}`), { displayMode: true, throwOnError: false });
      });
    } catch (e) {
      resultsContainer.innerHTML = `<div class="empty-state"><p style="color: var(--accent-red)">Discovery Error: ${e.message}</p></div>`;
    }
  });
}

// Fetch and Render Equations Catalog
async function fetchEquations() {
  try {
    const res = await fetch('/api/equations');
    allEquations = await res.json();
    renderCatalog();
  } catch (e) {
    console.error('Failed to load equations:', e);
  }
}

function setCatalogDomain(domain) {
  activeCatalogDomain = domain;
  document.querySelectorAll('#domain-filter-chips .filter-chip').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-domain') === domain);
  });
  renderCatalog();
}

function filterCatalog() {
  renderCatalog();
}

function renderCatalog() {
  const query = (document.getElementById('search-catalog')?.value || '').toLowerCase();
  const grid = document.getElementById('equations-grid');
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
    card.className = 'eq-card';
    card.innerHTML = `
      <div>
        <div class="eq-card-top">
          <span class="eq-domain-tag">${eq.domain}</span>
          <span style="font-size: 0.75rem; color: var(--text-muted)">${eq.id}</span>
        </div>
        <h3>${eq.name}</h3>
        <div class="eq-card-formula" id="eq-katex-${eq.id}"></div>
        <p class="eq-card-desc">${eq.description || ''}</p>
      </div>
      <button class="btn-sm" onclick="loadEquationToDerive('${eq.id}')">
        <i data-lucide="arrow-right"></i> Use in Derivation
      </button>
    `;
    grid.appendChild(card);
    katex.render(eq.latex, card.querySelector(`#eq-katex-${eq.id}`), { displayMode: true, throwOnError: false });
  });

  lucide.createIcons();
}

function loadEquationToDerive(eqId) {
  document.querySelector('[data-tab="derive"]').click();
  document.getElementById('starting-eqs').value = eqId;
}

// Fetch and Render Physical Ontology Table
async function fetchQuantities() {
  try {
    const res = await fetch('/api/quantities');
    allQuantities = await res.json();
    const tbody = document.getElementById('ontology-tbody');
    if (!tbody) return;

    tbody.innerHTML = allQuantities.map(q => `
      <tr>
        <td><strong>${q.name}</strong><br><small style="color: var(--text-muted)">${q.description}</small></td>
        <td><span class="step-badge">${q.symbol}</span></td>
        <td><code>${q.dimension}</code></td>
        <td style="color: var(--text-secondary)">${q.aliases.join(', ') || '—'}</td>
        <td><span class="eq-domain-tag">${q.is_constant ? 'Constant' : (q.domains[0] || 'Physical')}</span></td>
      </tr>
    `).join('');
  } catch (e) {
    console.error('Failed to load quantities:', e);
  }
}
