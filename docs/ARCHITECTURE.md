# Architecture and trust boundaries

## Runtime components

| Component | Responsibility | Data source |
|---|---|---|
| Browser UI | Collects request inputs, calls the API, renders weather and advisory | User input + API JSON |
| FastAPI | Validates input, coordinates upstream data and agent execution | Local application |
| Open-Meteo geocoding | Resolves the entered place name to coordinates | Open-Meteo Geocoding API |
| Open-Meteo forecast | Retrieves current conditions and a seven-day daily forecast | Open-Meteo Forecast API |
| Strands Agents SDK | Runs the model-driven agent loop and invokes the crop tool | Strands SDK |
| Crop guidance tool | Supplies limited, conservative crop/stage context | Curated code-backed starter guidance |
| Ollama | Runs the configured local language model | Local model installation |
| Weather consistency guard | Withholds selected explicit no-rain/dry claims when the source forecast has positive total rainfall | Agent text + Open-Meteo daily precipitation |

## Request lifecycle

1. The browser validates required fields and sends `POST /api/advisory`.
2. Pydantic validates and trims the request. Only English is enabled. Kannada was tested but disabled because the local model's output did not meet a basic quality check.
3. The backend resolves the place name and fetches current conditions plus seven daily forecast records from Open-Meteo.
4. The server retains the returned weather payload and its retrieval timestamp as the source-backed record.
5. The backend creates a Strands agent using the configured Ollama model. The agent receives the farmer's request and the weather snapshot, and is instructed to invoke `get_crop_guidance`.
6. The backend computes a small forecast summary and checks generated prose for a limited set of explicit dry/no-rain phrases that conflict with positive forecast rainfall.
7. The API returns the source weather, generated advisory, guard status, model name, and timestamps. The browser renders the facts and model interpretation in separate sections and shows the seven-day forecast.

## API contract

### `GET /api/health`

The health response checks Ollama's `/api/tags` endpoint and verifies that the configured model name is installed. It reports `ok` only when that model is available; otherwise it reports `degraded`.

### `POST /api/advisory`

| Field | Type | Validation |
|---|---|---|
| `location` | string | 2–120 characters after whitespace trimming |
| `crop` | string | 2–80 characters after whitespace trimming |
| `growth_stage` | string | Optional; defaults to `Not sure`; maximum 100 characters |
| `language` | string | `English` only in this build |
| `question` | string | Optional default; 3–1000 characters |

Success includes the advisory text, agent status, seven-day summary, full source weather snapshot, generation timestamp, configured model, framework, and weather source. Weather or model failures return an HTTP error; the backend does not manufacture fallback weather values.

## Trust boundaries and limitations

- Open-Meteo values are the source of truth for the weather panel. The LLM is not the source of forecast facts.
- The model's crop advice is generated text, even when grounded by a crop tool. It is not independently agronomically verified.
- The weather guard is phrase-based and narrow. It catches selected obvious contradictions but is not semantic verification and can miss other errors.
- The crop knowledge base covers a few starter crops. Unknown crops receive generic caution, not fabricated crop-specific instructions.
- The health endpoint checks local model availability, not end-to-end weather or agent success.
- The prototype has no authentication, database, farmer accounts, audit trail, rate limiting, or multi-user load validation. It is intended for a controlled demonstration, not public production use.
- Forecast and agent outputs are time-sensitive. High-stakes decisions must be checked with local KVK/ICAR/extension officers and official advisories.

## Verification strategy

- Unit tests cover the phrase guard.
- API tests mock the upstream weather and model boundaries to cover successful response construction, upstream failure, conflict withholding, request validation, health reporting, and static asset delivery.
- A manual end-to-end smoke test uses the real Open-Meteo endpoint, local Ollama model, Strands agent, and browser UI. Record its date, selected crop/location, status, and limitations; do not treat one successful run as production validation.
