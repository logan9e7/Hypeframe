from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    assert 'database' in response.json()

def test_moments_endpoint():
    with TestClient(app) as client:
        response = client.get('/api/moments')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_anonymous_legacy_submission_is_disabled():
    with TestClient(app) as client:
        response = client.post('/api/video-submissions',json={'moment_id':'gear-five','url':'https://www.youtube.com/watch?v=dQw4w9WgXcQ'})
    assert response.status_code == 410

def test_featured_requires_key(monkeypatch):
    monkeypatch.delenv('YOUTUBE_API_KEY',raising=False)
    with TestClient(app) as client:
        response = client.get('/api/videos/featured')
    assert response.status_code == 503
