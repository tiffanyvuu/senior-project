import json
import os
from pathlib import Path

import openai

from src.context_builder import (
    build_feedback_prompt_from_classes,
    build_robot_behavior_prompt,
)
from src.feedback_policy import FeedbackClass
from src.settings import get_navigator_model

DEFAULT_LLM_TIMEOUT_S = 30.0


def prepare_main_llm_request(
    task: str,
    student_message: str,
    available_blocks: list[str] | None,
    robot_behavior_summary: str,
    recent_messages: list[dict[str, str]],
    feedback_classes: set[FeedbackClass],
) -> dict[str, str]:
    prompt = build_feedback_prompt_from_classes(
        task=task,
        student_message=student_message,
        available_blocks=available_blocks,
        robot_behavior_summary=robot_behavior_summary,
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


def create_openai_client() -> openai.OpenAI:
    api_key, base_url = load_navigator_credentials()
    return openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=float(os.getenv("LLM_TIMEOUT_S", DEFAULT_LLM_TIMEOUT_S)),
    )


def execute_prompt(*, model: str, prompt: str) -> str:
    client = create_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return response.choices[0].message.content


def generate_robot_behavior_summary(task: str, raw_logs: str) -> dict[str, str]:
    model = get_navigator_model()
    prompt = build_robot_behavior_prompt(
        task=task,
        raw_logs=raw_logs,
    )
    response_text = execute_prompt(model=model, prompt=prompt)
    return {
        "model": model,
        "prompt": prompt,
        "response_text": response_text,
    }


def generate_main_llm_response(
    task: str,
    student_message: str,
    available_blocks: list[str] | None,
    robot_behavior_summary: str,
    recent_messages: list[dict[str, str]],
    feedback_classes: set[FeedbackClass],
) -> dict[str, str]:
    llm_request = prepare_main_llm_request(
        task=task,
        student_message=student_message,
        available_blocks=available_blocks,
        robot_behavior_summary=robot_behavior_summary,
        recent_messages=recent_messages,
        feedback_classes=feedback_classes,
    )
    response_text = execute_prompt(
        model=llm_request["model"],
        prompt=llm_request["prompt"],
    )
    return {
        "model": llm_request["model"],
        "prompt": llm_request["prompt"],
        "response_text": response_text,
    }
