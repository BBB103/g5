# backend.py on Railway

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import json
import eventlet
eventlet.monkey_patch()

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

COCKTAILS = {
    "RED": {"name": "紅色", "ingredients": {"red": 15} ,"descrption":"紅紅的", "image": "red.png"},
    "YELLOW": {"name": "黃色", "ingredients": {"yellow": 15},"descrption":"黃黃的", "image": "yellow.png"},
    "BLUE": {"name": "藍色", "ingredients": {"blue": 15},"descrption":"藍藍的", "image": "blue.png"},
    "GREEN": {"name": "綠色", "ingredients": {"yellow": 15, "blue": 15},"descrption":"綠綠的", "image": "green.png"},
    "PURPLE": {"name": "紫色", "ingredients": {"red": 15, "blue": 15},"descrption":"紫紫的", "image": "purple.png"}
}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/cocktails')
def get_cocktails():
    return json.dumps(COCKTAILS)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('order_cocktail')
def handle_order(data):
    print("Forwarding cocktail order to RPi...")
    socketio.emit('start_cocktail', data)  # 發給RPi
    emit('order_received', {'cocktail_id': data.get("cocktail_id")})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)