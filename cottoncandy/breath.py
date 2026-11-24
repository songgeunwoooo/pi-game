# breath.py : 입김 감지
# Uno가 USB로 0.2초마다 "경과초 습도 온도" 한 줄을 보내고, 여기서 읽어서 입김인지 판단함
import glob
import time
import serial

# 입김 판단 기준
THRESHOLD = 3   # 0.6초 전보다 이만큼 오르면 입김 (%p)
BACK = 3        # 몇 개 전 값과 비교 (0.2초 x 3 = 0.6초)
REST = 2        # 입김 인식 뒤 쉬는 시간(초). 한 번 불 때 여러 번 잡히는 걸 줄임

# 포트 열기
# Uno가 없으면 None으로 두고 입김은 항상 False
names = glob.glob("/dev/ttyUSB*")
try:
    port = serial.Serial(names[0], 9600, timeout=0)   # timeout=0: 기다리지 않음
    time.sleep(2)                                     # 열면 Uno가 재시작해서 대기
    port.reset_input_buffer()
except (IndexError, serial.SerialException):
    port = None

# 읽는 동안 기억해 둘 것
humidity = []     # 최근 습도 값들
buf = b""         # 아직 한 줄이 안 끝난 글자
last_blow = 0.0   # 마지막으로 입김을 인식한 시각


# 입김이 감지됐으면 True. 게임 루프에서 매 프레임 부름 (기다리지 않고 바로 돌아옴)
def blown():
    global buf, last_blow
    if port is None:
        return False

    # 와 있는 글자를 읽어서 줄 단위로 자름
    buf += port.read(port.in_waiting)
    lines = buf.split(b"\n")
    buf = lines.pop()        # 마지막은 덜 온 줄이라 다시 모아 둠

    found = False
    for line in lines:
        parts = line.split()
        if len(parts) != 3:   # 깨진 줄은 버림
            continue
        try:
            humidity.append(float(parts[1]))   # 가운데 값이 습도
        except ValueError:
            continue

        # 입김 판단. 절대값은 못 쓰고(입김 뒤 천천히 내려옴) 얼마나 올랐는지로 봄
        now = time.monotonic()
        if (len(humidity) > BACK                                      # 비교할 값이 쌓였고
                and humidity[-1] - humidity[-1 - BACK] >= THRESHOLD   # 0.6초 전보다 많이 올랐고
                and now - last_blow >= REST):                         # 쉬는 시간이 지났으면
            last_blow = now
            found = True

    del humidity[:-10]        # 최근 10개만 남김
    return found


# 여기서 실행하면 테스트 
if __name__ == "__main__":
    if port is None:
        print("Uno가 안 보여요")
    else:
        print("센서 쪽으로 불어 보세요 (Ctrl+C로 끝)")
        try:
            while True:
                if blown():
                    print("감지!")
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
