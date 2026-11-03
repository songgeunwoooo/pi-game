import time, random
import board, digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

W = H = 240
FPS = 20
STEP = 1 / 60
SWAP_LR = False   # 좌우가 반대로 느껴지면 True

cs  = digitalio.DigitalInOut(board.CE0)
dc  = digitalio.DigitalInOut(board.D25)
rst = digitalio.DigitalInOut(board.D24)
bl  = digitalio.DigitalInOut(board.D26)
bl.switch_to_output()
bl.value = True

disp = st7789.ST7789(
    board.SPI(), width=W, height=H, y_offset=80, rotation=180,
    cs=cs, dc=dc, rst=rst, baudrate=24000000,
)

def btn(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    return d

LEFT, RIGHT, CENTER = btn(board.D27), btn(board.D23), btn(board.D4)
BTN_B = btn(board.D6)
if SWAP_LR:
    LEFT, RIGHT = RIGHT, LEFT

img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

player = [W // 2, H - 40]
ball = [W // 2, 40]
score = 0
speed = 4

prev = time.monotonic()
acc = 0.0

try:
    while True:
        now = time.monotonic()
        acc += now - prev
        prev = now
        if acc > 0.25:
            acc = 0.0

        if not BTN_B.value:
            break

        while acc >= STEP:
            if not CENTER.value:
                score = 0
            else:
                if not LEFT.value:
                    player[0] -= speed
                if not RIGHT.value:
                    player[0] += speed
            player[0] = max(12, min(W - 12, player[0]))

            ball[1] += 3
            if ball[1] > H:
                ball[1] = 0
                ball[0] = random.randint(20, W - 20)
                score -= 1

            if abs(ball[1] - player[1]) < 12 and abs(ball[0] - player[0]) < 20:
                ball[1] = 0
                ball[0] = random.randint(20, W - 20)
                score += 1

            acc -= STEP

        draw.rectangle((0, 0, W, H), fill=(10, 10, 25))
        draw.rectangle((player[0] - 20, player[1] - 6,
                        player[0] + 20, player[1] + 6), fill=(0, 220, 140))
        draw.ellipse((ball[0] - 6, ball[1] - 6,
                      ball[0] + 6, ball[1] + 6), fill=(255, 200, 0))
        draw.text((8, 8), f"SCORE {score}", fill=(255, 255, 255))
        disp.image(img)

        time.sleep(max(0, 1 / FPS - (time.monotonic() - now)))
finally:
    draw.rectangle((0, 0, W, H), fill=(0, 0, 0))
    disp.image(img)
    bl.value = False
    print("종료, 최종 점수:", score)
