import subprocess

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    # Safe: pass args as a list so the shell is never invoked; host is never
    # interpreted as a shell command regardless of its content.
    try:
        stdout = subprocess.check_output(
            ["echo", "Pinging:", host], shell=False, text=True
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
