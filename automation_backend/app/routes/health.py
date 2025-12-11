from flask_smorest import Blueprint
from flask.views import MethodView

# Expose health under both root and /api to help platform health checks
blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class Index(MethodView):
    """
    Root index with brief service info and health.
    """
    # PUBLIC_INTERFACE
    def get(self):
        """Return service info and basic health (PUBLIC_INTERFACE)."""
        return {"message": "Healthy", "service": "Requirements Automation API", "health": "ok"}


@blp.route("/api/health")
class HealthCheck(MethodView):
    """
    Service liveness probe endpoint.
    """
    # PUBLIC_INTERFACE
    def get(self):
        """Return a simple JSON stating the service is healthy (PUBLIC_INTERFACE)."""
        return {"message": "Healthy"}
