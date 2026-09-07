from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from .alerts import send_alert
from .config import Settings
from .db import Database
from .decoys import TRANSPARENT_GIF_B64, callback_url, create_docx_decoy, create_html_decoy
from .triage import classify


class TokenCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    filename: str = Field(min_length=2, max_length=180)
    severity: str = Field(default="high", pattern="^(low|medium|high|critical)$")
    notes: str = Field(default="", max_length=500)


class DecoyCreate(BaseModel):
    token_id: str
    format: str = Field(default="html", pattern="^(html|docx)$")
    output_dir: str = "decoys"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    db = Database(settings.db_path)
    app = FastAPI(title="Canary Honeytoken MVP", version="0.1.0")
    app.state.settings = settings
    app.state.db = db

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/api/tokens")
    def create_token(body: TokenCreate) -> dict:
        token_id = secrets.token_urlsafe(18)
        token = db.create_token(token_id, body.name, body.filename, body.severity, body.notes)
        token["callback_url"] = callback_url(settings.base_url, token_id)
        return token

    @app.get("/api/tokens")
    def list_tokens() -> list[dict]:
        tokens = db.list_tokens()
        for token in tokens:
            token["callback_url"] = callback_url(settings.base_url, token["id"])
        return tokens

    @app.post("/api/tokens/{token_id}/disable")
    def disable_token(token_id: str) -> dict:
        if not db.get_token(token_id):
            raise HTTPException(404, "Token not found")
        db.set_active(token_id, False)
        return {"status": "disabled", "token_id": token_id}

    @app.post("/api/decoys")
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

    @app.get("/api/events")
    def list_events(limit: int = 100) -> list[dict]:
        return db.list_events(max(1, min(limit, 1000)))

    @app.get("/t/{token_id}/pixel.gif")
    def trigger(token_id: str, request: Request) -> Response:
        token = db.get_token(token_id)
        if not token or not token["active"]:
            # Do not disclose whether a historical token exists.
            raise HTTPException(404, "Not found")

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
        send_alert(settings, event, token)
        gif = base64.b64decode(TRANSPARENT_GIF_B64)
        return Response(content=gif, media_type="image/gif", headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

    return app


app = create_app()
