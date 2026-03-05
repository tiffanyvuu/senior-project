import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def main() -> None:
    input_path = Path(__file__).with_name("sample.json")
    parsed_rows = parse_file(input_path)
    print(json.dumps(parsed_rows[:3], indent=2))
    print(f"Parsed {len(parsed_rows)} records.")


if __name__ == "__main__":
    main()
