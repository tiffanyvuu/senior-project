import os
from uuid import UUID

import psycopg
from dotenv import load_dotenv


def get_conn() -> psycopg.Connection:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return psycopg.connect(database_url)


def insert_message(
    *,
    session_id: UUID,
    student_id: str,
    role: str,
    message_text: str,
    feedback_class: str | None = None,
    response_id: UUID | None = None,
) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO event_logs.messages (
                    session_id,
                    student_id,
                    role,
                    message_text,
                    feedback_class,
                    response_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    session_id,
                    student_id,
                    role,
                    message_text,
                    feedback_class,
                    response_id,
                ),
            )


def insert_message_feedback(
    *,
    message_id: int,
    student_id: str,
    thumb: str,
    comment: str | None = None,
) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO event_logs.message_feedback (
                    message_id,
                    student_id,
                    thumb,
                    comment
                )
                VALUES (%s, %s, %s, %s)
                """,
                (message_id, student_id, thumb, comment),
            )


def get_message_id_for_response(*, response_id: UUID, student_id: str) -> int | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM event_logs.messages
                WHERE response_id = %s
                  AND student_id = %s
                  AND role = 'assistant'
                LIMIT 1
                """,
                (response_id, student_id),
            )
            row = cur.fetchone()
            return row[0] if row else None
