from flask_login import AnonymousUserMixin
from flask import url_for
import json
import os


def _load_vite_manifest(app):
    manifest_path = os.path.join(app.static_folder, 'dist', '.vite', 'manifest.json')
    try:
        with open(manifest_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def register_template_helpers(app):
    static_ids = app.static_ids
    vite_manifest = _load_vite_manifest(app)

    @app.template_global()
    def vite_asset(entry):
        chunk = vite_manifest.get(entry, {})
        file = chunk.get('file', '')
        return url_for('static', filename=f'dist/{file}') if file else ''

    @app.template_global()
    def vite_css(entry):
        chunk = vite_manifest.get(entry, {})
        css_files = chunk.get('css', [])
        return [url_for('static', filename=f'dist/{f}') for f in css_files]

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
