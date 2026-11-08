# lab-4/tests/unit/test_app.py
import random as random_module

import pytest
from prometheus_client import REGISTRY

from app import create_app


@pytest.fixture()
def client():
    return create_app().test_client()


def _sample(status_code):
    value = REGISTRY.get_sample_value(
        'http_requests_total', {'status_code': str(status_code)}
    )
    return value if value is not None else 0.0


def test_health_returns_200_by_default(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_health_chaos_mode_disabled_ignores_random(client, monkeypatch):
    monkeypatch.setenv('CHAOS_MODE', 'false')
    monkeypatch.setattr(random_module, 'random', lambda: 0.0)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_health_chaos_mode_returns_500_below_threshold(client, monkeypatch):
    monkeypatch.setenv('CHAOS_MODE', 'true')
    monkeypatch.setattr(random_module, 'random', lambda: 0.1)
    response = client.get('/health')
    assert response.status_code == 500
    assert response.get_json() == {'status': 'error'}


def test_health_chaos_mode_returns_200_above_threshold(client, monkeypatch):
    monkeypatch.setenv('CHAOS_MODE', 'true')
    monkeypatch.setattr(random_module, 'random', lambda: 0.9)
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_new_feature_returns_200(client):
    response = client.get('/new-feature')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}


def test_metrics_endpoint_exposes_prometheus_format(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert response.mimetype == 'text/plain'
    assert b'http_requests_total' in response.data


def test_metrics_counter_increments_with_status_code(client):
    before = _sample(200)
    client.get('/health')
    after = _sample(200)
    assert after - before == 1.0


def test_metrics_counter_tracks_5xx(client, monkeypatch):
    monkeypatch.setenv('CHAOS_MODE', 'true')
    monkeypatch.setattr(random_module, 'random', lambda: 0.0)
    before = _sample(500)
    client.get('/health')
    after = _sample(500)
    assert after - before == 1.0