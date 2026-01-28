from app.utils import htmx_login_required
from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    make_response,
)
import logging
import json
from app.db_store import user_crud, driver_crud, trips_crud, tx_crud
from datetime import datetime
from flask_login import login_required, current_user
from app.utils import (
    static_name_resolver,
    transactional,
    require_ownership,
    render_pydantic_errors,
    send_email,
)
from app.models import TripSearchData, CreateTripData, ReviewData
from pydantic import ValidationError

trips_bp = Blueprint("trips", __name__, url_prefix="/trips")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@trips_bp.route("/create_trip", methods=["GET", "POST"])
@trips_bp.route("/create_trip/<driver_id>", methods=["GET", "POST"])
@transactional()
@htmx_login_required
def create_trip(conn, driver_id=None):
    user_id = current_user.user_id

    if request.method == "GET":
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

            if not driver_vehicles:
                messages = [
                    "Veuillez ajouter un véhicule pour pouvoir créer des voyages"
                ]
                response = make_response(
                    render_template(
                        "partials/server_msg.html", messages=messages, msg_case="info"
                    )
                )

            driver_info = {
                "data": driver_data,
                "preferences": driver_preferences,
                "vehicles": driver_vehicles,
            }

            if not driver_info:
                raise Exception("Driver info not found")

            return render_template("trips/create_trip.html", driver_info=driver_info)

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

            # GENERATE SUMMARY
            summary = trips_crud.generate_trip_summary(conn, new_trip)

            if not summary:
                raise Exception("Trip summary generation failed")

            logger.debug(f"trip created successfully : id {new_trip}, summary - {summary}")

            response = make_response("", 200)
            response.headers["HX-Trigger"] = json.dumps({
                "serverMsg": {
                    "type": "driver-trips-updated",
                    "message": "Trajet créé avec succès."
                }
            })
            return response

        except ValidationError as ve:
            logger.error("Validation error during trip creation: %s", ve.errors())
            errors = render_pydantic_errors(ve)
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


@trips_bp.route("/cancel_trip/<trip_id>", methods=["POST"])
@transactional()
@htmx_login_required
@require_ownership("for_trip")
def cancel_trip(conn, trip_id):
    try:
        # find participants and refund the txs created for this trip
        trip_passengers_userdata = trips_crud.get_trip_passengers_userdata(
            conn, trip_id
        )
        if not trip_passengers_userdata:
            logger.info("No passengers found for this trip") 

        trip_txs = tx_crud.get_trip_txs(conn, trip_id)
        if not trip_txs:
            logger.info("No transactions found for this trip")

        logger.info(trip_passengers_userdata)
        for passenger in trip_passengers_userdata:
            # revert txs
            # FOR VEM DROP :
            # REPLACE "id" WITH "user_id" 
            #  if volume rebuilt, init_db needs clean re-run
            passenger_id = passenger.get("id") 
            logger.info(f"passenger id : {passenger_id}")
            reverted = tx_crud.revert_tx(conn, passenger_id, trip_id)
            if not reverted:
                raise Exception("[DRIVER TRIP CANCEL] Error reverting tx for trip cancellation")

        canceled = trips_crud.cancel_trip(conn, trip_id)
        if not canceled:
            raise Exception("Trip cancellation failed")
        
        response = make_response("", 200)
        response.headers["HX-Trigger"] = json.dumps({
            "serverMsg": {
                "type": "driver-trips-updated",
                "message": "Vous avez annulé le trajet avec succès. Un email de confirmation a été envoyé aux passagers."
            }
        })
        
        app = current_app._get_current_object()

        @response.call_on_close
        def trip_cancellation_email():
            with app.app_context():
                logger.info("sending cancellation emails")
                mail_errors = []
                for passenger in trip_passengers_userdata:
                    try:
                        username = passenger.get("username")
                        email = passenger.get("email")
                        email_subject = "Annulation de votre trajet"
                        message_body = render_template(
                            "emails/trip_cancelled.txt",
                            username=username
                        )
                        mail_ok = send_email(
                            username=username, address=email, subject=email_subject, text=message_body
                        )
                        if not mail_ok:
                            mail_errors.append(
                                f"Failed to send email to {username} ({email}), error: {mail_ok}"
                            )
                            logger.warning(f"ERROR SENDING CANCELATION EMAIL {mail_errors}")
                    except Exception as e:
                        logger.warning(f"email for {passenger["email"]} failed: {e}")
        return response

    except Exception as e:
        conn.rollback()
        logger.error("Error canceling trip: %s", e)
        messages = ["Une erreur s'est, veuillez réessayer plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", messages=messages, msg_case="error"
            ),
            500,
        )
        return response


