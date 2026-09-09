from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import logging
import re
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
from .privacy import public_id, redact, safe_error


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
    app = FastAPI(title="Honey Token", version="0.2.2",
                  docs_url=None if settings.receiver_only else "/docs",
                  redoc_url=None if settings.receiver_only else "/redoc",
                  openapi_url=None if settings.receiver_only else "/openapi.json")
    app.state.settings = settings
    app.state.db = db
    app.state.azure_ingestor = ingestor

    def add_public_id(token: dict) -> dict:
        token = dict(token)
        token["canary_id"] = public_id(token["id"])
        return token

    def require_management_access(request: Request) -> None:
        """Protect management routes with an API key or local-only fallback."""
        if settings.receiver_only:
            raise HTTPException(status_code=404, detail="Not found")
        if settings.management_api_key:
            supplied = request.headers.get("x-canary-api-key", "")
            if not supplied or not secrets.compare_digest(supplied.encode("utf-8"), settings.management_api_key.encode("utf-8")):
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
            event["canary_id"] = public_id(raw_id) if raw_id else ""
            event["token_id"] = "[redacted]"
            event["request_path"] = "/t/[redacted]/pixel.gif"
            for field in ("alert_error", "sentinel_error"):
                if event.get(field):
                    event[field] = "[redacted diagnostic]"
            public_events.append(redact(event, raw_id))
        return public_events

    @app.get("/t/{token_id}/pixel.gif")
    def trigger(token_id: str, request: Request) -> Response:
        if not re.fullmatch(r"[A-Za-z0-9_-]{24}", token_id):
            raise HTTPException(404, "Not found")
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
        # Commit the original observation before triage or any downstream action.
        event = db.add_event(
            token_id=token_id, source_ip=source_ip, user_agent=user_agent,
            request_path="/t/[redacted]/pixel.gif", event_type="canary_trigger",
            triage_label="pending", severity="unknown", duplicate=False,
        )
        cutoff = (datetime.fromisoformat(event["occurred_at"]) - timedelta(seconds=settings.dedupe_seconds)).isoformat()
        repeats = db.matching_event_count(token_id, user_agent, cutoff, event["id"], event["occurred_at"])
        triage = classify(user_agent, token["severity"])
        fields = {
            **triage.fields(), "duplicate": repeats > 0, "first_hit": repeats == 0,
            "repeat_count": repeats, "active_canary": True,
            "triage_label": ("Possible automated scanner interaction" if triage.is_scanner else
                             "Honeytoken trigger - potential unauthorized access"),
        }
        db.set_triage(event["id"], fields)
        event.update(fields)

        def status(setter, status_value, error=""):
            try:
                setter(event["id"], status_value, error)
            except Exception as exc:
                # A status-write failure must not prevent the other delivery path.
                logging.getLogger(__name__).error("Delivery status write failed: %s", safe_error(exc))

        alert_error = ""
        try:
            alert_status = send_alert(settings, event, token)
        except Exception as exc:
            alert_status, alert_error = "failed", safe_error(exc)
        event["alert_status"] = alert_status
        status(db.set_alert_status, alert_status, alert_error)
        if ingestor:
            try:
                ingestor.publish(event, token, settings.receiver_version)
                status(db.set_sentinel_status, "sent")
            except Exception as exc:
                status(db.set_sentinel_status, "failed", safe_error(exc))
        else:
            status(db.set_sentinel_status, "disabled")
        gif = base64.b64decode(TRANSPARENT_GIF_B64)
        return Response(content=gif, media_type="image/gif", headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

    return app


app = create_app()
