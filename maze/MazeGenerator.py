from random import choice, randint, shuffle, seed
from sys import stderr
from os.path import realpath
from ansi_code import get_error


class MazeGenerator:
    DIRECTIONS = ((-1, 0, 1, 4), (0, 1, 2, 8), (1, 0, 4, 1), (0, -1, 8, 2))

    def __init__(
        self,
        width: int = 50,
        height: int = 50,
        filename: str = "maze.txt"
    ) -> None:
        self.__width: int = width
        self.__height: int = height
        self.__grid: list[list[int]] = []
        self.__path: list[list[int]] = []
        self.__entry: list[int] = [0, 0]
        self.__end: list[int] = [height - 1, width - 1]
        self.__filename: str = filename
        self.__perfect: bool = True
        self.__seed: int | None = None

    def grid_gen(self, motif: list[str]) -> None:
        m_w = len(motif[0])
        m_h = len(motif)

        self.__grid = [
            [15 for dx in range(self.__width)] for dy in range(self.__height)
        ]

        d_x = self.__width // 2 - (len(motif[0]) // 2)
        d_y = self.__height // 2 - (len(motif) // 2)

        if (
            d_x < 1
            or d_y < 1
            or d_x + m_w - 1 > self.__width - 2
            or d_y + m_h - 1 > self.__height - 2
        ):
            print(
                get_error("Maze too small for the 42 pattern, skipping it"),
                file=stderr,
            )
            return

        for dy in range(m_h):
            for dx in range(m_w):
                if motif[dy][dx] == "#":
                    self.__grid[d_y + dy][d_x + dx] = -1

    def entry_and_exit(self) -> None:
        stop = False

        while not stop:
            self.__entry = [
                randint(0, self.__height - 1),
                randint(0, self.__width - 1)
            ]
            if self.__grid[self.__entry[0]][self.__entry[1]] == -1:
                continue
            else:
                stop = True

        stop = False

        while not stop:
            self.__end = [
                randint(0, self.__height - 1),
                randint(0, self.__width - 1)
            ]
            if (
                self.__grid[self.__end[0]][self.__end[1]] == -1
                or self.__end == self.__entry
            ):
                continue
            else:
                stop = True

    def write_in_file(self) -> None:
        with open(self.__filename, "w", encoding="utf-8") as f:
            for i in range(len(self.__grid)):
                f.write(
                    "".join(format(valeur, "X").lower()
                            for valeur in self.__grid[i])
                )
                f.write("\n")

    def write_eof(self) -> str:
        with open(self.__filename, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"{self.__entry[1]},{self.__entry[0]}\n")
            f.write(f"{self.__end[1]},{self.__end[0]}\n")

            path_str = ""
            for i in range(len(self.__path) - 1):
                dl = self.__path[i + 1][0] - self.__path[i][0]
                dc = self.__path[i + 1][1] - self.__path[i][1]
                if dl == -1:
                    path_str += "N"
                elif dl == 1:
                    path_str += "S"
                elif dc == -1:
                    path_str += "W"
                elif dc == 1:
                    path_str += "E"
            f.write(path_str + "\n")
        return path_str

    def path_gen(self) -> None:
        stack: list[list[int]] = [list(self.__entry)]

        if self.__seed is not None:
            seed(self.__seed)

        while stack:
            head = stack[-1]

            if head == self.__end:
                self.__path = [list(pos) for pos in stack]

            neighbors: list[list[int]] = []

            for dl, dc, bit, bit_opp in MazeGenerator.DIRECTIONS:
                row = head[0] + dl
                col = head[1] + dc
                if (
                    0 <= row < self.__height
                    and 0 <= col < self.__width
                    and self.__grid[row][col] == 15
                ):
                    neighbors.append([row, col, bit, bit_opp])

            if neighbors:
                row, col, bit, bit_opp = choice(neighbors)
                self.__grid[head[0]][head[1]] &= ~bit
                self.__grid[row][col] &= ~bit_opp
                stack.append([row, col])
            else:
                stack.pop()

    def close_motif(self) -> None:
        for row in range(self.__height):
            for col in range(self.__width):
                if self.__grid[row][col] == -1:
                    self.__grid[row][col] = 15

    def parse_config(self, filename: str) -> None:
        mandatory: set[str] = {
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        }
        allowed = mandatory | {"SEED"}
        seen: set[str] = set()

        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(get_error(
                        f"Invalid configuration line: {line}"))

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key not in allowed:
                    raise ValueError(get_error(
                        f"Unknown configuration key: {key}"))
                if key in seen:
                    raise ValueError(get_error(
                        f"Duplicate configuration key: {key}"))
                seen.add(key)

                if key == "WIDTH":
                    self.__width = int(value)
                    if self.__width <= 0:
                        raise ValueError(
                            get_error("Width must be a positive integer"))
                elif key == "HEIGHT":
                    self.__height = int(value)
                    if self.__height <= 0:
                        raise ValueError(
                            get_error("Height must be a positive integer"))
                elif key == "ENTRY":
                    values = value.split(",")
                    if len(values) != 2:
                        raise ValueError(
                            get_error(
                                "Entry must be in the format 'ENTRY=x,y'"))
                    x, y = (item.strip() for item in values)
                    self.__entry = [int(y), int(x)]
                elif key == "EXIT":
                    values = value.split(",")
                    if len(values) != 2:
                        raise ValueError(
                            get_error("Exit must be in the format 'EXIT=x,y'"))
                    x, y = (item.strip() for item in values)
                    self.__end = [int(y), int(x)]
                elif key == "OUTPUT_FILE":
                    self.__filename = value
                elif key == "PERFECT":
                    if value not in ("True", "False"):
                        raise ValueError(
                            get_error("PERFECT must be True or False"))
                    self.__perfect = value == "True"
                elif key == "SEED":
                    self.__seed = int(value)

        missing = sorted(mandatory - seen)
        if missing:
            raise ValueError(
                get_error("Missing configuration keys: " + ", ".join(missing)))

        if realpath(self.__filename) == realpath(filename):
            raise ValueError(
                get_error("Output file cannot be the "
                          "same as the configuration file"))

    def check_entry_exit(self) -> None:
        if self.__entry[0] not in range(self.__height) or \
           self.__entry[1] not in range(self.__width):
            raise ValueError(
                get_error(f"Entry position {self.__entry} is out of bounds"))
        elif (
            self.__end[0] not in range(self.__height)
            or self.__end[1] not in range(self.__width)
        ):
            raise ValueError(
                get_error(f"Exit position {self.__end} is out of bounds"))
        elif self.__grid[self.__entry[0]][self.__entry[1]] == -1:
            raise ValueError(
                get_error(f"Entry position {self.__entry} is on the 42"))
        elif self.__grid[self.__end[0]][self.__end[1]] == -1:
            raise ValueError(
                get_error(f"Exit position {self.__end} is on the 42"))
        elif self.__entry == self.__end:
            raise ValueError(
                get_error(f"Entry position {self.__entry} and exit position "
                          "are the same")
            )

    def __is_dead_end(self, r: int, c: int) -> bool:
        value = self.__grid[r][c]
        return value != -1 and bin(value).count("1") == 3

    def __is_open_square(self, r: int, c: int) -> bool:
        if r < 0 or c < 0:
            return False
        if r + 2 >= self.__height or c + 2 >= self.__width:
            return False

        for row in range(r, r + 3):
            for col in range(c, c + 3):
                if self.__grid[row][col] == -1:
                    return False

        for row in range(r, r + 3):
            for col in (c, c + 1):
                if self.__grid[row][col] == -1:
                    return False
                if self.__grid[row][col] & 2:
                    return False

        for col in range(c, c + 3):
            for row in (r, r + 1):
                if self.__grid[row][col] == -1:
                    return False
                if self.__grid[row][col] & 4:
                    return False

        return True

    def __is_in_open_square(self, r: int, c: int) -> bool:
        for row in range(r - 2, r + 1):
            for col in range(c - 2, c + 1):
                if self.__is_open_square(row, col):
                    return True
        return False

    def braid(self) -> None:
        for r in range(self.__height):
            for c in range(self.__width):
                if not self.__is_dead_end(r, c):
                    continue

                dead_neighbors: list[tuple[int, int, int, int]] = []
                other_neighbors: list[tuple[int, int, int, int]] = []

                for dl, dc, bit, bit_opp in MazeGenerator.DIRECTIONS:
                    row = r + dl
                    col = c + dc
                    if not (
                        0 <= row < self.__height
                        and 0 <= col < self.__width
                    ):
                        continue
                    if self.__grid[row][col] == -1:
                        continue
                    if not (self.__grid[r][c] & bit):
                        continue

                    candidate = (row, col, bit, bit_opp)
                    if self.__is_dead_end(row, col):
                        dead_neighbors.append(candidate)
                    else:
                        other_neighbors.append(candidate)

                shuffle(dead_neighbors)
                shuffle(other_neighbors)
                candidates = dead_neighbors + other_neighbors

                for row, col, bit, bit_opp in candidates:
                    self.__grid[r][c] &= ~bit
                    self.__grid[row][col] &= ~bit_opp

                    if (
                        self.__is_in_open_square(r, c)
                        or self.__is_in_open_square(row, col)
                    ):
                        self.__grid[r][c] |= bit
                        self.__grid[row][col] |= bit_opp
                    else:
                        break

    # Getters

    @property
    def get_width(self) -> int:
        return self.__width

    @property
    def get_height(self) -> int:
        return self.__height

    @property
    def get_start_pos(self) -> list[int]:
        return self.__entry

    @property
    def get_end_pos(self) -> list[int]:
        return self.__end

    @property
    def get_file(self) -> str:
        return self.__filename

    @property
    def perfect_mode(self) -> bool:
        return self.__perfect

    @property
    def get_motif_coords(self) -> list[tuple[int, int]]:
        coords: list[tuple[int, int]] = []
        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                if self.__grid[y][x] == -1:
                    coords.append((x, y))
        return coords
