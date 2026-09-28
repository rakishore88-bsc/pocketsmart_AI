# PocketSmart AI

PocketSmart AI is a FastAPI + Jinja2 web application based on the supplied project documentation. It provides three budget planners: Home Interior, Party Planning, and Jewelry. The backend supports registration/login, JWT tokens, session cookies, recommendation history, Gemini multimodal integration, and deterministic fallback recommendations when Gemini is unavailable.

## Important implementation note

The supplied document names Gemini 1.5 Flash Pro. Model availability changes over time, so the model is configurable with `GEMINI_MODEL`. The sample `.env` uses `gemini-2.5-flash`; if your Google AI account still exposes a different supported Gemini model, change that value. The integration uses Google's current `google-genai` Python SDK pattern.

The destination-platform links are search links, not claims of live inventory or live prices. Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO are represented as research destinations in the recommendation output. No scraping is performed by this starter implementation.

## 1. VS Code setup

1. Install Python 3.11 or newer.
2. Open this project folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows CMD:
```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install packages:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Copy `.env.example` to `.env`.

PowerShell:
```powershell
Copy-Item .env.example .env
```

macOS/Linux:
```bash
cp .env.example .env
```

7. Put your Gemini API key into `.env`:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

If you leave `GEMINI_API_KEY` blank, the app still runs using deterministic fallback recommendations, which is useful for UI and end-to-end testing.

## 2. Run

From the project root:
```bash
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## 3. Test

Run:
```bash
pytest -q
```

## 4. User flow

1. Register at `/register`.
2. Login at `/login`.
3. Open a planner.
4. Submit a budget and preferences.
5. The frontend calls the FastAPI endpoint.
6. The Gemini service generates structured recommendations when configured.
7. If Gemini is unavailable or the request fails, the deterministic fallback service returns a usable plan.
8. The result is stored in SQLite and appears in `/history` and `/dashboard`.

## API endpoints

- `POST /register`
- `POST /login`
- `POST /logout`
- `POST /token`
- `GET /api/session-info`
- `GET /api/session-data`
- `POST /api/generate-home`
- `POST /api/generate-party`
- `POST /api/generate-jewelry`
- `GET /api/recommendations-details/{history_id}`
- `GET /api/history`
- `GET /health`
- `GET /startup`

## Production notes

For production, replace the local SQLite store with PostgreSQL, use a secrets manager, enforce HTTPS, add CSRF protection for cookie-authenticated state-changing requests, add rate limiting, add centralized logging, add real partner/product APIs where licensed, and review all generated recommendations before presenting them as factual product availability or price information.
