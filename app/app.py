import os

from flask import Flask, jsonify, redirect, render_template, request
from flask_cors import CORS

from .db import get_db
from .routes.accounts import accounts_bp
from .routes.admin import admin_bp
from .routes.fx import fx_bp
from .routes.statements import statements_bp
from .routes.transfers import transfers_bp

APP_NAME = "DemoBank AI SDLC"


def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="",
        template_folder="templates",
    )

    # Serve /api/fx and /api/fx/ identically, matching the Node app's routing
    # (Express did not 308-redirect on a missing trailing slash).
    app.url_map.strict_slashes = False

    # DEMO VULNERABILITY: insecure CORS wildcard (VULN-007)
    # Do not fix — required for Semgrep SAST demo finding demo-bank-insecure-cors
    CORS(app, origins="*")

    # API blueprints
    app.register_blueprint(accounts_bp, url_prefix="/api/accounts")
    app.register_blueprint(transfers_bp, url_prefix="/api/transfers")
    app.register_blueprint(statements_bp, url_prefix="/api/statements")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(fx_bp, url_prefix="/api/fx")

    # Dashboard
    @app.route("/")
    def dashboard():
        db = get_db()
        accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
        transactions = [
            dict(r)
            for r in db.execute(
                "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5"
            ).fetchall()
        ]
        return render_template(
            "dashboard.html",
            accounts=accounts,
            transactions=transactions,
            app_name=APP_NAME,
        )

    # Transfer page
    @app.route("/transfer")
    def transfer_page():
        db = get_db()
        accounts = [dict(r) for r in db.execute("SELECT * FROM accounts").fetchall()]
        return render_template(
            "transfer.html",
            accounts=accounts,
            app_name=APP_NAME,
            error=None,
            success=None,
        )

    # Bill payment page
    @app.route("/pay-bill")
    def pay_bill():
        return render_template("pay-bill.html", app_name=APP_NAME)

    # Login page
    @app.route("/login", methods=["GET"])
    def login_page():
        return render_template("login.html", app_name=APP_NAME, error=None)

    @app.route("/login", methods=["POST"])
    def login_submit():
        # Demo: accept any credentials
        return redirect("/")

    # DEMO VULNERABILITY: reflected XSS — query param reflected directly into HTML (VULN-006)
    # Do not fix — required for Semgrep SAST demo finding demo-bank-reflected-xss
    @app.route("/welcome")
    def welcome():
        name = request.args.get("name", "Guest")
        return (
            "<html><body><h1>Welcome to DemoBank, "
            + request.args.get("name", "")
            + "!</h1><p>This is a demo application.</p></body></html>"
        )

    # Health endpoint — correct path for liveness/readiness
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app
