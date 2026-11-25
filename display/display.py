from ansi_code import get_error

# Types definitions
Cell = dict[str, bool]
Grid = list[list[str]]
Point = tuple[int, int]

# Directions Constants
WALL_BITS: dict[str, int] = {
    "north": 1,
    "east": 2,
    "south": 4,
    "west": 8,
}

OFFSETS: dict[str, Point] = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}

OPPOSITE: dict[str, str] = {
    "north": "south",
    "east": "west",
    "south": "north",
    "west": "east",
}

AROUND: tuple[Point, ...] = tuple(
    (dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1))

NEIGHBORS: tuple[Point, ...] = tuple(p for p in AROUND if p != (0, 0))


def to_grid(x: int, y: int) -> Point:
    """Convert maze coordinates to display coordinates."""
    return x * 2 + 1, y * 2 + 1


class Display:
    """
    Render a maze seed in the terminal.

    Attributes:
        filename: Seed filename.
        start: Start coordinates.
        end: End coordinates.
        motif_coords: Motif coordinates.
        hints: Parsed seed.
        grid: Display grid.
        path: Maze solution path.
    """

    def __init__(
        self,
        filename: str,
        start: Point | list[int],
        end: Point | list[int],
        motif_coords: list[Point],
        path: str,
        chars: dict[str, str]
    ) -> None:
        self.filename = filename
        self.start = start
        self.end = end
        self.motif_coords = motif_coords
        self.hints: list[list[Cell]] = []
        self.grid: Grid = []
        self.path = path
        self.chars = chars

    @property
    def width(self) -> int:
        """Width of the displayed grid."""
        if not self.hints:
            raise ValueError(get_error("Hints are empty"))

        return len(self.hints[0]) * 2 + 1

    @property
    def height(self) -> int:
        """Height of the displayed grid."""
        if not self.hints:
            raise ValueError(get_error("Hints are empty"))

        return len(self.hints) * 2 + 1

    @staticmethod
    def parse_hex(nb: str) -> Cell:
        """Convert a hexadecimal character into wall directions."""
        value = int(nb, 16)

        if not 0 <= value <= 15:
            raise ValueError(get_error(f"Invalid hexadecimal value: {nb}"))

        return {name: bool(value & bit) for name, bit in WALL_BITS.items()}

    def parse_file(self) -> None:
        """Read and parse the seed file."""
        self.hints = []

        with open(self.filename, "r") as f:
            for line_number, line in enumerate(f, start=1):
                if line.startswith("\n"):
                    break
                line = line.split("#", 1)[0].strip()

                if not line:
                    continue

                try:
                    row = [self.parse_hex(c) for c in line]
                except ValueError as error:
                    raise ValueError(
                        get_error(f"Invalid seed at line {line_number}"
                                  f": {error}")
                    ) from error

                if self.hints and len(row) != len(self.hints[0]):
                    raise ValueError(get_error("Inconsistent row width at line"
                                               f"{line_number}"))

                self.hints.append(row)

        if not self.hints:
            raise ValueError(get_error("The seed file is empty"))

    def validate_hints(self) -> None:
        """Check consistency between neighboring cells."""
        height = len(self.hints)
        width = len(self.hints[0])

        for y, row in enumerate(self.hints):
            for x, hint in enumerate(row):
                for direction, (dx, dy) in OFFSETS.items():
                    nx, ny = x + dx, y + dy

                    if not (0 <= nx < width and 0 <= ny < height):
                        continue

                    opposite = OPPOSITE[direction]

                    if hint[direction] != self.hints[ny][nx][opposite]:
                        raise ValueError(
                            get_error(f"Inconsistent walls between "
                                      f"({x}, {y}) and ({nx}, {ny}): "
                                      f"{direction} != {opposite}")
                        )

    def validate_point(self, point: Point | list[int]) -> None:
        """Check whether a point belongs to the maze."""
        x, y = point

        if not (0 <= y < len(self.hints) and 0 <= x < len(self.hints[y])):
            raise ValueError(get_error(f"Invalid point: {point}"))

    def is_surrounded_by_walls(self, x: int, y: int) -> bool:
        """Check if a cell is surrounded by walls."""
        for dx, dy in NEIGHBORS:
            nx, ny = x + dx, y + dy

            if not (0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[ny])):
                return False

            if self.grid[ny][nx] != self.chars["WALL_CHAR"]:
                return False

        return True

    def init_displayed_map(self) -> None:
        """Initialize the display grid and place start/end."""
        width, height = self.width, self.height

        self.grid = [
            [self.chars["BORDER_CHAR"]] * width
            if y in (0, height - 1)
            else [self.chars["BORDER_CHAR"]] + [" "] * (width - 2) +
                 [self.chars["BORDER_CHAR"]]
            for y in range(height)
        ]

        self.validate_point(self.start)
        self.validate_point(self.end)

        sx, sy = to_grid(*self.start)
        ex, ey = to_grid(*self.end)

        self.grid[sy][sx] = self.chars["START_CHAR"]
        self.grid[ey][ex] = self.chars["END_CHAR"]

    def fill_map(self) -> None:
        """Fill the grid with the parsed seed."""
        for y, row in enumerate(self.hints):
            for x, hint in enumerate(row):
                cx, cy = to_grid(x, y)

                # Sides
                for name, (dx, dy) in OFFSETS.items():
                    if hint[name]:
                        self.grid[cy + dy][cx + dx] = self.chars["WALL_CHAR"]

        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                for dx, dy in OFFSETS.values():
                    if not (0 <= y + dy < self.height and
                            0 <= x + dx < self.width):
                        continue
                    if self.grid[y + dy][x + dx] == self.chars["WALL_CHAR"]:
                        self.grid[y][x] = self.chars["WALL_CHAR"]
                        break

    def draw_path(self) -> None:
        """Draw the maze solution."""
        x, y = self.start
        new_x, new_y = to_grid(x, y)
        for char in self.path:
            for i in range(2):
                if char == 'S':
                    new_y += 1
                if char == 'N':
                    new_y -= 1
                if char == 'E':
                    new_x += 1
                if char == 'W':
                    new_x -= 1
                if self.grid[new_y][new_x] != self.chars["END_CHAR"]:
                    self.grid[new_y][new_x] = self.chars["PATH_CHAR"]

    def draw_motif(self) -> None:
        """Paint motif's walls in red."""
        for x, y in self.motif_coords:
            self.validate_point((x, y))

            cx, cy = to_grid(x, y)

            for dx, dy in AROUND:
                nx, ny = cx + dx, cy + dy

                if not (0 <= ny < len(self.grid) and
                        0 <= nx < len(self.grid[ny])):
                    continue

                if self.grid[ny][nx] in (
                    self.chars["BORDER_CHAR"],
                    self.chars["START_CHAR"],
                    self.chars["END_CHAR"],
                ):
                    continue

                self.grid[ny][nx] = self.chars["MOTIF_CHAR"]

    def get_map(self) -> list[str]:
        """Parse the seed, format and display the maze."""
        self.parse_file()
        self.validate_hints()
        self.init_displayed_map()
        self.fill_map()
        self.draw_motif()
        self.draw_path()

        return ["".join(row) for row in self.grid]
