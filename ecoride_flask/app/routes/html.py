from flask import Blueprint, render_template, request, current_app
import datetime
from flask_login import login_required, current_user
from app.utils import static_id_resolver

html_bp = Blueprint("html", __name__, template_folder="../templates")

current_time = datetime.datetime.fromtimestamp(1347517370).strftime("%c")


@html_bp.route("/")
def index():
    return render_template(
        "pages/index.html",
        current_time=current_time,
        page_wrap="home",
    )


@html_bp.route("/registration")
def registration():
    return render_template(
        "pages/registration.html", page_wrap="register", case="register"
    )


@html_bp.route("/onboard")
@login_required
def onboard():
    return render_template(
        "pages/registration.html", page_wrap="register", case="onboard"
    )


@html_bp.route("/login")
def login():
    return render_template("pages/login.html", page_wrap="login")


@html_bp.route("/dashboard")
@login_required
def dashboard():
    current_access = str(current_user.account_access_id)

    current_access = static_id_resolver("account_access", current_access)

    return render_template(
        "pages/dashboard.html",
        current_time=current_time,
        page_wrap="dashboard",
        case=current_access,
    )


@html_bp.route("/contact")
def contact():
    return render_template("pages/contact.html", page_wrap="contact")
