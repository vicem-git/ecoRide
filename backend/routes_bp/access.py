from flask import current_app, Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from ..db_store.crud.access_crud import get_user_by_email, create_account
from ..db_store.crud.user_crud import create_user


register_bp = Blueprint("register", __name__)


@register_bp.route("/api/register", methods=["POST"])
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
            if get_user_by_email(conn, email):
                return jsonify({"error": "User already exists"}), 409

            hashed_pw = generate_password_hash(password)
            account_id = create_account(conn, email, hashed_pw)

            # create the user with the account ID
            user_id = create_user(conn, account_id, username)
            return jsonify({"message": "User created", "user_id": user_id}), 201
    except Exception as e:
        print("Error during registration:", str(e))
        return jsonify({"error": str(e)}), 500
