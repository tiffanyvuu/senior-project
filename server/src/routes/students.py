from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from src.block_catalog import resolve_available_blocks
from src.db import get_message_id_for_response, insert_message, insert_message_feedback
from src.feedback_policy import FeedbackClassInput, determine_feedback_class
from src.llm_service import generate_main_llm_response
from src.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    MessageRequest,
    MessageResponse,
    StudentResponseRequest,
    StudentResponseResponse,
)
from src.session_service import append_session_message, get_recent_session_messages
from src.task_catalog import resolve_task_description

router = APIRouter(prefix="/v1", tags=["students"])


def get_temporary_feedback_input(student_message: str) -> FeedbackClassInput:
    if student_message.strip().lower() == "help":
        return FeedbackClassInput(
            code_abandonment=True,
            early_quitter=True,
        )

    return FeedbackClassInput(
        trial_and_error=True,
        expected_completion=True,
        early_quitter=True,
    )


@router.post("/students/{student_id}/messages", response_model=MessageResponse)
def create_message(student_id: str, payload: MessageRequest) -> MessageResponse:
    message_id = uuid4()
    session_uuid = UUID(payload.session_id)
    source = "help_button" if payload.message == "" else "chat"
    append_session_message(
        student_id=student_id,
        playground=payload.playground,
        session_id=payload.session_id,
        role="student",
        content=payload.message if payload.message else "Help",
    )
    insert_message(
        session_id=session_uuid,
        student_id=student_id,
        role="student",
        message_text=payload.message if payload.message else "Help",
    )
    return MessageResponse(
        message_id=str(message_id),
        session_id=payload.session_id,
        student_id=student_id,
        playground=payload.playground,
        message=payload.message,
        source=source,
        status="received",
    )


@router.post("/students/{student_id}/responses", response_model=StudentResponseResponse)
def create_response(
    student_id: str,
    payload: StudentResponseRequest,
) -> StudentResponseResponse:
    response_id = uuid4()
    session_uuid = UUID(payload.session_id)
    llm_request = None
    response_text = payload.response_text
    feedback_classes = set()
    task = resolve_task_description(payload.playground)
    available_blocks = resolve_available_blocks(payload.playground)
    recent_messages = get_recent_session_messages(
        student_id,
        payload.playground,
        payload.session_id,
    )
    if task and payload.student_message:
        feedback_input = get_temporary_feedback_input(payload.student_message)
        feedback_classes = determine_feedback_class(feedback_input)

    if task and payload.student_message and feedback_classes:
        try:
            llm_request = generate_main_llm_response(
                task=task,
                student_message=payload.student_message,
                available_blocks=available_blocks,
                recent_messages=recent_messages,
                feedback_classes=feedback_classes,
            )
            response_text = llm_request["response_text"]
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error
    elif not response_text:
        raise HTTPException(
            status_code=400,
            detail="Either response_text or playground/student_message must be provided.",
        )

    append_session_message(
        student_id=student_id,
        playground=payload.playground,
        session_id=payload.session_id,
        role="assistant",
        content=response_text,
    )
    insert_message(
        session_id=session_uuid,
        student_id=student_id,
        role="assistant",
        message_text=response_text,
        feedback_class=", ".join(
            sorted(feedback_class.value for feedback_class in feedback_classes)
        )
        if feedback_classes
        else None,
        response_id=response_id,
    )

    return StudentResponseResponse(
        response_id=str(response_id),
        session_id=payload.session_id,
        student_id=student_id,
        playground=payload.playground,
        message_id=payload.message_id,
        response_text=response_text,
        llm_model=llm_request["model"] if llm_request else None,
        llm_prompt=llm_request["prompt"] if llm_request else None,
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
    try:
        response_uuid = UUID(response_id)
        message_id = get_message_id_for_response(
            response_id=response_uuid,
            student_id=student_id,
        )
        if message_id is None:
            raise HTTPException(
                status_code=404,
                detail="Assistant response not found for this student.",
            )
        insert_message_feedback(
            message_id=message_id,
            student_id=student_id,
            thumb=payload.thumb,
            comment=payload.comment,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail="response_id must be a valid UUID.") from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    return FeedbackResponse(
        student_id=student_id,
        response_id=response_id,
        thumb=payload.thumb,
        comment=payload.comment,
        status="received",
    )
