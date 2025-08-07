from functools import wraps
from flask import (
    abort,
    redirect,
    url_for,
    request,
    make_response,
    render_template,
    current_app,
)
from flask_login import current_user
import logging

# MODULE LOGGER
logger = logging.getLogger(__name__)


def transactional(commit=True):
    def transactional_decorator(f):
        @wraps(f)
        def transactional_wrapper(*args, **kwargs):
            with current_app.db_manager.connection() as conn:
                try:
                    result = f(conn, *args, **kwargs)
                    if commit:
                        logger.info(f"commiting for {f}")
                        conn.commit()
                    return result
                except Exception as te:
                    conn.rollback()
                    raise te

        return transactional_wrapper

    return transactional_decorator


def htmx_login_required(f):
    @wraps(f)
    def htmx_login_wrapper(conn, *args, **kwargs):
        try:
            if not current_user.is_authenticated:
                messages = ["Connectez-vous pour accéder à ce contenu."]
                if request.headers.get("HX-Request"):
                    response = make_response(
                        render_template(
                            "partials/server_msg.html",
                            messages=messages,
                            msg_case="info",
                        ),
                        401,
                    )
                    return response
                else:
                    return redirect(url_for("auth.login"))
        except Exception as e:
            logger.debug(f"ERROR during @htmx_login_required : {e} ")
        return f(conn, *args, **kwargs)

    return htmx_login_wrapper


def require_ownership(param="for_user"):
    def ownership_decorator(f):
        @wraps(f)
        def ownership_wrapper(conn, *args, **kwargs):
            try:
                if param == "for_user":
                    logger.debug(f"Checking ownership for : {param}")
                    user_id = request.args.get(param)
                    if not user_id or str(user_id) != str(current_user.user_id):
                        abort(403)

                elif param == "for_trip":
                    trip_id = request.args.get(param)
                    logger.debug(f"Checking ownership for: {trip_id}")
                    if not trip_id:
                        abort(403, "missing trip_id")

                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT 1 FROM trip_owner WHERE trip_id = %s AND user_id = %s",
                            (trip_id, current_user.user_id),
                        )
                        owner = cur.fetchone()

                    if not owner:
                        abort(
                            403,
                            "la suppression d'un voyage qui ne vous appartient pas échoue",
                        )
            except Exception as e:
                logger.error(f"Error checking trip ownership: {e}")
                abort(500, "Erreur interne du serveur")

            return f(conn, *args, **kwargs)

        return ownership_wrapper

    return ownership_decorator
