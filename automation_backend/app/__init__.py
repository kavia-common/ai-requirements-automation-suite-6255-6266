import os
import logging
from flask import Flask, jsonify, redirect, url_for
from flask_cors import CORS
from flask_smorest import Api
from .extensions import db, ma, migrate
from .config import Config
from .routes.health import blp as health_blp
from .routes.pipeline import blp as pipeline_blp


def create_app() -> Flask:
    """
    Factory to create the Flask app, configure extensions, register blueprints,
    and set OpenAPI configuration.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Basic logger to surface key startup info quickly
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("automation_backend")

    # CORS: allow React frontend default origin
    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:3000"]}},
        supports_credentials=True,
    )

    # OpenAPI / API docs config
    app.config["API_TITLE"] = "Requirements Automation API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    api = Api(app)

    # OpenAPI tags metadata for better documentation grouping
    app.config["OPENAPI_TAGS"] = [
        {"name": "Health", "description": "Health check route"},
        {"name": "Pipeline", "description": "Upload, parse, generate, execute, and report"},
    ]

    api.register_blueprint(health_blp)
    api.register_blueprint(pipeline_blp)

    # Ensure storage directories exist (fast, non-blocking)
    for path in [
        app.config["UPLOAD_FOLDER"],
        app.config["ARTIFACTS_FOLDER"],
        app.config["REPORTS_FOLDER"],
        app.config["GENERATED_CODE_FOLDER"],
        app.config["ALLURE_RESULTS_FOLDER"],
        app.config["ALLURE_REPORT_FOLDER"],
    ]:
        os.makedirs(path, exist_ok=True)

    # Add ultra-lightweight helper routes to reduce any chance of docs/health appearing to hang
    @app.get("/openapi.json")
    def openapi_json_redirect():
        """
        Return the dynamically generated OpenAPI JSON.
        Flask-Smorest publishes it under /docs/openapi.json; expose at /openapi.json as well.
        """
        # Using redirect keeps it simple and avoids heavy serialization here
        return redirect("/docs/openapi.json", code=302)

    @app.get("/_info")
    def info():
        """
        Minimal service info endpoint purely for diagnostics.
        """
        return jsonify({
            "service": "Requirements Automation API",
            "version": app.config.get("API_VERSION", "v1"),
            "health": "ok"
        })

    # Log key config without touching DB
    try:
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///automation_dev.db")
        log.info("Startup: Using database URI (masked): %s", ("sqlite" if db_uri.startswith("sqlite") else db_uri.split('@')[-1]))
        log.info("Storage base: %s", app.config.get("STORAGE_BASE"))
    except Exception:
        # Never let logging break startup
        pass

    return app


# PUBLIC_INTERFACE
def get_app() -> Flask:
    """Return the initialized Flask app (PUBLIC_INTERFACE)."""
    return create_app()


# Keep backward compatibility with run.py importing 'app'
app = create_app()
