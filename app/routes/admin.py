import re
import subprocess

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)

_ALLOWED_HOST_PATTERN = re.compile(r'^[a-zA-Z0-9.\-]{1,253}$')


@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    if not _ALLOWED_HOST_PATTERN.match(host):
        return jsonify({"error": "Invalid host"}), 400

    try:
        stdout = subprocess.check_output(
            ["echo", f"Pinging: {host}"], shell=False, text=True
        )
    except subprocess.CalledProcessError:
        return jsonify({"error": "Ping failed"}), 500
    return jsonify({"result": stdout.strip(), "host": host})


@admin_bp.route("/status", methods=["GET"])
def status():
    return jsonify(
        {
            "status": "admin panel active",
            "warning": "DEMO ONLY — not a real admin panel",
        }
    )
