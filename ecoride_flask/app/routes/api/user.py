from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
)
import logging
from app.db_store import user_crud, driver_crud
from flask_login import login_user, logout_user, login_required, current_user

user_bp = Blueprint("user", __name__, url_prefix="/user")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@user_bp.route("/driver_preferences_form")
@login_required
def edit_driver_preferences():
    with current_app.db_manager.connection() as conn:
        prefs = driver_crud.get_driver_preferences(conn, current_user.id)
    return render_template(
        "pages/driver_preferences_form.html",
        prefs=prefs,
    )


@user_bp.route("/update/driver_preferences", methods=["POST"])
def update_driver_preferences():
    preferences = request.form.getlist("preferences")
    with current_app.db_manager.connection() as conn:
        driver_crud.set_driver_preferences(conn, current_user.id, preferences)
    return render_template(
        "pages/driver_preferences_form.html",
        prefs=preferences,
    )
