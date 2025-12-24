# Accento Fullstack Application – Technical Documentation

## Overview

- Accento is an accent-aware speech recognition app. Users upload or record audio, the backend forwards it to a Hugging Face model via Gradio client, and the frontend displays the detected accent, confidence, transcript, and STT engine.
- The project comprises a Flask backend (`backend/app.py`) and a Create React App frontend (`frontend/frontend`).

## Architecture

- Frontend (`React` + `axios`):
  - UI for choosing/recording audio and visualizing results.
  - Posts `multipart/form-data` with an `audio` file to the backend `POST /api/predict`.
  - Parses backend response (string or JSON) and updates UI state.
- Backend (`Flask` + `gradio_client`):
  - Exposes `POST /api/predict` to accept `.wav`/`.mp3` files.
  - Temporarily saves the file and calls the Hugging Face Space/model via `gradio_client.Client.predict`.
  - Returns JSON with prediction.
  - CORS enables the frontend origin to access `/api/*` routes.

## Backend

- File: `backend/app.py`
- Key libraries: `flask`, `flask_cors`, `gradio_client`, `tempfile`, `os`.
- CORS:
  - Configured to allow origins from `https://accento-fullstack-project.netlify.app` for routes under `/api/*`.
- HF model integration:
  - `client = Client("Gitanjaliyadav29/accento-ml-model")`
  - `client.predict(audio_file=handle_file(temp_path), api_name="/predict")` passes the saved audio to the model.
- Routes:
  - `GET /`: health message `{ message: "Accento Flask API is live!", status: "OK" }`.
  - `POST /api/predict`:
    - Validates presence of `audio` file and extension (`.wav` or `.mp3`).
    - Saves to a temp path, predicts via HF client, returns `{ prediction: ... }`.
    - Cleans temp file in `finally`.
- Error handling:
  - Returns `400` for missing/invalid file types.
  - Returns `500` with error message for model failures; logs error to stdout.
- Runtime and dependencies:
  - `requirements.txt`: `flask`, `flask-cors`, `gradio_client`, `gunicorn`.
  - `runtime.txt`: `python-3.11.8` for platform runtime pinning.
- Local run:
  - `python backend/app.py` starts Flask at `http://0.0.0.0:5000`.
  - For production, use `gunicorn` (e.g., `gunicorn -w 4 -b 0.0.0.0:5000 app:app` from `backend/`).

## Frontend

- Bootstrapped with Create React App.
- File: `frontend/frontend/package.json`
  - Scripts: `start`, `build`, `test`, `eject` via `react-scripts`.
  - Dependencies: `react`, `react-dom`, `axios`, Testing Library packages, `web-vitals`.
- Entry: `src/index.js`
  - Creates root and renders `<App />` inside `React.StrictMode`.
  - Calls `reportWebVitals()` (no-op unless you pass a logger/endpoint).
- Main component: `src/App.js`
  - State:
    - `audioFile`, `previewUrl`: user-selected or recorded audio and its preview URL.
    - `error`, `loading`: UX around upload and prediction.
    - `isRecording`: microphone capture state using `MediaRecorder`.
    - `accent`, `confidence`, `sttEngine`, `transcript`, `wordCount`: derived from backend response.
    - `showSplash`, `showInfo`: control splash screen and info modal visibility.
  - Config:
    - `BACKEND_URL`: `https://accento-fullstack-project.onrender.com/api/predict` (deployed backend). In development, swap to local (e.g., `http://localhost:5000/api/predict`).
  - File input handling:
    - Validates `.wav`/`.mp3` via `validateAudioFile`.
    - Generates `previewUrl` with `URL.createObjectURL` and revokes it on cleanup.
  - Recording:
    - Uses `navigator.mediaDevices.getUserMedia({ audio: true })`.
    - Captures chunks via `MediaRecorder` and converts WebM → WAV in `blobToWav` by decoding with `AudioContext` and crafting a PCM WAV header.
  - Upload:
    - Builds `FormData`, appends `audio`, posts to `BACKEND_URL` via `axios`.
  - Response parsing:
    - Accepts either a string or a structured object.
    - `parsePredictionString(text)` extracts accent, confidence (0–1 or percentage), STT engine, transcript using regex:
      - `Accent\s*:\s*([^(
]+?)(?=\s*\(|\s*Engine\s*:|\s*Transcript\s*:|$)`
      - `conf(?:idence)?\s*:\s*([0-9]+(?:\.[0-9]+)?)`
      - `(?:STT\s*Engine|Engine)\s*:\s*([^\n]+?)(?=\s*Transcript\s*:|$)`
      - `Transcript\s*:\s*(.+)$`
    - Normalizes confidence (if > 1, treats as percentage and divides by 100).
    - Computes `wordCount` by splitting `transcript` on whitespace.
  - UI:
    - File choose, start/stop recording, upload & analyze.
    - Audio preview and animated recording bars.
    - Result cards: accent + confidence progress bar, STT engine chip, transcript box with word count.
    - Splash screen (`SplashScreen`) fades out and triggers `InfoModal` auto-show.
    - Info modal (`InfoModal`) displays a rotating image slider and description.
- Styles:
  - `src/App.css`: theme variables, layout, buttons, cards, progress, recording visualizer, chips, transcript box, footer, etc.
  - `src/SplashScreen.css`: full-screen splash with fade-out, loader, animations.
  - `src/InfoModal.css`: overlay, card, slider controls, transitions.
