from flask_login import UserMixin


class SessionUser(UserMixin):
    def __init__(
        self,
        account_id,
        email,
        status,
        access_type,
        user_id=None,
        username=None,
    ):
        self.id = str(account_id)
        self.email = email
        self.status = str(status)
        self.access_type = str(access_type)
        self.user_id = str(user_id) if user_id is not None else None
        self.username = username

    @property
    def is_active(self):
        from flask import current_app

        active_status_id = current_app.static_ids["account_status"]["active"]
        return self.status == active_status_id

    def get_id(self):
        return self.id
