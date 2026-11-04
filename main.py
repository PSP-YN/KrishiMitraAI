"""KrishiMitra AI — climate-to-action agent for smallholder farmers.

Weather: Open-Meteo (live forecast, no API key).
Agent orchestration: Strands Agents SDK.
Local model: Ollama (Qwen 2.5 VL 3B by default).
"""
from __future__ import annotations

import json
import os
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


@tool
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
                "Establishment and flowering stages can be sensitive to moisture stress; prioritize monitoring the crop and soil moisture.",
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


SYSTEM_PROMPT = """You are KrishiMitra, a climate-resilience assistant for smallholder farmers in India.
You MUST use get_weather_forecast for the requested location and get_crop_guidance for the crop before giving a climate advisory. Never invent weather values, rainfall, forecast, government advisories, or citations. If a tool fails, clearly state that the data could not be retrieved and do not fill the gap with guesses.
Explain the forecast in accessible language and answer in the requested language (Kannada or English). Give a concise structured response: (1) what the live forecast says, (2) possible crop/weather risk with uncertainty, (3) low-regret actions the farmer can consider, (4) what not to do without local expert advice, (5) sources and timestamp. Do not prescribe pesticide/fertilizer dosages, guarantee yields, or make high-risk irreversible decisions. Make clear this is decision support, not official agricultural advice. Mention when KVK/extension officer/official local advisory should be consulted."""


def build_agent() -> Agent:
    model = OllamaModel(host=OLLAMA_HOST, model_id=OLLAMA_MODEL, temperature=0.2)
    return Agent(model=model, tools=[get_weather_forecast, get_crop_guidance], system_prompt=SYSTEM_PROMPT)


class AdvisoryRequest(BaseModel):
    location: str = Field(min_length=2, max_length=120)
    crop: str = Field(min_length=2, max_length=80)
    growth_stage: str = Field(default="Not sure", max_length=100)
    language: str = Field(default="English", max_length=30)
    question: str = Field(default="What climate risks should I watch for this week?", max_length=1000)


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "agent_framework": "Strands Agents SDK", "model": OLLAMA_MODEL, "provider": "Ollama", "weather_source": "Open-Meteo"}


@app.post("/api/advisory")
def advisory(req: AdvisoryRequest):
    prompt = (
        f"Farmer location: {req.location}. Crop: {req.crop}. Growth stage: {req.growth_stage}. "
        f"Respond in {req.language}. Farmer question: {req.question}. "
        "Use the weather and crop guidance tools; do not assume data that the tools did not return."
    )
    try:
        agent = build_agent()
        result = agent(prompt)
        return {"advisory": str(result), "location": req.location, "crop": req.crop, "language": req.language,
                "generated_at": datetime.now(timezone.utc).isoformat(), "model": OLLAMA_MODEL,
                "agent_framework": "Strands Agents SDK", "weather_source": "Open-Meteo"}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent execution failed: {type(exc).__name__}: {str(exc)[:300]}") from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
