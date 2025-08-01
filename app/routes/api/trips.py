from app.utils import htmx_login_required
from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    make_response,
)
import logging
from app.db_store import driver_crud, trips_crud
from datetime import datetime
from flask_login import login_required, current_user
from app.utils.static_resolvers import static_name_resolver
from app.utils.custom_decorators import require_ownership
from app.models import TripSearchData
from pydantic import ValidationError

trips_bp = Blueprint("trips", __name__, url_prefix="/trips")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@trips_bp.route("/create_trip")
@login_required
def create_trip():
    return render_template("pages/create_trip.html", page_wrap="create_trip")


@trips_bp.route("/query_trips")
def query_trips():
    params = request.args

    with current_app.db_manager.connection() as conn:
        try:
            search_data = TripSearchData(**params)
            energy_type = search_data.energy_type

            results = trips_crud.search_summaries_asst(
                conn=conn,
                start_city=search_data.start_city,
                end_city=search_data.end_city,
                passenger_nr=search_data.passenger_nr,
                start_date=search_data.start_date,
                max_price=search_data.max_price,
                driver_rating=search_data.driver_rating,
                energy_type=energy_type,
            )

            return render_template(
                "trips/trip_results.html", page_wrap="query_trips", trips=results
            )

        except ValidationError as ve:
            logger.error("Validation error during trip query: %s", ve.errors())
            errors = ve.errors()
            messages = [
                error["msg"].removeprefix("Value error, ").strip() for error in errors
            ]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                400,
            )
            return response

        except Exception as e:
            logger.error("Error during trip query: %s", e)
            messages = [
                "Un erreur s'est produite lors de la recherche de trajets. reessayez plus tard."
            ]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                500,
            )
            return response


@trips_bp.route("/view_trip/<trip_id>")
@htmx_login_required
def view_trip():
    trip_id = request.view_args.get("trip_id")
    return render_template("trips/trip_detail.html", trip_id=trip_id)


@trips_bp.route("/passenger-trips/<status>")
@htmx_login_required
@require_ownership("for_user")
def passenger_trips_by_status(status):
    status = request.view_args.get("status")
    user_id = current_user.user_id

    print(status)

    try:
        status_id = static_name_resolver("trip_status", status)
    except Exception:
        return "Invalid status", 400

    with current_app.db_manager.connection() as conn:
        trips = trips_crud.get_passenger_trips(conn, user_id, status_id)

    return render_template("trips/profile_trip_item.html", trips=trips or [])


@trips_bp.route("/driver-trips/<status>")
@htmx_login_required
@require_ownership("for_user")
def driver_trips_by_status(status):
    status = request.view_args.get("status")
    user_id = current_user.user_id

    try:
        status_id = static_name_resolver("trip_status", status)
    except Exception:
        return "Invalid status", 400

    with current_app.db_manager.connection() as conn:
        driver_data = driver_crud.get_driver_data(conn, user_id)
        if not driver_data:
            return "Driver data not found", 404

        driver_id = driver_data.get("id")

        trips = trips_crud.get_driver_trips(conn, driver_id, status)

    return render_template("trips/profile_trip_item.html", trips=trips or [])
