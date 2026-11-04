# KrishiMitra AI: Turning Weather Forecasts into Climate-Aware Farm Guidance

## The problem

Smallholder farmers often receive weather forecasts without a clear explanation of what those forecasts may mean for a specific crop or growth stage. A forecast app can show temperature and rainfall probability, but translating those numbers into cautious, understandable decisions takes local context and time. Language accessibility is another barrier for farmers who prefer Kannada or other regional languages.

KrishiMitra AI is a prototype exploring this gap. It is built for the Climate Resilience focus area of the **Strands SDK: Workshop to Ship** hackathon.

## What KrishiMitra does

A farmer enters a location, crop, growth stage, preferred language, and question. KrishiMitra retrieves live weather information from Open-Meteo and uses a Strands Agents SDK agent with crop-guidance tools to produce an accessible climate brief.

The current prototype supports a starter crop set—ragi, paddy, maize, and groundnut—and English/Kannada output. It is designed to help users interpret information, not replace local agricultural extension services.

## Why an agent?

This workflow requires more than one model response. The agent can select tools, retrieve information, and combine the results:

1. Resolve a farmer's place name to coordinates.
2. Retrieve current conditions and a seven-day forecast from Open-Meteo.
3. Invoke crop-context guidance for the selected crop and growth stage.
4. Explain relevant considerations and low-regret actions.
5. Keep the forecast source and timestamp visible.

The Strands Agents SDK handles the agent loop and tool invocation. The application also fetches the weather snapshot independently of the model so that source data can be displayed and checked.

## Architecture

```text
Mobile-friendly browser UI
        │ POST /api/advisory
        ▼
FastAPI backend
        ├── Open-Meteo geocoding + forecast
        ├── Strands Agents SDK
        │      ├── weather retrieval tool
        │      └── crop guidance tool
        ├── weather consistency guard
        └── source-backed response
        ▼
Verified forecast facts + cautious crop guidance
```

### Technology

- Strands Agents SDK (Python)
- FastAPI
- Ollama with Qwen 2.5 3B for local, reproducible inference
- Open-Meteo forecast and geocoding APIs
- HTML, CSS, and JavaScript

The prototype can run locally without a paid inference API key. Weather retrieval requires internet access.

## Responsible design

Weather forecasts are probabilistic. KrishiMitra must not fabricate forecast values, official advisories, or crop prescriptions. The UI displays weather facts from the API separately from AI-generated interpretation. A consistency guard is being implemented to withhold AI text that directly contradicts the forecast snapshot.

The application does not prescribe pesticide/fertilizer doses, guarantee yield, or recommend irreversible actions. Farmers should verify high-stakes decisions with their local Krishi Vigyan Kendra (KVK), agricultural extension officer, or official advisory.

## Social impact and measurement

The intended beneficiaries are smallholder farmers and agricultural learners who need accessible climate information, including Kannada-speaking communities. The prototype has not yet been field-tested, so we make no crop-loss reduction or farmer-outcome claims.

Potential indicators for future validation:

- Live forecast retrieval success rate.
- Percentage of responses displaying source and timestamp.
- Agent/tool failure rate and latency.
- Farmer comprehension of forecast explanation.
- Farmer-reported usefulness and regional-language accessibility.

A next step would be to conduct supervised usability testing with farmers and local agricultural extension personnel, then expand the knowledge base only after source review.

## What I learned

The most important engineering lesson is that an AI agent should not be trusted to restate source data without verification. In testing, a small local model incorrectly summarized rainfall even when the API response was available. This led to separating verified weather facts from model interpretation and adding a consistency guard. For climate-resilience use cases, reliable source handling is more important than a fluent answer.

## Try it

- Source code: https://github.com/PSP-YN/KrishiMitraAI
- Run instructions: see the repository README.
- Demo video: to be added after recording and publication.

**Status:** Hackathon prototype; not an official weather alert or agricultural extension service.