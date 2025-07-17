# user CRUD operations for user management
from flask import current_app
from psycopg.rows import dict_row
from app.models import SessionUser


def create_account(conn, email, hashed_password):
    access_id = current_app.static_ids["account_access"]["user"]
    status_id = current_app.static_ids["account_status"]["active"]
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO accounts (email, password_hash, account_access_id, account_status_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (email, hashed_password, access_id, status_id),
        )
        account_id = cur.fetchone()[0]
        conn.commit()
        return account_id


def get_user_by_account_id(conn, account_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE account_id = %s", (account_id,))
        user_id = cur.fetchone()[0]
        return user_id  # returns None if not found


def create_user(conn, account_id, username):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, account_id) VALUES (%s, %s) RETURNING id",
            (username, account_id),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def request_login(conn, email):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, account_access_id, account_status_id FROM accounts WHERE email = %s ",
            (email,),
        )
        account_found = cur.fetchone()
    return account_found  # returns None if not found


def retrieve_password(conn, account_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT password_hash FROM accounts WHERE id = %s",
            (account_id,),
        )
        result = cur.fetchone()
        if result:
            return result[0]
        return None


def check_username(conn, username):
    with conn.cursor() as cur:
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            return result[0]
        return None


def set_username(conn, user_id, username):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        conn.commit()


def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM accounts WHERE email = %s", (email,))
        return cur.fetchone()  # returns None if not found


def get_user_object(conn, account_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT a.id, a.email, a.account_status_id, a.account_access_id, u.id, u.username FROM accounts a LEFT JOIN users u ON u.account_id = a.id WHERE a.id = %s",
            (account_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        (
            account_id,
            email,
            account_status_id,
            account_access_id,
            user_id,
            username,
        ) = row

        return SessionUser(
            account_id=account_id,
            email=email,
            account_status_id=account_status_id,
            account_access_id=account_access_id,
            user_id=user_id,
            username=username,
        )
