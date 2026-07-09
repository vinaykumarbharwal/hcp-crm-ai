# AI-First CRM HCP Module

AI-First CRM HCP Module is a CRM workflow for pharmaceutical field representatives. It helps reps turn free-form health care provider visit notes or structured call fields into a reviewable and saved interaction draft with sentiment, compliance status, follow-up actions, resource requests, and competitive intelligence.

The implementation uses a React/Vite frontend with Redux, a FastAPI backend, a LangGraph HCP interaction agent, Groq LLM extraction with the `gemma2-9b-it` model, and SQLAlchemy persistence against PostgreSQL.

## Features

- Log HCP interactions from either chat-style notes or structured form fields.
- Run a LangGraph agent workflow for interaction analysis.
- Use Groq `gemma2-9b-it` for LLM-backed summarization and entity extraction when `GROQ_API_KEY` is configured.
- Generate a draft interaction summary for rep review.
- Detect resource follow-up requests.
- Flag basic compliance risk signals.
- Extract simple competitive intelligence.
- Edit an existing generated draft without losing unchanged fields.
- Persist analyzed and edited interaction drafts to SQL storage.
- Run a local PostgreSQL database through Docker Compose.

## LangGraph Agent

The HCP agent in `backend/app/agents/hcp_agent.py` manages the interaction workflow as a LangGraph state graph. The graph keeps the sales workflow explicit and auditable:

1. `log_interaction` extracts HCP, product, sentiment, action items, and summary. With a Groq API key, this tool calls `gemma2-9b-it`; without a key, local deterministic extraction keeps tests and demos runnable.
2. `verify_compliance` checks the transcript for high-risk claims such as off-label or guaranteed outcome language.
3. `log_resource_request` identifies requests for samples, studies, brochures, and materials.
4. `extract_competitive_intelligence` captures competitor or alternative therapy mentions.
5. `build_draft` combines tool outputs into the `InteractionDraft` returned to the UI and saved to the database.

The required sales tools live in `backend/app/agents/tools.py`: `log_interaction`, `edit_interaction`, `verify_compliance_guidelines`, `log_resource_request`, and `extract_competitive_intelligence`.

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- agents/        LangGraph orchestration, Groq adapter, and CRM tools
|   |   |-- api/           FastAPI route handlers
|   |   |-- core/          Application settings
|   |   |-- models/        SQLAlchemy models
|   |   |-- schemas/       Pydantic request and response contracts
|   |   `-- services/      Database and persistence helpers
|   `-- tests/             Backend unit and API tests
|-- frontend/
|   |-- public/            Static assets
|   `-- src/
|       |-- components/    Interaction form and assistant UI
|       |-- services/      API client
|       `-- store/         Redux state slices
|-- infra/
|   `-- docker-compose.yml Local PostgreSQL service
|-- .env.example           Combined local environment reference
```

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Docker Desktop or another Docker Compose-compatible runtime
- Groq API key for live LLM-backed extraction

## Environment Setup

Copy the example environment files before running the app:

```bash
copy .env.example .env
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

On macOS or Linux, use `cp` instead of `copy`.

Default local settings:

- Backend API: `http://localhost:8000`
- Frontend dev server: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Database URL: `postgresql+psycopg://postgres:postgres@localhost:5432/hcp_crm_ai`
- Primary LLM model: `gemma2-9b-it`
- Support model: `llama-3.3-70b-versatile`

Set `GROQ_API_KEY` in `backend/.env` to enable live Groq calls. The backend keeps a deterministic fallback for local tests when no API key is present.

## Run Locally

Start the database:

```bash
cd infra
docker compose up -d
```

Start the backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Start the frontend in a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://localhost:5173`.

## API

The FastAPI app exposes these local endpoints:

- `GET /health` - returns service health.
- `POST /api/interactions/analyze` - analyzes transcript or form fields, saves the draft, and returns the saved interaction draft with an `id`.
- `POST /api/interactions/edit` - applies form updates to an existing draft and persists the edited interaction.

Interactive API docs are available at `http://localhost:8000/docs` while the backend is running.

## Run Tests

Backend tests:

```bash
cd backend
pytest
```

Frontend production build check:

```bash
cd frontend
npm run build
```

## Development Notes

- Frontend API calls use `VITE_API_URL`, defaulting to `http://localhost:8000`.
- Backend settings load from `backend/.env` when running commands from the `backend` directory.
- CORS allows `http://localhost:5173` by default through `ALLOWED_ORIGINS`.
- Tests set `DATABASE_URL` to a local SQLite file so backend tests do not require Docker.
- PostgreSQL remains the local application database through `infra/docker-compose.yml`.

## Roadmap

- Add authentication and role-based access for reps, managers, and compliance reviewers.
- Add approval states for draft, submitted, manager-reviewed, and compliance-reviewed interactions.
- Expand compliance checks with product-specific rule sources.