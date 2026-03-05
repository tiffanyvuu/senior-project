import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from psycopg.types.json import Json

from db import get_conn


SOURCE = "sample.json"


def parse_iso_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    # normalize trailing Z for Python's fromisoformat compatibility
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return value
    return dt.astimezone(timezone.utc).isoformat()


def parse_json_string(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return value


def parse_json_string_or_none(value: Any) -> Any:
    parsed = parse_json_string(value)
    if isinstance(parsed, str):
        return None
    return parsed


def require_non_null(record_id: Any, field_name: str, value: Any) -> Any:
    if value is None:
        raise ValueError(f"Record {record_id} is missing required field: {field_name}")
    return value


def build_parsed_event(raw_record: dict[str, Any]) -> dict[str, Any]:
    record_id = raw_record.get("id")
    payload = parse_json_string(raw_record.get("content"))
    if not isinstance(payload, dict):
        raise ValueError(f"Record {record_id} has invalid content JSON")

    session_id = require_non_null(record_id, "sessionID", payload.get("sessionID"))
    student_id = require_non_null(record_id, "studentID", payload.get("studentID"))
    event_ts = require_non_null(record_id, "timestamp", parse_iso_timestamp(payload.get("timestamp")))
    event_type = require_non_null(record_id, "eventType", payload.get("eventType"))

    return {
        "session_id": session_id,
        "student_id": student_id,
        "class_code": payload.get("classCode"),
        "event_ts": event_ts,
        "event_type": event_type,
        "program_type": payload.get("programType"),
        "playground": payload.get("playground"),
        "project_json": parse_json_string_or_none(payload.get("project")),
        "block_event_data_json": parse_json_string_or_none(payload.get("blockEventData")),
        "has_orphans": payload.get("hasOrphans"),
        "switch_block_count": payload.get("switchBlockCount"),
        "error_message": payload.get("errorMessage"),
        "source": SOURCE,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def parse_file(input_path: Path) -> list[dict[str, Any]]:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    return [build_parsed_event(record) for record in records]


def insert_rows(rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    sql = """
    INSERT INTO event_logs.parsed_events (
        session_id,
        student_id,
        class_code,
        event_ts,
        event_type,
        program_type,
        playground,
        project_json,
        block_event_data_json,
        has_orphans,
        switch_block_count,
        error_message,
        source
    )
    VALUES (
        %(session_id)s,
        %(student_id)s,
        %(class_code)s,
        %(event_ts)s,
        %(event_type)s,
        %(program_type)s,
        %(playground)s,
        %(project_json)s,
        %(block_event_data_json)s,
        %(has_orphans)s,
        %(switch_block_count)s,
        %(error_message)s,
        %(source)s
    )
    """

    payloads = [
        {
            "session_id": row["session_id"],
            "student_id": row["student_id"],
            "class_code": row["class_code"],
            "event_ts": row["event_ts"],
            "event_type": row["event_type"],
            "program_type": row["program_type"],
            "playground": row["playground"],
            "project_json": Json(row["project_json"]) if row["project_json"] is not None else None,
            "block_event_data_json": Json(row["block_event_data_json"]) if row["block_event_data_json"] is not None else None,
            "has_orphans": row["has_orphans"],
            "switch_block_count": row["switch_block_count"],
            "error_message": row["error_message"],
            "source": row["source"],
        }
        for row in rows
    ]

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, payloads)
    return len(payloads)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse raw event logs into parsed_events records.")
    parser.add_argument(
        "--input",
        default=str(Path(__file__).with_name("sample.json")),
        help="Path to JSON file containing raw log records",
    )
    parser.add_argument(
        "--insert",
        action="store_true",
        help="Insert parsed rows into event_logs.parsed_events using DATABASE_URL",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    parsed_rows = parse_file(input_path)
    if args.insert:
        inserted = insert_rows(parsed_rows)
        print(f"Inserted {inserted} rows into event_logs.parsed_events.")
        return

    print(json.dumps(parsed_rows[:3], indent=2))
    print(f"Parsed {len(parsed_rows)} records from {input_path}.")


if __name__ == "__main__":
    main()
