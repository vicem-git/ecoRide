from flask import (
    current_app,
    Blueprint,
    request,
    redirect,
    render_template,
    make_response,
    url_for,
)
import json
import logging
from app.db_store import crud_utilities, user_crud, driver_crud, auth_crud
from app.models import RegistrationData, LoginData, SessionUser, SessionAdmin
from pydantic import ValidationError
from flask_login import login_user, logout_user, login_required
from app.utils import bcrypt, transactional, static_id_resolver, static_name_resolver

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@auth_bp.route("/health")
@transactional(commit=False)
def health_check(conn):
    try:
        result = crud_utilities.test_connection(conn)
        if result:
            return {"status": "healthy"}, 200

    # IMPLEMENT LOGGING AND LOG ERORRS THERE
    except Exception as e:
        error_message = f"Database connection failed: {str(e)}"
        return {"status": error_message}, 500


@auth_bp.route("/register", methods=["POST"])
@transactional()
def register_user(conn):
    data = request.form.to_dict()
    data["roles"] = request.form.getlist("roles")

    try:
        reg_data = RegistrationData(**data)

        role_ids = []
        for role in reg_data.roles:
            static_role = static_name_resolver("roles", role)
            role_ids.append(str(static_role) if static_role else None)

        existing_account = user_crud.get_user_by_email(conn, reg_data.email)

        if existing_account:
            message = "un compte existe déjà avec cet email. veuillez vous connecter."
            response = make_response("", 200)
            response.headers["HX-Trigger"] = json.dumps({
                "serverMsg": {
                    "type": "message",
                    "message": message
                }
            })
            return response
        if user_crud.check_username(conn, reg_data.username):
            message = "Nom d'utilisateur déjà pris."
            response = make_response("", 200)
            response.headers["HX-Trigger"] = json.dumps({
                "serverMsg": {
                    "type": "message",
                    "message": message
                }
            })
            return response

        hashed_pw = bcrypt.generate_password_hash(reg_data.password, 14).decode("utf-8")
        account_id = user_crud.create_account(conn, reg_data.email, hashed_pw)
        user_id = user_crud.create_user(conn, account_id, reg_data.username)

        user_crud.set_user_roles(conn, user_id, role_ids)
        driver_id = current_app.static_ids["roles"]["driver"]

        if str(driver_id) in role_ids:
            driver_id = driver_crud.create_driver(conn, user_id)
            if driver_id is None:
                raise Exception("error while creating driver profile")

        session_user = SessionUser(
            account_id=account_id,
            email=reg_data.email,
            status=static_id_resolver("account_status", "active"),
            access_type=static_id_resolver("account_access_type", "user"),
            user_id=user_id,
            username=reg_data.username,
        )
        login_user(session_user)

        response = make_response(
            render_template(
                "partials/server_msg.html",
                messages=["Utilisateur inscrit, redirection..."],
                msg_case="success",
            )
        )
        response.headers["HX-Trigger"] = json.dumps(
            {"redirectTo": url_for("pages.login")}
        )

        return response

    except ValidationError as ve:
        logger.error("Validation error during registration: %s", ve.errors())
        errors = ve.errors()
        messages = [
            error["msg"].removeprefix("Value error, ").strip() for error in errors
        ]
        return make_response(
            render_template(
                "partials/server_msg.html", messages=messages, msg_case="error"
            ),
            400,
        )

    except Exception as e:
        logger.error("Registration failed: %s", str(e))
        message = ["Une erreur s'est produite. Réessayez plus tard."]
        return make_response(
            render_template(
                "partials/server_msg.html", message=message, mgs_case="error"
            ),
            500,
        )

@auth_bp.route("/login", methods=["POST"])
@transactional()
def login(conn):
    data = request.form.to_dict()

    try:
        # validate the login data
        login_data = LoginData(**data)

        login_response = user_crud.request_login(conn, login_data.email)

        if login_response is None:
            # if no account found, return error
            messages = ["No account found with this email."]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                400,
            )
            return response

        if login_response["status"] == "suspended":
            # if account found, but not suspended, return error
            messages = ["This account has been suspended."]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                400,
            )
            return response

        # if account found, and account_status != "suspended", try to retrieve the password hash
        hashed_pw = user_crud.retrieve_password(conn, account_id=login_response["id"])

        password_to_check = str(login_data.password)

        login_ok = bcrypt.check_password_hash(hashed_pw, password_to_check)

        if not login_ok:
            # if password does not match, return error
            messages = ["Incorrect password."]
            response = make_response(
                render_template(
                    "partials/server_msg.html", messages=messages, msg_case="error"
                ),
                400,
            )
            return response

        access_level = auth_crud.email_access_level(conn, login_data.email)

        access_name = static_id_resolver("account_access_type", access_level)

        if access_name in ("admin", "moderator"):
            session_obj = SessionAdmin(
                account_id=login_response["id"],
                email=login_data.email,
                status=login_response["status"],
                access_type=login_response["access_type"],
            )
        else:
            account_id = login_response.get("id")
            user_data = user_crud.get_user_by_account_id(conn, account_id)
            if not user_data:
                raise Exception("Could not retrieve user data after login.")

            session_obj = SessionUser(
                account_id=login_response["id"],
                email=login_data.email,
                status=login_response["status"],
                access_type=login_response["access_type"],
                user_id=user_data["id"],
                username=user_data["username"],
            )

        if not session_obj:
            raise Exception("Could not retrieve user object after login.")

        login_user(session_obj)

        if access_name == "admin":
            url = url_for("pages.admin_dashboard", identifier=session_obj.id)
        elif access_name == "moderator":
            url = url_for("pages.mod_dashboard", identifier=session_obj.id)
        elif access_name == "user" and session_obj.user_id is not None:
            url = url_for("pages.profile", identifier=session_obj.user_id)
        elif access_name == "user" and session_obj.user_id is None:
            url = url_for("pages.onboard")
        else:
            logging.warning(
                f"Unexpected login redirect state: access={access_name}, user_id={session_obj.user_id}"
            )
            url = url_for("pages.index")

        response = make_response(
            render_template(
                "partials/server_msg.html",
                messages=["Connexion réussie, redirection..."],
                msg_case="success",
            )
        )

        response.headers["HX-Trigger"] = json.dumps({"redirectTo": url})

        return response

    except ValidationError as ve:
        logger.error("Validation error during login: %s", ve.errors())
        errors = ve.errors()
        messages = [
            error["msg"].removeprefix("Value error, ").strip() for error in errors
        ]
        return make_response(
            render_template(
                "partials/server_msg.html", messages=messages, msg_case="error"
            ),
            400,
        )

    except Exception as e:
        logger.error("Login failed: %s", str(e))
        message = ["Une erreur s'est produite. Réessayez plus tard."]
        return make_response(
            render_template(
                "partials/server_msg.html", message=message, msg_case="error"
            ),
            500,
        )


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("pages.index"))
