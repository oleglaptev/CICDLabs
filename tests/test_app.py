from app import create_app


def test_health_returns_200():
    client = create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_new_feature_returns_200():
    client = create_app().test_client()

    response = client.get("/new-feature")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}