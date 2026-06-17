from flask import Flask, jsonify, request, send_from_directory

from webex_client import (
    WebexError,
    add_member,
    check_config,
    get_default_room_id,
    get_default_room_title,
    get_room,
    list_members,
    list_messages,
    send_message,
)

app = Flask(__name__, static_folder="static")


@app.errorhandler(WebexError)
def handle_webex_error(error):
    return jsonify({"error": str(error), "details": error.details}), error.status_code or 500


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/room")
def api_room():
    room = get_room()
    return jsonify({
        "id": room.get("id"),
        "title": room.get("title"),
        "created": room.get("created"),
        "lastActivity": room.get("lastActivity"),
    })


@app.route("/api/messages", methods=["GET"])
def api_list_messages():
    messages = list_messages()
    return jsonify({"items": messages})


@app.route("/api/messages", methods=["POST"])
def api_send_message():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "El campo text es obligatorio."}), 400

    message = send_message(text)
    return jsonify(message), 201


@app.route("/api/members", methods=["GET"])
def api_list_members():
    members = list_members()
    return jsonify({"items": members})


@app.route("/api/members", methods=["POST"])
def api_add_member():
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
    })


if __name__ == "__main__":
    check_config()
    try:
        get_room()
        print("Webex conectado. Sala:", get_default_room_title())
    except WebexError as error:
        print(f"ADVERTENCIA: no se pudo conectar a Webex ({error}).")
        print("Renueva ACCESS_TOKEN en 02. SCRIPTS PYTHON/config_local.py")
    app.run(host="0.0.0.0", port=5000, debug=True)
