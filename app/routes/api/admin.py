from flask import Blueprint, render_template, request, make_response
from app.db_store import admin_crud, user_crud
import logging
from app.utils import (
    internal_access,
    transactional,
    htmx_login_required,
    render_pydantic_errors,
)
from app.models import CreateModeratorData
from pydantic import ValidationError
from datetime import datetime, timedelta

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
            raise ValueError("No moderators found")

        response = make_response(
            render_template("admin/moderators_view.html", moderators=moderators), 200
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


@admin_bp.route("/create_moderator", methods=["POST"])
@internal_access
@transactional()
@htmx_login_required
def create_moderator(conn):
    moderator_data = request.form.to_dict()

    try:
        val_data = CreateModeratorData(**moderator_data)

        new_mod = admin_crud.create_moderator(
            conn, val_data.name, val_data.email, val_data.password
        )
        if not new_mod:
            raise ValueError("Failed to create moderator")

        response = make_response(render_template("admin/moderators_view.html"), 200)
        response.headers["HX-Message"] = "Modérateur créé avec succès."
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
        suspended = admin_crud.suspend_account_by_id(conn, account_id)
        if not suspended:
            raise ValueError("Failed to suspend account")
        response = make_response(render_template("admin/suspend_success.html"), 200)
        response.headers["HX-Message"] = "Compte suspendu avec succès."
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
        return {"error": str(e)}, 500
