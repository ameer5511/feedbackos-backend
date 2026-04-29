import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


@lru_cache(maxsize=1)
def load_environment() -> None:
    load_dotenv(dotenv_path=ENV_PATH)


def get_env(name: str, *, required: bool = False) -> Optional[str]:
    load_environment()
    value = os.getenv(name)
    if required and not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Expected it in {ENV_PATH}"
        )
    return value


def get_groq_model() -> str:
    return get_env("GROQ_MODEL") or DEFAULT_GROQ_MODEL
