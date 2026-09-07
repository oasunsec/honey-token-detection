from __future__ import annotations

from datetime import datetime, timezone
import uuid

from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential


class AzureTableDatabase:
    """Small Table Storage implementation matching the local Database contract."""

    def __init__(self, account_url: str, hits_table: str = "CanaryHits", outbox_table: str = "NotificationOutbox"):
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        self.service = TableServiceClient(endpoint=account_url, credential=credential)
        self.service.create_table_if_not_exists(hits_table)
        self.service.create_table_if_not_exists(outbox_table)
        self.hits = self.service.get_table_client(hits_table)
        self.outbox = self.service.get_table_client(outbox_table)

    def create_token(self, token_id: str, name: str, filename: str, severity: str, notes: str = "") -> dict:
        entity = {
            "PartitionKey": "token",
            "RowKey": token_id,
            "entity_type": "token",
            "name": name,
            "filename": filename,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "severity": severity,
            "notes": notes,
        }
        self.hits.upsert_entity(entity)
        return self.get_token(token_id)  # type: ignore[return-value]

    def get_token(self, token_id: str) -> dict | None:
        try:
            entity = self.hits.get_entity(partition_key="token", row_key=token_id)
        except Exception:
            return None
        token = dict(entity)
        token["id"] = token.get("RowKey", token_id)
        return token

    def list_tokens(self) -> list[dict]:
        rows = self.hits.query_entities("PartitionKey eq 'token'")
        tokens = []
        for row in rows:
            token = dict(row)
            token["id"] = token.get("RowKey", "")
            tokens.append(token)
        return sorted(tokens, key=lambda row: row.get("created_at", ""), reverse=True)

    def set_active(self, token_id: str, active: bool) -> None:
        token = self.get_token(token_id)
        if token is None:
            return
        token["active"] = bool(active)
        self.hits.update_entity(token, mode="merge")

    def recent_matching_event(self, token_id: str, source_ip: str, user_agent: str, since_iso: str) -> bool:
        rows = self.hits.query_entities(
            "PartitionKey eq 'event' and token_id eq @token_id and source_ip eq @source_ip and user_agent eq @user_agent",
            parameters={"token_id": token_id, "source_ip": source_ip, "user_agent": user_agent},
        )
        return any(row.get("occurred_at", "") >= since_iso for row in rows)

    def add_event(
        self,
        token_id: str,
        source_ip: str,
        user_agent: str,
        request_path: str,
        event_type: str,
        triage_label: str,
        severity: str,
        duplicate: bool,
    ) -> dict:
        token = self.get_token(token_id) or {}
        event_id = uuid.uuid4().hex
        entity = {
            "PartitionKey": "event",
            "RowKey": event_id,
            "entity_type": "event",
            "event_id": event_id,
            "id": event_id,
            "token_id": token_id,
            "token_name": token.get("name", ""),
            "filename": token.get("filename", ""),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "source_ip": source_ip,
            "user_agent": user_agent,
            "request_path": request_path,
            "event_type": event_type,
            "triage_label": triage_label,
            "severity": severity,
            "duplicate": bool(duplicate),
            "alert_status": "pending",
            "alert_error": "",
            "sentinel_status": "pending",
            "sentinel_error": "",
        }
        self.hits.create_entity(entity)
        return dict(entity)

    def set_alert_status(self, event_id: str, status: str, error: str = "") -> None:
        self._merge_event(event_id, {"alert_status": status, "alert_error": error})

    def set_sentinel_status(self, event_id: str, status: str, error: str = "") -> None:
        self._merge_event(event_id, {"sentinel_status": status, "sentinel_error": error})

    def _merge_event(self, event_id: str, values: dict) -> None:
        values = {"PartitionKey": "event", "RowKey": event_id, **values}
        self.hits.update_entity(values, mode="merge")

    def list_events(self, limit: int = 100) -> list[dict]:
        rows = [dict(row) for row in self.hits.query_entities("PartitionKey eq 'event'")]
        rows.sort(key=lambda row: row.get("occurred_at", ""), reverse=True)
        return rows[:limit]
