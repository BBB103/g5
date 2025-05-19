"""
調酒機後端伺服器 - 使用Flask和Flask-SocketIO實現WebSocket通訊
"""
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    import mock_GPIO as GPIO

import time
import json
import threading

# 初始化Flask應用
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'cocktail-machine-secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# GPIO設置
GPIO.setmode(GPIO.BCM)

# 假設每種酒都由一個特定的GPIO針腳控制的泵或閥門
PUMPS = {
    "vodka": 17,
    "rum": 18,
    "tequila": 27,
    "gin": 22,
    "triple_sec": 23,
    "lime_juice": 24,
    "orange_juice": 25,
    "soda": 4,
    "tonic": 5,
    "simple_syrup": 6,
    "cranberry": 12,
    "cola": 13
}

# 初始化GPIO針腳
for pump in PUMPS.values():
    GPIO.setup(pump, GPIO.OUT)
    GPIO.output(pump, GPIO.LOW)  # 確保所有泵都是關閉的

# 調酒配方
COCKTAILS = {
    "margarita": {
        "name": "經典瑪格麗特",
        "ingredients": {
            "tequila": 45,    # 毫升
            "triple_sec": 15,
            "lime_juice": 30
        },
        "description": "龍舌蘭、君度橙酒與萊姆汁的完美平衡",
        "image": "margarita.jpg"
    },
    "mojito": {
        "name": "莫希托",
        "ingredients": {
            "rum": 45,
            "lime_juice": 20,
            "simple_syrup": 15,
            "soda": 60
        },
        "description": "清新的薄荷與萊姆混合白朗姆酒",
        "image": "mojito.jpg"
    },
    "old_fashioned": {
        "name": "古典雞尾酒",
        "ingredients": {
            "whiskey": 45,
            "simple_syrup": 10
        },
        "description": "威士忌、苦精與糖的經典組合",
        "image": "old_fashioned.jpg"
    },
    "screwdriver": {
        "name": "螺絲起子",
        "ingredients": {
            "vodka": 45,
            "orange_juice": 90
        },
        "description": "伏特加與橙汁的簡單組合",
        "image": "screwdriver.jpg"
    },
    "gin_tonic": {
        "name": "琴通寧",
        "ingredients": {
            "gin": 45,
            "tonic": 90,
            "lime_juice": 5
        },
        "description": "琴酒與通寧水的經典組合",
        "image": "gin_tonic.jpg"
    },
    "long_island": {
        "name": "長島冰茶",
        "ingredients": {
            "vodka": 15,
            "rum": 15,
            "gin": 15,
            "tequila": 15,
            "triple_sec": 15,
            "lime_juice": 30,
            "cola": 60
        },
        "description": "多種烈酒與可樂的混合",
        "image": "long_island.jpg"
    }
}

# 調酒機狀態
machine_status = {
    "busy": False,
    "current_cocktail": None,
    "progress": 0
}

# 流量控制常數 (每毫升所需時間，單位：秒)
FLOW_RATE = 0.1  # 假設每毫升需要0.1秒

def pour_ingredient(ingredient, amount):
    """控制特定泵運行特定時間來倒出指定量的配料"""
    if ingredient in PUMPS:
        pump_pin = PUMPS[ingredient]
        pour_time = amount * FLOW_RATE
        
        # 打開泵
        GPIO.output(pump_pin, GPIO.HIGH)
        time.sleep(pour_time)
        # 關閉泵
        GPIO.output(pump_pin, GPIO.LOW)
        return True
    return False

def make_cocktail(cocktail_id):
    """製作特定雞尾酒的流程"""
    if cocktail_id not in COCKTAILS:
        return False
    
    # 更新機器狀態
    machine_status["busy"] = True
    machine_status["current_cocktail"] = cocktail_id
    machine_status["progress"] = 0
    socketio.emit('status_update', machine_status)
    
    cocktail = COCKTAILS[cocktail_id]
    ingredients = cocktail["ingredients"]
    
    # 計算總量用於進度更新
    total_amount = sum(ingredients.values())
    poured_amount = 0
    
    # 依次添加每種配料
    for ingredient, amount in ingredients.items():
        pour_ingredient(ingredient, amount)
        
        # 更新進度
        poured_amount += amount
        machine_status["progress"] = int((poured_amount / total_amount) * 100)
        socketio.emit('status_update', machine_status)
        time.sleep(0.5)  # 配料之間稍作停頓
    
    # 完成
    machine_status["busy"] = False
    machine_status["progress"] = 100
    socketio.emit('status_update', machine_status)
    socketio.emit('cocktail_ready', {"cocktail_id": cocktail_id})
    
    # 稍等片刻，然後重置狀態
    time.sleep(5)
    machine_status["current_cocktail"] = None
    machine_status["progress"] = 0
    socketio.emit('status_update', machine_status)
    
    return True

@app.route('/')
def index():
    """提供靜態HTML頁面"""
    return send_from_directory('static', 'index.html')

@app.route('/cocktails')
def get_cocktails():
    """返回所有可用雞尾酒的列表"""
    return json.dumps(COCKTAILS)

@socketio.on('connect')
def handle_connect():
    """處理客戶端連接"""
    print('Client connected')
    emit('status_update', machine_status)

@socketio.on('disconnect')
def handle_disconnect():
    """處理客戶端斷開連接"""
    print('Client disconnected')

@socketio.on('order_cocktail')
def handle_order(data):
    """處理雞尾酒訂單"""
    cocktail_id = data.get('cocktail_id')
    print(f"Received order for {cocktail_id}")
    
    if machine_status["busy"]:
        emit('error', {'message': '調酒機正忙，請稍後再試'})
        return
    
    if cocktail_id not in COCKTAILS:
        emit('error', {'message': '找不到該雞尾酒'})
        return
    
    # 在新線程中製作雞尾酒，避免阻塞主線程
    cocktail_thread = threading.Thread(target=make_cocktail, args=(cocktail_id,))
    cocktail_thread.start()
    
    emit('order_received', {'cocktail_id': cocktail_id})

if __name__ == '__main__':
    try:
        socketio.run(app, host='127.0.0.1', port=5000, debug=True)
    finally:
        # 清理GPIO
        GPIO.cleanup()