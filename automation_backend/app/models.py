from datetime import datetime
from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Job(db.Model, TimestampMixin):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), default="uploaded", nullable=False)
    notes = db.Column(db.Text, nullable=True)

    requirements = db.relationship("Requirement", backref="job", lazy=True, cascade="all, delete-orphan")
    artifacts = db.relationship("Artifact", backref="job", lazy=True, cascade="all, delete-orphan")
    runs = db.relationship("Run", backref="job", lazy=True, cascade="all, delete-orphan")


class Requirement(db.Model, TimestampMixin):
    __tablename__ = "requirements"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(50), nullable=True)
    component = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default="parsed", nullable=False)


class Artifact(db.Model, TimestampMixin):
    __tablename__ = "artifacts"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # excel, prompt, testcase, script, pom, etc.
    path = db.Column(db.String(500), nullable=False)
    meta = db.Column(db.Text, nullable=True)


class Run(db.Model, TimestampMixin):
    __tablename__ = "runs"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(db.String(50), default="created", nullable=False)  # created, running, passed, failed, error
    summary = db.Column(db.Text, nullable=True)
    allure_results_path = db.Column(db.String(500), nullable=True)
    allure_report_path = db.Column(db.String(500), nullable=True)

    steps = db.relationship("RunStep", backref="run", lazy=True, cascade="all, delete-orphan")
    reports = db.relationship("Report", backref="run", lazy=True, cascade="all, delete-orphan")


class RunStep(db.Model, TimestampMixin):
    __tablename__ = "run_steps"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default="pending", nullable=False)  # pending, running, passed, failed, error
    log = db.Column(db.Text, nullable=True)
    order_index = db.Column(db.Integer, nullable=False, default=0)


class Report(db.Model, TimestampMixin):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # allure, json, summary
    path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), nullable=True)  # passed/failed/...
    meta = db.Column(db.Text, nullable=True)
