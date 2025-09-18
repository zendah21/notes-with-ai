AI Notes (Live AI with Hugging Face Inference API)

Overview
- Flask + SQLite/SQLAlchemy + APScheduler + HTMX/Bootstrap
- Adds natural-language, live task editing via Hugging Face Inference API
- WebSocket streaming phases: thinking → parsed → applied → patch

HF Setup
- Create a Hugging Face token at huggingface.co/settings/tokens
- Create `.env` with:
  - HF_API_TOKEN=your_hf_token_here
  - HF_TASK_MODEL_TEXT2TEXT=google/flan-t5-base
  - HF_CLASSIFIER_MODEL_ZEROSHOT=facebook/bart-large-mnli
  - HF_NER_MODEL=dslim/bert-base-NER

Run
- python -m venv .venv
- . .venv/Scripts/Activate.ps1  (Windows)
- pip install -r requirements.txt
- set FLASK_APP=app.py; flask run --reload
- Open http://127.0.0.1:5000/ and /ai/console

Endpoints
- POST `/api/ai/interpret` – deterministic JSON tool-calling output
- GET `/ai/console` – command bar and live feed
- WS `/ws/ai` – streaming phases and row patch HTML

Deploy to Streamlit Community Cloud
- Push this repo to GitHub.
- In Streamlit, set entrypoint to `streamlit_app.py`.
- Add Secrets:
  - `HF_API_TOKEN`
  - Optional: `HF_TASK_MODEL_TEXT2TEXT`, `HF_CLASSIFIER_MODEL_ZEROSHOT`, `HF_NER_MODEL`
- The Streamlit app uses the same parsing/apply logic in-process; no WebSocket needed.

Local Streamlit run
- python -m pip install -r requirements.txt
- streamlit run streamlit_app.py

Examples
- Create: `Write polite rejection email`, tomorrow 10am, 30m, high, alerts 12h & 1h
- Move `Rise Advisory email` to Fri 9:30, set in progress, 20m, notify 1h
- New task `renew car reg` next Monday 8am, urgent, notify 24h/2h/0
- Mark `prepare slides` done

Notes
- Uses rule-first parsing (regex + dateutil) and falls back to HF models.
- All times normalized to UTC on save; UI shows UTC for simplicity.
- Simple in-memory rate-limiting (10 req/min/IP) for API.
- Logs prompts with basic PII redaction.
- Free-tier HF API may be slow; app caches responses for ~60s.
AI Notes – Live NLP Tasks with Hugging Face (Flask)

Overview
- Flask + SQLite/SQLAlchemy + APScheduler + HTMX/Bootstrap UI
- Natural‑language task editing via Hugging Face Inference API (free tier)
- WebSocket streaming: thinking → parsed → applied → patch
- Optional React + Tailwind demo frontend in `frontend/`

Features
- Create, update, complete/reopen, delete tasks with plain English
- Extracts: title, description, deadline (UTC), duration, priority, alerts, status, tags
- Multi‑item prompts: split on commas/semicolons/“+” and create multiple tasks in one go
- Ambiguity guard: leaves date empty when phrasing is unclear (“maybe Tue or Thu”)
- “Before Sunday” → 23:59 local that day (stored as UTC)
- Card UI with inline edit, deadline/duration/alerts editors, status/priority menus
- Light/Dark theme with polished dark palette and toggle

Quick Start (Windows PowerShell)
1) Create env
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
2) Install
   - `python -m pip install -r requirements.txt`
3) Configure Hugging Face
   - `Copy-Item .env.example .env`
   - Edit `.env`:
     - `HF_API_TOKEN=your_hf_token_here`
     - Optional: model overrides (see below)
4) Run
   - `flask --app app.py run --reload`
   - Open `http://127.0.0.1:5000/` and `http://127.0.0.1:5000/ai/console`

