# user CRUD operations for user management
from flask import current_app


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
