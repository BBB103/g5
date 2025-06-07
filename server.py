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

machine_status= {
    "busy" : False,
    "current_cocktail": None,
    "progress": "待機"
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

@socketio.on("pouring")
def handle_pour():
    machine_status["busy"] = True
    machine_status["progress"] = "正在倒入原料"
    socketio.emit('status_update', machine_status)

@socketio.on("closing")
def handle_close():
    machine_status["busy"] = True
    machine_status["progress"] = "正在關杯蓋"
    socketio.emit('status_update', machine_status)

@socketio.on("shaking")
def handle_shake():
    machine_status["busy"] = True
    machine_status["progress"] = "正在shake"
    socketio.emit('status_update', machine_status)
@socketio.on("done")
def handle_done():
    machine_status['current_cocktail'] = None
    machine_status['progress'] = 0
    socketio.emit('status_update', machine_status)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)