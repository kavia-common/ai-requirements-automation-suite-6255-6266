import os
from flask import Flask
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
    api.register_blueprint(health_blp)
    api.register_blueprint(pipeline_blp)

    # Ensure storage directories exist
    for path in [
        app.config["UPLOAD_FOLDER"],
        app.config["ARTIFACTS_FOLDER"],
        app.config["REPORTS_FOLDER"],
        app.config["GENERATED_CODE_FOLDER"],
        app.config["ALLURE_RESULTS_FOLDER"],
        app.config["ALLURE_REPORT_FOLDER"],
    ]:
        os.makedirs(path, exist_ok=True)

    return app


# PUBLIC_INTERFACE
def get_app() -> Flask:
    """Return the initialized Flask app (PUBLIC_INTERFACE)."""
    return create_app()


# Keep backward compatibility with run.py importing 'app'
app = create_app()
