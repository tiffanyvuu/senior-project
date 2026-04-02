from uuid import uuid4

from fastapi import APIRouter, HTTPException

from src.agent_pipeline import build_agent_response
from src.chat_history import attach_session_to_message, insert_chat_message, record_feedback

from src.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    MessageRequest,
    MessageResponse,
    StudentResponseRequest,
    StudentResponseResponse,
)

router = APIRouter(prefix="/v1", tags=["students"])


@router.post("/students/{student_id}/messages", response_model=MessageResponse)
def create_message(student_id: str, payload: MessageRequest) -> MessageResponse:
    message_id = str(uuid4())
    source = "help_button" if payload.message == "" else "chat"
    insert_chat_message(
        message_id=message_id,
        student_id=student_id,
        role="student",
        message_text=payload.message,
        source=source,
    )
    return MessageResponse(
        message_id=message_id,
        student_id=student_id,
        message=payload.message,
        source=source,
        status="received",
    )


@router.post("/students/{student_id}/responses", response_model=StudentResponseResponse)
def create_response(
    student_id: str,
    payload: StudentResponseRequest,
) -> StudentResponseResponse:
    response_id = str(uuid4())
    if payload.response_text is not None:
        insert_chat_message(
            message_id=response_id,
            student_id=student_id,
            role="assistant",
            message_text=payload.response_text,
            parent_message_id=payload.message_id,
        )
        return StudentResponseResponse(
            response_id=response_id,
            student_id=student_id,
            message_id=payload.message_id,
            response_text=payload.response_text,
            status="received",
        )

    source = payload.source or ("help_button" if payload.student_message == "" else "chat")
    try:
        bundle = build_agent_response(
            student_id,
            student_message=payload.student_message,
            source=source,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    insert_chat_message(
        message_id=response_id,
        student_id=student_id,
        role="assistant",
        message_text=bundle.response_text,
        session_id=bundle.session_id,
        source=source,
        parent_message_id=payload.message_id,
        feedback_classes=bundle.feedback_types,
    )
    if payload.message_id and bundle.session_id:
        attach_session_to_message(payload.message_id, bundle.session_id)

    return StudentResponseResponse(
        response_id=response_id,
        student_id=student_id,
        message_id=payload.message_id,
        response_text=bundle.response_text,
        status="generated",
        session_id=bundle.session_id,
        progress_pct=bundle.progress_pct,
        feedback_types=bundle.feedback_types,
        context_prompt=bundle.context_prompt,
        synced_log_count=bundle.synced_log_count,
    )


@router.post(
    "/students/{student_id}/responses/{response_id}/feedback",
    response_model=FeedbackResponse,
)
def create_feedback(
    student_id: str,
    response_id: str,
    payload: FeedbackRequest,
) -> FeedbackResponse:
    record_feedback(
        student_id=student_id,
        response_id=response_id,
        thumb=payload.thumb,
        comment=payload.comment,
    )
    return FeedbackResponse(
        student_id=student_id,
        response_id=response_id,
        thumb=payload.thumb,
        comment=payload.comment,
        status="received",
    )
