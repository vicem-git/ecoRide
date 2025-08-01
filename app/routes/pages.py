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
from app.faker.villes import villes

# MODULE LOGGER
logger = logging.getLogger(__name__)


pages_bp = Blueprint("pages", __name__, template_folder="../templates")


@pages_bp.route("/")
def index():
    return render_template(
        "pages/index.html",
        page_wrap="home",
        cities=list(villes.keys()),
    )


@pages_bp.route("/registration")
def registration():
    return render_template("pages/registration.html", page_wrap="register")


@pages_bp.route("/login")
def login():
    return render_template("pages/login.html", page_wrap="login")


@pages_bp.route("/profile/<user_id>")
@login_required
def profile(user_id):
    owner = str(current_user.user_id) == str(user_id)

    with current_app.db_manager.connection() as conn:
        profile_user = user_crud.get_user_public_data(conn, user_id)
        if not profile_user:
            return "User not found", 404

        profile_user_id = profile_user["id"]

        profile_user_roles = user_crud.get_user_roles(conn, profile_user_id)

        return render_template(
            "pages/profile.html",
            page_wrap="profile",
            profile_user=profile_user,
            owner=owner,
            roles=profile_user_roles,
        )


@pages_bp.route("/search_trips")
def search_trips():
    start_city = request.args.get("start_city")
    end_city = request.args.get("end_city")
    start_date = request.args.get("start_date") or datetime.now().isoformat()
    passenger_nr = int(request.args.get("passenger_nr") or 1)

    # NEED TO ESCAPE SMTH ?
    with current_app.db_manager.connection() as conn:
        try:
            trips = trips_crud.search_summaries_asst(
                conn,
                start_city=start_city,
                end_city=end_city,
                passenger_nr=passenger_nr,
                start_date=start_date,
            )
        except ValueError as e:
            flash("Veuillez sélectionner un point de départ et d’arrivée.")
            return redirect(url_for("pages.index"))

        except Exception as e:
            logger.error(f"Error searching trips: {e}")
            messages = ["Une erreur s'est produite. Réessayez plus tard."]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                500,
            )
            return response

    return render_template(
        "pages/search_trips.html",
        page_wrap="search_trips",
        trips=trips,
        cities=list(villes.keys()),
    )


@pages_bp.route("/contact")
def contact():
    return render_template("pages/contact.html", page_wrap="contact")


@pages_bp.route("/mentions_legales")
def mentions_legales():
    return render_template("pages/mentions_legales.html", page_wrap="mentions_legales")
