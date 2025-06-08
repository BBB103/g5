# backend.py on Railway
import eventlet
eventlet.monkey_patch()

from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

COCKTAILS = {
    "RED": {
        "name": "Bloody Mary (紅色)",
        "ingredients": {"red": 15},
        "descrption": "番茄汁為基底，鹹香微辣，適合早午餐或解宿醉時飲用，口感濃郁厚實。",
        "image": "Bloody-Mary.jpg"
    },
    "YELLOW": {
        "name": "Screwdriver (黃色)",
        "ingredients": {"yellow": 15},
        "descrption": "由伏特加與柳橙汁調製，清爽酸甜，適合午後小酌，口感滑順易飲。",
        "image": "screw.jpg"
    },
    "BLUE": {
        "name": "Blue Hawaii (藍色)",
        "ingredients": {"blue": 15},
        "descrption": "藍柑橘搭配鳳梨與蘭姆酒，熱帶風情濃厚，適合派對或海灘時享用，口感清新帶果香。",
        "image": "bluehaw.webp"
    },
    "GREEN": {
        "name": "Grasshopper (綠色)",
        "ingredients": {"yellow": 15, "blue": 15},
        "descrption": "薄荷酒與可可酒交織出的甜香，適合飯後作為甜點酒，口感冰涼滑順。",
        "image": "grasshopper.webp"
    },
    "PURPLE": {
        "name": "Aviation (紫色)",
        "ingredients": {"red": 15, "blue": 15},
        "descrption": "結合琴酒與紫羅蘭香甜酒，適合浪漫夜晚或安靜時刻品飲，口感淡雅略帶花香。",
        "image": "aviation.png"
    }
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
    machine_status["progress"] = "shakeing"
    socketio.emit('status_update', machine_status)
@socketio.on("done")
def handle_done():
    machine_status['current_cocktail'] = None
    machine_status['progress'] = 0
    socketio.emit('status_update', machine_status)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)