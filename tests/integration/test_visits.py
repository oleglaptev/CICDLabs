# lab-4/tests/integration/test_visits.py
import pytest
import psycopg2
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from flask import Flask
from app.visits import create_visits_blueprint


@pytest.fixture()
def app_client():
    with PostgresContainer("postgres:16") as pg, \
         RedisContainer("redis:7") as redis_c:

        conn = psycopg2.connect(
            pg.get_connection_url().replace("postgresql+psycopg2", "postgresql")
        )
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE visits (id SERIAL PRIMARY KEY, created_at TIMESTAMP)"
            )
        conn.commit()

        redis_url = f"redis://{redis_c.get_container_host_ip()}:{redis_c.get_exposed_port(6379)}"

        app = Flask(__name__)
        app.register_blueprint(create_visits_blueprint(conn, redis_url))

        yield app.test_client()

        conn.close()


def test_first_request_uses_database(app_client):
    response = app_client.get('/visits')
    assert response.status_code == 200
    assert response.get_json()['source'] == 'db'
    assert response.get_json()['count'] > 0


def test_second_request_uses_cache(app_client):
    app_client.get('/visits')
    response = app_client.get('/visits')
    assert response.get_json()['source'] == 'cache'
