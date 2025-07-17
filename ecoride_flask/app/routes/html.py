from flask import Blueprint, render_template, request, current_app
import datetime
from flask_login import login_required, current_user

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
    account_access = current_app.static_ids["account_access"]
    account_access_id = current_user.account_access_id

    print("Current user authenticated?", current_user.is_authenticated)
    print("Current user ID:", current_user.get_id())

    if not account_access_id:
        return "Missing account_access_id", 400

    if account_access_id == account_access["user"]:
        user_id = request.args.get("user_id")
        if user_id is None:
            return "Missing user_id", 400
        user_id = request.args.get("user_id")
        # fetch user info as needed
        return render_template(
            "dashboard.html", access="user", user_id=user_id, current_time=current_time
        )
    elif account_access_id == account_access["admin"]:
        return render_template("dashboard.html", access="admin")

    elif account_access_id == account_access["moderator"]:
        return render_template("dashboard.html", access="mod")

    else:
        return (
            "Unknown access type",
            400,
        )  # handle logic to retrieve user data based on account_access_id and user_id
