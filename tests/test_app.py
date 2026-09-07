import contextlib
import io
from pathlib import Path
import zipfile

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_client(tmp_path: Path, alert_mode: str = "none") -> TestClient:
    settings = Settings(
        db_path=str(tmp_path / "test.db"),
        base_url="http://testserver",
        alert_mode=alert_mode,
        dedupe_seconds=300,
    )
    return TestClient(create_app(settings))


def test_token_trigger_and_dedupe(tmp_path: Path):
    client = make_client(tmp_path)
    token = client.post(
        "/api/tokens",
        json={"name": "Finance bait", "filename": "Synthetic_Forecast.docx", "severity": "high"},
    ).json()

    first = client.get(f"/t/{token['id']}/pixel.gif", headers={"user-agent": "Mozilla/5.0"})
    second = client.get(f"/t/{token['id']}/pixel.gif", headers={"user-agent": "Mozilla/5.0"})
    assert first.status_code == 200
    assert first.headers["content-type"].startswith("image/gif")
    assert second.status_code == 200

    events = client.get("/api/events").json()
    assert len(events) == 2
    assert events[0]["duplicate"] == 1
    assert events[1]["duplicate"] == 0
    assert events[1]["event_type"] == "canary_trigger"


def test_scanner_triage(tmp_path: Path):
    client = make_client(tmp_path)
    token = client.post(
        "/api/tokens",
        json={"name": "Scanner test", "filename": "Executive_Bonus.docx", "severity": "high"},
    ).json()
    client.get(f"/t/{token['id']}/pixel.gif", headers={"user-agent": "curl/8.10"})
    event = client.get("/api/events").json()[0]
    assert event["severity"] == "medium"
    assert "scanner" in event["triage_label"].lower()


def test_disabled_token_returns_404(tmp_path: Path):
    client = make_client(tmp_path)
    token = client.post(
        "/api/tokens",
        json={"name": "Disable me", "filename": "Payroll.docx", "severity": "high"},
    ).json()
    assert client.post(f"/api/tokens/{token['id']}/disable").status_code == 200
    assert client.get(f"/t/{token['id']}/pixel.gif").status_code == 404


def test_console_alert_uses_triage_result(tmp_path: Path):
    client = make_client(tmp_path, alert_mode="console")
    token = client.post(
        "/api/tokens",
        json={"name": "Console test", "filename": "Console_Test.docx", "severity": "high"},
    ).json()

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        response = client.get(
            f"/t/{token['id']}/pixel.gif", headers={"user-agent": "LabBrowser/1.0"}
        )

    event = client.get("/api/events").json()[0]
    assert response.status_code == 200
    assert event["triage_label"] == "Honeytoken trigger - potential unauthorized access"
    assert event["severity"] == "high"
    assert "Triage: Honeytoken trigger - potential unauthorized access" in output.getvalue()
    assert "Severity: high" in output.getvalue()


def test_docx_relationship_and_filename_validation(tmp_path: Path):
    client = make_client(tmp_path)
    token = client.post(
        "/api/tokens",
        json={"name": "DOCX test", "filename": "DOCX_Test.docx", "severity": "high"},
    ).json()
    decoy = client.post(
        "/api/decoys",
        json={"token_id": token["id"], "format": "docx", "output_dir": str(tmp_path / "decoys")},
    )
    assert decoy.status_code == 200
    with zipfile.ZipFile(decoy.json()["path"]) as package:
        relationships = package.read("word/_rels/document.xml.rels").decode("utf-8")
    assert token["callback_url"] in relationships
    assert 'TargetMode="External"' in relationships

    invalid = client.post(
        "/api/tokens",
        json={"name": "Unsafe", "filename": "../outside.docx", "severity": "high"},
    )
    assert invalid.status_code == 422


def test_email_alert_content(tmp_path: Path):
    from app.alerts import render_alert

    token = {"id": "abc123", "name": "Finance bait", "filename": "Synthetic_Forecast.docx"}
    event = {
        "occurred_at": "2026-08-31T00:00:00+00:00",
        "source_ip": "203.0.113.10",
        "user_agent": "LabBrowser/1.0",
        "triage_label": "Honeytoken trigger - potential unauthorized access",
        "severity": "high",
        "duplicate": 0,
    }
    subject, body = render_alert(event, token)
    assert "Synthetic_Forecast.docx" in subject
    assert "203.0.113.10" in body
    assert "potential unauthorized access" in body
