# Web browser client - socket based chat project using
# Flask, JS, Python and flask-io

from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send, join_room, leave_room

import random
from string import ascii_uppercase

app = Flask(__name__)

# Insert a proper secret key instead of the default here
app.config["SECRET_KEY"] = "random_devkey1"
socketio = SocketIO(app)

# Landing Page for Chat rooms
@app.route("/", methods=["POST", "GET"])
def landing_page():
    return render_template("landing.html")


if __name__ == "__main__":
    socketio.run(app, debug=True)  # Auto refresh server
