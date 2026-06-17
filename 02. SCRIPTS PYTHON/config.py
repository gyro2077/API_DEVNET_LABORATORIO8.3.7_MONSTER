import os

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN", "TU_TOKEN_AQUI")
PERSON_EMAIL = os.environ.get("WEBEX_PERSON_EMAIL", "tu_email@ejemplo.com")
ROOM_ID = os.environ.get("WEBEX_ROOM_ID", "")
ROOM_TITLE = "DevNet Associate Training!"
MESSAGE = "Hello **DevNet Associates**!!"

OAUTH_CLIENT_ID = os.environ.get("WEBEX_OAUTH_CLIENT_ID", "TU_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.environ.get("WEBEX_OAUTH_CLIENT_SECRET", "TU_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.environ.get(
    "WEBEX_OAUTH_REDIRECT_URI",
    "http://localhost:5000/oauth/callback",
)
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "cambia-esta-clave-secreta")

OAUTH_SCOPES = " ".join([
    "spark:messages_read",
    "spark:messages_write",
    "spark:people_read",
    "spark:rooms_read",
    "spark:memberships_read",
])

try:
    from config_local import *  # noqa: F403
except ImportError:
    pass
