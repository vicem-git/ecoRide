from flask import current_app, Blueprint, request, jsonify
import time
from werkzeug.security import generate_password_hash
from app.db_store import crud_utilities, user_crud


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/time")
def get_current_time():
    return {"time": time.time()}


@api_bp.route("/health")
def health_check():
    with current_app.db_manager.get_conn() as conn:
        result = crud_utilities.test_connection(conn)
    return {"status": "healthy" if result else "unhealthy"}


@api_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data["email"]
    username = data["username"]
    password = data["password"]

    if not all([email, username, password]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        with current_app.pool.connection() as conn:
            print("pool connection established")
            if user_crud.get_user_by_email(conn, email):
                return jsonify({"error": "User already exists"}), 409

            hashed_pw = generate_password_hash(password)
            account_id = user_crud.create_account(conn, email, hashed_pw)

            # create the user with the account ID
            user_id = user_crud.create_user(conn, account_id, username)
            return jsonify({"message": "User created", "user_id": user_id}), 201
    except Exception as e:
        print("Error during registration:", str(e))
        return jsonify({"error": str(e)}), 500
