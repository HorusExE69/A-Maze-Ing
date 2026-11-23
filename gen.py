import sys

WIDTH = 30
HEIGHT = 30

motif =["#.#.###",
        "#.#...#",
        "###.###",
        "..#.#..",
        "..#.###"]

m_w = len(motif[0])
m_h = len(motif)

d_x = (WIDTH - m_w) // 2
d_y = (HEIGHT - m_h) // 2

grid = []

for dy in range(0, HEIGHT):
    ligne = ""
    for dx in range(0, WIDTH):
        ligne += '0'
    grid.append(ligne)

for dy in range(0, m_h):
    for dx in range(0, m_w):
        if (motif[dy][dx] == '#'):
            grid[d_y + dy] = grid[d_y + dy][:d_x + dx] + 'F' + grid[d_y + dy][d_x + dx + 1:]

with open(sys.argv[1], "w", encoding="utf-8") as f:
    for i in range(len(grid)):
        f.write(grid[i])
        f.write('\n')
