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
4. Run migrations:
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/001_create_parsed_events.sql"`
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/002_create_state_snapshots.sql"`
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/003_add_playground_data_to_parsed_events.sql"`
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/004_create_chat_messages.sql"`
5. Load parsed logs:
   - `python server/src/parse_event_logs.py --insert`

## Fetch VEX Logs From Invite Institute Hub

Store your Invite Hub credentials in the repo root `.env`:

- `INVITE_HUB_BASE_URL=https://inviteinstitutehub.org`
- `INVITE_HUB_USERNAME=YOUR_USERNAME`
- `INVITE_HUB_PASSWORD=YOUR_PASSWORD`

Then fetch the latest VEX logs and save them locally:

- `python server/src/fetch_invite_hub_logs.py`

Fetch and immediately parse + insert into Postgres:

- `python server/src/fetch_invite_hub_logs.py --insert`
