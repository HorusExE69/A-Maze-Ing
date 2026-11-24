from ansi_code import get_ansi

# Char constants
WALL_CHAR = get_ansi("@", "black")
MOTIF_CHAR = get_ansi("@", "red")
START_CHAR = get_ansi("S", "green")
END_CHAR = get_ansi("E", "green")

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

# Positioning constants
CORNERS: tuple[tuple[str, str], ...] = (
    ("north", "east"),
    ("east", "south"),
    ("south", "west"),
    ("west", "north"),
)

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
    ) -> None:
        self.filename = filename
        self.start = start
        self.end = end
        self.motif_coords = motif_coords
        self.hints: list[list[Cell]] = []
        self.grid: Grid = []
        self.path = path

    @property
    def width(self) -> int:
        """Width of the displayed grid."""
        if not self.hints:
            raise ValueError("Hints are empty")

        return len(self.hints[0]) * 2 + 1

    @property
    def height(self) -> int:
        """Height of the displayed grid."""
        if not self.hints:
            raise ValueError("Hints are empty")

        return len(self.hints) * 2 + 1

    @staticmethod
    def parse_hex(nb: str) -> Cell:
        """Convert a hexadecimal character into wall directions."""
        value = int(nb, 16)

        if not 0 <= value <= 15:
            raise ValueError(f"Invalid hexadecimal value: {nb}")

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
                        f"Invalid seed at line {line_number}: {error}"
                    ) from error

                if self.hints and len(row) != len(self.hints[0]):
                    raise ValueError("Inconsistent row width at line",
                                     line_number)

                self.hints.append(row)

        if not self.hints:
            raise ValueError("The seed file is empty")

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
                            f"Inconsistent walls between "
                            f"({x}, {y}) and ({nx}, {ny}): "
                            f"{direction} != {opposite}"
                        )

    def validate_point(self, point: Point | list[int]) -> None:
        """Check whether a point belongs to the maze."""
        x, y = point

        if not (0 <= y < len(self.hints) and 0 <= x < len(self.hints[y])):
            raise ValueError(f"Invalid point: {point}")

    def is_surrounded_by_walls(self, x: int, y: int) -> bool:
        """Check if a cell is surrounded by walls."""
        for dx, dy in NEIGHBORS:
            nx, ny = x + dx, y + dy

            if not (0 <= ny < len(self.grid) and 0 <= nx < len(self.grid[ny])):
                return False

            if self.grid[ny][nx] != WALL_CHAR:
                return False

        return True

    def init_displayed_map(self) -> None:
        """Initialize the display grid and place start/end."""
        width, height = self.width, self.height

        self.grid = [
            [WALL_CHAR] * width
            if y in (0, height - 1)
            else [WALL_CHAR] + [" "] * (width - 2) + [WALL_CHAR]
            for y in range(height)
        ]

        self.validate_point(self.start)
        self.validate_point(self.end)

        sx, sy = to_grid(*self.start)
        ex, ey = to_grid(*self.end)

        self.grid[sy][sx] = START_CHAR
        self.grid[ey][ex] = END_CHAR

    def clean_map(self) -> None:
        """Replace cells surrounded by walls."""
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[y]) - 1):
                if self.grid[y][x] in (
                    WALL_CHAR,
                    START_CHAR,
                    END_CHAR,
                ):
                    continue

                if self.is_surrounded_by_walls(x, y):
                    self.grid[y][x] = WALL_CHAR

    def fill_map(self) -> None:
        """Fill the grid with the parsed seed."""
        for y, row in enumerate(self.hints):
            for x, hint in enumerate(row):
                cx, cy = to_grid(x, y)

                # Sides
                for name, (dx, dy) in OFFSETS.items():
                    if hint[name]:
                        self.grid[cy + dy][cx + dx] = WALL_CHAR

                # Diagonals
                for a, b in CORNERS:
                    if hint[a] and hint[b]:
                        dx = OFFSETS[a][0] + OFFSETS[b][0]
                        dy = OFFSETS[a][1] + OFFSETS[b][1]

                        self.grid[cy + dy][cx + dx] = WALL_CHAR

    def draw_path(self) -> None:
        """Draw the maze solution."""
        pass

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
                    START_CHAR,
                    END_CHAR,
                ):
                    continue

                self.grid[ny][nx] = MOTIF_CHAR

    def display_map(self) -> None:
        """Parse the seed, format and display the maze."""
        self.parse_file()
        self.validate_hints()
        self.init_displayed_map()
        self.fill_map()
        self.clean_map()
        self.draw_path()
        self.draw_motif()

        for row in self.grid:
            print("".join(row))
