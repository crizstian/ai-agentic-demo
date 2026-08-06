from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")
    return jsonify({"result": f"Pinging: {host}", "host": host})


@admin_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "admin panel active",
            "warning": "DEMO ONLY — not a real admin panel",
        }
    )
