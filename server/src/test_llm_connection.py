import json
from pathlib import Path

import openai

from src.settings import get_navigator_model


def load_navigator_credentials() -> tuple[str, str]:
    key_file_path = Path(__file__).resolve().parents[1] / "navigator_api_keys.json"
    if not key_file_path.exists():
        raise FileNotFoundError(
            f"Could not find {key_file_path}. Create server/navigator_api_keys.json first."
        )

    with key_file_path.open("r", encoding="utf-8") as file:
        credentials = json.load(file)

    return credentials["OPENAI_API_KEY"], credentials["base_url"]


def main() -> None:
    api_key, base_url = load_navigator_credentials()
    model = get_navigator_model()

    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful pedagogical coding assistant.",
            },
            {
                "role": "user",
                "content": "Give one short hint about a while loop bug.",
            },
        ],
    )

    print(f"Model: {model}")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
