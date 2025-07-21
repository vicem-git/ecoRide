from flask import Blueprint, render_template, request, current_app
import datetime
from flask_login import login_required, current_user
from app.utils import static_id_resolver
from app.db_store import user_crud, driver_crud

pages_bp = Blueprint("pages", __name__, template_folder="../templates")

current_time = datetime.datetime.fromtimestamp(1347517370).strftime("%c")


@pages_bp.route("/")
def index():
    return render_template(
        "pages/index.html",
        current_time=current_time,
        page_wrap="home",
    )


@pages_bp.route("/registration")
def registration():
    return render_template(
        "pages/registration.html", page_wrap="register", case="register"
    )


@pages_bp.route("/onboard")
@login_required
def onboard():
    return render_template(
        "pages/registration.html", page_wrap="register", case="onboard"
    )


@pages_bp.route("/login")
def login():
    return render_template("pages/login.html", page_wrap="login")


@pages_bp.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    current_access = str(current_user.account_access_id)
    current_access = static_id_resolver("account_access", current_access)

    owner = current_user.id == user_id

    # get user roles
    with current_app.db_manager.connection() as conn:
        user_roles = user_crud.get_user_roles(conn, user_id)

        roles = []
        for role in user_roles:
            role_id = str(role["role_id"])
            role_name = static_id_resolver("roles", role_id)
            roles.append(role_name)

        if "driver" in roles:
            driver_data = driver_crud.get_driver_data(conn, user_id)
            driver_preferences = driver_crud.get_driver_preferences(conn, user_id)
            driver_vehicles = driver_crud.get_driver_vehicles(conn, user_id)

    return render_template(
        "pages/profile.html",
        current_time=current_time,
        page_wrap="profile",
        owner=owner,
        case=current_access,
    )


@pages_bp.route("/contact")
def contact():
    return render_template("pages/contact.html", page_wrap="contact")
