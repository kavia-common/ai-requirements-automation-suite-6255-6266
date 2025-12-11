import os
from typing import Optional


def _read_db_url_from_file_fallback(base_dir: str) -> Optional[str]:
    """
    Attempt to parse a database connection URL from the automation_database/db_connection.txt
    only if DATABASE_URL is not set. Supports lines like:
      mysql+pymysql://user:pass@host:5001/dbname
    or a simple host:port style that will be mapped to MySQL with missing pieces ignored.

    Returns:
        A URL string or None.
    """
    # Look two levels up to find sibling database workspace if present
    # Current file is .../automation_backend/app/config.py
    repo_root = os.path.abspath(os.path.join(base_dir, "..", ".."))
    candidate = os.path.join(repo_root, "ai-requirements-automation-suite-6255-6264", "automation_database", "db_connection.txt")
    if not os.path.isfile(candidate):
        # also try a generic path in case workspace name differs
        candidate = os.path.join(repo_root, "automation_database", "db_connection.txt")
        if not os.path.isfile(candidate):
            return None
    try:
        with open(candidate, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            return None
        # If it already looks like a full SQLAlchemy URL, return as is
        if "://" in text:
            return text
        # Otherwise, try to parse simple "host:port/dbname user pass" formats (very lenient)
        # Expected simple example: host:5001/dbname user pass
        parts = text.split()
        first = parts[0]
        user = parts[1] if len(parts) > 1 else "root"
        password = parts[2] if len(parts) > 2 else ""
        host = first
        dbname = "automation"
        if "/" in first:
            host, dbname = first.split("/", 1)
        port = "3306"
        if ":" in host:
            host, port = host.split(":", 1)
        # Construct mysql+pymysql URL
        auth = f"{user}:{password}@" if password else f"{user}@"
        return f"mysql+pymysql://{auth}{host}:{port}/{dbname}"
    except Exception:
        return None


class Config:
    """Flask configuration loaded from environment variables.

    Database URL format:
      - Example (MySQL): mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
      - If DATABASE_URL is unset, we will attempt a one-time fallback by reading:
        automation_database/db_connection.txt and parsing it.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # DATABASE_URL handling with fallback parse
    _env_db_url = os.getenv("DATABASE_URL", "").strip()
    if not _env_db_url:
        _fallback = _read_db_url_from_file_fallback(BASE_DIR)
        SQLALCHEMY_DATABASE_URI = _fallback if _fallback else "sqlite:///automation_dev.db"
    else:
        SQLALCHEMY_DATABASE_URI = _env_db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
