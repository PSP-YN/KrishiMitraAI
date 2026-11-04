# KrishiMitra AI: Climate-Aware Farm Guidance for Smallholder Farmers

## The problem

Smallholder farmers often receive weather forecasts without a clear explanation of what those forecasts may mean for a specific crop or growth stage. A forecast can show temperature and rainfall probability, but translating those numbers into cautious, local decisions takes context. Language accessibility is another barrier for farmers who prefer Kannada.

KrishiMitra AI is an open-source prototype exploring this gap for the Climate Resilience focus area of the Strands SDK: Workshop to Ship hackathon.

## What KrishiMitra does

A farmer enters a location, crop, growth stage, preferred language, and question. KrishiMitra retrieves current conditions and a seven-day forecast from Open-Meteo, then uses a Strands Agents SDK agent with crop-guidance tools to produce an accessible climate brief. The starter crop set includes ragi, paddy, maize, and groundnut. The interface supports English and Kannada.

## Why an agent

The workflow combines multiple steps: resolve a place name, retrieve live weather, retrieve crop context, and explain low-regret considerations. Strands Agents SDK provides the model-driven agent loop and tool invocation. The backend also fetches the weather snapshot independently of the model, so the application can display source-backed facts even if generated prose is unreliable.

## Technical architecture

```text
Mobile-friendly HTML/CSS/JavaScript interface
        │ POST /api/advisory
        ▼
FastAPI backend
        ├── Open-Meteo geocoding + forecast
        ├── Strands Agents SDK
        │      ├── weather tool
        │      └── crop-guidance tool
        ├── narrow weather-consistency guard
        └── verified forecast panel + cautious crop guidance
```

The prototype uses Python, FastAPI, Strands Agents SDK, Ollama with Qwen 2.5 3B for local inference, and Open-Meteo. It can run locally without a paid inference API key; live weather retrieval requires internet access.

## Reliability and responsible design

Weather forecasts are probabilistic. In testing, a small local model incorrectly summarized rainfall even when the API data was available. KrishiMitra therefore separates verified weather facts from AI interpretation. A narrow phrase-based consistency guard withholds common explicit claims such as “no rain expected” or “dry forecast” when the verified seven-day precipitation total is positive. This is a targeted safeguard, not general semantic fact verification; the source and retrieval timestamp remain visible.

The prototype does not claim to be an official weather alert or agricultural extension service. It does not guarantee yield, invent government advisories, prescribe pesticide or fertilizer dosages, or recommend irreversible actions. Users are directed to local Krishi Vigyan Kendras (KVKs), agricultural extension officers, and official advisories for high-stakes decisions.

## Social impact and validation

The intended beneficiaries are smallholder farmers and agricultural learners, including Kannada-speaking communities who need understandable climate information. The prototype has not yet been field-tested, so no crop-loss reduction or farmer-outcome claims are made. Future validation should measure forecast retrieval success, source/timestamp coverage, tool failure rate, response latency, farmer comprehension, and usefulness in supervised usability sessions with farmers and extension personnel.

## What I learned

The main engineering lesson is that a fluent agent response is not evidence of correctness. A model can misstate source data even when the tool result is available. Separating source facts from model interpretation, then checking generated claims against those facts, is essential for climate-related decision support.

## Try it

- Source code: https://github.com/PSP-YN/KrishiMitraAI
- Run instructions: see the repository README.
- Demo video: add the public recording URL after upload.

**Status:** Hackathon prototype; local testing only. Field validation and production deployment remain future work.
