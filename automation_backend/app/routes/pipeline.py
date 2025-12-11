import os
from flask import current_app, send_from_directory, request
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.exceptions import NotFound, BadRequest

from ..extensions import db
from ..models import Job, Requirement, Artifact, Run, RunStep, Report
from ..schemas import JobSchema, ArtifactSchema, RunSchema
from ..services.parser import parse_requirements
from ..services.generator import generate_testcases_and_code
from ..services.pom_builder import build_pom_scaffold
from ..services.executor import run_pytests_with_allure
from ..services.artifacts import save_uploaded_file, write_json


blp = Blueprint("Pipeline", "pipeline", url_prefix="/api", description="Upload, parse, generate, execute, and report")


@blp.route("/upload")
class UploadAPI(MethodView):
    """
    Upload a CSV or Excel file containing requirements. Creates a Job record.
    """
    # PUBLIC_INTERFACE
    def post(self):
        """
        PUBLIC_INTERFACE
        summary: Upload requirements file
        description: Accepts multipart/form-data with 'file' field.
        responses:
          200: A job object with status 'uploaded'
        """
        if "file" not in request.files:
            raise BadRequest("No file part in the request")
        file = request.files["file"]
        if not file.filename:
            raise BadRequest("Empty filename")
        upload_path = save_uploaded_file(file, current_app.config["UPLOAD_FOLDER"])
        job = Job(filename=file.filename, original_path=upload_path, status="uploaded")
        db.session.add(job)
        db.session.commit()
        return JobSchema().dump(job)


@blp.route("/parse/<int:job_id>")
class ParseAPI(MethodView):
    """
    Parse uploaded file into normalized requirements and persist them.
    """
    # PUBLIC_INTERFACE
    def post(self, job_id: int):
        """
        PUBLIC_INTERFACE
        summary: Parse requirements
        description: Parse the uploaded SRS file associated with a job id.
        responses:
          200: Job with parsed requirements and artifacts updated.
        """
        job = Job.query.get(job_id)
        if not job:
            raise NotFound("Job not found")
        reqs, warnings = parse_requirements(job.original_path)
        # persist requirements
        for r in reqs:
            db.session.add(Requirement(job_id=job.id, **r))
        # artifact: parsed.json
        parsed_path = os.path.join(current_app.config["ARTIFACTS_FOLDER"], f"job_{job.id}", "parsed.json")
        write_json({"requirements": reqs, "warnings": warnings}, parsed_path)
        db.session.add(Artifact(job_id=job.id, type="parsed", path=parsed_path))
        job.status = "parsed"
        db.session.commit()
        return JobSchema().dump(job)


@blp.route("/generate/<int:job_id>")
class GenerateAPI(MethodView):
    """
    Generate testcases, POM scaffolds, and test files for a job's requirements.
    """
    # PUBLIC_INTERFACE
    def post(self, job_id: int):
        """
        PUBLIC_INTERFACE
        summary: Generate test cases and code
        description: Create test case templates, POM structure, and pytest files for the job.
        responses:
          200: Job with artifacts of generated content.
        """
        job = Job.query.get(job_id)
        if not job:
            raise NotFound("Job not found")
        reqs = Requirement.query.filter_by(job_id=job.id).all()
        req_dicts = [
            {
                "title": r.title,
                "description": r.description or "",
                "priority": r.priority or "",
                "component": r.component or "",
                "tags": r.tags or "",
            }
            for r in reqs
        ]

        gen_base = os.path.join(current_app.config["GENERATED_CODE_FOLDER"], f"job_{job.id}")
        os.makedirs(gen_base, exist_ok=True)

        # Build POM scaffold
        pom_path = build_pom_scaffold(req_dicts, gen_base)
        db.session.add(Artifact(job_id=job.id, type="pom", path=pom_path))

        # Generate testcases and pytest modules
        testcases, script_paths = generate_testcases_and_code(req_dicts, gen_base)
        tcs_path = os.path.join(gen_base, "testcases.json")
        write_json(testcases, tcs_path)
        db.session.add(Artifact(job_id=job.id, type="testcases", path=tcs_path))
        for p in script_paths:
            db.session.add(Artifact(job_id=job.id, type="script", path=p))

        job.status = "generated"
        db.session.commit()
        return JobSchema().dump(job)


