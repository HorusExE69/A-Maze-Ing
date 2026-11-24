from random import choice, randint


class MazeGenerator:
    def __init__(self, width=50, height=50, filename="maze.txt"):
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
        with open(self.__filename, "a", encoding="utf-8") as f:
            f.write('\n')
            f.write(f"{self.__entry[1]},{self.__entry[0]}\n")
            f.write(f"{self.__end[1]},{self.__end[0]}\n")

            path_str = ""
            for i in range(0, len(self.__path) - 1):
                dl = self.__path[i + 1][0] - self.__path[i][0]
                dc = self.__path[i + 1][1] - self.__path[i][1]
                if dl == -1:
                    path_str += 'N'
                elif dl == 1:
                    path_str += 'S'
                elif dc == -1:
                    path_str += 'W'
                elif dc == 1:
                    path_str += 'E'
            f.write(path_str + '\n')

    def path_gen(self):
        stack = [list(self.__entry)]

        dir = ((-1, 0, 1, 4), (0, 1, 2, 8),
               (1, 0, 4, 1), (0, -1, 8, 2))

        while stack:
            head = stack[-1]

            if head == self.__end:
                self.__path = [list(pos) for pos in stack]

            neighbors = []

            for dl, dc, bit, bit_opp in dir:
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

    def parse_config(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        kept = []
        for line in lines:
            if line[0].isupper():
                kept.append(line[:-1])
        lines = kept
        for line in lines:
            if line.split('=')[0] == "WIDTH":
                self.__width = int(line[6:])
            elif line.split('=')[0] == "HEIGHT":
                self.__height = int(line[7:])
            elif line.split('=')[0] == "ENTRY":
                self.__entry = [int(line[6:].split(",")[1]),
                                int(line[6:].split(",")[0])]
            elif line.split('=')[0] == "EXIT":
                self.__end = [int(line[5:].split(",")[1]),
                              int(line[5:].split(",")[0])]
            elif line.split('=')[0] == "OUTPUT_FILE":
                self.__filename = line[12:]
            elif line.split('=')[0] == "PERFECT":
                self.__perfect = line[8:] == "True"
            else:
                print(f"Unknown configuration option: {line}")

    def check_entry_exit(self):
        if self.__entry[0] not in range(self.__height) or self.__entry[1] not in range(self.__width):
            raise ValueError(f"Entry position {self.__entry} is out of bounds")
        elif self.__end[0] not in range(self.__height) or self.__end[1] not in range(self.__width):
            raise ValueError(f"Exit position {self.__end} is out of bounds")
        elif self.__grid[self.__entry[0]][self.__entry[1]] == -1:
            raise ValueError(f"Entry position {self.__entry} is on the 42")
        elif self.__grid[self.__end[0]][self.__end[1]] == -1:
            raise ValueError(f"Exit position {self.__end} is on the 42")
        elif self.__entry == self.__end:
            raise ValueError(
                f"Entry position {self.__entry} and exit position {self.__end} are the same")

    # Getters

    def get_width(self):
        return self.__width

    def get_height(self):
        return self.__height

    def get_file(self):
        return self.__filename

    def get_motif_coords(self) -> list[tuple[int, int]]:
        coords: list[tuple[int, int]] = []
        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                if self.__grid[y][x] == -1:
                    coords.append((x, y))
        return coords
