from flask import (
    current_app,
    Blueprint,
    request,
    render_template,
    url_for,
    make_response,
)
import logging
from app.db_store import user_crud
from flask_login import current_user
from app.utils import (
    static_id_resolver,
    transactional,
    htmx_login_required,
    require_ownership,
)

users_bp = Blueprint("users", __name__, url_prefix="/users")

# MODULE LOGGER
logger = logging.getLogger(__name__)


@users_bp.route("/edit_roles", methods=["GET", "POST"])
@transactional()
@htmx_login_required
@require_ownership("for_user")
def edit_roles(conn):
    if request.method == "GET":
        all_roles = user_crud.get_roles_list(conn)
        current_roles = user_crud.get_user_roles(conn, current_user.user_id)

        return render_template(
            "users/edit_roles_form.html",
            all_roles=all_roles,
            current_roles=current_roles,
        )

    elif request.method == "POST":
        new_roles = request.form.getlist("roles")

        new_roles_ids = [
            role_id
            for role_id in new_roles
            if static_id_resolver("roles", role_id) is not None
        ]

        worked = user_crud.set_user_roles(conn, current_user.user_id, new_roles_ids)

        response = make_response("", 204)
        response.headers["HX-Redirect"] = url_for(
            "pages.profile", user_id=current_user.user_id
        )
        return response


@users_bp.route("/get_account_credits")
@transactional()
@htmx_login_required
@require_ownership("for_user")
def get_account_credits(conn):
    credits = user_crud.get_user_credits(conn, current_user.user_id)
    return render_template("users/credits_fragment.html", credits=credits)
