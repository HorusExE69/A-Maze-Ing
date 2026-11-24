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
WALL_BITS: dict[str, int] = {"north": 1, "east": 2, "south": 4, "west": 8}
OFFSETS: dict[str, Point] = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}

# Positioning constants
CORNERS: tuple[tuple[str, str], ...] = (
    ("north", "east"),
    ("east", "south"),
    ("south", "west"),
    ("west", "north"),
)
AROUND: tuple[Point, ...] = tuple(
    (dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
)
NEIGHBORS: tuple[Point, ...] = tuple(p for p in AROUND if p != (0, 0))


def to_grid(x: int, y: int) -> Point:
    """
    Multiply each coordinate by 2 then add 1

    Args:
        x (int): x position of the cell
        y (int): y position of the cell

    Returns:
        Point: new coordinates
    """
    return x * 2 + 1, y * 2 + 1


class Display:
    """
    Render a maze seed in the terminal.

    Attributes:
        filename (str): The name of the file which contains the seed
        start (Point): start coordinates of the maze
        end (Point): end coordinates of the maze
        motif_coords (list[Point]): Coordinates of the motif
        hints (list[list[Cell]]): available directions (parsed seed)
        grid (Grid): the grid to display
    """

    def __init__(
        self,
        filename: str,
        start: Point,
        end: Point,
        motif_coords: list[Point],
    ) -> None:
        self.filename = filename
        self.start = start
        self.end = end
        self.motif_coords = motif_coords
        self.hints: list[list[Cell]] = []
        self.grid: Grid = []

    @property
    def width(self) -> int:
        """Width of the displayed grid (needs parsed hints)."""
        return len(self.hints[0]) * 2 + 1

    @property
    def height(self) -> int:
        """Height of the displayed grid (needs parsed hints)."""
        return len(self.hints) * 2 + 1

    @staticmethod
    def parse_hex(nb: str) -> Cell:
        """
        Converts an hexadecimal string to int then create a dict with
        available directions

        Args:
            nb (str): the hex to parse

        Returns:
            Cell: available directions
        """
        value = int(nb, 16)
        return {name: bool(value & bit) for name, bit in WALL_BITS.items()}

    def parse_file(self) -> None:
        """
        Read the seed file and parse each char to fill self.hints with all
        available directions
        """
        self.hints = []
        with open(self.filename, "r") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
                if line:
                    self.hints.append([self.parse_hex(c) for c in line])

    def is_surrounded_by_walls(self, x: int, y: int) -> bool:
        """
        Check if the cell of the grid is surrounded by walls

        Args:
            x (int): the x coordinate of the cell
            y (int): the y coordinate of the cell

        Returns:
            bool: return True if the cell is surrounded by walls
        """
        return all(
            self.grid[y + dy][x + dx] == WALL_CHAR for dx, dy in NEIGHBORS
        )

    def init_displayed_map(self) -> None:
        """
        Initialize self.grid with the size of the seed
        then add start and end positions
        """
        width, height = self.width, self.height
        self.grid = [
            [WALL_CHAR] * width
            if y in (0, height - 1)
            else [WALL_CHAR] + [" "] * (width - 2) + [WALL_CHAR]
            for y in range(height)
        ]
        sx, sy = to_grid(*self.start)
        ex, ey = to_grid(*self.end)
        self.grid[sy][sx] = START_CHAR
        self.grid[ey][ex] = END_CHAR

    def clean_map(self) -> None:
        """Replace cells by walls if they're surrounded by walls"""
        for y in range(1, len(self.grid) - 1):
            for x in range(1, len(self.grid[y]) - 1):
                if self.grid[y][x] in (WALL_CHAR, START_CHAR, END_CHAR):
                    continue
                if self.is_surrounded_by_walls(x, y):
                    self.grid[y][x] = WALL_CHAR

    def fill_map(self) -> None:
        """Fill the grid with the seed parsed"""
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

    def draw_motif(self) -> None:
        """Paint motif's walls in red"""
        for x, y in self.motif_coords:
            cx, cy = to_grid(x, y)
            for dx, dy in AROUND:
                self.grid[cy + dy][cx + dx] = MOTIF_CHAR

    def display_map(self) -> None:
        """Parse the seed, format the grid then display it"""
        self.parse_file()
        self.init_displayed_map()
        self.fill_map()
        self.clean_map()
        self.draw_motif()
        for row in self.grid:
            print("".join(row))
