from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator

from .alerts import send_alert
from .azure_ingestion import AzureMonitorIngestor
from .azure_storage import AzureTableDatabase
from .config import Settings
from .db import Database
from .decoys import TRANSPARENT_GIF_B64, callback_url, create_docx_decoy, create_html_decoy, validate_filename
from .triage import classify


class TokenCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    filename: str = Field(min_length=2, max_length=180)
    severity: str = Field(default="high", pattern="^(low|medium|high|critical)$")
    notes: str = Field(default="", max_length=500)

    @field_validator("filename")
    @classmethod
    def filename_must_be_safe(cls, value: str) -> str:
        return validate_filename(value)


class DecoyCreate(BaseModel):
    token_id: str
    format: str = Field(default="html", pattern="^(html|docx)$")
    output_dir: str = "decoys"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    settings.validate()
    if settings.storage_backend == "azure_table":
        db = AzureTableDatabase(
            settings.azure_storage_account_url,
            settings.azure_table_hits,
            settings.azure_table_outbox,
        )
    else:
        db = Database(settings.db_path)
    ingestor = None
    if settings.azure_dcr_endpoint and settings.azure_dcr_immutable_id:
        ingestor = AzureMonitorIngestor(
            settings.azure_dcr_endpoint,
            settings.azure_dcr_immutable_id,
            settings.azure_dcr_stream_name,
        )
    app = FastAPI(title="Canary Honeytoken MVP", version="0.1.0")
    app.state.settings = settings
    app.state.db = db
    app.state.azure_ingestor = ingestor

    def add_public_id(token: dict) -> dict:
        token = dict(token)
        token["canary_id"] = hashlib.sha256(token["id"].encode()).hexdigest()[:16]
        return token

    def require_management_access(request: Request) -> None:
        """Protect management routes with an API key or local-only fallback."""
        if settings.receiver_only:
            raise HTTPException(status_code=404, detail="Not found")
        if settings.management_api_key:
            supplied = request.headers.get("x-canary-api-key", "")
            if not supplied or not secrets.compare_digest(supplied, settings.management_api_key):
                raise HTTPException(status_code=401, detail="Management API authentication required")
            return

        client_host = request.client.host if request.client else ""
        try:
            is_loopback = ipaddress.ip_address(client_host).is_loopback
        except ValueError:
            is_loopback = client_host == "testclient"
        if not is_loopback:
            raise HTTPException(
                status_code=503,
                detail="Set CANARY_MANAGEMENT_API_KEY before using the management API remotely",
            )

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "receiver_only": settings.receiver_only,
            "receiver_version": settings.receiver_version,
            "storage_backend": settings.storage_backend,
        }

    @app.post("/api/tokens", dependencies=[Depends(require_management_access)])
    def create_token(body: TokenCreate) -> dict:
        token_id = secrets.token_urlsafe(18)
        token = add_public_id(db.create_token(token_id, body.name, body.filename, body.severity, body.notes))
        token["callback_url"] = callback_url(settings.base_url, token_id)
        return token

    @app.get("/api/tokens", dependencies=[Depends(require_management_access)])
    def list_tokens() -> list[dict]:
        tokens = db.list_tokens()
        for token in tokens:
            token.update(add_public_id(token))
            token["callback_url"] = callback_url(settings.base_url, token["id"])
        return tokens

    @app.post("/api/tokens/{token_id}/disable", dependencies=[Depends(require_management_access)])
    def disable_token(token_id: str) -> dict:
        if not db.get_token(token_id):
            raise HTTPException(404, "Token not found")
        db.set_active(token_id, False)
        return {"status": "disabled", "token_id": token_id}

    @app.post("/api/decoys", dependencies=[Depends(require_management_access)])
    def generate_decoy(body: DecoyCreate) -> dict:
        token = db.get_token(body.token_id)
        if not token:
            raise HTTPException(404, "Token not found")
        out = Path(body.output_dir)
        url = callback_url(settings.base_url, body.token_id)
        filename = token["filename"]
        if body.format == "html":
            if not filename.lower().endswith((".html", ".htm")):
                filename = Path(filename).stem + ".html"
            path = create_html_decoy(out, filename, url)
        else:
            if not filename.lower().endswith(".docx"):
                filename = Path(filename).stem + ".docx"
            path = create_docx_decoy(out, filename, url)
        return {"path": str(path), "token_id": body.token_id, "callback_url": url, "format": body.format}

    @app.get("/api/events", dependencies=[Depends(require_management_access)])
    def list_events(limit: int = 100) -> list[dict]:
        public_events = []
        for event in db.list_events(max(1, min(limit, 1000))):
            event = dict(event)
            raw_id = str(event.get("token_id", ""))
            event["canary_id"] = hashlib.sha256(raw_id.encode()).hexdigest()[:16] if raw_id else ""
            event["token_id"] = "[redacted]"
            event["request_path"] = "/t/[redacted]/pixel.gif"
            public_events.append(event)
        return public_events

    @app.get("/t/{token_id}/pixel.gif")
    def trigger(token_id: str, request: Request) -> Response:
        token = db.get_token(token_id)
        if not token or not token["active"]:
            # Do not disclose whether a historical token exists.
            raise HTTPException(404, "Not found")
        token = add_public_id(token)

        if settings.trust_proxy_headers:
            forwarded = request.headers.get("x-forwarded-for", "")
            source_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        else:
            source_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")[:1000]
        label, severity = classify(user_agent, token["severity"])

        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=settings.dedupe_seconds)).isoformat()
        duplicate = db.recent_matching_event(token_id, source_ip, user_agent, cutoff)
        event = db.add_event(
            token_id=token_id,
            source_ip=source_ip,
            user_agent=user_agent,
            request_path=str(request.url.path),
            event_type="canary_trigger",
            triage_label=label,
            severity=severity,
            duplicate=duplicate,
        )
        try:
            alert_status = send_alert(settings, event, token)
        except Exception as exc:
            db.set_alert_status(event["id"], "failed", str(exc)[:500])
            raise
        db.set_alert_status(event["id"], alert_status)
        if ingestor:
            try:
                event["alert_status"] = alert_status
                ingestor.publish(event, token, settings.receiver_version)
                db.set_sentinel_status(event["id"], "sent")
            except Exception as exc:
                db.set_sentinel_status(event["id"], "failed", str(exc)[:500])
        gif = base64.b64decode(TRANSPARENT_GIF_B64)
        return Response(content=gif, media_type="image/gif", headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

    return app


app = create_app()
