from flask import current_app, session, Blueprint, request, jsonify


@app.route("/set-session")
def set_session():
    session["user_id"] = request.args.get("user_id", type=int)
    return jsonify({"message": "Session set", "user_id": session["user_id"]})
