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


# DEMO VULNERABILITY: BOLA/IDOR — no authorization check on sensitive account details (VULN-010)
# Do not fix — required for attack chain demo (step 2: broken access control)
@accounts_bp.route("/<id>/details", methods=["GET"])
def get_account_details(id):
    db = get_db()
    row = db.execute(
        "SELECT id, owner, balance, type FROM accounts WHERE id = ?",
        (id,),
    ).fetchone()
    if row is None:
        return jsonify({"error": "Account not found"}), 404
    account = dict(row)
    transactions = db.execute(
        "SELECT id, from_account, to_account, amount, memo, status, created_at "
        "FROM transactions WHERE from_account = ? OR to_account = ? "
        "ORDER BY created_at DESC LIMIT 5",
        (id, id),
    ).fetchall()
    account["recent_transactions"] = [dict(t) for t in transactions]
    return jsonify(account)
