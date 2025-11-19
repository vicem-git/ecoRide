from flask import session

def valid_csrf(token: str | None) -> bool:
    if not token:
        return False
    return token == session.get("csrf_token")

