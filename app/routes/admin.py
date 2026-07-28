import subprocess

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)


# FIXED: Command injection vulnerability - using safe subprocess call without shell=True
@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    # Validate host input - only allow alphanumeric, dots, and hyphens
    import re
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        return jsonify({"error": "Invalid host parameter"}), 400

    # Safe command execution without shell=True
    try:
        stdout = subprocess.check_output(
            ["echo", f"Pinging: {host}"],
            text=True,
            timeout=5
        )
    except subprocess.CalledProcessError:
        return jsonify({"error": "Ping failed"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Ping timeout"}), 500
    return jsonify({"result": stdout.strip(), "host": host})


@admin_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "admin panel active",
            "warning": "DEMO ONLY — not a real admin panel",
        }
    )
