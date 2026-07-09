# AI-First CRM HCP Module

AI-First CRM HCP Module is a starter CRM workflow for pharmaceutical field representatives. It helps reps turn free-form health care provider visit notes or structured call fields into a reviewable interaction draft with sentiment, compliance status, follow-up actions, resource requests, and competitive intelligence.

The current implementation uses a React/Vite frontend and a FastAPI backend with agent-style Python tools. The agent layer is intentionally separated so the heuristic extraction code can later be replaced with LangGraph and model-backed nodes without changing the API contract.

## Features

- Log HCP interactions from either chat-style notes or structured form fields.
- Generate a draft interaction summary for rep review.
- Detect resource follow-up requests.
- Flag basic compliance risk signals.
- Extract simple competitive intelligence.
- Edit an existing generated draft without losing unchanged fields.
- Run a local PostgreSQL database through Docker Compose for future persistence work.

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- agents/        Agent orchestration and extraction tools
|   |   |-- api/           FastAPI route handlers
|   |   |-- core/          Application settings
|   |   |-- models/        SQLAlchemy models
|   |   |-- schemas/       Pydantic request and response contracts
|   |   `-- services/      Database helpers
|   `-- tests/             Backend unit and API tests
|-- frontend/
|   |-- public/            Static assets
|   `-- src/
|       |-- components/    Interaction form and summary UI
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

`GROQ_API_KEY`, `PRIMARY_MODEL`, and `SUPPORT_MODEL` are included for the planned model-backed agent flow. The current heuristic implementation and tests run without a Groq API key.

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
- `POST /api/interactions/analyze` - analyzes transcript or form fields and returns an interaction draft.
- `POST /api/interactions/edit` - applies form updates to an existing draft.

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
- The database model and Docker Compose service are in place, but the current analyze/edit endpoints return drafts rather than persisting approved interactions.

## Roadmap

- Replace heuristic extraction with LangGraph nodes backed by Groq models.
- Add persistence endpoints for approving and editing interaction drafts.
- Add authentication and role-based access for reps, managers, and compliance reviewers.
- Expand compliance checks with product-specific rule sources.
