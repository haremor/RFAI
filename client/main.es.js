const form = document.getElementById('soilForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const resultsDisplay = document.getElementById('resultsDisplay');

function showLoading() {
    if (emptyState) emptyState.classList.add('hidden');
    if (resultsDisplay) resultsDisplay.classList.add('hidden');
    if (loadingState) loadingState.classList.remove('hidden');
    if (analyzeBtn) analyzeBtn.disabled = true;
}

function hideLoading() {
    if (loadingState) loadingState.classList.add('hidden');
    if (resultsDisplay) resultsDisplay.classList.remove('hidden');
    if (analyzeBtn) analyzeBtn.disabled = false;
}

function readInputs() {
    // Return array in model order: [Nitro, Phosph, Potassium, temp, humid, ph, rainfall]
    const get = id => document.getElementById(id)?.value ?? null;
    const nitrogen = parseFloat(get('nitrogen')) || 0;
    const phosphorus = parseFloat(get('phosphorus')) || 0;
    const potassium = parseFloat(get('potassium')) || 0;
    const temperature = parseFloat(get('temperature')) || 0;
    const humidity = parseFloat(get('humidity')) || 0;
    const ph = parseFloat(get('ph')) || 7.0;
    const rainfall = parseFloat(get('rainfall')) || 0;

    return [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall];
}

async function postPredict(sample) {
    const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sample, lang: 'es' }),
    });
    return res.json();
}

function renderCardForItem(item) {
    const name = item.name ?? item.crop ?? item[0] ?? 'Ítem';
    const suitability = item.suitability ?? null;
    const reason = item.reason ?? item.description ?? '';
    const soilBenefits = item.soilBenefits ?? '';
    const score = typeof item.score === 'number' ? item.score : null;

    const badgeClass = suitability === 'Excellent' ? 'badge-excellent'
        : suitability === 'Good' ? 'badge-good'
            : 'badge-fair';

    let badgeHtml = '';
    if (suitability) badgeHtml = `<span class="badge ${badgeClass}">${suitability}</span>`;
    else if (score !== null) badgeHtml = `<span class="badge badge-good">${(score * 100).toFixed(1)}%</span>`;

    return `
                <div class="card">
                    <div class="recommendation-title" style="display:flex;align-items:center;justify-content:space-between;gap:1rem;">
                        <h3 style="margin:0">${name}</h3>
                        ${badgeHtml}
                    </div>
                    ${reason ? `<p style="color:#15803d;margin-top:0.5rem">${reason}</p>` : ''}
                    ${soilBenefits ? `<p style="margin-top:0.5rem">${soilBenefits}</p>` : ''}
                </div>
            `;
}

function renderResults(data) {
    // Normalize to an array of items
    let items = [];
    if (!data) {
        resultsDisplay.innerHTML = '<div class="card"><p>No se devolvieron datos</p></div>';
        return;
    }

    if (Array.isArray(data)) {
        items = data;
    } else if (data.error) {
        resultsDisplay.innerHTML = `<div class="card"><p style="color:#78350f">Error: ${data.error}</p></div>`;
        return;
    } else if (typeof data === 'object') {
        const valuesAreNumbers = Object.values(data).every(v => typeof v === 'number');
        if (valuesAreNumbers) {
            items = Object.entries(data).map(([name, score]) => ({ name, score }));
        } else {
            // Try to pick values as list
            items = Object.values(data);
        }
    }

    if (!items.length) {
        resultsDisplay.innerHTML = '<div class="card"><p>No se encontraron recomendaciones</p></div>';
        return;
    }

    // Header
    let html = `
                <div class="recommendations-container">
                    <div class="card card-gradient">
                        <div style="display:flex;gap:0.75rem;align-items:center;">
                            <h3 style="margin:0">Análisis completado</h3>
                            <p style="margin:0;color:#15803d;">Se encontraron ${items.length} recomendación(es)</p>
                        </div>
                    </div>
            `;

    items.forEach(item => {
        html += renderCardForItem(item);
    });

    html += `</div>`;
    resultsDisplay.innerHTML = html;
}

form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();
    const sample = readInputs();
    try {
        const data = await postPredict(sample);
        renderResults(data);
    } catch (err) {
        resultsDisplay.innerHTML = `<div class="card"><p style="color:#78350f">Fallo en la petición: ${err.message}</p></div>`;
    } finally {
        hideLoading();
    }
});