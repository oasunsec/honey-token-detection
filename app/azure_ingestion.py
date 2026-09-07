from __future__ import annotations

from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient


class AzureMonitorIngestor:
    def __init__(self, endpoint: str, immutable_id: str, stream_name: str):
        self.immutable_id = immutable_id
        self.stream_name = stream_name
        self.client = LogsIngestionClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(exclude_interactive_browser_credential=True),
        )

    def publish(self, event: dict, token: dict, receiver: str) -> None:
        record = {
            "TimeGenerated": event["occurred_at"],
            "EventType": event["event_type"],
            "CanaryId": token.get("canary_id", ""),
            "ArtifactName": token.get("filename", ""),
            "SourceIp": event.get("source_ip", ""),
            "UserAgent": event.get("user_agent", ""),
            "Classification": event.get("triage_label", ""),
            "FirstHit": not bool(event.get("duplicate")),
            "RepeatCount": 1 if event.get("duplicate") else 0,
            "Receiver": receiver,
            "NotificationStatus": event.get("alert_status", "pending"),
            "EventId": str(event.get("id", event.get("event_id", ""))),
        }
        self.client.upload(rule_id=self.immutable_id, stream_name=self.stream_name, logs=[record])
