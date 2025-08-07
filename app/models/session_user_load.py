from app.models import SessionUser
from app.utils import login_manager
import logging

logger = logging.getLogger(__name__)


def session_user_loader(app):
    @login_manager.user_loader
    def user_loader(account_id):
        try:
            with app.db_manager.connection() as _conn:
                conn = _conn
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT a.id, a.email, a.status, a.access_type, u.id, u.username FROM accounts a LEFT JOIN users u ON u.account_id = a.id WHERE a.id = %s",
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

                conn_address = hex(id(conn))
                logger.debug(
                    f"[bold blue] user_loader [/bold blue] triggered, connection: {conn_address}"
                )

                conn.rollback()

                return SessionUser(
                    account_id=account_id,
                    email=email,
                    status=status,
                    access_type=access_type,
                    user_id=user_id,
                    username=username,
                )
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(
                f"[bold red]LOGIN MANAGER : user_loader failed :[/bold red] {e}"
            )
