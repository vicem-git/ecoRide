from app.utils.static_resolvers import static_id_resolver
from flask import Blueprint, render_template, request, make_response, url_for
from app.db_store import admin_crud, user_crud
import logging
from app.utils import (
    internal_access,
    transactional,
    htmx_login_required,
    render_pydantic_errors,
    bcrypt,
)
from app.models import CreateModeratorData
from pydantic import ValidationError
from datetime import datetime, timedelta
import json

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

logger = logging.getLogger(__name__)

# PERIODS FOR GRAPHS
period_start = datetime.now() - timedelta(days=30)
period_end = datetime.now()


@admin_bp.route("/get_balance")
@internal_access
@transactional()
@htmx_login_required
def get_balance(conn):
    try:
        balance = admin_crud.get_platform_balance(conn)
        if not balance:
            raise ValueError("No balance data found")

        balance = balance[0]

        response = make_response(
            render_template("admin/balance.html", balance=balance), 200
        )

        return response

    except Exception as e:
        logger.error(f"Error fetching trips data: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500


@admin_bp.route("/get_trips_timeline")
@internal_access
@transactional()
@htmx_login_required
def get_trips_timeline(conn):
    try:
        trips_data = admin_crud.get_trips_per_day(conn, period_start, period_end)
        if not trips_data:
            raise ValueError("No trips data found for the specified period")

        labels = [row["trip_date"][5:].replace("-", "_") for row in trips_data]
        values = [row["total_trips"] for row in trips_data]

        response = make_response(
            render_template(
                "admin/trips_timeline.html",
                chart_data=True,
                labels=labels,
                values=values,
            ),
            200,
        )
        return response

    except Exception as e:
        logger.error(f"Error fetching trips data: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500


@admin_bp.route("/get_income_timeline")
@internal_access
@transactional()
@htmx_login_required
def get_income_timeline(conn):
    try:
        income_data = admin_crud.get_income_per_day(
            conn, period_start=period_start, period_end=period_end
        )
        if not income_data:
            raise ValueError("No income data found for the specified period")

        labels = [row["income_date"][5:].replace("-", "_") for row in income_data]
        values = [row["total_earned"] for row in income_data]

        response = make_response(
            render_template(
                "admin/income_timeline.html",
                chart_data=True,
                labels=labels,
                values=values,
            ),
            200,
        )
        return response

    except Exception as e:
        logger.error(f"Error fetching trips data: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500


@admin_bp.route("/get_moderators")
@internal_access
@transactional()
@htmx_login_required
def get_moderators(conn):
    try:
        moderators = admin_crud.get_moderators(conn)

        if not moderators:
            moderators = []

        moderators = [
            {
                "id": mod.get("id"),
                "email": mod.get("email"),
                "status": static_id_resolver("account_status", mod.get("status")),
            }
            for mod in moderators
        ]

        response = make_response(
            render_template("admin/moderators_view.html", moderators=moderators), 200
        )

        return response

    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500


@admin_bp.route("/create_moderator", methods=["GET", "POST"])
@internal_access
@transactional()
@htmx_login_required
def create_moderator(conn):
    if request.method == "GET":
        response = make_response(render_template("admin/create_moderator.html"), 200)
        return response

    moderator_data = request.form.to_dict()

    try:
        val_data = CreateModeratorData(**moderator_data)

        hashed_pw = bcrypt.generate_password_hash(val_data.password, 14).decode("utf-8")

        new_mod = admin_crud.create_moderator(conn, val_data.email, hashed_pw)
        if not new_mod:
            raise ValueError("Failed to create moderator")

        response = make_response("", 204)
        response.headers["HX-Location"] = json.dumps(
            {
                "path": url_for(
                    "admin.get_moderators", success="Moderateur creé avec succès."
                ),
                "target": "#moderators-view",
                "swap": "innerHTML",
            }
        )
        return response

    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        messages = render_pydantic_errors(e)
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            400,
        )

    except Exception as e:
        logger.error(f"Error fetching trips data: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return {"error": str(e)}, 500


@admin_bp.route("/get_user/<email>", methods=["GET"])
@internal_access
@transactional()
@htmx_login_required
def get_user(conn, email):
    try:
        user_data = user_crud.get_user_public_data(conn, email)
        if not user_data:
            raise ValueError("No user data found for the specified email")

        response = make_response(
            render_template("admin/user_view.html", user_data=user_data), 200
        )
        return response

    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return response


@admin_bp.route("/suspend_account/<account_id>", methods=["POST"])
@internal_access
@transactional()
@htmx_login_required
def suspend_account(conn, account_id):
    try:
        target = request.headers.get("HX-Target")
        header = "refresh-mods" if target == "moderators-view" else "refresh-users"

        suspended = admin_crud.suspend_account_by_id(conn, account_id)
        if not suspended:
            raise ValueError("Failed to suspend account")

        response = make_response("", 204)
        response.headers["HX-Trigger"] = header

        return response

    except Exception as e:
        logger.error(f"Error suspending account: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return response


@admin_bp.route("/activate_account/<account_id>", methods=["POST"])
@internal_access
@transactional()
@htmx_login_required
def activate_account(conn, account_id):
    try:
        target = request.headers.get("HX-Target")
        header = "refresh-mods" if target == "moderators-view" else "refresh-users"

        activated = admin_crud.activate_account_by_id(conn, account_id)
        if not activated:
            raise ValueError("Failed to activate account")

        response = make_response("", 204)
        response.headers["HX-Trigger"] = header
        return response

    except Exception as e:
        logger.error(f"Error activating account: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        response = make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
        return response


@admin_bp.route("/query_users", methods=["POST"])
@internal_access
@transactional()
@htmx_login_required
def query_users(conn):
    try:
        search_term = request.form.get("search-term", "").strip()
        if not search_term.strip():
            users = []
        users = admin_crud.query_users(conn, search_term)

        return make_response(
            render_template("admin/users_search_results.html", users=users), 200
        )
    except Exception as e:
        logger.error(f"Error querying users: {str(e)}")
        messages = ["Une erreur s'est produite. Réessayez plus tard."]
        return make_response(
            render_template(
                "partials/server_msg.html", message=messages, msg_case="error"
            ),
            500,
        )