@trips_bp.route("/start_trip/<trip_id>", methods=["POST"])
@transactional()
@htmx_login_required
@require_ownership("for_trip")
def start_trip(conn, trip_id):
    try:
        started_status = current_app.static_ids["trip_status"]["in_progress"]
        started = trips_crud.update_trip_status(conn, trip_id, started_status)
        if not started:
            raise Exception("Trip startup failed")

        response = make_response("", 200)
        response.headers["HX-Trigger"] = json.dumps({
            "serverMsg": {
                "type": "driver-trips-updated",
                "message": "Trajet démarré avec succès."
            }
        })

        return response
    except Exception as e:
        logger.error("Error starting trip: %s", e)
        messages = ["Une erreur s'est produite, reessayez plus tard."]
        response = make_response(
            render_template(
                "trips/server_msg.html", messages=messages, msg_case="error"
            ),
            500,
        )
        return response

@trips_bp.route("/complete_trip/<trip_id>", methods=["POST"])
@transactional()
@htmx_login_required
@require_ownership("for_trip")
def complete_trip(conn, trip_id):
    try:
        passengers = trips_crud.get_trip_passengers_userdata(conn, trip_id)
        
        completed_status = current_app.static_ids["trip_status"]["completed"]
        completed = trips_crud.update_trip_status(conn, trip_id, completed_status)
        if not completed:
            raise Exception("Trip completion failed")

        response = make_response("", 200)
        response.headers["HX-Trigger"] = json.dumps({
            "serverMsg": {
                "type": "driver-trips-updated",
                "message": "Trajet terminé avec succès."
            }
        })
        app = current_app._get_current_object()

        @response.call_on_close
        def trip_completion_email():
            with app.app_context():
                for passenger in passengers:
                    try:
                        username = passenger["username"]
                        address = passenger["email"]
                        message_body = render_template(
                            "emails/trip_completed.txt",
                            username=username,
                        )
                        result = send_email(username, address, "Trip completed!", message_body)
                        logger.debug(f"sending notification to {address}: {result}")
                    except Exception as e:
                        logger.warning(f"email for {passenger["email"]} failed: {e}")
        return response
    except Exception as e:
        logger.error("Error completing trip: %s", e)
        messages = ["Une erreur s'est produite, veuillez réessayer plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", messages=messages, msg_case="error"
            ),
            500,
        )
        return response

@trips_bp.route("/query_trips")
@transactional()
def query_trips(conn):
    params = request.args

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
@transactional()
@htmx_login_required
def view_trip(conn, trip_id):
    trip_id = request.view_args.get("trip_id")

    result = trips_crud.get_trip_summary_asst(conn, trip_id)
    return render_template("trips/trip_detail.html", trip=result)


@trips_bp.route("/join_trip/<trip_id>", methods=["GET", "POST"])
@transactional()
@htmx_login_required
def join_trip(conn, trip_id):
    if request.method == "GET":
        user_id = current_user.user_id

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

    driver_id = trips_crud.get_trip_driver_id(conn, trip_id)
    driver_user = driver_crud.get_driver_user(conn, driver_id)
    if not driver_user:
        raise Exception("Driver_user not found for trip")

    allow_join = tx_crud.allow_tx(conn, user_id, trip_id)
    allow_ok = allow_join.get("allow_ok")
    trip_price = allow_join.get("trip_price")

    if not allow_ok:
        response = make_response(
            render_template(
                "partials/server_msg.html",
                messages=["Vous n'avez pas assez de fonds pour rejoindre ce trajet."],
                msg_case="error",
            ),
            400,
        )
        return response

    try:
        psg_added = trips_crud.add_user_to_trip(conn, trip_id, user_id)
        if not psg_added:
            response = make_response(
                render_template(
                    "partials/server_msg.html",
                    messages=["Vous avez déjà rejoint ce trajet."],
                    msg_case="info",
                ),
                400,
            )

        tx_created = tx_crud.create_tx(conn, user_id, driver_user, trip_price, trip_id)
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


@trips_bp.route("/leave_trip/<trip_id>", methods=["POST"])
@transactional()
@htmx_login_required
@require_ownership("for_participant")
def leave_trip(conn, trip_id):
    try:
        left_trip = trips_crud.remove_user_from_trip(
            conn, trip_id, current_user.user_id
        )
        if not left_trip:
            raise Exception("Failed to leave trip")

        # RESTORE CREDITS !
        reverted = tx_crud.revert_tx(conn, user_id=current_user.user_id, trip_id=trip_id)
        if not reverted:
            raise Exception(f"failed to revert user's transaction: user - {current_user.user_id}, trip - {trip_id}") 

        response = make_response("",200,)
        response.headers["HX-Trigger"] = json.dumps({
            "serverMsg": {
                "type": "user-trips-updated",
                "message": "Vous avez quitté le voyage."
            }
        })
        return response

    except Exception as e:
        logger.error("Error leaving trip: %s", e)
        messages = ["Une erreur s'est produite, reessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", messages=messages, msg_case="error"
            ),
            500,
        )
        return response


