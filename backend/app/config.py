import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _parse_ids(value):
    ids = []
    if not value:
        return ids
    for chunk in str(value).split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.append(int(chunk))
        except ValueError:
            continue
    return ids


class Settings:
    def __init__(self):
        self.app_name = "NEXUS"
        self.database_url = os.getenv(
            "DATABASE_URL", f"sqlite:///{(BASE_DIR / 'nexus.db').as_posix()}"
        )
        self.llm_api_key = (
            os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        ).strip()
        self.llm_base_url = (
            os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
        ).rstrip("/")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.llm_timeout = float(os.getenv("LLM_TIMEOUT", "60"))
        self.force_demo = _as_bool(os.getenv("DEMO_MODE"), False)

        self.telegram_bot_token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
        self.telegram_allowed_chat_ids = _parse_ids(
            os.getenv("TELEGRAM_ALLOWED_CHAT_IDS")
        )
        default_chat = (os.getenv("TELEGRAM_DEFAULT_CHAT_ID") or "").strip()
        self.telegram_default_chat_id = int(default_chat) if default_chat else None

        self.cors_origins = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        ]

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key)

    @property
    def telegram_configured(self) -> bool:
        return bool(self.telegram_bot_token)

    @property
    def demo_mode(self) -> bool:
        return self.force_demo or not self.llm_configured

    def telegram_chat_allowed(self, chat_id) -> bool:
        if not self.telegram_allowed_chat_ids:
            return True
        return chat_id in self.telegram_allowed_chat_ids


settings = Settings()
