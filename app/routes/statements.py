import os

from flask import Blueprint, jsonify, request, send_file

statements_bp = Blueprint("statements", __name__)

STATEMENTS_DIR = os.path.join(os.path.dirname(__file__), "../../demo-statements")


@statements_bp.route("/", methods=["GET"])
def statements():
    file = request.args.get("file")

    if not file:
        return jsonify(
            {
                "statements": [
                    {"name": "statement-jan-2024.pdf", "date": "2024-01-31"},
                    {"name": "statement-feb-2024.pdf", "date": "2024-02-29"},
                    {"name": "statement-mar-2024.pdf", "date": "2024-03-31"},
                ]
            }
        )

    # FIXED: Path traversal vulnerability - using os.path.commonpath for robust path validation
    base = os.path.realpath(STATEMENTS_DIR)
    file_path = os.path.realpath(os.path.join(base, file))

    # Verify the resolved path is within the allowed directory
    try:
        common_path = os.path.commonpath([base, file_path])
        if common_path != base:
            return jsonify({"error": "Invalid file path"}), 400
    except ValueError:
        # Different drives on Windows or other path mismatch
        return jsonify({"error": "Invalid file path"}), 400

    if not os.path.exists(file_path):
        return jsonify({"error": "Statement file not found"}), 404
    if not os.path.isfile(file_path):
        return jsonify({"error": "Invalid file path"}), 400

    return send_file(file_path, as_attachment=True)
