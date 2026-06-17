import json
import os
import re
import sys

import requests

from config import ACCESS_TOKEN, MESSAGE, PERSON_EMAIL, ROOM_ID, ROOM_TITLE

BASE_URL = "https://webexapis.com/v1"


def headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def check_config():
    if not ACCESS_TOKEN or ACCESS_TOKEN == "TU_TOKEN_AQUI":
        print("ERROR: Configura ACCESS_TOKEN en config_local.py o exporta WEBEX_ACCESS_TOKEN.")
        print("  cp config_local.py.example config_local.py")
        sys.exit(1)


def print_step(name, response):
    print(f"\n=== {name} ===")
    try:
        print(json.dumps(response.json(), indent=4))
    except ValueError:
        print(response.text)
    if not response.ok:
        sys.exit(f"Fallo en {name} (HTTP {response.status_code})")


def update_room_id_in_config(room_id):
    config_path = "config_local.py"
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(
                f'ACCESS_TOKEN = "{ACCESS_TOKEN}"\n'
                f'PERSON_EMAIL = "{PERSON_EMAIL}"\n'
                f'ROOM_ID = "{room_id}"\n'
            )
        print(f"\nCreado {config_path} con ROOM_ID actualizado.")
        return

    with open(config_path, encoding="utf-8") as f:
        content = f.read()

    if re.search(r"^ROOM_ID\s*=", content, re.MULTILINE):
        content = re.sub(
            r'^ROOM_ID\s*=\s*["\'].*?["\']',
            f'ROOM_ID = "{room_id}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        content += f'\nROOM_ID = "{room_id}"\n'

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nROOM_ID actualizado en {config_path}.")


def main():
    check_config()

    auth = requests.get(f"{BASE_URL}/people/me", headers=headers())
    print_step("1. Autenticacion", auth)

    email = PERSON_EMAIL
    if email == "tu_email@ejemplo.com" and auth.ok:
        email = auth.json().get("emails", [email])[0]
        print(f"\nUsando email autenticado: {email}")

    people = requests.get(
        f"{BASE_URL}/people",
        headers=headers(),
        params={"email": email},
    )
    print_step("2. Listar persona", people)

    rooms = requests.get(
        f"{BASE_URL}/rooms",
        headers=headers(),
        params={"max": "100"},
    )
    print_step("3. Listar salas", rooms)

    room_id = ROOM_ID
    if not room_id:
        created = requests.post(
            f"{BASE_URL}/rooms",
            headers=headers(),
            json={"title": ROOM_TITLE},
        )
        print_step("4. Crear sala", created)
        if created.ok:
            room_id = created.json()["id"]
            update_room_id_in_config(room_id)
    else:
        print(f"\n=== 4. Crear sala ===\nOmitido: ROOM_ID ya configurado ({room_id})")

    memberships = requests.get(
        f"{BASE_URL}/memberships",
        headers=headers(),
        params={"roomId": room_id},
    )
    print_step("5. Listar membresias", memberships)

    membership = requests.post(
        f"{BASE_URL}/memberships",
        headers=headers(),
        json={"roomId": room_id, "personEmail": email},
    )
    if membership.status_code == 409:
        print("\n=== 6. Crear membresia ===")
        print("Omitido: el usuario ya es participante de la sala (creador).")
    else:
        print_step("6. Crear membresia", membership)

    message = requests.post(
        f"{BASE_URL}/messages",
        headers=headers(),
        json={"roomId": room_id, "markdown": MESSAGE},
    )
    print_step("7. Enviar mensaje", message)

    print("\nLaboratorio completado correctamente.")


if __name__ == "__main__":
    main()
