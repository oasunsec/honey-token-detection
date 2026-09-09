"""Detection metadata and independent delivery contracts."""
import json
import sqlite3
import ssl
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from app import main
from app.config import Settings
from app.db import Database
from app.privacy import public_id
from app.azure_storage import AzureTableDatabase
from app import alerts
from app.triage import classify
from azure.core.exceptions import ResourceNotFoundError


def client_and_token(tmp_path, monkeypatch, upload=None, **settings):
    if upload is not None:
        class Client:
            def __init__(self, **kwargs):
                pass
            def upload(self, **kwargs):
                upload(kwargs)
        monkeypatch.setattr('app.azure_ingestion.LogsIngestionClient', Client)
        settings.update(azure_dcr_endpoint='https://ingest.example.test', azure_dcr_immutable_id='test-dcr')
    client = TestClient(main.create_app(Settings(db_path=str(tmp_path/'events.db'), alert_mode='none', **settings)))
    token = client.post('/api/tokens', json={'name':'Detection test','filename':'Synthetic.docx'}).json()
    return client, token


@pytest.mark.parametrize('ua,classification,severity,scanner', [
    ('Microsoft Office/16.0', 'honeytoken_access','high',False),
    ('curl/8.0','automated_scanner','medium',True),
    ('Proofpoint','automated_scanner','medium',True),
    ('','honeytoken_access','high',False),
])
def test_structured_triage(ua, classification, severity, scanner):
    result = classify(ua)
    assert (result.classification, result.severity, result.is_scanner) == (classification, severity, scanner)
    assert result.reason and result.recommended_action == ('review' if scanner else 'investigate')


@pytest.mark.parametrize('ua,expected,scanner', [('Word/16.0','high',False),('curl/8.0','medium',True)])
def test_siem_metadata_and_repeat_counts(tmp_path, monkeypatch, ua, expected, scanner):
    captured=[]
    client, token = client_and_token(tmp_path, monkeypatch, captured.append)
    for _ in range(3):
        assert client.get(token['callback_url'], headers={'user-agent':ua}).status_code == 200
    rows=[call['logs'][0] for call in captured]
    assert [r['RepeatCount'] for r in rows] == [0,1,2]
    assert [r['IsDuplicate'] for r in rows] == [False,True,True]
    assert [r['FirstHit'] for r in rows] == [True,False,False]
    assert [r['AlertStatus'] for r in rows] == ['disabled','suppressed','suppressed']
    assert all(r['Severity'] == expected and r['IsScanner'] == scanner for r in rows)
    assert all(r['Classification'] == ('automated_scanner' if scanner else 'honeytoken_access') for r in rows)
    assert all(r['ActiveCanary'] and r['EventTime'] and r['ReceiverVersion'] for r in rows)
    assert len({r['EventId'] for r in rows}) == 3
    assert token['id'] not in json.dumps(captured)
    assert len(client.app.state.db.list_events()) == 3
    assert all(e['sentinel_status'] == 'sent' for e in client.app.state.db.list_events())


def test_ingestion_failure_preserves_event_and_pixel(tmp_path, monkeypatch):
    def fail(_):
        raise RuntimeError('credential or endpoint must never appear in diagnostics')
    client, token = client_and_token(tmp_path, monkeypatch, fail)
    response=client.get(token['callback_url'])
    assert response.status_code == 200 and response.headers['content-type'] == 'image/gif'
    event=client.get('/api/events').json()[0]
    assert event['sentinel_status'] == 'failed'
    assert event['sentinel_error'] == '[redacted diagnostic]'
    assert client.app.state.db.list_events()[0]['sentinel_error'] == 'RuntimeError'
    assert event['classification'] == 'honeytoken_access'
    assert event['alert_status'] == 'disabled'


def test_persistence_precedes_triage_and_delivery(tmp_path, monkeypatch):
    client, token = client_and_token(tmp_path, monkeypatch)
    original=main.classify
    def inspect(*args):
        events=client.app.state.db.list_events()
        assert len(events) == 1
        assert events[0]['triage_label'] == 'pending'
        return original(*args)
    monkeypatch.setattr(main, 'classify', inspect)
    assert client.get(token['callback_url']).status_code == 200


