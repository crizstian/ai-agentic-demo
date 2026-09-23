import re
import shlex
import subprocess

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)

_SAFE_HOST_RE = re.compile(r"^[a-zA-Z0-9._\-]+$")


@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    if not _SAFE_HOST_RE.match(host):
        return jsonify({"error": "Invalid host parameter"}), 400

    try:
        stdout = subprocess.check_output(
            ["echo", f"Pinging: {host}"],
            text=True,
            timeout=10,
        )
    except subprocess.CalledProcessError:
        return jsonify({"error": "Ping failed"}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Ping timed out"}), 504
    return jsonify({"result": stdout.strip(), "host": host})


@admin_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "admin panel active",
            "warning": "DEMO ONLY — not a real admin panel",
        }
    )
