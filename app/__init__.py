# lab-4/app/__init__.py
import os
import random
from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST


http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['status_code']
)


def create_app():
    app = Flask(__name__)

    # Middleware для автоматического подсчёта всех HTTP-ответов
    @app.after_request
    def record_metrics(response):
        http_requests_total.labels(status_code=response.status_code).inc()
        return response

    # Эндпоинт для Prometheus. Отдаёт метрики в нужном формате.
    @app.route('/metrics')
    def metrics():
        return Response(
            generate_latest(),
            mimetype=CONTENT_TYPE_LATEST
        )

    # Модифицированный /health с поддержкой CHAOS_MODE
    @app.route("/health")
    def health():
        chaos_mode = os.environ.get('CHAOS_MODE', 'false').lower() == 'true'
        if chaos_mode and random.random() < 0.3:
            return jsonify(status="error"), 500
        return jsonify(status="ok"), 200

    @app.route("/new-feature")
    def new_feature():
        return jsonify(status="ok"), 200

    return app
