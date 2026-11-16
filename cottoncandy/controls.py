# controls.py : 조이스틱, 버튼 읽기
import board, digitalio


# 핀 하나를 버튼으로 설정
def btn(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP   # 누르면 LOW
    return d


# 조이스틱 방향 4개 + 가운데
UP = btn(board.D17)
DOWN = btn(board.D22)
LEFT = btn(board.D27)
RIGHT = btn(board.D23)
CENTER = btn(board.D4)

# 버튼 A, B
BTN_A = btn(board.D5)
BTN_B = btn(board.D6)


# 방향 -> (dx, dy), 안 누르면 (0, 0)
def direction():
    if not CENTER.value:   # 가운데 누르면 다른 방향도 같이 눌려서 무시
        return (0, 0)
    if not UP.value:
        return (0, -1)
    if not DOWN.value:
        return (0, 1)
    if not LEFT.value:
        return (-1, 0)
    if not RIGHT.value:
        return (1, 0)
    return (0, 0)


# A 눌렀는지
def button_a():
    return not BTN_A.value


# B 눌렀는지
def button_b():
    return not BTN_B.value


# 아무 버튼이나 눌렸는지
def any_pressed():
    for pin in (UP, DOWN, LEFT, RIGHT, CENTER, BTN_A, BTN_B):
        if not pin.value:
            return True
    return False
