"""Credential-free integration test through a real loopback SMTP connection."""
import socketserver
import threading
from email import policy
from email.parser import BytesParser

from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app


def test_callback_delivers_triaged_message_to_loopback_sink(tmp_path):
    messages = []
    smtp_trace = []

    class SMTPHandler(socketserver.StreamRequestHandler):
        def handle(self):
            self.connection.settimeout(5)
            self.wfile.write(b"220 local.test ESMTP\r\n")
            smtp_trace.append("S: 220 loopback SMTP sink ready")
            while line := self.rfile.readline():
                raw_line = line.rstrip(b"\r\n").decode("ascii", errors="replace")
                command = line.split(b" ", 1)[0].strip().upper()
                if command in {b"MAIL", b"RCPT"}:
                    smtp_trace.append(f"C: {command.decode()} [REDACTED]")
                elif command in {b"EHLO", b"HELO"}:
                    smtp_trace.append(f"C: {command.decode()} [LOCAL CLIENT]")
                elif command == b"DATA":
                    smtp_trace.append("C: DATA")
                else:
                    smtp_trace.append(f"C: {raw_line}")
                if command == b"DATA":
                    self.wfile.write(b"354 End with dot\r\n")
                    smtp_trace.append("S: 354 End with dot")
                    lines = []
                    while (line := self.rfile.readline()) not in (b".\r\n", b""):
                        lines.append(line)
                    messages.append(b"".join(lines))
                    self.wfile.write(b"250 Accepted\r\n")
                    smtp_trace.append("S: 250 Accepted")
                elif command == b"QUIT":
                    self.wfile.write(b"221 Bye\r\n")
                    smtp_trace.append("S: 221 Bye")
                    return
                else:
                    self.wfile.write(b"250 OK\r\n")
                    smtp_trace.append("S: 250 OK")

    with socketserver.TCPServer(("127.0.0.1", 0), SMTPHandler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = TestClient(create_app(Settings(
                db_path=str(tmp_path / "smtp.db"), alert_mode="email",
                smtp_host="127.0.0.1", smtp_port=server.server_address[1],
                smtp_starttls=False, smtp_user="", smtp_password="",
                smtp_from="canary@local.test", alert_to="qa@local.test",
            )))
            token = client.post("/api/tokens", json={"name": "SMTP QA", "filename": "Synthetic.docx"}).json()
            url = f"/t/{token['id']}/pixel.gif"
            assert client.get(url, headers={"user-agent": "LabBrowser/1.0"}).status_code == 200
            assert client.get(url, headers={"user-agent": "LabBrowser/1.0"}).status_code == 200
            assert len(messages) == 1
            message = BytesParser(policy=policy.default).parsebytes(messages[0])
            body = message.get_content()
            events = client.get("/api/events").json()
            assert [e["alert_status"] for e in events] == ["suppressed", "sent"]
            event = events[1]
            for field in ("occurred_at", "source_ip", "user_agent", "triage_label", "severity"):
                assert event[field] in body
            assert "Synthetic.docx" in body
            assert token["canary_id"] in body
            assert token["id"] not in body
            print("\nSMTP sink transcript (redacted)")
            print("\n".join(smtp_trace))
            print(
                "Result: callbacks=2 | persisted_events=2 | accepted_messages=1 "
                "| alert_statuses=suppressed,sent | raw_token_in_message=absent"
            )
        finally:
            server.shutdown()
            thread.join(timeout=5)