@trips_bp.route("/review_trip/<trip_id>", methods=["GET", "POST"])
@transactional()
@htmx_login_required
@require_ownership("for_participant")
def review_trip(conn, trip_id):
    if request.method == "GET":
        driver_id = trips_crud.get_trip_driver_id(conn, trip_id)
        if not driver_id:
            raise Exception(f"REVIEW ERROR : trip data missing, driver_id : {driver_id}")
        
        response = make_response(
            render_template(
                "trips/review_trip.html",
                trip_id=trip_id,
                driver_id=driver_id
            )
        )
        return response
 
    if request.method == "POST":
        try:
            reviewed_trip = request.form.get("trip_id")
            reviewed_driver = request.form.get("driver_id")
            logger.debug(request.form)
            if not reviewed_trip or not reviewed_driver:
                    raise Exception("REVIEW ERROR : driver_id/ trip_id missing.")
            
            review_data = request.form.to_dict()
            data = ReviewData(**review_data)

            passenger_id = current_user.user_id
            trip_evaluation = data.trip_evaluation
            driver_rating = data.driver_rating
            review_comment = data.review_comment

            review_id = current_app.mongo_store.add_trip_review(
                    trip_id=reviewed_trip,
                    driver_id=reviewed_driver,
                    passenger_id=passenger_id,
                    trip_evaluation=trip_evaluation,
                    driver_rating=driver_rating,
                    review_comment=review_comment
            )
            if not review_id:
                raise Exception("REVIEW ERROR")
            response = make_response("", 200)
            response.headers["HX-Trigger"] = json.dumps({
                "serverMsg": {
                    "type": "user-trips-updated",
                    "message": "Merci de valider votre voyage."
                }
            })
            return response

        except ValueError as ve:
            logger.error("Validation error during review creation: %s", ve)
            messages = ["Une erreur s'est produite, veuillez réessayer plus tard."]
            return make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                400,
            )

        except Exception as e:
            logger.error("Error during review creation: %s", e)
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

@trips_bp.route("/passenger-trips")
@transactional()
@htmx_login_required
@require_ownership("for_user")
def passenger_trips(conn):
    try:
        user_id = current_user.user_id

        trips = trips_crud.get_passenger_trips(conn, user_id)

        completed = [t for t in trips if t["status"] == "completed"]
        upcoming = [t for t in trips if t["status"] == "upcoming"]
        
        to_review = []

        if len(completed) > 0: 
            for trip in completed:
                trip_id = trip.get("trip_id")
                revd = current_app.mongo_store.has_reviewed_trip(
                    passenger_id=user_id,
                    trip_id=trip_id
                )
                logger.debug(f"reviewed EXISTS : {revd}")
                if not revd:
                    to_review.append(trip)
                

        return render_template(
            "trips/passenger_trip_items.html",
            completed=completed or [],
            to_review=to_review,
            upcoming=upcoming or []
        )

    except Exception as e:
        logger.error("Error retrieving passenger trips: %s", e)
        response = make_response(
            render_template(
                "partials/server_msg.html",
                messages=["Une erreur s'est produite, reessayez plus tard."],
                msg_case="error",
            ),
            500,
        )
        return response
    

@trips_bp.route("/driver-trips")
@transactional()
@htmx_login_required
@require_ownership("for_user")
def driver_trips(conn):
    try:
        user_id = current_user.user_id

        driver_data = driver_crud.get_driver_data(conn, user_id)
        if not driver_data:
            return "Driver data not found", 404

        driver_id = driver_data.get("id")
        trips = trips_crud.get_driver_trips(conn, driver_id)

        completed = [t for t in trips if t["status"] == "completed"]
        upcoming = [t for t in trips if t["status"] == "upcoming"]
        active = [t for t in trips if t["status"] == "in_progress"]

        return render_template(
            "trips/driver_trip_items.html",
            completed=completed or [],
            upcoming=upcoming or [],
            active=active or []
        )

    except Exception as e:
        logger.error("Error retrieving driver trips: %s", e)
        messages = ["Une erreur s'est produite, reessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", messages=messages, msg_case="error"
            ),
            500,
        )
        return response
