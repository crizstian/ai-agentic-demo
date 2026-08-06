from flask import Blueprint, jsonify, request

from ..db import get_db

transfers_bp = Blueprint("transfers", __name__)


@transfers_bp.route("/", methods=["POST"])
def create_transfer():
    body = request.get_json(silent=True) or request.form
    from_account = body.get("fromAccount")
    to_account = body.get("toAccount")
    amount = body.get("amount")
    memo = body.get("memo")

    if not from_account or not to_account or amount is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    db = get_db()

    src = db.execute(
        "SELECT id FROM accounts WHERE id = ?", (from_account,)
    ).fetchone()
    if src is None:
        return jsonify({"error": "Source account not found"}), 404

    cursor = db.execute(
        "INSERT INTO transactions (from_account, to_account, amount, memo, status) VALUES (?, ?, ?, ?, ?)",
        [from_account, to_account, amount, memo or "", "completed"],
    )
    db.commit()
    return jsonify(
        {
            "success": True,
            "message": "Transfer completed successfully",
            "transferId": cursor.lastrowid,
            "amount": amount,
        }
    )


@transfers_bp.route("/", methods=["GET"])
def list_transfers():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 20"
    ).fetchall()
    return jsonify([dict(r) for r in rows])
