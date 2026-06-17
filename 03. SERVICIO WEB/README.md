# Servicio Web - Chat en vivo Webex

Panel web que muestra en tiempo casi real los mensajes de una sala Webex.

## Requisitos

- Token y `ROOM_ID` configurados en `../02. SCRIPTS PYTHON/config_local.py`
- Python 3 con `flask` y `requests`

## Instalación

```bash
cd "03. SERVICIO WEB"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```bash
source .venv/bin/activate
python app.py
```

Abrir en el navegador: `http://localhost:5000`

Si ves error 401, renueva el token en [developer.webex.com](https://developer.webex.com) y actualiza `config_local.py`.

## Uso con compañeros

1. Cada compañero debe tener cuenta Webex gratuita.
2. Invítalo desde la web con su email de Webex.
3. El compañero abre la app Webex y entra a la sala.
4. Cuando escriba en la app, el mensaje aparecerá en esta página en unos segundos.

## Endpoints

- `GET /api/room` - información de la sala
- `GET /api/messages` - listar mensajes
- `POST /api/messages` - enviar mensaje como admin
- `GET /api/members` - listar participantes
- `POST /api/members` - invitar por email
