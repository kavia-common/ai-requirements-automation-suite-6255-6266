import os


class Config:
    """Flask configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        # Example: mysql+pymysql://user:password@host:3306/dbname
        "sqlite:///automation_dev.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    STORAGE_BASE = os.getenv(
        "STORAGE_BASE",
        os.path.join(BASE_DIR, "storage")
    )
    UPLOAD_FOLDER = os.path.join(STORAGE_BASE, "uploads")
    ARTIFACTS_FOLDER = os.path.join(STORAGE_BASE, "artifacts")
    REPORTS_FOLDER = os.path.join(STORAGE_BASE, "reports")
    GENERATED_CODE_FOLDER = os.path.join(STORAGE_BASE, "generated")
    ALLURE_RESULTS_FOLDER = os.path.join(STORAGE_BASE, "allure-results")
    ALLURE_REPORT_FOLDER = os.path.join(STORAGE_BASE, "allure-report")

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # Execution settings
    PYTEST_TIMEOUT = int(os.getenv("PYTEST_TIMEOUT", "600"))  # seconds
    PYTEST_EXTRA_ARGS = os.getenv("PYTEST_EXTRA_ARGS", "")
