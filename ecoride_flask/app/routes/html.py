from flask import Blueprint, render_template
import time

html_bp = Blueprint("html", __name__, template_folder="../templates")


@html_bp.route("/")
def index():
    return render_template(
        "pages/index.html", current_time=time.time(), page_wrap="home"
    )


@html_bp.route("/registration")
def registration():
    return render_template("pages/registration.html", page_wrap="register")


@html_bp.route("/login")
def login():
    return render_template("pages/login.html", page_wrap="login")
