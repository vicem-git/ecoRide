from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    make_response,
    jsonify,
    url_for,
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.db_store import crud_utilities, user_crud
from app.models import RegistrationData, OnboardingData, LoginData, SessionUser
from pydantic import ValidationError
from app.utils import bcrypt
from flask_login import login_user

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health")
def health_check():
    conn = None
    try:
        with current_app.db_manager.get_conn() as conn:
            result = crud_utilities.test_connection(conn)
            if result:
                return {"status": "healthy"}, 200

    except Exception as e:
        error_message = f"Database connection failed: {str(e)}"
        return {"status": error_message}, 500
    finally:
        if conn is not None:
            current_app.pool.release_conn(conn)


@api_bp.route("/register", methods=["POST"])
def register_user():
    data = request.form.to_dict()

    # validation here
    reg_data = RegistrationData(**data)

    conn = None
    try:
        with current_app.pool.connection() as conn:
            existing_account = user_crud.get_user_by_email(conn, reg_data.email)

            if existing_account:
                error_message = "A user with this email already exists."

                response = make_response(
                    render_template(
                        "partials/redirect_to_login.html", errors=error_message
                    )
                )
                response.headers["HX-Redirect"] = "{{ url_for('html.login' }}"

                return response, 409

            hashed_pw = bcrypt.generate_password_hash(reg_data.password)
            account_id = user_crud.create_account(conn, reg_data.email, hashed_pw)

            # AUTHENTICATE THE USER
            account = SessionUser.authenticate(conn, reg_data.email, reg_data.password)

            # load user to login manager
            if account:
                login_user(account)

            response = make_response(
                render_template("partials/onboard_form.html", account_id=account_id)
            )
            response.headers["HX-Redirect"] = "{{ url_for('html.onboard') }}"
            return response, 201

    except ValidationError as ve:
        errors = ve.errors()
        response = make_response(
            render_template("partials/error_fragment.html", errors=errors)
        )
        return response, 400

    except Exception as e:
        print("Error during registration:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500
    finally:
        if conn is not None:
            current_app.pool.release_conn(conn)


@api_bp.route("/onboard", methods=["POST"])
def onboard_user():
    data = request.form.to_dict()
    # validation here
    onboard_data = OnboardingData(**data)

    conn = None
    try:
        with current_app.pool.get_conn() as conn:
            # check if the user is already onboarded
            existing_user = user_crud.get_user_by_account_id(
                conn, onboard_data.account_id
            )

            if existing_user:
                # return fragment that redirects to corresponding user dashboard
                response = make_response(
                    render_template(
                        "partials/already_onboarded_fragment.html",
                        user_id=existing_user["id"],
                    )
                )
                response.headers["HX-Redirect"] = (
                    "{{ url_for('dashboard', user_id=existing_user['id']) }}"
                )

                return response

            # if not onboarded, create a user with the account ID
            user_id = user_crud.create_user(
                conn, onboard_data.account_id, onboard_data.username
            )

            response = make_response(
                render_template("partials/onboarding_successful.html", user_id=user_id)
            )
            response.headers["HX-Redirect"] = "{{ url_for('html.dashboard') }}"
            return response, 201

    except ValidationError as ve:
        return render_template("partials/error_fragment.html", errors=ve.errors()), 400
    except Exception as e:
        print("Error during registration:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500
    finally:
        if conn is not None:
            current_app.pool.release_conn(conn)


@api_bp.route("/login", methods=["POST"])
def login_user():
    data = request.form.to_dict()

    try:
        login_data = LoginData(**data)
    except ValidationError as e:
        # handle errors as before
        errors = e.errors()
        html = render_template("partials/error_fragment.html", errors=errors)
        resp = make_response(html, 400)
        return resp

    conn = None
    try:
        with current_app.pool.get_conn() as conn:
            login_response = user_crud.request_login(conn, login_data.email)

            if login_response is None:
                # if no account found, return error
                html = render_template(
                    "partials/error_fragment.html",
                    errors=["No account found with this email."],
                )
                resp = make_response(html, 404)
                return resp, 404

            if login_response["account_status_id"] == "suspended":
                # if account found, but not suspended, return error
                return render_template(
                    "partials/error_fragment.html",
                    errors=["This account has been suspended."],
                ), 403

            # if account found, and account_status_id != "suspended", try to retrieve the password hash
            hashed_pw = user_crud.retrieve_password(
                conn, account_id=login_response["id"]
            )
            login_ok = bcrypt.check_password_hash(hashed_pw, login_data.password)

            if not login_ok:
                # if password does not match, return error
                return render_template(
                    "partials/error_fragment.html",
                    errors=["Incorrect password."],
                ), 401

            args = {"account_access_id": login_response["account_access_id"]}
            user_access = current_app.load_static_ids["account_access"]["user"]

            if login_response["account_access_id"] == user_access:
                user_id = user_crud.get_user_by_account_id(conn, login_response["id"])
                if user_id:
                    args["user_id"] = user_id

            redirect_url = url_for("dashboard", **args)
            response = make_response("", 204)
            response.headers["HX-Redirect"] = redirect_url
            return response
    except Exception as e:
        print("Error during user login:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500
    finally:
        if conn is not None:
            current_app.pool.release_conn(conn)
