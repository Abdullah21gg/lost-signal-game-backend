from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
app = Flask(__name__)
CORS(app)
DB_PATH = os.path.join(os.path.dirname(__file__), "scores.db")
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db()
    conn.execute("""
    create table if not exists Scores (
    ID integer primary key autoincrement,
    name text not null,
    score integer not null,
    created_at DateTime deault current_timestamp
    )
    """)
    conn.commit()
    conn.close()
@app.route("/score", methods=["POST"])
def submit_score():
    data = request.get_json(silent=True)
    if not data or "name" not in data or "score" in data:
        return jsonify ({"error": "expected json with 'name' and 'score'" }), 400
    name = str(data["name"]).strip()[:20]
    if not name:
        name="anonymous"
    try:
        score = int(data["score"])
    except (ValueError, TypeError):
        return jsonify({"error": "'score' must be a number"}), 400
    conn = get_db()
    conn.execute("insert into scores (name, score) VALUES (?,?)", (name, score))
    conn.commit()
    conn.close()
    return jsonify({"status": "saved", "name": name, "score": score}), 201
@app.route("/scores", methods=["GET"])
def top_scores():
    conn = get_db
    rows = conn.execute(
        "Select name, score from scores order by score desc Limit 10"
    ).fetchall()
    conn.close()
    return jsonify([{"name": r["name"], "score": r["score"]} for r in rows])
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "signal lost API is running"})
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)