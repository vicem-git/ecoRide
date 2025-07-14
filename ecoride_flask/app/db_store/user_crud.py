# user CRUD operations for user management
from flask import current_app
from psycopg.rows import dict_row


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


def get_user_by_account_id(conn, account_id):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE account_id = %s", (account_id,))
        return cur.fetchone()  # returns None if not found


def create_user(conn, account_id, username):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (username) WHERE account_id = %s
            VALUES (%s)
            RETURNING id
            """,
            (account_id, username),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id


def request_login(conn, email):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT account_id, account_access_id, account_status_id FROM accounts WHERE email = %s 
            """,
            (email),
        )
        account_found = cur.fetchone()
    return account_found  # returns None if not found


def retrieve_password(conn, account_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT password_hash FROM accounts WHERE id = %s
            """,
            (account_id,),
        )
        return cur.fetchone()


def set_username(conn, user_id, username):
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET username = %s WHERE id = %s", (username, user_id))
        conn.commit()


def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM accounts WHERE email = %s", (email,))
        return cur.fetchone()  # returns None if not found
