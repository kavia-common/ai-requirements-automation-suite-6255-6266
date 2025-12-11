from marshmallow import fields
from .extensions import ma


class RequirementSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    job_id = fields.Int()
    title = fields.Str()
    description = fields.Str(allow_none=True)
    priority = fields.Str(allow_none=True)
    component = fields.Str(allow_none=True)
    tags = fields.Str(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class ArtifactSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    job_id = fields.Int()
    type = fields.Str()
    path = fields.Str()
    meta = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class RunStepSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    run_id = fields.Int()
    name = fields.Str()
    status = fields.Str()
    log = fields.Str(allow_none=True)
    order_index = fields.Int()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class ReportSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    run_id = fields.Int()
    type = fields.Str()
    path = fields.Str()
    status = fields.Str(allow_none=True)
    meta = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class RunSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    job_id = fields.Int()
    status = fields.Str()
    summary = fields.Str(allow_none=True)
    allure_results_path = fields.Str(allow_none=True)
    allure_report_path = fields.Str(allow_none=True)
    steps = fields.List(fields.Nested(RunStepSchema))
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class JobSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    filename = fields.Str()
    original_path = fields.Str()
    status = fields.Str()
    notes = fields.Str(allow_none=True)
    requirements = fields.List(fields.Nested(RequirementSchema))
    artifacts = fields.List(fields.Nested(ArtifactSchema))
    runs = fields.List(fields.Nested(RunSchema))
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
