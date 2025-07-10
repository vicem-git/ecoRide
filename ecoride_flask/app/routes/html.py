from flask import Blueprint, render_template
import time

html_bp = Blueprint("html", __name__, template_folder="../templates")


@html_bp.route("/")
def index():
    return render_template("index.html", current_time=time.time())
