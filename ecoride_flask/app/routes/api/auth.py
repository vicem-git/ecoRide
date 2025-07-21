from flask import (
    current_app,
    Blueprint,
    request,
    redirect,
    render_template,
    make_response,
    jsonify,
    url_for,
    flash,
)
import logging
from app.db_store import crud_utilities, user_crud, driver_crud
from app.models import RegistrationData, OnboardingData, LoginData, SessionUser
from pydantic import ValidationError
from app.utils import bcrypt
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@auth_bp.route("/health")
def health_check():
    conn = None
    try:
        with current_app.db_manager.connection() as conn:
            result = crud_utilities.test_connection(conn)
            if result:
                return {"status": "healthy"}, 200

    # IMPLEMENT LOGGING AND LOG ERORRS THERE
    except Exception as e:
        error_message = f"Database connection failed: {str(e)}"
        return {"status": error_message}, 500


@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.form.to_dict()

    conn = None
    try:
        # validation here
        reg_data = RegistrationData(**data)

        with current_app.db_manager.connection() as conn:
            existing_account = user_crud.get_user_by_email(conn, reg_data.email)

            if existing_account:
                error_message = "A user with this email already exists. please head over to the login page"
                flash(error_message)
                response = make_response("", 409)
                return response

            hashed_pw = bcrypt.generate_password_hash(reg_data.password, 14).decode(
                "utf-8"
            )
            account_created = user_crud.create_account(conn, reg_data.email, hashed_pw)

            if account_created:
                response = make_response("", 201)
                response.headers["HX-Redirect"] = url_for("pages.login")
                return response

    except ValidationError as ve:
        for err in ve.errors():
            flash(f"{err['loc'][0]}: {err['msg']}")
        return make_response("", 400)

    except Exception as e:
        logger.error("Error during registration:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500


@auth_bp.route("/onboard", methods=["POST"])
def onboard_user():
    data = request.form.to_dict()

    conn = None
    try:
        # validate data
        onboard_data = OnboardingData(**data)

        with current_app.db_manager.connection() as conn:
            # check if the user is already onboarded
            existing_user = user_crud.get_user_by_account_id(
                conn, onboard_data.account_id
            )

            if existing_user:
                # return fragment that redirects to corresponding user profile
                response = make_response("", 204)
                response.headers["HX-Redirect"] = url_for(
                    "pages.profile", user_id=existing_user
                )
                return response

            # check username uniqueness
            username_exists = user_crud.check_username(conn, onboard_data.username)

            if username_exists:
                flash("Username already exists. Please choose a different username.")
                response = make_response("", 409)
                return response

            # if not onboarded, create a user with the account ID
            user_id = user_crud.create_user(
                conn, onboard_data.account_id, onboard_data.username
            )

            if not user_id:
                flash("Failed to create user. Please try again later.")
                response = make_response("", 500)
                return response

            user_crud.set_user_roles(conn, user_id, onboard_data.roles)
            flash("Welcome aboard!")
            response = make_response("", 201)
            response.headers["HX-Redirect"] = url_for("pages.profile", user_id=user_id)
            return response

    except ValidationError as ve:
        for err in ve.errors():
            flash(f"{err['loc'][0]}: {err['msg']}")
        return make_response("", 400)

    except Exception as e:
        logger.error("Error during onboarding:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form.to_dict()

    conn = None
    try:
        # validate the login data
        login_data = LoginData(**data)

        with current_app.db_manager.connection() as conn:
            login_response = user_crud.request_login(conn, login_data.email)

            if login_response is None:
                # if no account found, return error
                flash("No account found with this email.")
                response = make_response("", 404)
                return response

            if login_response["account_status_id"] == "suspended":
                # if account found, but not suspended, return error
                flash("This account has been suspended.")
                response = make_response("", 403)
                return response

            # if account found, and account_status_id != "suspended", try to retrieve the password hash
            hashed_pw = user_crud.retrieve_password(
                conn, account_id=login_response["id"]
            )

            password_to_check = str(login_data.password)

            login_ok = bcrypt.check_password_hash(hashed_pw, password_to_check)

            if not login_ok:
                # if password does not match, return error
                flash("Incorrect password.")
                response = make_response("", 401)
                return response

            session_user = user_crud.get_user_object(conn, login_response["id"])

            login_user(session_user)

            response = make_response("", 204)
            response.headers["HX-Redirect"] = url_for(
                "pages.profile", user_id=session_user.id
            )
            return response

    except ValidationError as ve:
        logger.error("Validation error:", ve.errors())
        for err in ve.errors():
            flash(f"{err['loc'][0]}: {err['msg']}")
        return make_response("", 400)

    except Exception as e:
        logger.error("Error during user login:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("html.index"))
