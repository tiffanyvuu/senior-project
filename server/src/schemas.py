from typing import Literal

from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    message: str = Field(default="", description="Student message text.")


class MessageResponse(BaseModel):
    message_id: str
    student_id: str
    message: str
    source: Literal["chat", "help_button"]
    status: Literal["received"]


class StudentResponseRequest(BaseModel):
    message_id: str | None = Field(
        default=None,
        description="Associated inbound message identifier, if available.",
    )
    response_text: str = Field(description="LLM-generated text shown to the student.")


class StudentResponseResponse(BaseModel):
    response_id: str
    student_id: str
    message_id: str | None
    response_text: str
    status: Literal["received"]


class FeedbackRequest(BaseModel):
    thumb: Literal["up", "down"] = Field(description="Student reaction.")
    comment: str | None = Field(
        default=None,
        description="Optional freeform student feedback.",
    )


class FeedbackResponse(BaseModel):
    student_id: str
    response_id: str
    thumb: Literal["up", "down"]
    comment: str | None
    status: Literal["received"]
