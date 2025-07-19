# helper for checking account acces against static ids
from flask import current_app


def access_resolver(access_id):
    access_ids = current_app.static_ids["account_access"]

    for kind, ids in access_ids.items():
        if str(access_id) in ids:
            return str(kind)
