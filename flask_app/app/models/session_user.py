from flask_login import UserMixin


class BaseSessionUser(UserMixin):
    def __init__(self, account_id, email, status, access_type):
        self.id = str(account_id)  # required by UserMixin
        self.email = email
        self.status = str(status)
        self.access_type = str(access_type)

    @property
    def is_active(self):
        from flask import current_app

        active_status_id = current_app.static_ids["account_status"]["active"]
        return self.status == active_status_id

    def get_id(self):
        # KEEP CLASS REF TO KNOW WHICH TYPE TO LOAD
        return f"{self.__class__.__name__}:{self.id}"


class SessionUser(BaseSessionUser):
    def __init__(self, account_id, email, status, access_type, user_id, username):
        super().__init__(account_id, email, status, access_type)
        self.user_id = str(user_id)
        self.username = username


class SessionAdmin(BaseSessionUser):
    def __init__(self, account_id, email, status, access_type):
        super().__init__(account_id, email, status, access_type)