def test_alert_status_write_failure_does_not_skip_ingestion(tmp_path, monkeypatch):
    captured=[]
    client, token=client_and_token(tmp_path,monkeypatch,captured.append)
    def fail(*args):
        raise OSError('diagnostic-secret')
    monkeypatch.setattr(client.app.state.db,'set_alert_status',fail)
    assert client.get(token['callback_url']).status_code == 200
    assert len(captured)==1
    assert client.app.state.db.list_events()[0]['sentinel_status']=='sent'


@pytest.mark.parametrize('bad', ['bad', 'x'*300, 'bad%20token', 'bad.token'])
def test_malformed_token_returns_404_without_storage_lookup(tmp_path, monkeypatch, bad):
    client, _=client_and_token(tmp_path,monkeypatch)
    def unexpected(*args):
        pytest.fail('Malformed token reached storage')
    monkeypatch.setattr(client.app.state.db,'get_token',unexpected)
    assert client.get('/t/'+bad+'/pixel.gif').status_code==404


def test_no_token_leaks_through_user_agent_or_errors(tmp_path, monkeypatch):
    captured=[]
    client,token=client_and_token(tmp_path,monkeypatch,captured.append)
    assert client.get(token['callback_url'],headers={'user-agent':token['callback_url']}).status_code==200
    assert token['id'] not in json.dumps(captured)
    assert token['id'] not in client.get('/api/events').text


@pytest.mark.parametrize('route', ['/docs','/redoc','/openapi.json','/api/tokens','/api/events'])
def test_receiver_only_no_management_schema(tmp_path, route):
    client=TestClient(main.create_app(Settings(db_path=str(tmp_path/'receiver.db'),receiver_only=True)))
    assert client.get(route).status_code==404


def test_forwarded_headers_untrusted_by_default(tmp_path,monkeypatch):
    client,token=client_and_token(tmp_path,monkeypatch)
    client.get(token['callback_url'],headers={'x-forwarded-for':'198.51.100.42','user-agent':'Word'})
    assert client.app.state.db.list_events()[0]['source_ip']=='testclient'


def test_repeat_window_expiry_starts_new_window(tmp_path,monkeypatch):
    client,token=client_and_token(tmp_path,monkeypatch)
    client.get(token['callback_url'])
    old=(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat()
    with client.app.state.db.conn() as con:
        con.execute('UPDATE events SET occurred_at=?',(old,))
    client.get(token['callback_url'])
    event=client.app.state.db.list_events()[0]
    assert event['first_hit'] and event['repeat_count']==0


def test_azure_lookup_does_not_hide_service_outage():
    db=object.__new__(AzureTableDatabase)
    class Table:
        def get_entity(self,**kwargs):
            raise OSError('service outage')
    db.hits=Table()
    with pytest.raises(OSError):
        db.get_token('test')
    def missing(**kwargs):
        raise ResourceNotFoundError('not found')
    db.hits.get_entity=missing
    assert db.get_token('test') is None


def test_existing_sqlite_database_migrates_without_losing_events(tmp_path):
    path=tmp_path/'legacy.db'
    with sqlite3.connect(path) as con:
        con.execute('CREATE TABLE tokens (id TEXT PRIMARY KEY, name TEXT, filename TEXT, created_at TEXT, active INTEGER, severity TEXT, notes TEXT)')
        con.execute('CREATE TABLE events (id INTEGER PRIMARY KEY, token_id TEXT, occurred_at TEXT, source_ip TEXT, user_agent TEXT, request_path TEXT, event_type TEXT, triage_label TEXT, severity TEXT, duplicate INTEGER)')
        con.execute("INSERT INTO tokens VALUES('legacy','Example','Example.docx','2026-01-01',1,'high','')")
        con.execute("INSERT INTO events VALUES(1,'legacy','2026-01-01','127.0.0.1','Word','/t/legacy/pixel.gif','canary_trigger','old','high',0)")
    db=Database(str(path))
    rows=db.list_events()
    assert len(rows)==1 and rows[0]['triage_label']=='old'
    assert rows[0]['classification']=='pending'


def test_source_changes_do_not_reset_canary_ua_window(tmp_path,monkeypatch):
    client,token=client_and_token(tmp_path,monkeypatch)
    client.get(token['callback_url'])
    with client.app.state.db.conn() as con:
        con.execute("UPDATE events SET source_ip='198.51.100.10'")
    client.get(token['callback_url'])
    event=client.app.state.db.list_events()[0]
    assert event['duplicate'] and event['repeat_count']==1 and event['alert_status']=='suppressed'


def test_simultaneous_same_token_and_user_agent_has_one_first_hit(tmp_path, monkeypatch):
    client, token = client_and_token(tmp_path, monkeypatch)
    db = client.app.state.db
    original_add_event = db.add_event
    committed = threading.Barrier(2)

    def add_event_then_wait(*args, **kwargs):
        event = original_add_event(*args, **kwargs)
        committed.wait(timeout=5)
        return event

    monkeypatch.setattr(db, 'add_event', add_event_then_wait)
    callback = token['callback_url']
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(
            lambda _: client.get(callback, headers={'user-agent': 'Word/16.0'}),
            range(2),
        ))

    assert [response.status_code for response in responses] == [200, 200]
    events = db.list_events()
    assert len(events) == 2
    assert sum(event['first_hit'] for event in events) == 1
    assert sorted(event['repeat_count'] for event in events) == [0, 1]
    assert sum(event['alert_status'] != 'suppressed' for event in events) == 1