- HTML template: `public/index.html`
  - Sets meta tags, preconnect to Google Fonts, loads Inter font, CRA placeholders (`%PUBLIC_URL%`).
  - Title: "Accento – Accent Classifier".

## API Contract

- Endpoint: `POST /api/predict`
  - Content-Type: `multipart/form-data`
  - Form field: `audio` (file, `.wav` or `.mp3`)
- Success response:
  - `{ "prediction": string }` where string may include Accent/Confidence/Engine/Transcript lines; or
  - `{ "prediction": { accent?: string, confidence?: number, stt_engine?: string, transcription?: string } }`
- Error responses:
  - `400`: `{ error: "No audio file uploaded" }` or `{ error: "Invalid file type..." }`
  - `500`: `{ error: "..." }` when HF call fails.

## Data Flow

- User selects or records audio in the frontend.
- Frontend constructs `FormData` (`audio` file) and POSTs to backend.
- Backend saves file to temp, forwards file to Hugging Face model via `gradio_client`.
- Backend returns JSON `{ prediction }`.
- Frontend parses response (string or object) and updates UI: accent, confidence, transcript, STT engine, word count.

## Environment & Configuration

- Backend CORS allows `https://accento-fullstack-project.netlify.app` to call `/api/*`.
- Frontend uses `BACKEND_URL` pointing to Render; for local dev set `REACT_APP_BACKEND_URL` and read it in code to avoid hardcoding.
- Recommended:
  - Use environment variables for backend model ID, allowed origins, and timeouts.
  - Do not commit local `venv` to source control; rely on `requirements.txt` for dependency install.

## Development

- Backend:
  - Create virtual environment and install deps:
    - `python -m venv .venv`
    - `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
    - `pip install -r requirements.txt`
  - Run: `python backend/app.py`
  - Test health: `GET http://localhost:5000/` → `{ message: ..., status: "OK" }`.
- Frontend:
  - `cd frontend/frontend`
  - `npm install`
  - `npm start` → `http://localhost:3000`
  - Update a `.env` file with `REACT_APP_BACKEND_URL=http://localhost:5000/api/predict` and read it in `App.js`.

## Deployment

- Backend:
  - Container or PaaS (Render/Heroku/Fly.io). Use `gunicorn` and multiple workers:
    - `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
  - Configure environment variables: `HF_MODEL_ID`, `CORS_ALLOWED_ORIGINS`, `REQUEST_TIMEOUT`.
  - Add health endpoint `/` and consider `/healthz` for liveness probes.
- Frontend:
  - Build: `npm run build` and deploy to Netlify/Vercel.
  - Set environment variable `REACT_APP_BACKEND_URL` at build time.
  - Enable asset compression (gzip/brotli) and a CDN.

## Scalability & Production Readiness

- API robustness:
  - Timeouts and retries around HF client with circuit breaker (e.g., `tenacity` in Python).
  - Input validation: enforce max file size, sample rate constraints, and duration limits (reject > N seconds).
  - Rate limiting and auth (API key or JWT) to prevent abuse.
- Performance:
  - Use `FastAPI` + `uvicorn` for higher throughput if needed; or increase `gunicorn` workers and tune worker class.
  - Offload HF calls to a queue (Celery/RQ) and notify via polling or websockets if latency is high.
  - Cache repeated predictions (hash file content) using Redis.
- Storage:
  - Stream uploads and avoid writing to disk when possible; or use ephemeral temp dirs.
  - Persist audio to object storage (S3/GCS) if needed.
- Observability:
  - Structured logging (JSON) with request IDs.
  - Metrics (Prometheus/OpenTelemetry) for request rate, latency, errors.
  - Error tracking (Sentry) with alerts.
- Security:
  - Strict CORS (env-driven, not hardcoded), HTTPS everywhere.
  - Validate MIME types server-side, sanitize filenames, and use scanned libraries for security.
  - Limit upload sizes and concurrent requests.
- Frontend hardening:
  - Load `BACKEND_URL` from `process.env` and handle 4xx/5xx uniformly.
  - Accessibility checks and performance budgets (Lighthouse/Web Vitals).
- CI/CD:
  - Automated tests (unit for regex parsing, integration for `/api/predict`).
  - Build, test, lint on push; deploy on main with environment-specific configs.

## Testing Strategy

- Backend:
  - Unit tests for file type validation, error handling, and HF client wrapper.
  - Integration tests using a stubbed HF endpoint to return synthetic predictions.
- Frontend:
  - Unit tests for `parsePredictionString` covering multiple formats.
  - Component tests for upload/record flows with mocked `axios`.

## Known Considerations

- `BACKEND_URL` is hardcoded; move to environment variable for flexibility.
- CORS origin is single-host; support multiple origins via env config.
- Local `venv` is present under `backend/venv`; typically you exclude it from VCS.

## Future Enhancements

- Support additional audio formats and automatic conversion server-side.
- Real-time streaming transcription with WebRTC/WebSocket.
- Multi-language accent detection and confidence calibration.
- Persist prediction history and analytics dashboards.

## Quick Start

- Run backend locally: `python backend/app.py`.
- Run frontend locally:
  - `cd frontend/frontend && npm install && npm start`.
  - Update code to read `process.env.REACT_APP_BACKEND_URL` for the API endpoint.