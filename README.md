# Pedagogial AI Agent

## Local DB Setup (Team Workflow)

Use local Postgres per team member, and apply the same migration files.

1. Create and activate a virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1`
2. Install shared dependencies:
   - `pip install -r server/requirements.txt`
3. Create your own `.env` at repo root:
   - `DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/DBNAME`
4. Run migration:
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/001_create_parsed_events.sql"`
5. Load parsed logs:
   - `python server/src/parse_event_logs.py --insert`
