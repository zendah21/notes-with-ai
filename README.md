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