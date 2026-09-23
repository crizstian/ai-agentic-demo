from flask import Blueprint, jsonify

from ..db import get_db

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/<id>", methods=["GET"])
def get_account(id):
    db = get_db()
    row = db.execute("SELECT * FROM accounts WHERE id = ?", [id]).fetchone()
    if row is None:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(dict(row))


@accounts_bp.route("/", methods=["GET"])
def list_accounts():
    db = get_db()
    rows = db.execute("SELECT * FROM accounts").fetchall()
    return jsonify([dict(r) for r in rows])
