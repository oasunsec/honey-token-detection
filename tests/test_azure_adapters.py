from app.azure_ingestion import AzureMonitorIngestor
from app.azure_storage import AzureTableDatabase


def test_azure_storage_uses_service_table_creation(monkeypatch):
    created = []

    class FakeService:
        def __init__(self, *args, **kwargs):
            pass

        def create_table_if_not_exists(self, name):
            created.append(name)

        def get_table_client(self, name):
            return object()

    monkeypatch.setattr("app.azure_storage.TableServiceClient", FakeService)
    AzureTableDatabase("https://storage.example", "Hits", "Outbox")
    assert created == ["Hits", "Outbox"]


def test_ingestion_record_excludes_raw_callback_token(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def upload(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("app.azure_ingestion.LogsIngestionClient", FakeClient)
    ingestor = AzureMonitorIngestor("https://ingest.example", "dcr-id", "Custom-CanaryHit_CL")
    ingestor.publish(
        {"id": "event-1", "occurred_at": "2026-09-07T00:00:00+00:00", "event_type": "canary_trigger", "source_ip": "203.0.113.10", "user_agent": "Word", "triage_label": "trigger", "duplicate": False, "alert_status": "sent"},
        {"id": "raw-secret-token", "canary_id": "public-id", "filename": "Finance.docx"},
        "validation",
    )
    record = captured["logs"][0]
    assert record["CanaryId"] == "public-id"
    assert "raw-secret-token" not in str(record)
