from flask import Blueprint, render_template

html_bp = Blueprint("html", __name__, template_folder="../templates")


@html_bp.route("/")
def index():
    return render_template("index.html")
