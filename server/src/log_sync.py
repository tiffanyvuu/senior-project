from __future__ import annotations

import os
from pathlib import Path

try:
    from src.fetch_invite_hub_logs import (
        DEFAULT_BASE_URL,
        DEFAULT_PAGE_SIZE,
        DEFAULT_STATE_PATH,
        build_query_string,
        fetch_vex_logs_incremental,
        get_auth_token,
        load_local_env,
        parse_source_log_id,
        read_sync_state,
        write_sync_state,
    )
    from src.parse_event_logs import insert_rows, parse_records
except ModuleNotFoundError:
    from server.src.fetch_invite_hub_logs import (
        DEFAULT_BASE_URL,
        DEFAULT_PAGE_SIZE,
        DEFAULT_STATE_PATH,
        build_query_string,
        fetch_vex_logs_incremental,
        get_auth_token,
        load_local_env,
        parse_source_log_id,
        read_sync_state,
        write_sync_state,
    )
    from server.src.parse_event_logs import insert_rows, parse_records


def sync_invite_hub_logs(*, student_id: str | None = None) -> int:
    load_local_env()
    base_url = os.getenv("INVITE_HUB_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    token = get_auth_token(base_url)
    state_path = Path(DEFAULT_STATE_PATH)
    state = read_sync_state(state_path)
    last_source_log_id = state.get("last_source_log_id")
    if last_source_log_id is not None and not isinstance(last_source_log_id, int):
        raise RuntimeError("Sync state last_source_log_id must be an integer.")

    raw_records = fetch_vex_logs_incremental(
        base_url,
        token,
        build_query_string(student_id=student_id),
        page_size=DEFAULT_PAGE_SIZE,
        last_source_log_id=last_source_log_id,
    )
    if not raw_records:
        return 0

    parsed_rows = parse_records(raw_records, "invite_hub_incremental")
    insert_rows(parsed_rows)
    newest_source_log_id = max(parse_source_log_id(record) for record in raw_records)
    write_sync_state(state_path, newest_source_log_id)
    return len(raw_records)
