# hcp-crm-ai

hcp-crm-ai is a starter CRM module for pharmaceutical field representatives. It turns natural language HCP visit notes into a structured draft with sentiment, compliance status, resource requests, and competitive intelligence.

## Folder Structure

```text
.
|-- frontend/              React, Redux, and Vite UI
|   `-- src/
|       |-- components/    Log interaction screen components
|       |-- services/      API client
|       `-- store/         Redux state
|-- backend/               FastAPI application
|   |-- app/
|   |   |-- agents/        LangGraph-ready agent and tool layer
|   |   |-- api/           REST routes
|   |   |-- core/          Settings
|   |   |-- models/        SQLAlchemy models
|   |   |-- schemas/       Pydantic contracts
|   |   `-- services/      Database helpers
|   `-- tests/             Backend tests
|-- infra/                 Local infrastructure files
```

## Run Locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Database:

```bash
cd infra
docker compose up -d
```

## Current Functionality

- React screen for logging HCP interactions in chat or form mode.
- Redux state for transcript, draft, loading, and error handling.
- FastAPI endpoint at `POST /api/interactions/analyze`.
- Agent-style orchestration for the five planned tools:
  - `log_interaction`
  - `edit_interaction`
  - `verify_compliance_guidelines`
  - `log_resource_request`
  - `extract_competitive_intelligence`
- SQLAlchemy model and PostgreSQL docker compose setup.

## Next Steps

- Replace heuristic extraction with LangGraph nodes backed by Groq.
- Add persistence endpoints for approving and editing interaction drafts.
- Add authentication and role-based access for field reps, managers, and compliance reviewers.
