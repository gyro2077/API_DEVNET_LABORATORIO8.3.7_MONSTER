import sys
from pathlib import Path
from urllib.parse import urlencode

import requests

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "02. SCRIPTS PYTHON"
sys.path.insert(0, str(SCRIPTS_DIR))

from config import (  # noqa: E402
    ACCESS_TOKEN,
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_REDIRECT_URI,
    OAUTH_SCOPES,
    ROOM_ID,
    ROOM_TITLE,
)

BASE_URL = "https://webexapis.com/v1"
AUTHORIZE_URL = "https://webexapis.com/v1/authorize"
TOKEN_URL = "https://webexapis.com/v1/access_token"


class WebexError(Exception):
    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


def _headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def _handle_response(response):
    if response.ok:
        return response.json() if response.content else {}

    try:
        details = response.json()
        message = details.get("message", response.text)
    except ValueError:
        details = None
        message = response.text

    raise WebexError(message, status_code=response.status_code, details=details)


def check_config():
    if not ROOM_ID:
        raise WebexError("Configura ROOM_ID en 02. SCRIPTS PYTHON/config_local.py")
    if not OAUTH_CLIENT_ID or OAUTH_CLIENT_ID == "TU_CLIENT_ID":
        raise WebexError("Configura OAUTH_CLIENT_ID en config_local.py")
    if not OAUTH_CLIENT_SECRET or OAUTH_CLIENT_SECRET == "TU_CLIENT_SECRET":
        raise WebexError("Configura OAUTH_CLIENT_SECRET en config_local.py")
    if not ACCESS_TOKEN or ACCESS_TOKEN == "TU_TOKEN_AQUI":
        raise WebexError(
            "Configura ACCESS_TOKEN (admin) para invitar usuarios a la sala"
        )


def build_authorize_url(state):
    params = urlencode({
        "client_id": OAUTH_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": OAUTH_REDIRECT_URI,
        "scope": OAUTH_SCOPES,
        "state": state,
    })
    return f"{AUTHORIZE_URL}?{params}"


def exchange_code_for_token(code):
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": OAUTH_CLIENT_ID,
            "client_secret": OAUTH_CLIENT_SECRET,
            "code": code,
            "redirect_uri": OAUTH_REDIRECT_URI,
        },
        headers={"Accept": "application/json"},
        timeout=30,
    )
    return _handle_response(response)


def get_me(access_token):
    response = requests.get(
        f"{BASE_URL}/people/me",
        headers=_headers(access_token),
        timeout=30,
    )
    return _handle_response(response)


def get_room(access_token, room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.get(
        f"{BASE_URL}/rooms/{room_id}",
        headers=_headers(access_token),
        timeout=30,
    )
    return _handle_response(response)


def list_messages(access_token, room_id=None, max_items=50):
    room_id = room_id or ROOM_ID
    response = requests.get(
        f"{BASE_URL}/messages",
        headers=_headers(access_token),
        params={"roomId": room_id, "max": max_items},
        timeout=30,
    )
    data = _handle_response(response)
    items = data.get("items", [])
    items.sort(key=lambda item: item.get("created", ""))
    return items


def send_message(access_token, text, room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.post(
        f"{BASE_URL}/messages",
        headers=_headers(access_token),
        json={"roomId": room_id, "text": text},
        timeout=30,
    )
    return _handle_response(response)


def list_members(access_token, room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.get(
        f"{BASE_URL}/memberships",
        headers=_headers(access_token),
        params={"roomId": room_id},
        timeout=30,
    )
    data = _handle_response(response)
    return data.get("items", [])


def add_member(email, room_id=None, admin_token=None):
    room_id = room_id or ROOM_ID
    token = admin_token or ACCESS_TOKEN
    response = requests.post(
        f"{BASE_URL}/memberships",
        headers=_headers(token),
        json={"roomId": room_id, "personEmail": email},
        timeout=30,
    )
    if response.status_code == 409:
        return {
            "message": "El usuario ya es participante de la sala.",
            "alreadyMember": True,
        }
    return _handle_response(response)


def ensure_room_membership(email):
    return add_member(email)


def get_default_room_id():
    return ROOM_ID


def get_default_room_title():
    return ROOM_TITLE
