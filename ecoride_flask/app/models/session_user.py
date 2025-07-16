from app.utils import bcrypt
from flask_login import UserMixin


class SessionUser(UserMixin):
    def __init__(
        self,
        account_id,
        email,
        account_status_id,
        account_access_id,
        user_id=None,
        username=None,
    ):
        self.id = str(account_id)  # Flask-Login uses .id
        self.email = email
        self.account_status_id = account_status_id
        self.account_access_id = account_access_id
        self.user_id = user_id
        self.username = username

    @property
    def is_active(self):
        from flask import current_app

        active_status_id = current_app.load_static_ids["account_status"]["active"]
        return self.account_status_id == active_status_id

    @staticmethod
    def authenticate(conn, email, password):
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    a.id,
                    a.email,
                    a.account_status_id,
                    a.account_access_id,
                    a.password_hash,
                    u.id,
                    u.username
                FROM accounts a
                LEFT JOIN users u ON u.account_id = a.id
                WHERE a.email = %s
                """,
                (email,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            (
                account_id,
                email,
                account_status_id,
                account_access_id,
                pw_hash,
                user_id,
                username,
            ) = row

            if not bcrypt.check_password_hash(pw_hash, password):
                return None

            return SessionUser(
                account_id=account_id,
                email=email,
                account_status_id=account_status_id,
                account_access_id=account_access_id,
                user_id=user_id,
                username=username,
            )

