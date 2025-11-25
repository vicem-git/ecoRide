import logging
from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    make_response,
)
from flask_login import current_user
from app.utils import (
    internal_access,
    transactional,
    require_ownership,
    htmx_login_required,
)
from app.db_store import driver_crud, mod_crud, user_crud

mods_bp = Blueprint("mods", __name__, url_prefix="/mods")

# MODULE LOGGER
logger = logging.getLogger(__name__)


# query all pending ok reviews, approve/ reject
# query all pending bad reviews w/trip summary, approve/ reject


@mods_bp.route("/get_pending_reviews", methods=["GET"])
@internal_access
@transactional()
@htmx_login_required
def get_pending_reviews(conn):
    try:
        filter = (
                request.form.get("select_reviews")
                or request.args.get("select_reviews")
                or None
        )
        if filter == "all":
            filter = None

        pending = mod_crud.get_pending_reviews(batch=50, filter=filter)
        pending = [p for p in pending] 

        response = make_response(
            render_template("moderators/pending_reviews.html", pending_r=pending),
            200,
        )
        return response

    except Exception as e:
        logger.error(f"Error fetching pending reviews: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500   


@mods_bp.route("/get_review_details/<review_id>", methods=["GET"])
@internal_access
@transactional()
@htmx_login_required
def get_review_details(conn, review_id):
    try:
        review = current_app.mongo_store.get_trip_review(review_id)
        if not review:
            raise Exception("Review not found")

        trip_id = review["trip_id"]
        passenger_id = review["passenger_id"]

        trip_details = mod_crud.get_trip_details(conn, trip_id)
        if not trip_details:
            raise Exception("Trip details not found")

        driver_id = trip_details["driver_id"]
        logger.debug(f"REVIEW TRIP DETAILS: {trip_details}")

        driver_user = driver_crud.get_driver_user(conn, driver_id)

        driver_email = user_crud.get_user_email(conn, driver_user)
        passenger_email = user_crud.get_user_email(conn, passenger_id)

        trip_details["passenger"] = passenger_email
        trip_details["driver"] = driver_email

        response = make_response(
            render_template(
                "moderators/review_details.html", review=review, trip=trip_details
            ),
            200,
        )
        return response

    except Exception as e:
        logger.error(f"Error fetching review details: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500


@mods_bp.route("/approve_review", methods=["POST"])
@internal_access
@transactional()
@htmx_login_required
def approve_review(conn):
    response = make_response("approved review", 200)
    response.headers["HX-Trigger"] = {
        "serverMsg": {
            "type": "mod-reviews-updated",
            "message": "La revue a été accepté avec succès.",
        }
    }

    return response


@mods_bp.route("/reject_review", methods=["POST"])
@internal_access
@transactional()
@htmx_login_required
def reject_review(conn):
    response = make_response("rejected review", 200)
    response.headers["HX-Trigger"] = {
        "serverMsg": {
            "type": "mod-reviews-updated",
            "message": "La revue a été rejetée avec succès.",
        }
    }
    return response
