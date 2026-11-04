# KrishiMitra AI — Pitch Notes

## One-line pitch
KrishiMitra AI is an open-source climate decision-support prototype that turns local weather forecasts into cautious, crop-stage-aware guidance for smallholder farmers.

## 30-second pitch
Smallholder farmers can see a weather forecast, but they still have to work out what it means for a particular crop and growth stage. KrishiMitra connects a live seven-day Open-Meteo forecast with crop context through a Strands Agents SDK agent. Farmers enter a location, crop, stage, and question; the app presents verified weather facts separately from the agent's practical monitoring suggestions. A consistency safeguard withholds certain AI responses when explicit dry-weather claims conflict with a positive rainfall forecast. It is designed as decision support, not a replacement for local agricultural experts.

## 90-second pitch
Weather information is useful only when people can interpret it in context. For smallholder farmers, a rainfall probability or temperature range does not automatically answer practical questions about a crop at a particular growth stage. Accessible explanations and locally relevant context can make that harder.

KrishiMitra AI addresses this gap with a simple workflow. A farmer enters a village or city, selects a crop such as ragi, paddy, maize, or groundnut, chooses its growth stage, and asks a question. The backend resolves the location and fetches current conditions and a seven-day forecast from Open-Meteo. A Strands Agents SDK agent uses a crop-guidance tool to generate cautious, low-regret monitoring suggestions.

The important design choice is separating evidence from interpretation. Weather values, source, and retrieval time are displayed directly from the backend rather than being trusted to the language model. A narrow consistency guard can withhold an answer if it explicitly claims a dry or rain-free forecast while the seven-day source data reports positive rainfall. The current submission build is English-only. Kannada localization is deliberately disabled because local-model output did not meet a basic quality check; native-speaker validation is required before enabling it.

This is an open-source hackathon prototype, not a field-validated product or official agricultural advisory. The next step is supervised testing with farmers and KVK or extension personnel, measuring comprehension, usefulness, forecast reliability, and safe decision support.

## Demo flow
1. Open the local demo and show the climate-resilience problem statement.
2. Enter Mysuru, Karnataka; choose Ragi and Vegetative.
3. Ask: What crop-stage checks and low-risk actions should I consider? Do not describe the weather.
4. Point out the live forecast panel: current temperature, current rainfall, seven-day rainfall total, peak rainfall probability, source, and retrieval timestamp.
5. Explain that the agent response is crop guidance; weather facts are not model-generated.
6. Explain the consistency guard and the fallback behavior when a contradiction is detected.
7. Close with the open-source repository and the validation roadmap.

## Architecture
- Frontend: responsive HTML, CSS, and JavaScript interface.
- API: FastAPI request validation and orchestration.
- Weather data: Open-Meteo geocoding and forecast API.
- Agent: Strands Agents SDK with a local Ollama Qwen 2.5 3B model.
- Tooling: server-side Open-Meteo retrieval plus a Strands crop-guidance tool for starter crops.
- Reliability layer: verified weather snapshot, separate source-backed UI panel, and a narrow contradiction guard.
- Repository: https://github.com/PSP-YN/KrishiMitraAI

## What is genuinely implemented
- Live location resolution and seven-day weather retrieval.
- Crop and growth-stage input for ragi, paddy, maize, and groundnut.
- Strands agent orchestration and crop-guidance tool.
- English response mode; Kannada is disabled pending native-speaker validation.
- Source-backed weather facts displayed separately from generated advice.
- Conservative fallback when a defined weather contradiction is detected.
- Thirteen automated tests covering API success/failure paths, input validation, healthy/degraded model status, frontend asset delivery, and the weather-consistency guard.
- Health endpoint and live API request verified locally.

## Limitations to state clearly
- This is a hackathon prototype; it has not been field-tested with farmers.
- It is not an official KVK, ICAR, or government advisory.
- Kannada response quality failed a basic local-model check; it is disabled pending native-speaker review and a more reliable generation/translation path.
- The weather contradiction guard is phrase-based and narrow; it is not general fact verification.
- Forecasts are probabilistic and may change. Users must verify local field conditions.
- The current prototype uses a local model and has not been production-deployed or load-tested.

## Likely judge questions

**Why use an agent instead of a normal chatbot?**
The workflow has tool-backed steps: resolve a place, retrieve live weather, retrieve crop context, and then explain low-regret considerations. Strands provides the agent loop and tool orchestration. The model is not treated as the source of weather facts.

**How do you reduce hallucinations?**
The backend fetches weather independently, shows those values directly with source and timestamp, and checks generated prose for a narrow class of contradictions. If a contradiction is detected, the app withholds the generated text and returns conservative fallback guidance.

**Does the guard prove the answer is correct?**
No. It catches a limited set of explicit dry/no-rain claims when the forecast rainfall total is positive. It does not perform broad semantic verification. That limitation is documented.

**Can farmers act on the advice without an expert?**
The prototype intentionally avoids pesticide or fertilizer dosages, yield guarantees, and irreversible decisions. It directs users to local KVK and extension services for consequential decisions.

**What is the social impact?**
The intended impact is better understanding of local climate information by smallholder farmers. Impact has not yet been measured; the next phase is supervised usability research, native-speaker localization work, and field validation.

**How would you scale it?**
Move inference to a managed deployment, add caching and rate limits for forecast requests, monitor latency and tool failures, and integrate validated regional crop advisories. Run staged load tests before public rollout.

## Validation metrics for the next phase
- Forecast retrieval success rate and data freshness.
- Tool-call success rate and end-to-end response latency.
- Rate of unsupported or contradictory claims found in expert review.
- Farmer comprehension and perceived usefulness in supervised sessions.
- Correct referral to KVK or extension officers for high-risk questions.