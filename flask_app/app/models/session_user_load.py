from app.models import SessionUser, SessionAdmin
from app.utils import login_manager
import logging

logger = logging.getLogger(__name__)


def session_user_loader(app):
    @login_manager.user_loader
    def user_loader(account_key):
        try:
            cls_name, account_id = account_key.split(":", 1)

            with app.db_manager.connection() as _conn:
                conn = _conn
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT a.id, a.email, a.status, a.access_type, u.id, u.username 
                        FROM accounts a 
                        LEFT JOIN users u ON u.account_id = a.id
                        WHERE a.id = %s
                        """,
                        (account_id,),
                    )
                    row = cursor.fetchone()

                if not row:
                    conn.rollback()
                    return None

                (
                    account_id,
                    email,
                    status,
                    access_type,
                    user_id,
                    username,
                ) = row

                conn.rollback()

                if cls_name == "SessionUser":
                    return SessionUser(
                        account_id=account_id,
                        email=email,
                        status=status,
                        access_type=access_type,
                        user_id=user_id,
                        username=username,
                    )

                elif cls_name == "SessionAdmin":
                    return SessionAdmin(
                        account_id=account_id,
                        email=email,
                        status=status,
                        access_type=access_type,
                    )
                else:
                    logger.warning(f"Unknown session user class: {cls_name}")

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(
                f"[bold red]LOGIN MANAGER : user_loader failed :[/bold red] {e}"
            )
