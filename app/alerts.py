from __future__ import annotations

from email.message import EmailMessage
import hashlib
import smtplib
import ssl

from .config import Settings
from .privacy import redact


def render_alert(event: dict, token: dict) -> tuple[str, str]:
    event = redact(event, token["id"])
    token = {**token, "filename": redact(token["filename"], token["id"]), "name": redact(token["name"], token["id"])}
    subject = f"[CANARY] {token['filename']} triggered ({event['severity'].upper()})"
    body = "\n".join(
        [
            "A decoy/honeytoken was accessed.",
            "",
            f"Canary: {token['name']}",
            f"Canary ID: {token.get('canary_id') or hashlib.sha256(token['id'].encode()).hexdigest()[:16]}",
            f"File: {token['filename']}",
            f"Time: {event['occurred_at']}",
            f"Source IP: {event['source_ip']}",
            f"User-Agent: {event['user_agent'] or '(none)'}",
            f"Triage: {event['triage_label']}",
            f"Severity: {event['severity']}",
            f"Classification: {event.get('classification', 'unknown')}",
            f"Scanner: {bool(event.get('is_scanner'))}",
            f"First hit: {bool(event.get('first_hit', not event.get('duplicate')))}",
            f"Related earlier hits in window: {event.get('repeat_count', 0)}",
            f"Reason: {event.get('reason', '')}",
            f"Recommended action: {event.get('recommended_action', '')}",
            f"Duplicate in suppression window: {bool(event['duplicate'])}",
            "",
            "Treat this as a detection signal. Correlate with identity, endpoint, file audit, DLP, and network telemetry before attributing activity to a person.",
        ]
    )
    return subject, body


def send_alert(settings: Settings, event: dict, token: dict) -> str:
    if event.get("duplicate"):
        return "suppressed"
    subject, body = render_alert(event, token)
    mode = settings.alert_mode.lower()
    if mode == "none":
        return "disabled"
    if mode == "console":
        print(f"\n{subject}\n{body}\n")
        return "sent"
    if mode != "email":
        raise ValueError(f"Unsupported alert mode: {settings.alert_mode}")
    if not (settings.smtp_host and settings.alert_to):
        raise RuntimeError("Email mode requires CANARY_SMTP_HOST and CANARY_ALERT_TO")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = settings.alert_to
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_starttls:
            smtp.starttls(context=ssl.create_default_context())
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)
    return "sent"
