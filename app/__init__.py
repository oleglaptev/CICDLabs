from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    @app.route("/new-feature")
    def new_feature():
        return jsonify(status="new", data="untested"), 200

    @app.route("/users")
    def users():
        return jsonify(users=["Alice", "Bob", "Charlie"]), 200

    @app.route("/products")
    def products():
        return jsonify(products=[
            {"id": 1, "name": "Laptop", "price": 1000},
            {"id": 2, "name": "Phone", "price": 500},
            {"id": 3, "name": "Tablet", "price": 300},
        ]), 200

    @app.route("/orders")
    def orders():
        return jsonify(orders=[
            {"id": 101, "user": "Alice", "product": "Laptop"},
            {"id": 102, "user": "Bob", "product": "Phone"},
        ]), 200

    @app.route("/stats")
    def stats():
        return jsonify(
            total_users=3,
            total_products=3,
            total_orders=2,
            revenue=1500
        ), 200
    return app
