# Pedagogial AI Agent

## Running Client and Server
1. Client:
   - `cd client`
   - `npm install`
   - `npm run dev`
2. Server:
   - `cd server`
   - `source .venv/bin/activate`
   - `uvicorn src.app:app --reload --log-level info`

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
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/004_create_messages.sql"`
   - `psql "$env:DATABASE_URL" -f "server/db/migrations/005_create_message_feedback.sql"`
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

## Navigator
- Go to https://docs.rc.ufl.edu/training/NaviGator_Toolkit/ and follow instructions to set up API key.
- Insert your API key in server/navigator_api_keys.example.json.
