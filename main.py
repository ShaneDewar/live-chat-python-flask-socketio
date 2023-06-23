# Web browser client - socket based chat project using
# Flask, JS, Python and flask-io -- real time chat project

from flask import Flask, render_template, request, url_for, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room
import random
from datetime import datetime
from string import ascii_uppercase

app = Flask(__name__)

# Insert a proper secret key instead of the default here
app.config["SECRET_KEY"] = "random_devkey1"
socketio = SocketIO(app)

# data stored in ram, could add DB for persistance
rooms = {}


def generate_unique_code(code_len):
    while True:
        code = ""
        for _ in range(code_len):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code


# Landing Page for Chat rooms
@app.route("/", methods=["POST", "GET"])
def landing_page():
    # Clear existing session to allow user to access different rooms
    session.clear()

    # Grab new room requests
    if request.method == "POST":
        name = request.form.get("handle")
        code = request.form.get("code")
        join = request.form.get("join_room", False)
        create = request.form.get("create_room", False)

        if not name:
            return render_template("landing.html",
                                   error="You must select a handle",
                                   code=code, name=name)

        if join is not False and not code:
            return render_template("landing.html",
                                   error="Please provide a room code.",
                                   code=code, name=name)

        room_id = code

        if create is not False:
            # Room id value must be unique
            room_id = generate_unique_code(8)
            rooms[room_id] = {"messages": [], "users": 0}

        elif code not in rooms:
            return render_template("landing.html",
                                   error="Room with this ID does not exist.",
                                   code=code, name=name)

        session["room"] = room_id
        session["name"] = name
        return redirect(url_for("chatroom"))

    return render_template("landing.html")


@app.route("/chatroom")
def chatroom():
    room = session.get("room")
    # Prevent direct room joining; must have appropriate session object.
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("landing.html"))

    return render_template("chatroom.html",
                           room=room, messages=rooms[room]["messages"])


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["msg"],
        # Here is where date sent should be stored for messages for each room
        "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    }

    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def connect(auth):
    # extract room info from socketio for our app
    room = session.get("room")
    name = session.get("name")

    # kick user back to landing if there is no session data
    if not room or not name:
        return

    # boot user to landing if session data is invalid
    if room not in rooms:
        leave_room(room)
        return

    # properly intialize the socket only once the user joins a room
    join_room(room)
    # send JSON announcing new user in room
    send({"name": name, "message": "has entered the room",
          "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S')}, to=room)
    rooms[room]["users"] += 1
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["users"] -= 1
        # cleanup unused rooms
        if rooms[room]["users"] <= 0:
            del rooms[room]

    send({"name": name, "message": " has left the room",
          "date": datetime.today().strftime('%Y-%m-%d %H:%M:%S')}, to=room)
    print(f"{name} has left the room {room}")


if __name__ == "__main__":
    socketio.run(app, debug=True)  # Auto refresh server
