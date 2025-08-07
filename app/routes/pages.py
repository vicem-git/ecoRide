from app.utils.custom_decorators import transactional
from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    make_response,
    redirect,
    url_for,
    flash,
)
import logging
from datetime import datetime
from flask_login import login_required, current_user
from app.utils import static_id_resolver
from app.db_store import user_crud, trips_crud
from app.models import TripSearchData
from pydantic import ValidationError

# MODULE LOGGER
logger = logging.getLogger(__name__)


pages_bp = Blueprint("pages", __name__, template_folder="../templates")


@pages_bp.route("/")
def index():
    return render_template(
        "pages/index.html",
        page_wrap="home",
    )


@pages_bp.route("/registration")
def registration():
    return render_template("pages/registration.html", page_wrap="register")


@pages_bp.route("/login")
def login():
    return render_template("pages/login.html", page_wrap="login")


@pages_bp.route("/profile/<identifier>")
@login_required
@transactional()
def profile(conn, identifier):
    profile_user = user_crud.get_user_public_data(conn, identifier)

    if not profile_user:
        return "User not found", 404

    if profile_user.get("error"):
        logger.error(profile_user)
        return "User not found", 404

    profile_user_id = profile_user["id"]
    owner = str(current_user.user_id) == str(profile_user_id)
    profile_user_roles = user_crud.get_user_roles(conn, profile_user_id)

    return render_template(
        "pages/profile.html",
        page_wrap="profile",
        profile_user=profile_user,
        owner=owner,
        roles=profile_user_roles,
    )


@pages_bp.route("/admin")
@login_required
@transactional(commit=False)
def admin_dashboard(conn, identifier):
    # rides per day
    # total earned
    # earned by day
    # create_moderator, query_moderators, suspend_moderator_by_id
    # query users, suspend_user_by_id
    admin_template = render_template(
        "pages/admin_dashboard.html", page_wrap="admin", identifier=identifier
    )
    response = make_response(admin_template, 200)
    return response


@pages_bp.route("/moderator")
@login_required
@transactional()
def mod_dashboard(conn, identifier):
    # query all pending ok reviews, approve/ reject
    # query all pending bad reviews w/trip summary, approve/ reject
    mod_dashboard = render_template(
        "pages/mod_dashboard.html", page_wrap="mod", identifier=identifier
    )
    response = make_response(mod_dashboard, 200)
    return response


@pages_bp.route("/search_trips")
@transactional()
def search_trips(conn):
    start_city = request.args.get("start_city")
    end_city = request.args.get("end_city")

    if not start_city or not end_city:
        return render_template("pages/search_trips.html")

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

        return render_template("pages/search_trips.html", trips=results)

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


@pages_bp.route("/contact")
def contact():
    return render_template("pages/contact.html", page_wrap="contact")


@pages_bp.route("/mentions_legales")
def mentions_legales():
    return render_template("pages/mentions_legales.html", page_wrap="mentions_legales")
