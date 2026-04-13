import os

from dotenv import load_dotenv


DEFAULT_NAVIGATOR_MODEL = "gpt-oss-20b"
DEFAULT_INVITE_HUB_BACKGROUND_SYNC_ENABLED = True
DEFAULT_INVITE_HUB_BACKGROUND_SYNC_INTERVAL_S = 5.0


def _get_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be a boolean value like true/false.")


def _get_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        parsed = float(raw_value)
    except ValueError as error:
        raise RuntimeError(f"{name} must be a number of seconds.") from error
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than 0.")
    return parsed


def get_navigator_model() -> str:
    load_dotenv()
    return os.getenv("NAVIGATOR_MODEL", DEFAULT_NAVIGATOR_MODEL)


def get_invite_hub_background_sync_enabled() -> bool:
    load_dotenv()
    return _get_bool_env(
        "INVITE_HUB_BACKGROUND_SYNC_ENABLED",
        DEFAULT_INVITE_HUB_BACKGROUND_SYNC_ENABLED,
    )


def get_invite_hub_background_sync_interval_s() -> float:
    load_dotenv()
    return _get_float_env(
        "INVITE_HUB_BACKGROUND_SYNC_INTERVAL_S",
        DEFAULT_INVITE_HUB_BACKGROUND_SYNC_INTERVAL_S,
    )


def is_invite_hub_sync_configured() -> bool:
    load_dotenv()
    token = os.getenv("INVITE_HUB_TOKEN")
    username = os.getenv("INVITE_HUB_USERNAME")
    password = os.getenv("INVITE_HUB_PASSWORD")
    return bool(token) or bool(username and password)
