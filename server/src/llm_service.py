import json
from pathlib import Path

import openai

from src.context_builder import build_feedback_prompt_from_classes
from src.feedback_policy import FeedbackClass
from src.settings import get_navigator_model


def prepare_main_llm_request(
    task: str,
    student_message: str,
    available_blocks: list[str] | None,
    raw_logs: str,
    recent_messages: list[dict[str, str]],
    feedback_classes: set[FeedbackClass],
) -> dict[str, str]:
    prompt = build_feedback_prompt_from_classes(
        task=task,
        student_message=student_message,
        available_blocks=available_blocks,
        raw_logs=raw_logs,
        recent_messages=recent_messages,
        feedback_classes=feedback_classes,
    )
    return {
        "model": get_navigator_model(),
        "prompt": prompt,
    }


def load_navigator_credentials() -> tuple[str, str]:
    key_file_path = Path(__file__).resolve().parents[1] / "navigator_api_keys.json"
    if not key_file_path.exists():
        raise FileNotFoundError(
            f"Could not find {key_file_path}. Create server/navigator_api_keys.json first."
        )

    with key_file_path.open("r", encoding="utf-8") as file:
        credentials = json.load(file)

    return credentials["OPENAI_API_KEY"], credentials["base_url"]


def generate_main_llm_response(
    task: str,
    student_message: str,
    available_blocks: list[str] | None,
    raw_logs: str,
    recent_messages: list[dict[str, str]],
    feedback_classes: set[FeedbackClass],
) -> dict[str, str]:
    llm_request = prepare_main_llm_request(
        task=task,
        student_message=student_message,
        available_blocks=available_blocks,
        raw_logs=raw_logs,
        recent_messages=recent_messages,
        feedback_classes=feedback_classes,
    )
    api_key, base_url = load_navigator_credentials()
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    response = client.chat.completions.create(
        model=llm_request["model"],
        messages=[
            {
                "role": "user",
                "content": llm_request["prompt"],
            }
        ],
    )
    return {
        "model": llm_request["model"],
        "prompt": llm_request["prompt"],
        "response_text": response.choices[0].message.content,
    }