@blp.route("/execute/<int:job_id>")
class ExecuteAPI(MethodView):
    """
    Execute generated tests for a given job and collect Allure results/report.
    """
    # PUBLIC_INTERFACE
    def post(self, job_id: int):
        """
        PUBLIC_INTERFACE
        summary: Execute tests with Allure
        description: Run pytest for generated tests and store allure results and report.
        responses:
          200: Run entity containing status and paths for results/report.
        """
        job = Job.query.get(job_id)
        if not job:
            raise NotFound("Job not found")

        gen_base = os.path.join(current_app.config["GENERATED_CODE_FOLDER"], f"job_{job.id}")
        tests_dir = os.path.join(gen_base, "tests")
        if not os.path.isdir(tests_dir):
            raise NotFound("No generated tests found; run generation first.")

        run = Run(job_id=job.id, status="running")
        db.session.add(run)
        db.session.commit()

        steps = [
            ("prepare", "Preparing environment"),
            ("pytest", "Executing pytest"),
            ("allure", "Generating Allure report"),
        ]
        step_entities = []
        for idx, (name, msg) in enumerate(steps):
            s = RunStep(run_id=run.id, name=name, status="running", log=msg, order_index=idx)
            db.session.add(s)
            step_entities.append(s)
        db.session.commit()

        allure_results = os.path.join(current_app.config["ALLURE_RESULTS_FOLDER"], f"job_{job.id}_run_{run.id}")
        allure_report = os.path.join(current_app.config["ALLURE_REPORT_FOLDER"], f"job_{job.id}_run_{run.id}")

        return_code, stdout, stderr = run_pytests_with_allure(
            tests_dir=tests_dir,
            allure_results_dir=allure_results,
            allure_report_dir=allure_report,
            timeout=current_app.config["PYTEST_TIMEOUT"],
            extra_args=current_app.config["PYTEST_EXTRA_ARGS"],
        )

        # Update steps
        step_entities[0].status = "passed"
        step_entities[0].log = "Preparation complete"
        step_entities[1].status = "passed" if return_code == 0 else "failed"
        step_entities[1].log = stdout + ("\n" + stderr if stderr else "")
        step_entities[2].status = "passed"
        step_entities[2].log = "Allure report generation attempted"

        run.status = "passed" if return_code == 0 else "failed"
        run.summary = f"Pytest return code: {return_code}"
        run.allure_results_path = allure_results
        run.allure_report_path = allure_report

        # Add report artifacts
        db.session.add(Report(run_id=run.id, type="allure-results", path=allure_results, status=run.status))
        db.session.add(Report(run_id=run.id, type="allure-report", path=allure_report, status=run.status))

        db.session.commit()

        return RunSchema().dump(run)


@blp.route("/artifacts/<int:job_id>")
class ArtifactsAPI(MethodView):
    """
    List artifacts for a job.
    """
    # PUBLIC_INTERFACE
    def get(self, job_id: int):
        """
        PUBLIC_INTERFACE
        summary: List artifacts
        description: Returns a list of artifacts created for the job.
        responses:
          200: List of artifacts
        """
        arts = Artifact.query.filter_by(job_id=job_id).order_by(Artifact.created_at.asc()).all()
        return ArtifactSchema(many=True).dump(arts)


@blp.route("/allure/<int:job_id>/<int:run_id>/report/<path:path>")
class AllureReportServe(MethodView):
    """
    Serve generated Allure static files if available.
    """
    # PUBLIC_INTERFACE
    def get(self, job_id: int, run_id: int, path: str):
        """
        PUBLIC_INTERFACE
        summary: Serve Allure report files
        description: Serves files from the generated Allure report directory.
        responses:
          200: Static file
        """
        run = Run.query.get(run_id)
        if not run or run.job_id != job_id:
            raise NotFound("Run not found")
        report_dir = run.allure_report_path
        if not report_dir or not os.path.isdir(report_dir):
            raise NotFound("Allure report not available")
        return send_from_directory(report_dir, path)


@blp.route("/jobs/<int:job_id>/allure/<path:path>")
class AllureJobStatic(MethodView):
    """
    Serve Allure report for the latest run of a job at a stable mount point.

    Mounted at: /api/jobs/<job_id>/allure/<path>
    Example index.html: /api/jobs/1/allure/index.html
    """
    # PUBLIC_INTERFACE
    def get(self, job_id: int, path: str):
        """
        PUBLIC_INTERFACE
        summary: Serve Allure static by job
        description: Finds the most recent run for a job and serves its Allure report statics.
        responses:
          200: Static file
        """
        run = (
            Run.query.filter_by(job_id=job_id)
            .order_by(Run.created_at.desc())
            .first()
        )
        if not run:
            raise NotFound("No runs found for job")
        report_dir = run.allure_report_path
        if not report_dir or not os.path.isdir(report_dir):
            raise NotFound("Allure report not available")
        return send_from_directory(report_dir, path)
