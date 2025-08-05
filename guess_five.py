from flask import Flask, render_template_string, request, redirect, url_for
from flask_socketio import SocketIO, join_room, emit
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'couplegame'
socketio = SocketIO(app)

games = {}

home_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Guess My 5 Multiplayer</title>
</head>
<body style="font-family: Arial; text-align: center; background-color: #fff0f5;">
    <h1>💖 Guess My 5 - Multiplayer 💖</h1>
    <form action="/create_game" method="POST">
        <button type="submit">Create Game</button>
    </form>
    <br>
    <form action="/join_game" method="POST">
        <input type="text" name="room" placeholder="Enter Room Code" required>
        <button type="submit">Join Game</button>
    </form>
</body>
</html>
"""

game_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Room {{ room }}</title>
    <script src="https://cdn.socket.io/4.3.2/socket.io.min.js"></script>
</head>
<body style="font-family: Arial; text-align: center; background-color: #fff0f5;">
    <h1>Room Code: {{ room }}</h1>
    <div id="stage">
        <h2>Enter Category</h2>
        <input type="text" id="category" placeholder="Category">
        <button onclick="sendCategory()">Set Category</button>
    </div>
    <div id="messages"></div>

    <script>
        var socket = io();
        var room = "{{ room }}";

        socket.emit("join", {room: room});

        socket.on("message", function(data) {
            document.getElementById("messages").innerHTML += "<p>" + data + "</p>";
        });

        function sendCategory() {
            var cat = document.getElementById("category").value;
            socket.emit("set_category", {room: room, category: cat});
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(home_template)

@app.route("/create_game", methods=["POST"])
def create_game():
    room = str(uuid.uuid4())[:6].upper()
    games[room] = {"category": None, "players": {}}
    return redirect(url_for("game_room", room=room))

@app.route("/join_game", methods=["POST"])
def join_game():
    room = request.form["room"].strip().upper()
    if room in games:
        return redirect(url_for("game_room", room=room))
    return "Room not found", 404

@app.route("/room/<room>")
def game_room(room):
    if room not in games:
        return "Room not found", 404
    return render_template_string(game_template, room=room)

@socketio.on("join")
def on_join(data):
    room = data["room"]
    join_room(room)
    emit("message", "A player joined the room!", to=room)

@socketio.on("set_category")
def set_category(data):
    room = data["room"]
    category = data["category"]
    games[room]["category"] = category
    emit("message", f"Category set to: {category}", to=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)

