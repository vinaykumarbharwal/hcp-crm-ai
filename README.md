# hcp-crm-ai

hcp-crm-ai is an AI-assisted CRM module for pharmaceutical field representatives. It helps a user turn quick HCP visit notes into a structured draft with the HCP name, product, sentiment, compliance status, resource requests, and competitor mentions.

The goal is to reduce manual form filling after a field visit. A representative can write a short note, review the AI-generated draft, and then save it after checking the details.

## What This Project Includes

- React frontend for entering HCP interaction notes.
- Redux store for form data, loading state, errors, and draft results.
- FastAPI backend for receiving notes and returning structured draft data.
- Agent-style backend layer with five CRM tools.
- PostgreSQL setup using Docker Compose.
- Simple backend test for the current agent flow.

## Folder Structure

```text
.
|-- backend/                         FastAPI backend
|   |-- .env.example                 Backend environment example
|   |-- requirements.txt             Python dependencies
|   |-- app/
|   |   |-- main.py                   FastAPI app entry point
|   |   |-- agents/
|   |   |   |-- hcp_agent.py           Agent workflow
|   |   |   `-- tools.py               CRM tool logic
|   |   |-- api/
|   |   |   `-- interactions.py        Interaction API routes
|   |   |-- core/
|   |   |   `-- config.py              App settings
|   |   |-- models/
|   |   |   `-- interaction.py         Database model
|   |   |-- schemas/
|   |   |   `-- interaction.py         Request and response schemas
|   |   `-- services/
|   |       `-- database.py           Database connection helper
|   `-- tests/
|       `-- test_agent_tools.py      Backend test
|-- frontend/                        React frontend
|   |-- .env.example                 Frontend environment example
|   |-- index.html                   Vite HTML entry file
|   |-- package.json                 Frontend dependencies and scripts
|   `-- src/
|       |-- App.jsx                  Main app layout
|       |-- main.jsx                 React entry point
|       |-- styles.css               App styling
|       |-- components/
|       |   |-- InteractionForm.jsx    Input form and mode switch
|       |   `-- InteractionSummary.jsx Draft result panel
|       |-- services/
|       |   `-- api.js                Backend API client
|       `-- store/
|           |-- interactionSlice.js   Redux state slice
|           `-- store.js             Redux store setup
|-- infra/
|   `-- docker-compose.yml           Local PostgreSQL setup
|-- .env                             Local environment values
|-- .env.example                     Shared environment example
|-- .gitignore                       Files ignored by git
`-- README.md                        Project guide
```

## Requirements

Install these before running the project:

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- Docker Desktop

## Environment Files

The project has these environment files:

```text
.env                  Local values used during development
.env.example          Shared example for the full project
backend/.env.example  Backend-specific example
frontend/.env.example Frontend-specific example
```

Important values:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/hcp_crm_ai
GROQ_API_KEY=your_api_key_here
VITE_API_URL=http://localhost:8000
```

`GROQ_API_KEY` can stay empty while using the current rule-based demo logic. Add a real key when the backend is upgraded to call Groq models.

## Setup Steps

Follow this order for local development.

## 1. Start the Database

```bash
cd infra
docker compose up -d
```

This starts a local PostgreSQL database named `hcp_crm_ai`.

## 2. Start the Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

## 3. Start the Frontend

Open a new terminal and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

## Main API Endpoint

```text
POST /api/interactions/analyze
```

This endpoint accepts one field, `transcript`, and returns a draft interaction summary.

Example request:

```json
{
  "transcript": "Met Dr. Sharma. Discussed product CardioMax. He was interested but worried about pricing and requested study material."
}
```

Example response:

```json
{
  "hcp_name": "Dr. Sharma",
  "product": "CardioMax",
  "sentiment": "positive",
  "action_items": ["Send requested resources"],
  "compliance_status": "clear",
  "resource_request": "resource_follow_up_needed",
  "competitive_intelligence": null,
  "draft_summary": "Dr. Sharma discussed CardioMax with positive sentiment. Compliance status: clear."
}
```

## Test the API Manually

After the backend is running, you can test it from PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/api/interactions/analyze" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"transcript":"Met Dr. Sharma. Discussed product CardioMax. He was interested and requested study material."}'
```

You can also open the FastAPI Swagger page in the browser:

```text
http://localhost:8000/docs
```

## How It Works

1. The user enters HCP visit notes in the frontend.
2. The frontend sends the notes to the FastAPI backend.
3. The backend agent reads the notes and runs the CRM tools.
4. The backend returns a structured draft.
5. The frontend shows the draft for review.
6. In a future version, the approved draft can be saved to the database.

## Current Agent Tools

The backend currently has these tool functions:

```text
log_interaction                  Extracts HCP, product, sentiment, and action items
edit_interaction                 Applies safe updates to an existing interaction object
verify_compliance_guidelines     Flags risky phrases for review
log_resource_request             Detects sample, study, brochure, or material requests
extract_competitive_intelligence Detects competitor or alternative product mentions
```

## Run Checks

Check backend syntax:

```bash
python -m compileall backend\app backend\tests
```

Run the backend test from the `backend` folder after installing dependencies:

```bash
pytest
```

## Common Problems

If the frontend cannot connect to the backend, check that the backend is running at `http://localhost:8000` and that `VITE_API_URL` points to the same URL.

If Docker fails to start PostgreSQL, check whether another database is already using port `5432`.

If Python cannot import `app`, run backend commands from the `backend` folder.

If the AI result looks basic, that is expected in the current starter version. The current logic is rule-based and can later be replaced with LangGraph and Groq model calls.

## Current Status

This is a starter version of the project. It has a working frontend and backend flow, but the AI extraction is currently simple rule-based logic. The code is ready to be upgraded with LangGraph and Groq API calls.

## Next Improvements

- Add real LangGraph nodes for the agent workflow.
- Connect Groq models for better note understanding.
- Save approved interaction drafts to PostgreSQL.
- Add login and role-based access.
- Add a compliance review screen.
