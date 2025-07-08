from flask import request, jsonify
from werkzeug.security import generate_password_hash
from db_store.crud.user_crud import get_user_by_email, create_user
from app import pool


@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    email = data["email"]
    username = data["username"]
    password = data["password"]

    with pool.connection() as conn:
        if get_user_by_email(conn, email):
            return jsonify({"error": "User already exists"}), 409

        hashed_pw = generate_password_hash(password)
        user_id = create_user(conn, email, username, hashed_pw)
        return jsonify({"message": "User created", "user_id": user_id}), 201

