import time
import board, digitalio

PINS = {
    "pin17": board.D17, "pin22": board.D22,
    "pin27": board.D27, "pin23": board.D23,
    "pin4": board.D4,
}
btns = {}
for name, pin in PINS.items():
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    btns[name] = b

def pressed():
    return sorted(n for n, b in btns.items() if not b.value)

def wait_release():
    while pressed():
        time.sleep(0.02)
    time.sleep(0.3)

for want in ["위로", "아래로", "왼쪽으로", "오른쪽으로", "가운데 수직으로 누르기"]:
    wait_release()
    print(f"\n[{want}] 하고 그대로 유지하세요 (누를 때까지 기다림)...")
    while not pressed():
        time.sleep(0.01)
    time.sleep(0.4)
    print(f"  {want} -> {pressed()}")
    print("  손을 떼세요")
print("\n끝")
