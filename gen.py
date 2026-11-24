from sys import argv
from random import choice, randint
from display import display_map


class MazeGenerator:
    def __init__(self, width = 50, height = 50, filename = "maze.txt"):
        self.__width = width
        self.__height = height
        self.__grid = []
        self.__path = []
        self.__entry = [0, 0]
        self.__end = [height - 1, width - 1]
        self.__filename = filename
        self.__perfect = True

    def grid_gen(self, motif):

        m_w = len(motif[0])
        m_h = len(motif)

        d_x = (self.__width - m_w) // 2
        d_y = (self.__height - m_h) // 2

        self.__grid = [[15 for dx in range(self.__width)]
                       for dy in range(self.__height)]

        for dy in range(0, m_h):
            for dx in range(0, m_w):
                if (motif[dy][dx] == '#'):
                    self.__grid[d_y + dy][d_x + dx] = -1

    def entry_and_exit(self):

        stop = False

        while not stop:
            self.__entry = [randint(0, self.__height - 1),
                            randint(0, self.__width - 1)]
            if self.__grid[self.__entry[0]][self.__entry[1]] == -1:
                continue
            else:
                stop = True

        stop = False

        while not stop:
            self.__end = [randint(0, self.__height - 1),
                          randint(0, self.__width - 1)]
            if self.__grid[self.__end[0]][self.__end[1]] == -1 \
                    or self.__end == self.__entry:
                continue
            else:
                stop = True

    def write_in_file(self):
        with open(self.__filename, "w", encoding="utf-8") as f:
            for i in range(len(self.__grid)):
                f.write(''.join(format(valeur, 'X').lower()
                                for valeur in self.__grid[i]))
                f.write('\n')

    def write_eof(self):
        with open(self.__filename, "a", encoding = "utf-8") as f:
            f.write(f"{self.__entry[0]},{self.__entry[1]}\n")
            f.write(f"{self.__end[0]},{self.__end[1]}\n")

    def path_gen(self):
        stack = [list(self.__entry)]

        directions = ((-1, 0, 1, 4), (0, 1, 2, 8),
                      (1, 0, 4, 1), (0, -1, 8, 2))

        while stack:
            head = stack[-1]

            if head == self.__end:
                self.__path = [list(position) for position in stack]

            neighbors = []

            for dl, dc, bit, bit_opp in directions:
                row = head[0] + dl
                column = head[1] + dc
                if 0 <= row < self.__height and 0 <= column < self.__width \
                        and self.__grid[row][column] == 15:
                    neighbors.append([row, column, bit, bit_opp])

            if neighbors:
                row, column, bit, bit_opp = choice(neighbors)
                self.__grid[head[0]][head[1]] &= ~bit
                self.__grid[row][column] &= ~bit_opp
                stack.append([row, column])
            else:
                stack.pop()

        for row in range(self.__height):
            for column in range(self.__width):
                if self.__grid[row][column] == -1:
                    self.__grid[row][column] = 15

    def get_motif_coords(self) -> list[tuple[int, int]]:
        coords: list[tuple[int, int]] = []
        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                if self.__grid[y][x] == -1:
                    coords.append((x, y))
        return coords

    def parse_config(self, filename) :
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        kept = []
        for l in lines:
            if l[0].isupper():
                kept.append(l[:-1])
        lines = kept
        for l in lines:
            if l.split('=')[0] == "WIDTH":
                self.__width = int(l[6:])
            elif l.split('=')[0] == "HEIGHT":
                self.__height = int(l[7:])
            elif l.split('=')[0] == "ENTRY":
                self.__entry = [int(l[6:].split(",")[0]), int(l[6:].split(",")[1])]
            elif l.split('=')[0] == "EXIT":
                self.__end = [int(l[5:].split(",")[0]), int(l[5:].split(",")[1])]
            elif l.split('=')[0] == "OUTPUT_FILE":
                self.__filename = l[12:]
            elif l.split('=')[0] == "PERFECT":
                self.__perfect = l[8:] == "True"
            else:
                print(f"Unknown configuration option: {l}")


    # Getters
    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    def get_file(self):
        return self.__filename



motif = ["#.#.###",
         "#.#...#",
         "###.###",
         "..#.#..",
         "..#.###"
         ]

maze = MazeGenerator()
maze.parse_config(argv[1])
maze.grid_gen(motif)
motif_coords = maze.get_motif_coords()
maze.entry_and_exit()
maze.path_gen()
maze.write_in_file()

START_POS = (0, 0)
END_POS = (maze.get_width() - 1, maze.get_height() - 1)
display_map(maze.get_file(), START_POS, END_POS, motif_coords)

maze.write_eof()
