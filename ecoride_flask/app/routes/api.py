from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    make_response,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.db_store import crud_utilities, user_crud
from app.utils import RegistrationData, OnboardingData, LoginData
from pydantic import ValidationError

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health")
def health_check():
    with current_app.db_manager.get_conn() as conn:
        result = crud_utilities.test_connection(conn)
    return {"status": "healthy" if result else "unhealthy"}


@api_bp.route("/register", methods=["POST"])
def register_user():
    data = request.form.to_dict()

    # validation here
    reg_data = RegistrationData(**data)

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
                response.headers["HX-Redirect"] = "/login"

                return response, 409

            hashed_pw = generate_password_hash(reg_data.password)
            account_id = user_crud.create_account(conn, reg_data.email, hashed_pw)

            return render_template(
                "partials/onboard_form.html", account_id=account_id
            ), 201
    except ValidationError as ve:
        errors = ve.errors()
        return render_template("partials/error_fragment.html", errors=errors), 400
    except Exception as e:
        print("Error during registration:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500


@api_bp.route("/onboard", methods=["POST"])
def onboard_user():
    data = request.form.to_dict()
    # validation here
    onboard_data = OnboardingData(**data)

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
                response.headers["HX-Redirect"] = f"/dashboard/{existing_user['id']}"

                return response

            # if not onboarded, create a user with the account ID
            user_id = user_crud.create_user(
                conn, onboard_data.account_id, onboard_data.username
            )

            return render_template("pages/user_dashboard", user_id=user_id), 201

    except ValidationError as ve:
        return render_template("partials/error_fragment.html", errors=ve.errors()), 400
    except Exception as e:
        print("Error during registration:", str(e))
        return jsonify(
            {"error": "A server error occurred. Please try again later."}
        ), 500


@api_bp.route("/login", methods=["POST"])
def login_user():
    data = request.form.to_dict()

    login_data = LoginData(**data)

    try:
        with current_app.pool.get_conn() as conn:
            login_response = user_crud.request_login(conn, login_data.email)
            
            # if account found, and account_status_id == "active", try to retrieve the password hash
            hashed_pw = crud_utilities.retrieve_password(conn, account_id=login_response["id"])
            login_ok = check_password_hash(login_response, login_data.password)

            # handle errors or start session with the proper access level
            
        
            




