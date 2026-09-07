from __future__ import annotations

from email.message import EmailMessage
import smtplib

from .config import Settings


def render_alert(event: dict, token: dict) -> tuple[str, str]:
    subject = f"[CANARY] {token['filename']} triggered ({event['severity'].upper()})"
    body = "\n".join(
        [
            "A decoy/honeytoken was accessed.",
            "",
            f"Token: {token['name']} ({token['id']})",
            f"File: {token['filename']}",
            f"Time: {event['occurred_at']}",
            f"Source IP: {event['source_ip']}",
            f"User-Agent: {event['user_agent'] or '(none)'}",
            f"Triage: {event['triage_label']}",
            f"Severity: {event['severity']}",
            f"Duplicate in suppression window: {bool(event['duplicate'])}",
            "",
            "Treat this as a detection signal. Correlate with identity, endpoint, file audit, DLP, and network telemetry before attributing activity to a person.",
        ]
    )
    return subject, body


def send_alert(settings: Settings, event: dict, token: dict) -> None:
    if event.get("duplicate"):
        return
    subject, body = render_alert(event, token)
    mode = settings.alert_mode.lower()
    if mode == "none":
        return
    if mode == "console":
        print(f"\n{subject}\n{body}\n")
        return
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
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)