Environment Variables (.env)
- `HF_API_TOKEN` (required)
- `HF_TASK_MODEL_TEXT2TEXT` default `google/flan-t5-base`
- `HF_CLASSIFIER_MODEL_ZEROSHOT` default `facebook/bart-large-mnli`
- `HF_NER_MODEL` default `dslim/bert-base-NER`
- `DATABASE_URL` default `sqlite:///ai_notes.db` (recommend `sqlite:///instance/ai_notes.db`)
- `SECRET_KEY` development secret

Endpoints
- `POST /api/ai/interpret` → deterministic JSON tool‑calling output
- `GET /ai/console` → command bar & live stream
- `WS /ws/ai` → phases and row patch HTML

AI Contract (JSON)
Input:
```
{ "utterance": "move rise email to friday 9:30, set high, 20m, alert 1h",
  "context": { "now_tz": "Asia/Kuwait" } }
```
Output (example):
```
{ "operation":"update",
  "target": {"by":"title","value":"rise email"},
  "fields": {
    "priority":"high",
    "estimated_duration_minutes":20,
    "deadline_utc":"2025-09-19T06:30:00Z",
    "notify_offsets_minutes":[60]
  },
  "notes": "Rule-first parse with HF assist; times normalized to UTC" }
```

WebSocket Phases
- `{"phase":"thinking"}`
- `{"phase":"parsed","json":{...}}`
- Optional `{"phase":"need_clarification","options":[{"id","title"},…]}`
- `{"phase":"applied","task_id":123}`
- `{"phase":"patch","task_id":123,"html":"<div id=task-card-…>…</div>"}`

Example Prompts
- Create “Write polite rejection email” tomorrow 10am, 30m, high, alerts 12h and 1h
- Move “Rise Advisory email” to Fri 9:30, set in progress, 20m, notify 1h
- New task “renew car reg” next Monday 8am, urgent, notify 24h/2h/0
- Mark “prepare slides” done
- Multiple: Research project asap, giveaway gifts, grade students projects 2pm

Models & Timeouts
- Zero‑shot intent: `facebook/bart-large-mnli` (6s timeout)
- NER: `dslim/bert-base-NER` (6s timeout)
- Text2Text fallback: `google/flan-t5-base` (10s timeout)
- 60s caching and exponential retry/backoff for rate‑limits

How parsing works (rule‑first, model‑assist)
- Regex + dateutil extract duration, priority (“asap”→urgent), notifications (“alerts 12h & 1h”, “30m before”), status (“in progress”), and dates (local→UTC).
- Ambiguous wording (maybe/or between days) defers setting a date.
- NER adds coarse tags; Text2Text fills missing fields (`title`, `description`) when rules have low signal.
- WebSocket sharding: splits multi‑task prompts by commas/semicolons/“+” and applies each fragment.

UI Tips
- Dark theme toggle in navbar; refined contrast and chip colors in dark mode.
- Hover deadline chip to see local‑time tooltip.
- Use the Edit & Schedule drawer on a card for a single Save across time/duration/alerts.

Tests
- `pytest -q`
  - `tests/test_ai_router_parsing.py` (regex rules)
  - `tests/test_ai_apply_flows.py` (create/update/complete)
  - `tests/test_timezones.py` (UTC conversion)

Streamlit Frontend (optional)
- `pip install -r requirements.txt`
- `streamlit run streamlit_app.py`
- Set secrets in `.streamlit/secrets.toml` (see example file) or environment.

React + Tailwind Frontend (optional)
- `cd frontend && npm install && npm run dev`
- Open `http://localhost:5173` (proxy to Flask on /api and /ws).

Troubleshooting
- “no such column: task.description” → Stop app, restart; schema migrates automatically. If needed, delete `ai_notes.db` or use `sqlite:///instance/ai_notes.db`.
- Hugging Face 429 or slow: the app retries and caches; consider reducing concurrent prompts.
- WebSocket not connecting on prod: use a WS‑capable server (gunicorn + gevent‑websocket) or host on Render/Railway.

License
- For internal/demo use. Add your license as needed.
