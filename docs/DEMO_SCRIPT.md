# KrishiMitra AI — Demo Video Script (target: 2:40)

## Recording plan

Use a screen recording of the local app at `http://localhost:8000`. Keep the video under 3 minutes. Do not show credentials, private email, or AWS sandbox secrets.

### 0:00–0:20 — Problem

**Narration:** “Smallholder farmers may receive weather data without a clear explanation of what it means for their crop. KrishiMitra turns a live forecast into accessible climate context, with source data visible.”

Show the landing page and the climate brief form.

### 0:20–0:45 — Inputs

Enter:
- Location: Mysuru, Karnataka
- Crop: Ragi
- Growth stage: Vegetative
- Language: English

Ask: “What should I monitor this week?”

### 0:45–1:25 — Agent execution

Click Generate climate advisory. Show the loading state and the returned response.

**Narration:** “The backend fetches real Open-Meteo forecast data. Strands Agents SDK coordinates the model and crop guidance tool. The agent is not simply answering from its training data.”

### 1:25–1:55 — Evidence and safety

Point to the verified weather snapshot: temperature, current rainfall, seven-day rainfall total, probability, source, and retrieval time.

**Narration:** “Weather facts are displayed separately from model interpretation. Forecasts are probabilistic, so the app avoids treating them as certainty. The consistency guard blocks model text that contradicts the live data.”

### 1:55–2:20 — Social good and accessibility

Switch the response language to Kannada and show a second request if time permits.

**Narration:** “The goal is accessible climate information for smallholder farmers, including Kannada-speaking users. This is a decision-support prototype—not an official advisory.”

### 2:20–2:40 — Technical close

Show the GitHub repository and architecture diagram briefly.

**Narration:** “KrishiMitra is open source and built with Strands Agents SDK, FastAPI, Ollama, and Open-Meteo. The next step is supervised validation with farmers and local agricultural extension officers.”

## Checklist before recording

- [ ] Backend responds to `/api/health`.
- [ ] Ollama model is loaded and the Strands tool call succeeds.
- [ ] Open-Meteo returns current data.
- [ ] Weather facts match the API response.
- [ ] AI contradiction guard is tested.
- [ ] Browser zoom is readable and notifications are hidden.
- [ ] Video is under 180 seconds.
- [ ] Upload to a public video URL and add it to the Builder Center project.