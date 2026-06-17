# Servicio Web - Chat en vivo Webex con OAuth

Cada compañero inicia sesión con **su cuenta Webex** y chatea desde el navegador con su propio nombre.

## Configuración (una sola vez)

### 1. Crear Integration en Webex

1. Ve a [developer.webex.com/my-apps](https://developer.webex.com/my-apps)
2. Crea una **Integration**
3. Agrega Redirect URI: `http://localhost:5000/oauth/callback`
4. Copia **Client ID** y **Client Secret**

### 2. Configurar `config_local.py`

En `../02. SCRIPTS PYTHON/config_local.py`:

```python
ACCESS_TOKEN = "tu_token_admin"          # para invitar a la sala
ROOM_ID = "tu_room_id"
OAUTH_CLIENT_ID = "tu_client_id"
OAUTH_CLIENT_SECRET = "tu_client_secret"
OAUTH_REDIRECT_URI = "http://localhost:5000/oauth/callback"
FLASK_SECRET_KEY = "una-clave-secreta-larga"
```

## Ejecutar

```bash
cd "03. SERVICIO WEB"
source .venv/bin/activate
python app.py
```

Abrir: `http://localhost:5000`

## Flujo de uso

1. El compañero abre `http://localhost:5000`
2. Clic en **Iniciar sesión con Webex**
3. Autoriza con su cuenta Webex
4. Entra al chat y escribe; los mensajes salen con **su email**
5. La sala se actualiza en tiempo casi real (polling cada 2 s)

## Notas

- Sí necesitan cuenta Webex gratuita.
- Al iniciar sesión, el sistema intenta agregarlos automáticamente a la sala.
- El `ACCESS_TOKEN` admin solo se usa para invitar miembros, no para enviar mensajes de los usuarios.
