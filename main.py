"""KrishiMitra AI — climate-to-action agent for smallholder farmers.

Weather: Open-Meteo (live forecast, no API key).
Agent orchestration: Strands Agents SDK.
Local model: Ollama (Qwen 2.5 3B by default).
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from strands import Agent, tool
from strands.models.ollama import OllamaModel

ROOT = Path(__file__).resolve().parent
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
WEATHER_TIMEOUT = 12

app = FastAPI(title="KrishiMitra AI", version="0.1.0", description="Climate-resilience agent for smallholder farmers")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


def get_weather_forecast(location: str) -> str:
    """Fetch a real 7-day weather forecast for a city, village, or place name using Open-Meteo."""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
            timeout=WEATHER_TIMEOUT,
        )
        geo.raise_for_status()
        results = geo.json().get("results", [])
        if not results:
            return json.dumps({"error": f"No geocoding result for {location}. Ask for a nearby town or district."})
        place = results[0]
        forecast = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,et0_fao_evapotranspiration",
                "forecast_days": 7,
                "timezone": "auto",
            },
            timeout=WEATHER_TIMEOUT,
        )
        forecast.raise_for_status()
        data = forecast.json()
        data["resolved_location"] = {
            "name": place.get("name"), "admin1": place.get("admin1"), "country": place.get("country"),
            "latitude": place.get("latitude"), "longitude": place.get("longitude"),
        }
        data["source"] = "Open-Meteo"
        data["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
        return json.dumps(data)
    except requests.RequestException as exc:
        return json.dumps({"error": "Weather service is temporarily unavailable", "detail": str(exc)[:300]})


@tool
def get_crop_guidance(crop: str, growth_stage: str = "unspecified") -> str:
    """Retrieve conservative general crop/climate guidance for a crop and growth stage. This is not a replacement for local agricultural extension advice."""
    normalized = crop.strip().lower()
    guidance: dict[str, dict[str, Any]] = {
        "ragi": {
            "name": "Finger millet (ragi)",
            "notes": [
                "Avoid treating a single forecast as a guarantee; verify rainfall locally before irrigation or sowing decisions.",
                "Moisture needs vary across establishment, vegetative, flowering, and grain-filling stages; monitor soil moisture and confirm stage-specific decisions with local extension guidance.",
                "Do not recommend a fertilizer or pesticide dose without soil, crop-stage, and local extension context.",
            ],
        },
        "finger millet": {"name": "Finger millet (ragi)", "notes": ["Monitor soil moisture around establishment and flowering; validate timing with local extension guidance.", "Do not infer irrigation quantities from weather forecasts alone."]},
        "paddy": {"name": "Rice (paddy)", "notes": ["Water management depends on variety, soil, stage, irrigation system, and local practice.", "Check drainage preparedness before heavy-rain forecasts and local advisories before irrigation changes."]},
        "rice": {"name": "Rice (paddy)", "notes": ["Water management depends on variety, soil, stage, irrigation system, and local practice.", "Check drainage preparedness before heavy-rain forecasts and local advisories before irrigation changes."]},
        "maize": {"name": "Maize", "notes": ["Moisture needs vary by growth stage; flowering and grain filling are important periods to monitor.", "Heavy rainfall can increase waterlogging risk in poorly drained fields; inspect field drainage."]},
        "groundnut": {"name": "Groundnut", "notes": ["Moisture and drainage management vary with soil and growth stage.", "Avoid waterlogging; check local recommendations for sowing and pegging stages."]},
    }
    item = guidance.get(normalized)
    if not item:
        item = {"name": crop, "notes": ["Crop-specific recommendations were not found in the curated starter knowledge base.", "Use local agricultural extension/ICAR/KVK guidance; do not make irreversible crop decisions from this generic response."]}
    return json.dumps({"crop": item["name"], "growth_stage": growth_stage, "general_guidance": item["notes"], "caution": "General educational guidance only. Confirm decisions with local KVK/extension officers and official advisories."})


WEATHER_CONFLICT_PATTERNS = [
    r"no rain (?:is )?(?:expected|forecast)",
    r"no precipitation (?:is )?(?:expected|forecast)",
    r"rain[- ]free",
    r"dry (?:period|spell|forecast)",
    r"precipitation.{0,30}(?:zero|0 mm)",
    r"rainfall.{0,30}(?:zero|0 mm)",
]


def weather_conflict_detected(agent_text: str, precipitation_total_mm: float) -> bool:
    """Conservatively catch explicit dry/no-rain claims against a wet 7-day forecast.

    This is a narrow phrase-based guard, not general semantic fact verification.
    """
    if precipitation_total_mm <= 0:
        return False
    return any(re.search(pattern, agent_text, re.IGNORECASE) for pattern in WEATHER_CONFLICT_PATTERNS)


SYSTEM_PROMPT = """You are KrishiMitra, a cautious climate-resilience assistant for smallholder farmers in India.
You MUST call get_crop_guidance for the crop and growth stage before answering. The backend retrieves weather independently and displays verified facts separately. Never repeat weather numbers or make claims that it is rainy, dry, or rain-free. Focus on crop-stage monitoring, low-risk actions, and questions that need local expert advice. Do not invent crop facts, government schemes, official advisories, or citations. Never prescribe pesticide/fertilizer doses, guarantee yields, or recommend irreversible actions. Reply in simple English and no more than five concise points (about 120 words). State that this is decision support, not official agricultural advice, and recommend local KVK/extension guidance for high-stakes decisions."""


def build_agent() -> Agent:
    model = OllamaModel(host=OLLAMA_HOST, model_id=OLLAMA_MODEL, temperature=0.2, max_tokens=768)
    # Weather is fetched once by the API so verified source facts and the
    # model's interpretation remain separate. The agent tool supplies crop context.
    return Agent(model=model, tools=[get_crop_guidance], system_prompt=SYSTEM_PROMPT)


class AdvisoryRequest(BaseModel):
    model_config = {"str_strip_whitespace": True}

    location: str = Field(min_length=2, max_length=120)
    crop: str = Field(min_length=2, max_length=80)
    growth_stage: str = Field(default="Not sure", max_length=100)
    language: str = Field(default="English", pattern="^English$")
    question: str = Field(default="What climate risks should I watch for this week?", min_length=3, max_length=1000)


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    """Report real local model availability instead of assuming the agent is ready."""
    ollama_reachable = False
    model_available = False
    try:
        response = requests.get(f"{OLLAMA_HOST.rstrip('/')}/api/tags", timeout=2)
        response.raise_for_status()
        ollama_reachable = True
        available = {item.get("name") for item in response.json().get("models", [])}
        model_available = OLLAMA_MODEL in available
    except (requests.RequestException, ValueError):
        pass
    return {
        "status": "ok" if model_available else "degraded",
        "agent_framework": "Strands Agents SDK",
        "model": OLLAMA_MODEL,
        "provider": "Ollama",
        "ollama_reachable": ollama_reachable,
        "model_available": model_available,
        "weather_source": "Open-Meteo",
    }


@app.post("/api/advisory")
def advisory(req: AdvisoryRequest):
    try:
        # Fetch weather outside the LLM so the UI can show verified source data
        # and the model receives a trusted snapshot rather than relying on memory.
        weather = json.loads(get_weather_forecast(req.location))
        if weather.get("error"):
            raise HTTPException(status_code=502, detail=weather["error"])
        snapshot = {
            "resolved_location": weather.get("resolved_location"),
            "current": weather.get("current"),
            "daily": weather.get("daily"),
            "source": weather.get("source"),
            "retrieved_at_utc": weather.get("retrieved_at_utc"),
        }
        prompt = (
            f"Farmer location: {req.location}. Crop: {req.crop}. Growth stage: {req.growth_stage}. "
            f"Respond in {req.language}. Farmer question: {req.question}.\n\n"
            "TRUSTED LIVE WEATHER SNAPSHOT (from server-side Open-Meteo API; use exact values):\n"
            f"{json.dumps(snapshot, ensure_ascii=False)}\n\n"
            "Weather snapshot is context only; the UI displays forecast facts separately. Do not state forecast values, dates, or claim rain/no-rain/dry/rainy. "
            "Use get_crop_guidance and return crop-stage considerations, low-regret actions, and what needs local expert advice. "
            "Do not invent crop facts or government recommendations."
        )
        agent = build_agent()
        result = agent(prompt)
        agent_text = str(result)
        daily = snapshot.get("daily") or {}
        precip = [float(v or 0) for v in daily.get("precipitation_sum", [])]
        precip_total = round(sum(precip), 1)
        probs = [int(v or 0) for v in daily.get("precipitation_probability_max", [])]
        highs = [float(v) for v in daily.get("temperature_2m_max", []) if v is not None]
        lows = [float(v) for v in daily.get("temperature_2m_min", []) if v is not None]
        weather_summary = {
            "forecast_start": (daily.get("time") or [None])[0],
            "forecast_end": (daily.get("time") or [None])[-1],
            "precipitation_total_mm": precip_total,
            "max_precipitation_probability_percent": max(probs, default=0),
            "temperature_min_c": min(lows, default=None),
            "temperature_max_c": max(highs, default=None),
            "source": "Open-Meteo",
        }
        conflict = weather_conflict_detected(agent_text, precip_total)
        agent_status = "rejected_weather_conflict" if conflict else "accepted"
        if conflict:
            agent_text = ("The AI response was withheld by KrishiMitra's weather-consistency guard because it contradicted the live forecast. "
                          "Verified forecast facts are shown above. For this crop stage, monitor soil moisture and field drainage, "
                          "check the timing of local rainfall, and verify soil conditions before changing irrigation. "
                          "Do not make irreversible crop decisions from a forecast alone; consult your local KVK/extension officer.")
        return {"advisory": agent_text, "agent_status": agent_status, "weather_summary": weather_summary,
                "location": req.location, "crop": req.crop, "language": req.language,
                "weather": snapshot, "generated_at": datetime.now(timezone.utc).isoformat(), "model": OLLAMA_MODEL,
                "agent_framework": "Strands Agents SDK", "weather_source": "Open-Meteo"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent execution failed: {type(exc).__name__}: {str(exc)[:300]}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
