# lab-4/app/visits.py
from flask import Blueprint, jsonify
import redis as redis_lib


def create_visits_blueprint(db_conn, redis_url):
    bp = Blueprint('visits', __name__)
    r = redis_lib.from_url(redis_url)

    @bp.route('/visits')
    def visits():
        cached = r.get('visits_count')
        if cached:
            return jsonify(count=int(cached), source='cache')

        with db_conn.cursor() as cur:
            cur.execute("INSERT INTO visits (created_at) VALUES (NOW()) RETURNING id")
            new_id = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM visits")
            count = cur.fetchone()[0]
        db_conn.commit()

        r.setex('visits_count', 10, count)
        return jsonify(count=count, source='db', lastId=new_id)

    return bp
