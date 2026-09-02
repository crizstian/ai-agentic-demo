from flask import Blueprint, jsonify

from ..db import get_db

accounts_bp = Blueprint("accounts", __name__)


# DEMO VULNERABILITY: SQL injection via string concatenation (VULN-001)
# Do not fix — required for Semgrep SAST demo finding demo-bank-sql-injection
@accounts_bp.route("/<id>", methods=["GET"])
def get_account(id):
    db = get_db()
    query = "SELECT * FROM accounts WHERE id = '" + id + "'"
    row = db.execute(query).fetchone()
    if row is None:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(dict(row))


@accounts_bp.route("/", methods=["GET"])
def list_accounts():
    db = get_db()
    rows = db.execute("SELECT * FROM accounts").fetchall()
    return jsonify([dict(r) for r in rows])
