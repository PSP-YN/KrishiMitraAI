const form = document.getElementById('form');
const button = document.getElementById('submit');
const output = document.getElementById('output');
const statusBox = document.getElementById('status');
const forecastPanel = document.getElementById('forecast-panel');
const forecastGrid = document.getElementById('forecast-grid');

function renderSafeMarkdown(value) {
  const escaped = String(value).replace(/[&<>]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch]));
  return escaped
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

function renderForecast(daily) {
  const days = daily?.time || [];
  if (!days.length) {
    forecastPanel.hidden = true;
    return;
  }
  forecastGrid.replaceChildren();
  days.forEach((date, index) => {
    const card = document.createElement('article');
    card.className = 'forecast-day';
    const heading = document.createElement('strong');
    heading.textContent = new Date(`${date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });
    const temperature = document.createElement('span');
    const high = daily.temperature_2m_max?.[index];
    const low = daily.temperature_2m_min?.[index];
    temperature.textContent = `${low ?? '—'}° / ${high ?? '—'}°C`;
    const rain = document.createElement('small');
    rain.textContent = `Rain ${daily.precipitation_sum?.[index] ?? '—'} mm · ${daily.precipitation_probability_max?.[index] ?? '—'}% chance`;
    card.append(heading, temperature, rain);
    forecastGrid.append(card);
  });
  forecastPanel.hidden = false;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  button.disabled = true;
  button.textContent = 'Agent working…';
  statusBox.className = 'status show';
  statusBox.textContent = 'Fetching live weather and crop context. The local model may take 30–90 seconds.';
  output.className = 'empty';
  output.textContent = 'Analyzing forecast… Strands is coordinating the agent tools. Keep this page open.';
  forecastPanel.hidden = true;

  try {
    const response = await fetch('/api/advisory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: document.getElementById('location').value.trim(),
        crop: document.getElementById('crop').value,
        growth_stage: document.getElementById('stage').value,
        language: document.getElementById('language').value,
        question: document.getElementById('question').value.trim()
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Agent request failed');

    const weather = data.weather || {};
    const current = weather.current || {};
    const daily = weather.daily || {};
    const place = weather.resolved_location || {};
    const rainTotal = (daily.precipitation_sum || []).reduce((sum, value) => sum + Number(value || 0), 0);
    const rainChance = Math.max(0, ...(daily.precipitation_probability_max || []).map(Number));

    output.className = 'advisory';
    output.replaceChildren();
    const facts = document.createElement('section');
    facts.className = 'weatherfacts';
    const factsTitle = document.createElement('h3');
    factsTitle.textContent = 'Verified live weather snapshot';
    const metrics = document.createElement('div');
    metrics.className = 'weathergrid';
    const metricValues = [
      ['Current temperature', `${current.temperature_2m ?? '—'} °C`],
      ['Current rainfall', `${current.precipitation ?? '—'} mm`],
      ['7-day rainfall total', `${rainTotal.toFixed(1)} mm`],
      ['Peak rain probability', `${rainChance}%`]
    ];
    metricValues.forEach(([label, value]) => {
      const metric = document.createElement('div');
      metric.className = 'weathermetric';
      const caption = document.createElement('small');
      caption.textContent = label;
      const number = document.createElement('strong');
      number.textContent = value;
      metric.append(caption, number);
      metrics.append(metric);
    });
    const source = document.createElement('p');
    source.className = 'weather-source';
    source.textContent = `${place.name || data.location}, ${place.admin1 || ''} · ${data.weather_source} · Retrieved ${weather.retrieved_at_utc}`;
    facts.append(factsTitle, metrics, source);

    const advisory = document.createElement('div');
    advisory.className = 'advisory-text';
    advisory.innerHTML = renderSafeMarkdown(data.advisory);
    output.append(facts, advisory);
    renderForecast(daily);
    statusBox.textContent = `Completed · ${data.model} · ${new Date(data.generated_at).toLocaleString()}`;
  } catch (error) {
    output.className = 'empty';
    output.replaceChildren();
    const title = document.createElement('h3');
    title.textContent = 'Could not generate advisory';
    const message = document.createElement('p');
    message.textContent = `${error.message} — check backend, network access, and Ollama model availability.`;
    output.append(title, message);
    statusBox.textContent = 'Agent failed; no fabricated forecast was shown.';
  } finally {
    button.disabled = false;
    button.textContent = 'Generate climate advisory →';
  }
});
