from flask import Flask, render_template ,send_from_directory
from flask_socketio import SocketIO, emit
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    import mock_GPIO as GPIO

import time
import json

# initialize
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'cocktail-machine-secert!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
# set up GPIO
GPIO.setmode(GPIO.BCM)

PUMPS={
    "red": 15,
    "yellow": 16,
    "blue": 17,
    "black": 18,
    "white": 19,
    "purple": 20,
}

# initiallize GPIO pins
for pump in PUMPS.values():
    GPIO.setup(pump, GPIO.OUT)
    GPIO.output(pump,GPIO.LOW)

# recipe
COCKTAILS = {
    # one-ingrediented product
    "RED": {
        "name": "紅色",
        "ingredients":{
            "red": 15,
        },
        "description": "紅紅的",
        "image": "red.png"
    },
    "YELLOW": {
        "name": "黃色",
        "ingredients":{
            "yellow": 15,
        },
        "description": "黃黃的",
        "image": "yellow.png"
    },
    "BLUE": {
        "name": "藍色",
        "ingredients":{
            "blue": 15,
        },
        "description": "藍藍的",
        "image": "blue.png"
    },

    # mixture 

    "GREEN": {
        "name": "綠色",
        "ingredients":{
            "yellow": 15,
            "blue": 15
        },
        "description": "綠綠的"
    },
    "PURPLE": {
        "name": "紫色",
        "ingredients":{
            "red": 15,
            "blue": 15
        },
        "description": "紫紫的"
    }
}

# status of the machine
machine_status = {
    "busy" : False,
    "current_cocktail": None,
    "progress": 0
}
# flow constant 
flow_rate = 0.1

def pour_ingredient(ingrdient,amount):
    if ingrdient in PUMPS:
        pump_pin = PUMPS[ingrdient] # read the corresponding pin number of the ingredient 
        pour_time = amount * flow_rate # amount is the unit time needed
        # open the valve
        GPIO.output(pump_pin, GPIO.HIGH)
        time.sleep(pour_time)
        # shut the valve
        GPIO.output(pump_pin, GPIO.LOW)
        return True
    return False

def make_cocktail(cocktail_id):
    if cocktail_id not in COCKTAILS:  # if not in recipe
        return False

    machine_status['busy'] = True
    machine_status["current_cocktail"] = cocktail_id
    machine_status["progress"] =  0
    socketio.emit('status_update', machine_status)
    socketio.sleep(0.1)

    cocktail = COCKTAILS[cocktail_id]
    ingredients = cocktail["ingredients"]

    # calaulate total amount to update progress
    total_amount = sum(ingredients.values())
    poured = 0
    # for ingredient, amount in ingredients.items():
    #     pour_ingredient(ingredient, amount)

    #     poured += amount
    #     machine_status["progress"] = int (100*(poured/total_amount))
    #     socketio.emit('status_update', machine_status)
    #     time.sleep(1)
    for ingredient, amount in ingredients.items():
        status_msg = f"正在加入 {ingredient}"
        socketio.emit('status_update', {
            **machine_status,
            "message": status_msg
        })
        socketio.sleep(0.1)
        pour_ingredient(ingredient, amount)


    poured += amount
    machine_status["progress"] = int((poured / total_amount) * 100)
    socketio.emit('status_update', {
        **machine_status,
        "message": f"{ingredient} 加入完成"
    })
    socketio.sleep(0.1)
    time.sleep(1)
    machine_status['busy'] = False
    machine_status['progress'] = 100
    socketio.emit('status_update', machine_status)
    socketio.sleep(0.1)
    socketio.emit('cocktail_ready', {"cocktail_id": cocktail_id})
    # hold before reset
    time.sleep(5)
    machine_status['current_cocktail'] = None
    machine_status['progress'] = 0
    socketio.emit('status_update', machine_status)
    socketio.sleep(0.1)
    return True


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route("/cocktails")
def get_cocktails():
    return json.dumps(COCKTAILS)

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_connect():
    print("Client disconnected")

@socketio.on('order_cocktail')
def handle_order(data):
    cocktail_id = data.get('cocktail_id')
    print(f"Received order for {cocktail_id}")

    if machine_status["busy"]:
        emit('error',{'message': 'busymakingcocktails!!!'})
        return
    
    if cocktail_id not in COCKTAILS:
        emit('error', {'message': '404cocktailnotfound'})
        return
    emit('order_received', {'cocktail_id': cocktail_id})
    make_cocktail(cocktail_id)
    # print(machine_status["progress"])
    # cocktail_thread = threading.Thread(target=make_cocktail, args=(cocktail_id,))
    # cocktail_thread.start()
    

if __name__ == '__main__':
    try:
        socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    finally:
        # 清理GPIO
        GPIO.cleanup()