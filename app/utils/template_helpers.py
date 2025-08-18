from flask_login import AnonymousUserMixin


def register_template_helpers(app):
    static_ids = app.static_ids

    @app.template_test("access")
    def has_access(account, *roles):
        return any(
            account.access_type == static_ids["account_access_type"][role]
            for role in roles
        )

    @app.template_test("role")
    def has_role(user, *roles):
        return any(user.role_id == static_ids["roles"][role] for role in roles)

    @app.template_test("anonymous")
    def is_anonymous(user):
        return isinstance(user, AnonymousUserMixin) or not user.is_authenticated
