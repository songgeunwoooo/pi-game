# maze.py : 지도

# 한 칸 크기. 240 / 16 = 15칸
TILE = 16

# 지도. # 솜사탕(벽)   . 길   S 시작   E 출구
# 1단계는 벽이 한 겹이라 구멍 2개면 나갈 수 있음
STAGE1 = [
    "###############",
    "#S...#....#...#",
    "#....#....#...#",
    "#.##.#.##.#...#",
    "#.##.#.##.#.#.#",
    "#....#....#...#",
    "#....#....#...#",
    "#.#..#..#.#...#",
    "#.#..#..#.#.#.#",
    "#....#....#...#",
    "#....#.##.#...#",
    "#....#....#...#",
    "#.##.#....#.#.#",
    "#....#....#..E#",
    "###############",
]


# 구멍 뚫을 수 있게 글자 목록을 리스트로 바꿈
def make_grid(rows):
    return [list(row) for row in rows]


# ch가 있는 칸의 (x, y)
def find(grid, ch):
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c == ch:
                return x, y


# 갈 수 있는 칸인지 (지도 밖이거나 #이면 못 감)
def can_walk(grid, x, y):
    if x < 0 or y < 0 or y >= len(grid) or x >= len(grid[0]):
        return False
    return grid[y][x] != "#"
