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

## Fetch VEX Logs From Invite Institute Hub

Store your Invite Hub credentials in the repo root `.env`:

- `INVITE_HUB_BASE_URL=https://inviteinstitutehub.org`
- `INVITE_HUB_USERNAME=YOUR_USERNAME`
- `INVITE_HUB_PASSWORD=YOUR_PASSWORD`

Then fetch the latest VEX logs and save them locally:

- `python server/src/fetch_invite_hub_logs.py`

Fetch and immediately parse + insert into Postgres:

- `python server/src/fetch_invite_hub_logs.py --insert`

Useful filters:

- `python server/src/fetch_invite_hub_logs.py --student-id test_student`
- `python server/src/fetch_invite_hub_logs.py --class-code VUUUFR --event-type blockMoved`
- `python server/src/fetch_invite_hub_logs.py --date-from 2026-03-01T00:00 --date-to 2026-03-31T23:59`

The fetcher defaults to the bulk download endpoint. If needed, you can fall back to paged API retrieval:

- `python server/src/fetch_invite_hub_logs.py --method paged --page-size 500`

To test incremental syncing, first seed the current newest upstream log ID:

- `python server/src/fetch_invite_hub_logs.py --seed-head`

Then later fetch only logs newer than that saved cursor:

- `python server/src/fetch_invite_hub_logs.py --incremental`

The incremental cursor is stored in `server/src/invite_hub_sync_state.json`.
