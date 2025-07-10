# user CRUD operations for user management
from flask import current_app


def create_account(conn, email, hashed_password):
    access_id = current_app.load_static_ids["account_access"]["user"]
    status_id = current_app.load_static_ids["account_status"]["active"]
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO accounts (email, password_hash, account_access_id, account_status_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (email, hashed_password, access_id, status_id),
        )
        account_id = cur.fetchone()[0]
        conn.commit()
        return account_id


def create_user(conn, account_id, username):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (account_id, username)
            VALUES (%s, %s)
            RETURNING id
            """,
            (account_id, username),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def set_username(conn, user_id, username):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        conn.commit()


def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM accounts WHERE email = %s", (email,))
        return cur.fetchone()  # returns None if not found
