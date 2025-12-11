from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    """
    Service liveness probe endpoint.
    """
    # PUBLIC_INTERFACE
    def get(self):
        """Return a simple JSON stating the service is healthy (PUBLIC_INTERFACE)."""
        return {"message": "Healthy"}
