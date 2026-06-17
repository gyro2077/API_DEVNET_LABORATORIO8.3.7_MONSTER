import sys
from pathlib import Path

import requests

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "02. SCRIPTS PYTHON"
sys.path.insert(0, str(SCRIPTS_DIR))

from config import ACCESS_TOKEN, ROOM_ID, ROOM_TITLE  # noqa: E402

BASE_URL = "https://webexapis.com/v1"


class WebexError(Exception):
    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


def _headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
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
    if not ACCESS_TOKEN or ACCESS_TOKEN == "TU_TOKEN_AQUI":
        raise WebexError("Configura ACCESS_TOKEN en 02. SCRIPTS PYTHON/config_local.py")
    if not ROOM_ID:
        raise WebexError("Configura ROOM_ID en 02. SCRIPTS PYTHON/config_local.py")


def get_room(room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.get(f"{BASE_URL}/rooms/{room_id}", headers=_headers())
    return _handle_response(response)


def list_messages(room_id=None, max_items=50):
    room_id = room_id or ROOM_ID
    response = requests.get(
        f"{BASE_URL}/messages",
        headers=_headers(),
        params={"roomId": room_id, "max": max_items},
    )
    data = _handle_response(response)
    items = data.get("items", [])
    items.sort(key=lambda item: item.get("created", ""))
    return items


def send_message(text, room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.post(
        f"{BASE_URL}/messages",
        headers=_headers(),
        json={"roomId": room_id, "text": text},
    )
    return _handle_response(response)


def list_members(room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.get(
        f"{BASE_URL}/memberships",
        headers=_headers(),
        params={"roomId": room_id},
    )
    data = _handle_response(response)
    return data.get("items", [])


def add_member(email, room_id=None):
    room_id = room_id or ROOM_ID
    response = requests.post(
        f"{BASE_URL}/memberships",
        headers=_headers(),
        json={"roomId": room_id, "personEmail": email},
    )
    if response.status_code == 409:
        return {"message": "El usuario ya es participante de la sala.", "alreadyMember": True}
    return _handle_response(response)


def get_default_room_id():
    return ROOM_ID


def get_default_room_title():
    return ROOM_TITLE
