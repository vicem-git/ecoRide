import requests
from config import Config
from urllib.parse import urlparse


api_url: str = Config.MAIL_API_URL
api_key: str = Config.MAIL_API_KEY

parsed_url = urlparse(api_url)
if not (parsed_url.scheme and parsed_url.netloc):
    raise ValueError(f"Invalid MAIL_API_URL: {api_url}")

if not api_key or not isinstance(api_key, str):
    raise ValueError("MAIL_API_KEY must be a non-empty string")


def send_email(username, address, subject, text):
    response = requests.post(
        api_url,
        auth=("api", api_key),
        data={
            "from": "EcoRide <postmaster@vem-drop.xyz>",
            "to": f"{username} <{address}>",
            "subject": f"{subject}",
            "text": f"{text}",
        },
    )

    if response.status_code == 200:
        return {"success": True, "message": response.json().get("message")}
    else:
        return {
            "success": False,
            "error": response.text,
            "status": response.status_code,
        }
