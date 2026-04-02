from __future__ import annotations

from typing import Literal

try:
    from src.db import get_conn
except ImportError:
    from db import get_conn


ChatRole = Literal["student", "assistant"]
ChatSource = Literal["chat", "help_button"]


def insert_chat_message(
    *,
    message_id: str,
    student_id: str,
    role: ChatRole,
    message_text: str,
    session_id: str | None = None,
    source: ChatSource | None = None,
    parent_message_id: str | None = None,
    feedback_classes: list[str] | None = None,
) -> None:
    sql = """
    INSERT INTO messages.chat_messages (
        id,
        session_id,
        student_id,
        role,
        source,
        parent_message_id,
        message_text,
        feedback_classes
    )
    VALUES (
        %(id)s::uuid,
        %(session_id)s::uuid,
        %(student_id)s,
        %(role)s,
        %(source)s,
        %(parent_message_id)s::uuid,
        %(message_text)s,
        %(feedback_classes)s
    )
    """
    params = {
        "id": message_id,
        "session_id": session_id,
        "student_id": student_id,
        "role": role,
        "source": source,
        "parent_message_id": parent_message_id,
        "message_text": message_text,
        "feedback_classes": feedback_classes or [],
    }
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()


def attach_session_to_message(message_id: str, session_id: str) -> None:
    sql = """
    UPDATE messages.chat_messages
    SET session_id = %(session_id)s::uuid,
        updated_at = NOW()
    WHERE id = %(message_id)s::uuid
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"message_id": message_id, "session_id": session_id})
        conn.commit()


def record_feedback(
    *,
    student_id: str,
    response_id: str,
    thumb: Literal["up", "down"],
    comment: str | None,
) -> None:
    sql = """
    UPDATE messages.chat_messages
    SET feedback_thumb = %(thumb)s,
        feedback_comment = %(comment)s,
        updated_at = NOW()
    WHERE id = %(response_id)s::uuid
      AND student_id = %(student_id)s
      AND role = 'assistant'
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                {
                    "student_id": student_id,
                    "response_id": response_id,
                    "thumb": thumb,
                    "comment": comment,
                },
            )
        conn.commit()
