"""Redaction at telemetry and diagnostic boundaries."""
import hashlib
import re


def public_id(token_id: str) -> str:
    return hashlib.sha256(token_id.encode()).hexdigest()[:16]


def redact(value, token_id: str = ""):
    if isinstance(value, dict):
        return {key: redact(item, token_id) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, token_id) for item in value]
    if isinstance(value, str):
        if token_id:
            value = value.replace(token_id, "[redacted]")
        value = re.sub(r"/t/[^/\s?]+/pixel\.gif", "/t/[redacted]/pixel.gif", value)
        return value.replace("\r", " ").replace("\n", " ")
    return value


def safe_error(exc: Exception) -> str:
    # SDK/SMTP messages can contain URLs, credentials, or response bodies.
    code = getattr(exc, "status_code", None) or getattr(exc, "smtp_code", None)
    return type(exc).__name__ + (f" (status={code})" if isinstance(code, int) else "")
