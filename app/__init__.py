from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    return app

    @app.route("/new-feature")
    def new_feature():
        return jsonify(status="new", data="untested"), 200