# Run and verify the live KrishiMitra demo

## Prerequisites

- Python 3.11–3.13 and the project dependencies.
- Ollama running locally with `qwen2.5:3b` installed (or set `OLLAMA_MODEL` to another installed model).
- Internet access for Open-Meteo geocoding and forecast requests.

## Start

```bash
ollama serve
# In another terminal, from the repository root:
ollama pull qwen2.5:3b
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
./scripts/run-local.sh
```

Open `http://127.0.0.1:8000`. The launcher verifies that Ollama is reachable and the configured model exists before starting FastAPI. It binds to loopback by default; use `HOST=0.0.0.0` only when you intentionally need LAN access.

## Verify

```bash
curl -fsS http://127.0.0.1:8000/api/health
curl -fsS http://127.0.0.1:8000/
PYTHONPATH=. python -m pytest -q
```

Submit a real request from the browser with `Mysuru, Karnataka`, `Ragi`, and `Vegetative`. Confirm the response includes a resolved location, Open-Meteo source timestamp, seven forecast days, an agent advisory, and `agent_status`. A live request requires internet access and local model inference; CI intentionally tests deterministic mocked boundaries and does not download or run an LLM.

## Current deployment boundary

The interactive app is a local-first FastAPI + Ollama application. The public Vercel page is a project overview, not a hosted multi-user AI service. Do not describe the local model as cloud-hosted. The app has no authentication, database, rate limiting, or production load/security validation.
