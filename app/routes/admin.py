import subprocess

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)


# SECURITY FIX: Use allowlist to prevent command injection (VULN-002)
@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    # Safe: validate host against allowlist before processing
    allowed_hosts = ["localhost", "127.0.0.1"]
    if host not in allowed_hosts:
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
