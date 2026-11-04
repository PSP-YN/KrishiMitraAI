# KrishiMitra AI — Demo Video Script (target: 2:40)

## Recording plan

Record the actual local app at `http://localhost:8000`. Keep the video under 3 minutes. Hide desktop notifications and do not show credentials, private email, or AWS sandbox secrets.

### 0:00–0:20 — Problem

Narration: “Smallholder farmers may receive weather data without a clear explanation of what it means for their crop. KrishiMitra turns a live forecast into accessible climate context, with source data visible.”

Show the landing page and climate brief form.

### 0:20–0:45 — Inputs

Enter location `Mysuru, Karnataka`, crop `Ragi`, growth stage `Vegetative`, language `English`, and ask: “What should I monitor this week?”

### 0:45–1:25 — Agent execution

Generate the climate advisory and show the returned response.

Narration: “The backend fetches real Open-Meteo forecast data. Strands Agents SDK coordinates the model and crop-guidance tool. The application does not rely on the model's memory for weather facts.”

### 1:25–1:55 — Evidence and safety

Point to the verified weather snapshot: temperature, current rainfall, seven-day rainfall total, probability, source, and retrieval time.

Narration: “Weather facts are displayed separately from model interpretation. A narrow consistency guard catches common explicit no-rain or dry-forecast claims when the live seven-day rainfall total is positive. It is a targeted safeguard, not a guarantee of correctness.”

### 1:55–2:20 — Social good and accessibility

Show that the current prototype is English-only. Explain that Kannada localization is planned but deliberately disabled until native-speaker review confirms that the model's agronomic wording is understandable and accurate.

Narration: “The goal is to make climate information easier to interpret for smallholder farmers. Kannada localization is a planned next step, not a currently enabled feature. This is a decision-support prototype, not an official advisory.”

### 2:20–2:40 — Technical close

Show the GitHub repository and architecture briefly.

Narration: “KrishiMitra is open source and built with Strands Agents SDK, FastAPI, Ollama, and Open-Meteo. The next step is supervised validation with farmers and local agricultural extension officers.”

## Checklist

- [ ] `/api/health` responds.
- [ ] Strands agent request completes.
- [ ] Open-Meteo returns current data and a seven-day forecast.
- [ ] Weather facts match the source response.
- [ ] Weather guard unit tests pass.
- [ ] The demo clearly states that Kannada localization is not enabled in this build.
- [ ] Browser zoom is readable and notifications are hidden.
- [ ] Final video is under 180 seconds.
- [ ] Upload to a public/unlisted video URL and add it to Builder Center.
