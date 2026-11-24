# main.py : 시작 화면, 꼬마 이동, 구멍 뚫기(입김), 숨 횟수, 클리어, 제한 시간
import time
import board, digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import maze
import controls
import breath

# 화면 크기, 초당 프레임, 이동 간격, 제한 시간, 숨 횟수
W = H = 240
FPS = 20
MOVE_DELAY = 0.15   # 한 칸 가는 간격(초)
TIME_LIMIT = 60     # 제한 시간(초)
BREATHS = 5         # 구멍을 뚫을 수 있는 횟수

# 화면 핀 (수업 샘플이랑 game.py 참고)
cs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D25)
rst = digitalio.DigitalInOut(board.D24)

# 백라이트 켜기
bl = digitalio.DigitalInOut(board.D26)
bl.switch_to_output()
bl.value = True

# 화면 만들기
disp = st7789.ST7789(
    board.SPI(), width=W, height=H, y_offset=80, rotation=180,
    cs=cs, dc=dc, rst=rst, baudrate=24000000,
)

# 색
PINK = (255, 170, 205)
PURPLE = (70, 50, 90)

# 지도 글자별 색
COLOR = {
    "#": PINK,               # 솜사탕
    ".": PURPLE,             # 길
    "S": (100, 200, 255),    # 시작 칸
    "E": (255, 220, 60),     # 출구
}
KID_COLOR = (255, 140, 40)   # 꼬마

# 한글 글꼴
FONT_PATH = "/usr/share/fonts/truetype/naver-d2coding/D2Coding-Ver1.3.2-20180524-all.ttc"
TITLE_FONT = ImageFont.truetype(FONT_PATH, 32)   # 제목
SMALL_FONT = ImageFont.truetype(FONT_PATH, 16)   # 안내 글

# 여기에 그려서 화면으로 보냄
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)


# 지도 그리기. 칸마다 색 네모
def draw_map(grid):
    t = maze.TILE
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            draw.rectangle((x * t, y * t, x * t + t - 1, y * t + t - 1),
                           fill=COLOR[ch])


# 꼬마 그리기. 주황 동그라미 + 바라보는 쪽 흰 점
def draw_kid(x, y, face):
    t = maze.TILE
    left, top = x * t, y * t
    draw.ellipse((left + 2, top + 2, left + t - 3, top + t - 3), fill=KID_COLOR)
    cx = left + t // 2 + face[0] * 5
    cy = top + t // 2 + face[1] * 5
    draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(255, 255, 255))


# 글자 가로 가운데
def draw_centered(text, y, font, color):
    x = (W - int(draw.textlength(text, font=font))) // 2
    draw.text((x, y), text, font=font, fill=color)


# 시작 화면 그리기
def draw_title():
    draw.rectangle((0, 0, W, H), fill=PURPLE)
    draw_centered("구멍송송", 60, TITLE_FONT, PINK)
    draw_centered("솜사탕", 105, TITLE_FONT, PINK)
    draw_centered("아무 버튼이나 누르세요", 185, SMALL_FONT, (255, 255, 255))


# 끝 화면 그리기 (클리어, 시간 초과 같이 씀)
def draw_end(title, line):
    draw.rectangle((0, 0, W, H), fill=PURPLE)
    draw_centered(title, 75, TITLE_FONT, PINK)
    draw_centered(line, 125, SMALL_FONT, (255, 255, 255))
    draw_centered("아무 버튼이나 누르세요", 185, SMALL_FONT, (255, 255, 255))


# 새 지도와 시작 칸 (다시 시작할 때도 씀)
def new_game():
    grid = maze.make_grid(maze.STAGE1)
    x, y = maze.find(grid, "S")
    return grid, x, y


# 처음 상태
grid, kid_x, kid_y = new_game()
face = (1, 0)       # 바라보는 방향
last_move = 0.0     # 마지막으로 움직인 시각
start_time = 0.0    # 게임을 시작한 시각
end_time = 0.0      # 끝난 시각
breaths = BREATHS   # 남은 숨
score = 0           # 클리어했을 때 남은 시간
state = "title"     # title / play / clear / over

# 게임 루프. 한 바퀴가 한 프레임
try:
    while True:
        now = time.monotonic()
        blow = breath.blown()   # 입김 읽기. 화면과 상관없이 매번 읽어서 글자가 쌓이지 않게
        if blow:
            print("입김 감지")     # 확인용, 나중에 지움

        if state == "title":
            # 시작 화면: 아무 버튼이나 누르면 게임으로
            if controls.any_pressed():
                while controls.any_pressed():   # 손 뗄 때까지 대기 (#6으로 시작하면 바로 꺼져서)
                    time.sleep(0.05)
                start_time = time.monotonic()
                breaths = BREATHS
                state = "play"
            draw_title()
        elif state in ("clear", "over"):
            # 1초는 화면을 보여 주고, 그 뒤 아무 버튼이나 누르면 처음으로
            if state == "clear":
                draw_end("클리어!", f"남은 시간 {score}초")
            else:
                draw_end("시간 초과", "")
            if now - end_time >= 1 and controls.any_pressed():
                while controls.any_pressed():   # 손 뗄 때까지 대기
                    time.sleep(0.05)
                grid, kid_x, kid_y = new_game()
                face = (1, 0)
                state = "title"
        else:
            # 게임 중 #6은 종료
            if controls.button_b():
                break

            # 입김(안 되면 A 버튼): 바라보는 앞 칸 뚫기. 실제로 뚫렸을 때만 숨이 줄어듦
            if (blow or controls.button_a()) and breaths > 0:
                if maze.dig(grid, kid_x + face[0], kid_y + face[1]):
                    breaths -= 1

            # 조이스틱 방향 읽기
            dx, dy = controls.direction()
            if (dx, dy) != (0, 0):
                face = (dx, dy)       # 막혀도 방향은 바뀜
                # 일정 간격마다 한 칸, 벽이면 안 움직임
                if now - last_move >= MOVE_DELAY:
                    if maze.can_walk(grid, kid_x + dx, kid_y + dy):
                        kid_x += dx
                        kid_y += dy
                    last_move = now

            # 남은 시간
            left = int(TIME_LIMIT - (now - start_time))

            # 출구에 닿으면 클리어, 시간이 다 되면 시간 초과
            if grid[kid_y][kid_x] == "E":
                score = left
                state = "clear"
                end_time = now
            elif left <= 0:
                state = "over"
                end_time = now

            # 지도 위에 꼬마, 남은 시간(왼쪽), 남은 숨(오른쪽) 그리기
            draw_map(grid)
            draw_kid(kid_x, kid_y, face)
            draw.text((4, 0), f"남은 시간 {left}", font=SMALL_FONT, fill=PURPLE)
            breath_text = f"숨 {breaths}"
            breath_x = W - 4 - int(draw.textlength(breath_text, font=SMALL_FONT))
            draw.text((breath_x, 0), breath_text, font=SMALL_FONT, fill=PURPLE)

        # 화면에 보내고 프레임 시간 맞추기
        disp.image(img)
        time.sleep(max(0, 1 / FPS - (time.monotonic() - now)))
except KeyboardInterrupt:
    pass
finally:
    # 끝낼 때 화면 끄기
    draw.rectangle((0, 0, W, H), fill=(0, 0, 0))
    disp.image(img)
    bl.value = False
    print("종료")
