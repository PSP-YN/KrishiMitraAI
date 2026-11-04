# KrishiMitra AI 🌾

**A climate-to-action agent for smallholder farmers, built with the Strands Agents SDK.**

KrishiMitra translates a live weather forecast into cautious, crop-aware guidance in English or Kannada. It is a hackathon prototype for climate resilience and regional accessibility.

## What it does

- Geocodes a farmer's location and retrieves a real 7-day forecast from [Open-Meteo](https://open-meteo.com/).
- Uses a Strands Agents SDK agent with tool calling to retrieve weather and crop context.
- Supports ragi, paddy, maize, groundnut and a safe fallback for other crops.
- Returns a simple explanation, potential risks, low-regret actions and uncertainty.
- Runs locally with Ollama; no paid inference API key is required for the demo.
- Reports model/weather failures rather than fabricating observations.

## Architecture

```text
Browser UI (HTML/CSS/JS)
        │ POST /api/advisory
        ▼
FastAPI backend
        │
        ▼
Strands Agent ───── Ollama (local Qwen model)
   ├── get_weather_forecast(location)
   │      ├── Open-Meteo geocoding
   │      └── Open-Meteo forecast
   └── get_crop_guidance(crop, growth_stage)
          └── curated starter guidance + caution
```

## Run locally (Fedora/Linux)

Prerequisites: Python 3.13+, Git, [Ollama](https://ollama.com/), and internet access for Open-Meteo.

```bash
# 1. Install a local model (one-time)
ollama pull qwen2.5:3b

# 2. Set up the Python environment
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Ensure Ollama is running
ollama serve   # if it is not already running

# 4. Start the app
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000.

### Configuration

```bash
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:3b
export PORT=8000
```

## API

- `GET /api/health` — reports backend/agent configuration.
- `POST /api/advisory` — accepts `location`, `crop`, `growth_stage`, `language`, and `question`.

Example:

```json
{
  "location": "Mysuru, Karnataka",
  "crop": "Ragi",
  "growth_stage": "Vegetative",
  "language": "Kannada",
  "question": "What climate risks should I watch for this week?"
}
```

## Social impact and measurement

Target population: smallholder farmers and agricultural learners who need climate information in accessible language, including Kannada-speaking communities.

Potential measurable indicators (to be validated with users; no impact claims are made yet):

- Successful live forecast retrieval rate.
- Share of advisories with traceable weather-source/time metadata.
- Response time and agent/tool failure rate.
- Farmer comprehension of the forecast explanation.
- Farmer-reported usefulness and accessibility.

## Safety and limitations

- Prototype only; not an official weather alert or agricultural extension service.
- Weather forecasts are probabilistic and may change.
- Crop guidance is general, not a local prescription.
- Do not make pesticide/fertilizer dose, yield, or irreversible sowing/irrigation decisions from this tool alone.
- Verify urgent or high-stakes decisions with local KVK/ICAR/extension officers and official advisories.
- The starter knowledge base is limited; expanding it requires source review and field validation.

## Hackathon

Built for **Strands SDK: Workshop to Ship** (AWS Builder Center), in the Climate Resilience focus area.

- Framework: Strands Agents SDK
- Model: Ollama (local Qwen model for the reproducible demo)
- Weather: Open-Meteo
- API: FastAPI
- UI: HTML/CSS/JavaScript

## License

MIT (see `LICENSE`).
