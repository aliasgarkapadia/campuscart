import os, socket
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "dev")

def db_password():
    f = os.getenv("DB_PASSWORD_FILE")
    return open(f).read().strip() if f else os.getenv("DB_PASSWORD", "")

def get_conn():
    c = psycopg2.connect(host=os.getenv("DB_HOST", "db"),
                         dbname=os.getenv("DB_NAME", "campuscart"),
                         user=os.getenv("DB_USER", "campuscart"),
                         password=db_password())
    with c.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS orders(id SERIAL PRIMARY KEY, item TEXT, qty INT)")
    c.commit()
    return c

@app.get("/health")
def health():
    if os.getenv("BROKEN") == "true":
        return jsonify(status="fail", version=VERSION), 500
    return jsonify(status="ok", version=VERSION, instance=socket.gethostname())

@app.get("/orders")
def list_orders():
    with get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, item, qty FROM orders ORDER BY id")
        rows = [dict(id=r[0], item=r[1], qty=r[2]) for r in cur.fetchall()]
    return jsonify(orders=rows, served_by=socket.gethostname())

@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    if not data.get("item") or not isinstance(data.get("qty"), int):
        return jsonify(error="item and integer qty required"), 400
    with get_conn() as c, c.cursor() as cur:
        cur.execute("INSERT INTO orders(item, qty) VALUES (%s,%s) RETURNING id", (data["item"], data["qty"]))
        new_id = cur.fetchone()[0]
    return jsonify(id=new_id, served_by=socket.gethostname()), 201
