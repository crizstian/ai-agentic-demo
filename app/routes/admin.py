import re

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)

_SAFE_HOST_RE = re.compile(r"^[a-zA-Z0-9.\-]{1,253}$")


@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    if not _SAFE_HOST_RE.match(host):
        return jsonify({"error": "Invalid host"}), 400

    return jsonify({"result": f"Pinging: {host}", "host": host})


@admin_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "admin panel active",
            "warning": "DEMO ONLY — not a real admin panel",
        }
    )