def test_diagnostics_are_redacted_at_management_api_but_retained_in_sqlite(tmp_path, monkeypatch):
    client, token = client_and_token(tmp_path, monkeypatch)
    db = client.app.state.db
    event = db.add_event(
        token_id=token['id'], source_ip='testclient', user_agent='Word/16.0',
        request_path='/t/[redacted]/pixel.gif', event_type='canary_trigger',
        triage_label='pending', severity='unknown', duplicate=False,
    )
    secret = 'operator-only-secret-9f4d'
    db.set_alert_status(event['id'], 'failed', secret)
    db.set_sentinel_status(event['id'], 'failed', secret)

    stored = db.list_events()[0]
    assert stored['alert_error'] == secret
    assert stored['sentinel_error'] == secret
    public = client.get('/api/events')
    assert public.status_code == 200
    body = public.json()[0]
    assert body['alert_error'] == '[redacted diagnostic]'
    assert body['sentinel_error'] == '[redacted diagnostic]'
    assert secret not in public.text


def test_smtp_starttls_uses_verified_context_before_login_and_send(monkeypatch):
    calls = []

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            calls.append(('connect', host, port, timeout))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            calls.append(('close',))

        def starttls(self, context):
            assert context.verify_mode == ssl.CERT_REQUIRED
            assert context.check_hostname is True
            calls.append(('starttls',))

        def login(self, user, password):
            assert calls[-1] == ('starttls',)
            calls.append(('login', user))

        def send_message(self, message):
            assert calls[-1] == ('login', 'operator')
            calls.append(('send', message['Subject']))

    monkeypatch.setattr(alerts.smtplib, 'SMTP', FakeSMTP)
    result = alerts.send_alert(
        Settings(alert_mode='email', smtp_host='smtp.example.test', smtp_port=587,
                 smtp_user='operator', smtp_password='password',
                 smtp_from='canary@example.test', alert_to='soc@example.test'),
        {'occurred_at': '2026-09-07T00:00:00+00:00', 'source_ip': '127.0.0.1',
         'user_agent': 'Word/16.0', 'triage_label': 'Honeytoken access',
         'severity': 'high', 'duplicate': False},
        {'id': 'a' * 24, 'name': 'Synthetic', 'filename': 'Synthetic.docx',
         'severity': 'high'},
    )
    assert result == 'sent'
    assert [call[0] for call in calls] == ['connect', 'starttls', 'login', 'send', 'close']
