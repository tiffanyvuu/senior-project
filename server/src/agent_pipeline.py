from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from src.context_builder import FEEDBACK_SPECS, build_feedback_prompt
    from src.current_state_metrics import (
        CognitionCategory,
        CurrentStateSnapshot,
        PersistenceCategory,
        analyze_current_state,
        fetch_events_from_db,
        upsert_snapshot,
    )
    from src.db import get_conn
    from src.feedback_policy import FeedbackClass, FeedbackClassInput, determine_feedback_class
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
except ImportError:
    from context_builder import FEEDBACK_SPECS, build_feedback_prompt
    from current_state_metrics import (
        CognitionCategory,
        CurrentStateSnapshot,
        PersistenceCategory,
        analyze_current_state,
        fetch_events_from_db,
        upsert_snapshot,
    )
    from db import get_conn
    from feedback_policy import FeedbackClass, FeedbackClassInput, determine_feedback_class
    from fetch_invite_hub_logs import (
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
    from parse_event_logs import insert_rows, parse_records


FEEDBACK_CLASS_TO_SPEC_NAME = {
    FeedbackClass.POSITIVE_FEEDBACK: "Positive Feedback",
    FeedbackClass.PARTIAL_CORRECTNESS: "Partial Correctness",
    FeedbackClass.CORRECTIVE_GUIDANCE: "Corrective Guidance",
    FeedbackClass.EVIDENCE_BASED_PRAISE: "Evidence-Based Praise",
    FeedbackClass.REASSURE: "Reassure",
    FeedbackClass.ERROR_FLAGGING: "Error Flagging",
    FeedbackClass.HOW_TO: "How To",
    FeedbackClass.INFORM: "Inform",
    FeedbackClass.NUDGE: "Hint",
    FeedbackClass.DIAGNOSE: "Encourage Testing (Diagnose)",
    FeedbackClass.QUESTION: "Question",
    FeedbackClass.ELABORATE: "Elaborate",
    FeedbackClass.REPEAT: "Remind",
    FeedbackClass.NEXT_STEP: "Next Step (this is a last resort action when others have not worked)",
}

DEFAULT_FEEDBACK_SPEC = "Inform"
DEFAULT_GO_MARS_TASK = "Complete GO-Mars tasks to score 5 points before the timer runs out."


@dataclass(frozen=True)
class AgentResponseBundle:
    response_text: str
    session_id: str | None
    progress_pct: float | None
    feedback_types: list[str]
    context_prompt: str | None
    synced_log_count: int
    snapshot: dict[str, Any] | None


def sync_invite_hub_logs() -> int:
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
        build_query_string(),
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


def fetch_latest_session_id(student_id: str) -> str | None:
    sql = """
    SELECT session_id
    FROM event_logs.parsed_events
    WHERE student_id = %(student_id)s
    ORDER BY event_ts DESC, id DESC
    LIMIT 1
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"student_id": student_id})
            row = cur.fetchone()
    return str(row[0]) if row else None


def snapshot_to_feedback_input(snapshot: CurrentStateSnapshot) -> FeedbackClassInput:
    return FeedbackClassInput(
        long_term_stalled_progress=snapshot.cognition == CognitionCategory.LONG_TERM_STALLED_PROGRESS,
        development_increases_progress=snapshot.cognition == CognitionCategory.DEVELOPMENT_INCREASES_PROGRESS,
        development_static_progress=snapshot.cognition == CognitionCategory.DEVELOPMENT_STATIC_PROGRESS,
        development_decreases_progress=snapshot.cognition == CognitionCategory.DEVELOPMENT_DECREASES_PROGRESS,
        trial_and_error=snapshot.cognition == CognitionCategory.TRIAL_AND_ERROR,
        code_abandonment=snapshot.cognition == CognitionCategory.CODE_ABANDONMENT,
        step_by_step_elimination=snapshot.cognition == CognitionCategory.STEP_BY_STEP_ELIMINATION,
        snap_n_test=snapshot.cognition == CognitionCategory.SNAP_N_TEST,
        expected_completion=snapshot.persistence == PersistenceCategory.EXPECTED_COMPLETION,
        high_persister=snapshot.persistence == PersistenceCategory.HIGH_PERSISTER,
        early_quitter=snapshot.persistence == PersistenceCategory.EARLY_QUITTER,
    )


def choose_feedback_types(snapshot: CurrentStateSnapshot) -> list[str]:
    feedback_input = snapshot_to_feedback_input(snapshot)
    feedback_classes = determine_feedback_class(feedback_input)
    feedback_type_names = [
        FEEDBACK_CLASS_TO_SPEC_NAME[feedback_class]
        for feedback_class in sorted(feedback_classes, key=lambda item: item.value)
        if feedback_class in FEEDBACK_CLASS_TO_SPEC_NAME
    ]
    if feedback_type_names:
        return feedback_type_names
    return [DEFAULT_FEEDBACK_SPEC]


def summarize_struggle(
    snapshot: CurrentStateSnapshot,
    *,
    student_message: str,
    source: str,
) -> str:
    if student_message.strip():
        return (
            f"The student asked: {student_message.strip()} "
            f"They are in {snapshot.playground} with {snapshot.progress_pct:.0f}% progress, "
            f"{snapshot.direction.value.lower()} progress direction, and {snapshot.cognition.value.lower()}."
        )
    if source == "help_button":
        return (
            f"The student pressed Help in {snapshot.playground}. "
            f"They are at {snapshot.progress_pct:.0f}% progress with "
            f"{snapshot.cognition.value.lower()} and {snapshot.persistence.value.lower()}."
        )
    return (
        f"The student is in {snapshot.playground} with {snapshot.progress_pct:.0f}% progress, "
        f"{snapshot.direction.value.lower()} direction, and {snapshot.cognition.value.lower()}."
    )


def build_student_response_text(
    snapshot: CurrentStateSnapshot,
    feedback_types: list[str],
    *,
    student_message: str,
) -> str:
    if snapshot.progress_pct >= 100.0:
        return (
            "You have already reached the 5-point GO-Mars goal. "
            "If you want to keep improving, try optimizing your path or aiming for more points."
        )
    if "How To" in feedback_types:
        return (
            f"You are at about {snapshot.progress_pct:.0f}% of the GO-Mars goal. "
            "Pick one 1-point task and test just that part of your code first."
        )
    if "Hint" in feedback_types or "Question" in feedback_types:
        return (
            f"You are at about {snapshot.progress_pct:.0f}% progress. "
            "Which single GO-Mars task are you trying to finish next?"
        )
    if "Reassure" in feedback_types:
        return (
            f"You are at about {snapshot.progress_pct:.0f}% progress in GO-Mars. "
            "Keep going one task at a time and test after each change."
        )
    if student_message.strip():
        return (
            f"I synced your latest GO-Mars logs and you are at about {snapshot.progress_pct:.0f}% progress. "
            "Try focusing on one task worth 1 point before changing the rest of the program."
        )
    return (
        f"I synced your latest GO-Mars logs and you are at about {snapshot.progress_pct:.0f}% progress. "
        "Try testing one task at a time so you can see exactly what is working."
    )


def build_agent_response(
    student_id: str,
    *,
    student_message: str,
    source: str,
) -> AgentResponseBundle:
    synced_log_count = sync_invite_hub_logs()
    session_id = fetch_latest_session_id(student_id)
    if session_id is None:
        response_text = (
            "I could not find recent GO-Mars logs for this student yet. "
            "Try running the project once, then ask again."
        )
        return AgentResponseBundle(
            response_text=response_text,
            session_id=None,
            progress_pct=None,
            feedback_types=[],
            context_prompt=None,
            synced_log_count=synced_log_count,
            snapshot=None,
        )

    events = fetch_events_from_db(student_id, session_id)
    snapshot = analyze_current_state(events)
    upsert_snapshot(snapshot)

    feedback_types = choose_feedback_types(snapshot)
    context_prompt = build_feedback_prompt(
        task=DEFAULT_GO_MARS_TASK,
        struggle=summarize_struggle(snapshot, student_message=student_message, source=source),
        feedback_types=feedback_types,
        feedback_specs=FEEDBACK_SPECS,
    )
    response_text = build_student_response_text(
        snapshot,
        feedback_types,
        student_message=student_message,
    )
    return AgentResponseBundle(
        response_text=response_text,
        session_id=session_id,
        progress_pct=snapshot.progress_pct,
        feedback_types=feedback_types,
        context_prompt=context_prompt,
        synced_log_count=synced_log_count,
        snapshot=snapshot.to_dict(),
    )
