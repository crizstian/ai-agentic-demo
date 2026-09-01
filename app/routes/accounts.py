from flask import Blueprint, jsonify

from ..db import get_db

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/<id>", methods=["GET"])
def get_account(id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM accounts WHERE id = ?", (id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(dict(row))


@accounts_bp.route("/", methods=["GET"])
def list_accounts():
    db = get_db()
    rows = db.execute("SELECT * FROM accounts").fetchall()
    return jsonify([dict(r) for r in rows])


# [REMEDIATED] VULN-010: Added authorization check via X-Account-Owner header
@accounts_bp.route("/<id>/details", methods=["GET"])
def get_account_details(id):
    from flask import request

    db = get_db()
    row = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (id,),
    ).fetchone()
    if row is None:
        return jsonify({"error": "Account not found"}), 404

    account_owner = request.headers.get("X-Account-Owner")
    if not account_owner or account_owner != row["owner"]:
        return jsonify({"error": "Forbidden — account owner mismatch"}), 403

    account = dict(row)
    transactions = db.execute(
        "SELECT id, from_account, to_account, amount, memo, status, created_at "
        "FROM transactions WHERE from_account = ? OR to_account = ? "
        "ORDER BY created_at DESC LIMIT 5",
        (id, id),
    ).fetchall()
    account["recent_transactions"] = [dict(t) for t in transactions]
    return jsonify(account)
