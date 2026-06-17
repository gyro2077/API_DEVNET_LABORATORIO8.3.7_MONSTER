import os

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN", "TU_TOKEN_AQUI")
PERSON_EMAIL = os.environ.get("WEBEX_PERSON_EMAIL", "tu_email@ejemplo.com")
ROOM_ID = os.environ.get("WEBEX_ROOM_ID", "")
ROOM_TITLE = "DevNet Associate Training!"
MESSAGE = "Hello **DevNet Associates**!!"

try:
    from config_local import *  # noqa: F403
except ImportError:
    pass
