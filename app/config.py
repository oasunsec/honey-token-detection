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
    storage_backend: str = os.getenv("CANARY_STORAGE_BACKEND", "sqlite").lower()
    base_url: str = os.getenv("CANARY_BASE_URL", "http://127.0.0.1:8000")
    management_api_key: str = os.getenv("CANARY_MANAGEMENT_API_KEY", "")
    receiver_only: bool = _bool("CANARY_RECEIVER_ONLY", False)
    receiver_version: str = os.getenv("CANARY_RECEIVER_VERSION", "local")
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
    azure_storage_account_url: str = os.getenv("CANARY_AZURE_STORAGE_ACCOUNT_URL", "")
    azure_table_hits: str = os.getenv("CANARY_AZURE_TABLE_HITS", "CanaryHits")
    azure_table_outbox: str = os.getenv("CANARY_AZURE_TABLE_OUTBOX", "NotificationOutbox")
    azure_dcr_endpoint: str = os.getenv("CANARY_AZURE_DCR_ENDPOINT", "")
    azure_dcr_immutable_id: str = os.getenv("CANARY_AZURE_DCR_IMMUTABLE_ID", "")
    azure_dcr_stream_name: str = os.getenv("CANARY_AZURE_DCR_STREAM_NAME", "Custom-CanaryHit_CL")

    def validate(self) -> None:
        if self.storage_backend not in {"sqlite", "azure_table"}:
            raise ValueError("CANARY_STORAGE_BACKEND must be sqlite or azure_table")
        if self.storage_backend == "azure_table" and not self.azure_storage_account_url:
            raise ValueError("CANARY_AZURE_STORAGE_ACCOUNT_URL is required for azure_table")
