import subprocess

from flask import Blueprint, jsonify, request

admin_bp = Blueprint("admin", __name__)


# DEMO VULNERABILITY: command injection via user-controlled host parameter (VULN-002)
# Do not fix — required for Semgrep SAST demo finding demo-bank-command-injection
@admin_bp.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "localhost")

    # Intentionally unsafe: user-controlled input passed directly to the shell
    cmd = "echo 'Pinging: " + host + "'"
    try:
        stdout = subprocess.check_output(cmd, shell=True, text=True)
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
