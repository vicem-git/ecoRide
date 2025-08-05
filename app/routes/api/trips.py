from app.utils import htmx_login_required
from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    make_response,
)
import logging
from app.db_store import user_crud, driver_crud, trips_crud, tx_crud
from datetime import datetime
from flask_login import login_required, current_user
from app.utils import static_name_resolver, require_ownership, render_pydantic_errors
from app.models import TripSearchData, CreateTripData
from pydantic import ValidationError

trips_bp = Blueprint("trips", __name__, url_prefix="/trips")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@trips_bp.route("/create_trip", methods=["GET", "POST"])
@trips_bp.route("/create_trip/<driver_id>", methods=["GET", "POST"])
@htmx_login_required
def create_trip(driver_id=None):
    user_id = current_user.user_id

    if request.method == "GET":
        with current_app.db_manager.connection() as conn:
            try:
                driver_data = driver_crud.get_driver_data(conn, user_id)
                driver_id = driver_data.get("id") if driver_data else None

                if not driver_id:
                    response = make_response(
                        render_template(
                            "partials/server_msg.html",
                            messages=[
                                "Vous devez être conducteur pour créer un trajet. modifier les paramètres de votre profil"
                            ],
                            msg_case="info",
                        ),
                        400,
                    )
                    return response

                driver_preferences = driver_crud.get_driver_preferences(conn, driver_id)
                driver_vehicles = driver_crud.get_driver_vehicles(conn, driver_id)

                driver_info = {
                    "data": driver_data,
                    "preferences": driver_preferences,
                    "vehicles": driver_vehicles,
                }

                if not driver_info:
                    raise Exception("Driver info not found")

                return render_template(
                    "trips/create_trip.html", driver_info=driver_info
                )

            except ValueError as ve:
                logger.error("Validation error during driver status check: %s", ve)
                messages = ["Une erreur s'est produite, veuillez réessayer plus tard."]
                return make_response(
                    render_template(
                        "partials/server_msg.html", messages=messages, msg_case="error"
                    ),
                    400,
                )

            except Exception as e:
                logger.error("Error checking driver status: %s", e)
                messages = ["Une erreur s'est produite, veuillez réessayer plus tard."]
                response = make_response(
                    render_template(
                        "partials/server_msg.html",
                        messages=messages,
                        msg_case="error",
                    ),
                    500,
                )
                return response

    if request.method == "POST":
        print(f"driver id :{driver_id}")

        start_date = request.form.get("start_date")
        start_time = request.form.get("start_time")
        start_datetime = datetime.strptime(
            f"{start_date} {start_time}", "%Y-%m-%d %H:%M"
        )

        start_city = request.form.get("start_city")
        end_city = request.form.get("end_city")
        vehicle_id = request.form.get("vehicle_id")
        price = request.form.get("price")

        try:
            create_params = CreateTripData(
                start_city=start_city,
                end_city=end_city,
                start_datetime=start_datetime,
                vehicle_id=vehicle_id,
                price=price,
            )

            with current_app.db_manager.connection() as conn:
                new_trip = trips_crud.create_trip(
                    conn,
                    driver_id=driver_id,
                    vehicle_id=create_params.vehicle_id,
                    start_city=create_params.start_city,
                    end_city=create_params.end_city,
                    start_time=create_params.start_datetime,
                    price=create_params.price,
                )
                if not new_trip:
                    raise Exception("Trip creation failed")

                response = make_response(
                    render_template(
                        "partials/server_msg.html",
                        messages=["Trajet créé avec succès."],
                        msg_case="success",
                    ),
                    200,
                )
                return response
        except ValidationError as ve:
            logger.error("Validation error during trip creation: %s", ve.errors())
            errors = render_pydantic_errors(ve)
            print(errors)
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=errors, msg_case="error"
                ),
                400,
            )
            return response

        except Exception as e:
            logger.error("Error parsing trip data: %s", e)
            messages = ["Une erreur s'est produite, veuillez réessayer plus tard."]
            response = make_response(
                render_template(
                    "partials/server_msg.html",
                    messages=messages,
                    msg_case="error",
                ),
                500,
            )
            return response


@trips_bp.route("/query_trips")
def query_trips():
    params = request.args

    with current_app.db_manager.connection() as conn:
        try:
            search_data = TripSearchData(**params)
            energy_type = search_data.energy_type
            print(search_data)

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

            return render_template("trips/trip_results.html", trips=results)

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
def view_trip(trip_id):
    trip_id = request.view_args.get("trip_id")

    with current_app.db_manager.connection() as conn:
        result = trips_crud.get_trip_summary_asst(conn, trip_id)
        return render_template("trips/trip_detail.html", trip=result)


@trips_bp.route("/join_trip/<trip_id>", methods=["GET", "POST"])
@htmx_login_required
def join_trip(trip_id):
    if request.method == "GET":
        user_id = current_user.user_id

        with current_app.db_manager.connection() as conn:
            allow_join = tx_crud.allow_tx(conn, user_id, trip_id)
            allow_ok = allow_join.get("allow_ok")
            trip_price = allow_join.get("trip_price")
            user_balance = allow_join.get("user_balance")

            if not allow_ok:
                response = make_response(
                    render_template(
                        "partials/server_msg.html",
                        messages=[
                            "Vous n'avez pas assez de fonds pour rejoindre ce trajet."
                        ],
                        msg_case="error",
                    ),
                    400,
                )
                return response

        return render_template(
            "trips/join_trip.html",
            trip_id=trip_id,
            trip_price=trip_price,
            user_balance=user_balance,
        )

    trip_id = request.view_args.get("trip_id")
    user_id = current_user.user_id

    with current_app.db_manager.connection() as conn:
        driver_id = trips_crud.get_trip_driver_id(conn, trip_id)
        if not driver_id:
            raise Exception("Driver ID not found for trip")

        allow_join = tx_crud.allow_tx(conn, user_id, trip_id)
        allow_ok = allow_join.get("allow_ok")
        trip_price = allow_join.get("trip_price")

        if not allow_ok:
            response = make_response(
                render_template(
                    "partials/server_msg.html",
                    messages=[
                        "Vous n'avez pas assez de fonds pour rejoindre ce trajet."
                    ],
                    msg_case="error",
                ),
                400,
            )
            return response

        try:
            psg_added = trips_crud.add_user_to_trip(conn, trip_id, user_id)
            if not psg_added:
                raise Exception("Failed to add passenger to trip")

            tx_created = tx_crud.create_tx(
                conn, user_id, driver_id, trip_price, trip_id
            )
            if not tx_created:
                raise Exception("Transaction creation failed")

            messages = ["Vous avez rejoint le trajet avec succès."]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="success"
                ),
                200,
            )
            return response

        except Exception as e:
            logger.error("Error joining trip: %s", e)
            messages = ["Une erreur s'est produite, reessayez plus tard."]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                500,
            )
            return response


@trips_bp.route("/passenger-trips/<status>")
@htmx_login_required
@require_ownership("for_user")
def passenger_trips_by_status(status):
    status = request.view_args.get("status")
    user_id = current_user.user_id

    try:
        status_id = static_name_resolver("trip_status", status)
    except Exception:
        return "Invalid status", 400

    with current_app.db_manager.connection() as conn:
        trips = trips_crud.get_passenger_trips(conn, user_id, status_id)

    return render_template("trips/passenger_trip_item.html", trips=trips or [])


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

        trips = trips_crud.get_driver_trips(conn, driver_id, status_id)

    return render_template("trips/driver_trip_item.html", trips=trips or [])
