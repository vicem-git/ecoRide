import logging
from psycopg.rows import dict_row
from app.models import SessionUser
import uuid
import random

logger = logging.getLogger(__name__)

photo_urls = [
    "graphics/profiles/profile1.jpg",
    "graphics/profiles/profile2.jpg",
    "graphics/profiles/profile3.jpg",
    "graphics/profiles/profile4.jpg",
    "graphics/profiles/profile5.jpg",
    "graphics/profiles/profile6.jpg",
    "graphics/profiles/profile7.jpg",
    "graphics/profiles/profile8.jpg",
    "graphics/profiles/profile9.jpg",
    "graphics/profiles/profile10.jpg",
    "graphics/profiles/profile11.jpg",
    "graphics/profiles/profile12.jpg",
    "graphics/profiles/profile13.jpg",
    "graphics/profiles/profile14.jpg",
    "graphics/profiles/profile15.jpg",
    "graphics/profiles/profile16.jpg",
    "graphics/profiles/profile17.jpg",
    "graphics/profiles/profile18.jpg",
    "graphics/profiles/profile19.jpg",
    "graphics/profiles/profile20.jpg",
    "graphics/profiles/profile21.jpg",
    "graphics/profiles/profile22.jpg",
    "graphics/profiles/profile23.jpg",
    "graphics/profiles/profile24.jpg",
    "graphics/profiles/profile25.jpg",
    "graphics/profiles/profile26.jpg",
    "graphics/profiles/profile27.jpg",
    "graphics/profiles/profile28.jpg",
    "graphics/profiles/profile29.jpg",
]


def random_photo():
    photo = random.choice(photo_urls)
    return photo


def create_account(conn, email, hashed_password):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO accounts (email, password_hash, access_type, status) 
            VALUES (%s, %s, (
                SELECT id FROM account_access_type WHERE name = 'user'
                ), (
                SELECT id FROM account_status WHERE name = 'active'
                )
            ) 
            RETURNING id""",
            (email, hashed_password),
        )
        account_id = cur.fetchone()[0]
        return account_id


def get_user_by_account_id(conn, account_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, username FROM users WHERE account_id = %s", (account_id,)
        )
        user_data = cur.fetchone()
        return user_data if user_data else None


def get_user_public_data(conn, identifier):
    with conn.cursor(row_factory=dict_row) as cur:
        try:
            uuid_obj = uuid.UUID(identifier, version=4)
            cur.execute(
                "SELECT id, username, photo_url FROM users WHERE id = %s",
                (str(uuid_obj),),
            )
        except ValueError:
            cur.execute(
                "SELECT id, username, photo_url FROM users WHERE username = %s",
                (identifier,),
            )
        except Exception as e:
            return {"error": str(e)}

        user_data = cur.fetchone()
        return user_data if user_data else None


def create_user(conn, account_id, username):
    photo = random_photo()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, account_id, photo_url) VALUES (%s, %s, %s) RETURNING id",
            (username, account_id, photo),
        )
        user_id = cur.fetchone()[0]
        return user_id


def request_login(conn, email):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, access_type, status FROM accounts WHERE email = %s ",
            (email,),
        )
        account_found = cur.fetchone()
    return account_found if account_found else None


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
    return True


def get_user_by_email(conn, email):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM accounts WHERE email = %s", (email,))
        found = cur.fetchone()
        return found[0] if found else None


def get_user_email(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT a.email 
            FROM accounts a 
            JOIN users u 
            ON u.account_id = a.id 
            WHERE u.id = %s
            """,
            (user_id,),
        )
        found = cur.fetchone()
        return found[0] if found else None


def get_user_object(conn, account_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT a.id, a.email, a.status, a.access_type, u.id, u.username FROM accounts a LEFT JOIN users u ON u.account_id = a.id WHERE a.id = %s",
            (account_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        (
            account_id,
            email,
            status,
            access_type,
            user_id,
            username,
        ) = row

        return SessionUser(
            account_id=account_id,
            email=email,
            status=status,
            access_type=access_type,
            user_id=user_id,
            username=username,
        )


def get_roles_list(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM roles")
        role_list = cur.fetchall()
        return [{"id": row[0], "name": row[1]} for row in role_list]


def get_user_roles(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT r.name FROM roles r JOIN user_roles ur ON ur.role_id = r.id WHERE ur.user_id = %s",
            (user_id,),
        )
        roles = [row[0] for row in cur.fetchall()]
        return roles


def set_user_roles(conn, user_id, roles):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
        for role in roles:
            cur.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                (user_id, role),
            )
        return True


def get_user_credits(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT credits FROM users WHERE id = %s",
            (user_id,),
        )
        credits = cur.fetchone()
        return credits[0] if credits else 0
