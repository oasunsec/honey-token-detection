from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS tokens (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    severity TEXT NOT NULL DEFAULT 'high',
    notes TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    source_ip TEXT NOT NULL,
    user_agent TEXT NOT NULL,
    request_path TEXT NOT NULL,
    event_type TEXT NOT NULL,
    triage_label TEXT NOT NULL,
    severity TEXT NOT NULL,
    duplicate INTEGER NOT NULL DEFAULT 0,
    alert_status TEXT NOT NULL DEFAULT 'pending',
    alert_error TEXT NOT NULL DEFAULT '',
    FOREIGN KEY(token_id) REFERENCES tokens(id)
);
CREATE INDEX IF NOT EXISTS idx_events_token_time ON events(token_id, occurred_at);
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.init()

    @contextmanager
    def conn(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def init(self) -> None:
        with self.conn() as con:
            con.executescript(SCHEMA)
            columns = {row[1] for row in con.execute("PRAGMA table_info(events)")}
            if "alert_status" not in columns:
                con.execute("ALTER TABLE events ADD COLUMN alert_status TEXT NOT NULL DEFAULT 'pending'")
            if "alert_error" not in columns:
                con.execute("ALTER TABLE events ADD COLUMN alert_error TEXT NOT NULL DEFAULT ''")

    def create_token(self, token_id: str, name: str, filename: str, severity: str, notes: str = "") -> dict:
        created_at = datetime.now(timezone.utc).isoformat()
        with self.conn() as con:
            con.execute(
                "INSERT INTO tokens(id,name,filename,created_at,active,severity,notes) VALUES(?,?,?,?,1,?,?)",
                (token_id, name, filename, created_at, severity, notes),
            )
        return self.get_token(token_id)

    def get_token(self, token_id: str) -> dict | None:
        with self.conn() as con:
            row = con.execute("SELECT * FROM tokens WHERE id=?", (token_id,)).fetchone()
        return dict(row) if row else None

    def list_tokens(self) -> list[dict]:
        with self.conn() as con:
            rows = con.execute("SELECT * FROM tokens ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def set_active(self, token_id: str, active: bool) -> None:
        with self.conn() as con:
            con.execute("UPDATE tokens SET active=? WHERE id=?", (1 if active else 0, token_id))

    def recent_matching_event(self, token_id: str, source_ip: str, user_agent: str, since_iso: str) -> bool:
        with self.conn() as con:
            row = con.execute(
                """SELECT 1 FROM events
                   WHERE token_id=? AND source_ip=? AND user_agent=? AND occurred_at>=?
                   LIMIT 1""",
                (token_id, source_ip, user_agent, since_iso),
            ).fetchone()
        return row is not None

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
        occurred_at = datetime.now(timezone.utc).isoformat()
        with self.conn() as con:
            cur = con.execute(
                """INSERT INTO events(
                    token_id,occurred_at,source_ip,user_agent,request_path,event_type,triage_label,severity,duplicate,
                    alert_status,alert_error
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    token_id,
                    occurred_at,
                    source_ip,
                    user_agent,
                    request_path,
                    event_type,
                    triage_label,
                    severity,
                    1 if duplicate else 0,
                    "pending",
                    "",
                ),
            )
            event_id = cur.lastrowid
            row = con.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        return dict(row)

    def set_alert_status(self, event_id: int, status: str, error: str = "") -> None:
        with self.conn() as con:
            con.execute(
                "UPDATE events SET alert_status=?, alert_error=? WHERE id=?",
                (status, error, event_id),
            )

    def list_events(self, limit: int = 100) -> list[dict]:
        with self.conn() as con:
            rows = con.execute(
                """SELECT e.*, t.name AS token_name, t.filename AS filename
                   FROM events e JOIN tokens t ON e.token_id=t.id
                   ORDER BY e.id DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]
