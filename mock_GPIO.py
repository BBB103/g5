# mock_GPIO.py

BCM = 11
BOARD = 10
OUT = 0
IN = 1
HIGH = True
LOW = False

def setmode(mode):
    print(f"[MOCK] 設置 GPIO 模式: {mode}")

def setup(pin, direction, pull_up_down=None):
    print(f"[MOCK] 設置 PIN {pin} 為 {'輸出' if direction == OUT else '輸入'}")

def output(pin, value):
    print(f"[MOCK] PIN {pin} 設置為 {'1' if value else '0'}")

def input(pin):
    print(f"[MOCK] 讀取 PIN {pin} 的值")
    return LOW

def cleanup():
    print("[MOCK] 清理 GPIO 設置")

# 其他可能需要的方法...
PUD_UP = 1
PUD_DOWN = 2