import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from src.block_catalog import resolve_available_blocks
from src.current_state_metrics import build_raw_logs_context, compute_snapshot_for_student_session
from src.db import get_message_id_for_response, insert_message, insert_message_feedback
from src.feedback_policy import FeedbackClass, determine_feedback_class
from src.llm_service import generate_main_llm_response
from src.log_sync import sync_invite_hub_logs
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
logger = logging.getLogger(__name__)


def log_stage(stage: str, **fields: object) -> None:
    lines = [f"[{stage}]"]
    lines.extend(f"  {key}: {value}" for key, value in fields.items())
    logger.info("\n".join(lines))

@router.post("/students/{student_id}/messages", response_model=MessageResponse)
def create_message(student_id: str, payload: MessageRequest) -> MessageResponse:
    message_id = uuid4()
    session_uuid = UUID(payload.session_id)
    source = "help_button" if payload.message == "" else "chat"
    student_message_text = payload.message if payload.message else "Help"
    append_session_message(
        student_id=student_id,
        playground=payload.playground,
        session_id=payload.session_id,
        role="student",
        content=student_message_text,
    )
    insert_message(
        session_id=session_uuid,
        student_id=student_id,
        role="student",
        message_text=student_message_text,
    )
    log_stage(
        "Student Message Received",
        student_id=student_id,
        session_id=payload.session_id,
        playground=payload.playground,
        source=source,
        message=student_message_text,
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
    synced_log_count = 0
    task = resolve_task_description(payload.playground)
    available_blocks = resolve_available_blocks(payload.playground)
    raw_logs = "None"
    recent_messages: list[dict[str, str]] = []
    if task and payload.student_message:
        try:
            synced_log_count = sync_invite_hub_logs(student_id=student_id)
            snapshot = compute_snapshot_for_student_session(
                student_id=student_id,
                session_id=payload.session_id,
                insert=True,
            )
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Current state analysis failed: {error}",
            ) from error
        log_stage(
            "Current State Analyzer Output",
            student_id=student_id,
            session_id=payload.session_id,
            synced_log_count=synced_log_count,
            snapshot=snapshot.to_dict(),
        )
        feedback_classes = determine_feedback_class(snapshot)
        if not feedback_classes:
            feedback_classes = {FeedbackClass.QUESTION}
        raw_logs = build_raw_logs_context(
            student_id=student_id,
            session_id=payload.session_id,
        )
        recent_messages = get_recent_session_messages(
            student_id,
            payload.playground,
            payload.session_id,
        )
        log_stage(
            "Feedback Policy Output",
            student_id=student_id,
            session_id=payload.session_id,
            synced_log_count=synced_log_count,
            feedback_classes=sorted(
                feedback_class.value for feedback_class in feedback_classes
            ),
        )

    if task and payload.student_message and feedback_classes:
        try:
            log_stage(
                "LLM Request Starting",
                student_id=student_id,
                session_id=payload.session_id,
                model=task,
                feedback_classes=sorted(
                    feedback_class.value for feedback_class in feedback_classes
                ),
            )
            llm_request = generate_main_llm_response(
                task=task,
                student_message=payload.student_message,
                available_blocks=available_blocks,
                raw_logs=raw_logs,
                recent_messages=recent_messages,
                feedback_classes=feedback_classes,
            )
            log_stage(
                "LLM Prompt Sent",
                student_id=student_id,
                session_id=payload.session_id,
                model=llm_request["model"],
                prompt=llm_request["prompt"],
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
    log_stage(
        "Assistant Response Sent",
        student_id=student_id,
        session_id=payload.session_id,
        response_id=str(response_id),
        message=response_text,
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
