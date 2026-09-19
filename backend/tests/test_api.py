from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models.usage import UsageRecord
from app.models.user import User
from conftest import SessionLocal

client = TestClient(app)


def register_and_login(email: str) -> str:
    response = client.post('/api/v1/auth/register', json={
        'email': email,
        'password': 'secret123',
        'confirm_password': 'secret123',
        'full_name': 'Test Operator',
    })
    assert response.status_code == 201
    login = client.post('/api/v1/auth/login', data={'username': email, 'password': 'secret123'})
    assert login.status_code == 200
    return login.json()['access_token']


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_telemetry_validation():
    token = register_and_login('telemetry@example.com')
    payload = {
        'service': 'API Gateway',
        'event_type': 'http_request',
        'summary': 'teapot',
        'payload': {'status_code': 200},
    }
    response = client.post('/api/v1/telemetry/events', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201


def test_incident_creation():
    token = register_and_login('incidents@example.com')
    payload = {
        'title': 'Database latency spike',
        'description': 'The database is timing out under load.',
        'severity': 'HIGH',
        'status': 'INVESTIGATING',
        'affected_services': ['Database', 'API Gateway'],
    }
    response = client.post('/api/v1/incidents', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == payload['title']


def test_auth_flow():
    register = client.post('/api/v1/auth/register', json={
        'email': 'demo@example.com',
        'password': 'secret123',
        'full_name': 'Demo User',
    })
    assert register.status_code == 201

    login = client.post('/api/v1/auth/login', data={
        'username': 'demo@example.com',
        'password': 'secret123',
    })
    assert login.status_code == 200
    token = login.json()['access_token']
    assert token
    me = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200
    assert me.json()['plan'] == 'FREE'
    usage = client.get('/api/v1/auth/usage', headers={'Authorization': f'Bearer {token}'})
    assert usage.status_code == 200
    assert usage.json()['plan'] == 'FREE'


def test_ai_fallback_service():
    token = register_and_login('ai@example.com')
    response = client.post('/api/v1/ai/analyze', json={
        'incident_id': 1,
        'incident_title': 'Synthetic incident',
        'description': 'Latency increased across the gateway.',
        'severity': 'HIGH',
        'affected_services': ['API Gateway'],
        'logs': ['ERROR: database timeout'],
        'anomalies': ['latency_ms=640'],
        'metrics': ['error-rate=0.03'],
        'events': ['backpressure started'],
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code in {200, 404}


def test_auth_rejects_duplicate_and_invalid_password():
    register_and_login('duplicate@example.com')
    duplicate = client.post('/api/v1/auth/register', json={
        'email': 'duplicate@example.com', 'password': 'secret123', 'full_name': 'Duplicate User'
    })
    assert duplicate.status_code == 400
    invalid = client.post('/api/v1/auth/login', data={'username': 'duplicate@example.com', 'password': 'wrongpass'})
    assert invalid.status_code == 401


def test_pro_authorization_and_upgrade():
    token = register_and_login('plans@example.com')
    headers = {'Authorization': f'Bearer {token}'}
    incident = client.post('/api/v1/incidents', json={
        'title': 'Restricted analysis incident',
        'description': 'A real incident for plan authorization testing.',
        'severity': 'HIGH',
        'affected_services': ['API Gateway'],
    }, headers=headers)
    assert incident.status_code == 201
    payload = {
        'incident_id': incident.json()['id'],
        'incident_title': 'Restricted analysis',
        'description': 'Test',
        'severity': 'HIGH',
        'affected_services': ['API Gateway'],
    }
    forbidden = client.post('/api/v1/ai/pro-analysis', json=payload, headers=headers)
    assert forbidden.status_code == 403
    assert forbidden.json()['detail']['code'] == 'PLAN_REQUIRED'

    db = SessionLocal()
    user = db.query(User).filter(User.email == 'plans@example.com').first()
    assert user is not None
    user.plan = 'PRO'
    db.commit()
    db.close()
    allowed = client.post('/api/v1/ai/pro-analysis', json=payload, headers=headers)
    assert allowed.status_code == 200
    assert allowed.json()['confidence'] >= 0


def test_protected_routes_require_authentication():
    response = client.get('/api/v1/dashboard/summary')
    assert response.status_code == 401


def test_usage_limit_is_enforced_server_side():
    token = register_and_login('quota@example.com')
    db = SessionLocal()
    user = db.query(User).filter(User.email == 'quota@example.com').first()
    assert user is not None
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    db.add(UsageRecord(user_id=user.id, metric='logs', value=500, period_start=start, period_end=start + timedelta(days=1)))
    db.commit()
    db.close()
    response = client.post('/api/v1/telemetry/logs', json={
        'service': 'API Gateway', 'level': 'ERROR', 'message': 'quota test'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    assert response.json()['detail']['code'] == 'USAGE_LIMIT_EXCEEDED'


def test_incident_retrieval_and_status_change():
    token = register_and_login('lifecycle@example.com')
    headers = {'Authorization': f'Bearer {token}'}
    created = client.post('/api/v1/incidents', json={
        'title': 'Lifecycle incident', 'description': 'Investigating a test issue', 'severity': 'MEDIUM',
        'affected_services': ['API Gateway'],
    }, headers=headers)
    incident_id = created.json()['id']
    retrieved = client.get(f'/api/v1/incidents/{incident_id}', headers=headers)
    assert retrieved.status_code == 200
    updated = client.patch(f'/api/v1/incidents/{incident_id}/status', json={'status': 'RESOLVED'}, headers=headers)
    assert updated.status_code == 200
    assert updated.json()['status'] == 'RESOLVED'
