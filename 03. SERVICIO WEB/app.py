import secrets

from flask import Flask, jsonify, redirect, request, send_from_directory, session

from webex_client import (
    WebexError,
    add_member,
    build_authorize_url,
    check_config,
    ensure_room_membership,
    exchange_code_for_token,
    get_default_room_id,
    get_default_room_title,
    get_me,
    get_room,
    list_members,
    list_messages,
    send_message,
)

app = Flask(__name__, static_folder="static")
app.secret_key = None


def _load_secret_key():
    import sys
    from pathlib import Path

    scripts_dir = Path(__file__).resolve().parent.parent / "02. SCRIPTS PYTHON"
    sys.path.insert(0, str(scripts_dir))
    from config import FLASK_SECRET_KEY  # noqa: E402

    app.secret_key = FLASK_SECRET_KEY


_load_secret_key()


def get_user_token():
    return session.get("access_token")


def require_login():
    token = get_user_token()
    if not token:
        return None
    return token


@app.errorhandler(WebexError)
def handle_webex_error(error):
    return jsonify({"error": str(error), "details": error.details}), error.status_code or 500


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/auth/me")
def api_auth_me():
    token = require_login()
    if not token:
        return jsonify({"authenticated": False}), 401

    return jsonify({
        "authenticated": True,
        "email": session.get("email"),
        "displayName": session.get("display_name"),
        "personId": session.get("person_id"),
    })


@app.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state
    return redirect(build_authorize_url(state))


@app.route("/oauth/callback")
def oauth_callback():
    error = request.args.get("error")
    if error:
        return redirect(f"/?error={error}")

    state = request.args.get("state")
    if not state or state != session.get("oauth_state"):
        return redirect("/?error=invalid_state")

    code = request.args.get("code")
    if not code:
        return redirect("/?error=missing_code")

    token_data = exchange_code_for_token(code)
    access_token = token_data["access_token"]
    profile = get_me(access_token)

    email = profile.get("emails", [""])[0]
    session["access_token"] = access_token
    session["email"] = email
    session["display_name"] = profile.get("displayName") or email
    session["person_id"] = profile.get("id")
    session.pop("oauth_state", None)

    try:
        ensure_room_membership(email)
    except WebexError:
        pass

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/api/room")
def api_room():
    token = require_login()
    if not token:
        return jsonify({"error": "Debes iniciar sesión con Webex."}), 401

    room = get_room(token)
    return jsonify({
        "id": room.get("id"),
        "title": room.get("title"),
        "created": room.get("created"),
        "lastActivity": room.get("lastActivity"),
    })


@app.route("/api/messages", methods=["GET"])
def api_list_messages():
    token = require_login()
    if not token:
        return jsonify({"error": "Debes iniciar sesión con Webex."}), 401

    messages = list_messages(token)
    return jsonify({"items": messages})


@app.route("/api/messages", methods=["POST"])
def api_send_message():
    token = require_login()
    if not token:
        return jsonify({"error": "Debes iniciar sesión con Webex."}), 401

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "El campo text es obligatorio."}), 400

    message = send_message(token, text)
    return jsonify(message), 201


@app.route("/api/members", methods=["GET"])
def api_list_members():
    token = require_login()
    if not token:
        return jsonify({"error": "Debes iniciar sesión con Webex."}), 401

    members = list_members(token)
    return jsonify({"items": members})


@app.route("/api/members", methods=["POST"])
def api_add_member():
    token = require_login()
    if not token:
        return jsonify({"error": "Debes iniciar sesión con Webex."}), 401

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    if not email:
        return jsonify({"error": "El campo email es obligatorio."}), 400

    result = add_member(email)
    status = 200 if result.get("alreadyMember") else 201
    return jsonify(result), status


@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "ok",
        "roomId": get_default_room_id(),
        "roomTitle": get_default_room_title(),
        "auth": "oauth",
    })


if __name__ == "__main__":
    check_config()
    print("Sala:", get_default_room_title())
    print("OAuth redirect:", "http://localhost:5000/oauth/callback")
    print("Cada usuario debe iniciar sesión con su cuenta Webex.")
    app.run(host="0.0.0.0", port=5000, debug=True)
