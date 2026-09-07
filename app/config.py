from dataclasses import dataclass
import os


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    db_path: str = os.getenv("CANARY_DB_PATH", "canary.db")
    base_url: str = os.getenv("CANARY_BASE_URL", "http://127.0.0.1:8000")
    alert_mode: str = os.getenv("CANARY_ALERT_MODE", "console")  # console | email | none
    alert_to: str = os.getenv("CANARY_ALERT_TO", "")
    smtp_host: str = os.getenv("CANARY_SMTP_HOST", "")
    smtp_port: int = int(os.getenv("CANARY_SMTP_PORT", "587"))
    smtp_user: str = os.getenv("CANARY_SMTP_USER", "")
    smtp_password: str = os.getenv("CANARY_SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("CANARY_SMTP_FROM", "canary-alerts@localhost")
    smtp_starttls: bool = _bool("CANARY_SMTP_STARTTLS", True)
    trust_proxy_headers: bool = _bool("CANARY_TRUST_PROXY_HEADERS", False)
    dedupe_seconds: int = int(os.getenv("CANARY_DEDUPE_SECONDS", "300"))
