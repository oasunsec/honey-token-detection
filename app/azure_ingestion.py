from __future__ import annotations

from azure.identity import DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient
from .privacy import public_id, redact


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
            "CanaryId": public_id(token["id"]),
            "ArtifactName": token.get("filename", ""),
            "SourceIp": event.get("source_ip", ""),
            "UserAgent": event.get("user_agent", ""),
            "Classification": event.get("classification", "unknown"),
            "Severity": event.get("severity", "unknown"),
            "IsScanner": bool(event.get("is_scanner", False)),
            "IsDuplicate": bool(event.get("duplicate", False)),
            "ActiveCanary": bool(event.get("active_canary", False)),
            "Reason": event.get("reason", ""),
            "RecommendedAction": event.get("recommended_action", ""),
            "EventTime": event["occurred_at"],
            "AlertStatus": event.get("alert_status", "pending"),
            "ReceiverVersion": receiver,
            "FirstHit": bool(event.get("first_hit", False)),
            "RepeatCount": int(event.get("repeat_count", 0)),
            "Receiver": receiver,
            "NotificationStatus": event.get("alert_status", "pending"),
            "EventId": str(event.get("event_id", event.get("id", ""))),
        }
        self.client.upload(rule_id=self.immutable_id, stream_name=self.stream_name, logs=[redact(record, token["id"])])
