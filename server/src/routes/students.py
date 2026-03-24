from uuid import uuid4

from fastapi import APIRouter

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
    source = "help_button" if payload.message == "" else "chat"
    return MessageResponse(
        message_id=str(uuid4()),
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
    return StudentResponseResponse(
        response_id=str(uuid4()),
        student_id=student_id,
        message_id=payload.message_id,
        response_text=payload.response_text,
        status="received",
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
    return FeedbackResponse(
        student_id=student_id,
        response_id=response_id,
        thumb=payload.thumb,
        comment=payload.comment,
        status="received",
    )
