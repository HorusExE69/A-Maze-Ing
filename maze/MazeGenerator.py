from random import choice, randint
from sys import stderr
from os.path import realpath


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
        self.__seed = None

    def grid_gen(self, motif):

        m_w = len(motif[0])
        m_h = len(motif)

        self.__grid = [[15 for dx in range(self.__width)]
                       for dy in range(self.__height)]

        if self.__width < m_w + 2 or self.__height < m_h + 2:
            print(
                "Maze too small for the 42 pattern, skipping it",
                file=stderr,
            )
            return

        d_x = (self.__width - m_w) // 2
        d_y = (self.__height - m_h) // 2

        for dy in range(0, m_h):
            for dx in range(0, m_w):
                if motif[dy][dx] == '#':
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
        mandatory = {
            "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
        }
        allowed = mandatory | {"SEED"}
        seen = set()

        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    raise ValueError(f"Invalid configuration line: {line}")

                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key not in allowed:
                    raise ValueError(f"Unknown configuration key: {key}")
                if key in seen:
                    raise ValueError(f"Duplicate configuration key: {key}")
                seen.add(key)

                if key == "WIDTH":
                    self.__width = int(value)
                    if self.__width <= 0:
                        raise ValueError("Width must be a positive integer")
                elif key == "HEIGHT":
                    self.__height = int(value)
                    if self.__height <= 0:
                        raise ValueError("Height must be a positive integer")
                elif key == "ENTRY":
                    values = value.split(',')
                    if len(values) != 2:
                        raise ValueError(
                            "Entry must be in the format 'ENTRY=x,y'"
                        )
                    x, y = (item.strip() for item in values)
                    self.__entry = [int(y), int(x)]
                elif key == "EXIT":
                    values = value.split(',')
                    if len(values) != 2:
                        raise ValueError(
                            "Exit must be in the format 'EXIT=x,y'"
                        )
                    x, y = (item.strip() for item in values)
                    self.__end = [int(y), int(x)]
                elif key == "OUTPUT_FILE":
                    self.__filename = value
                elif key == "PERFECT":
                    if value not in ("True", "False"):
                        raise ValueError("PERFECT must be True or False")
                    self.__perfect = value == "True"
                elif key == "SEED":
                    self.__seed = int(value)

        missing = sorted(mandatory - seen)
        if missing:
            raise ValueError(
                "Missing configuration keys: " + ', '.join(missing)
            )

        if realpath(self.__filename) == realpath(filename):
            raise ValueError(
                "Output file cannot be the same as the configuration file"
            )

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

    @property
    def get_width(self):
        return self.__width

    @property
    def get_height(self):
        return self.__height

    @property
    def get_file(self):
        return self.__filename

    @property
    def get_motif_coords(self) -> list[tuple[int, int]]:
        coords: list[tuple[int, int]] = []
        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                if self.__grid[y][x] == -1:
                    coords.append((x, y))
        return coords

    @property
    def get_path(self) -> list[list[int]]:
        return self.__path
