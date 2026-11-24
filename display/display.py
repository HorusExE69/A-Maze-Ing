from typing import TextIO
from ansi_code import get_ansi

# Char constants
WALL_CHAR = get_ansi('@', "black")
MOTIF_CHAR = get_ansi('@', "red")
START_CHAR = get_ansi('S', "green")
END_CHAR = get_ansi('E', "green")

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

    def parse_file(self, file: TextIO) -> list[list[Cell]]:
        """
        Read a file and parse each char to create a list with all
        available direction in the seed

        Args:
            file (TextIO): The file to read

        Returns:
            list[list[Cell]]: The list of all available directions
        """
        data: list[list[Cell]] = []
        for line in file:
            line = line.split("#", 1)[0].strip()
            if line:
                data.append([self.parse_hex(char) for char in line])
        return data

    @staticmethod
    def is_surrounded_by_walls(grid: Grid, x: int, y: int) -> bool:
        """
        Check if the current cell is surrounded by walls

        Args:
            grid (Grid): the complete grid
            y (int): the y coordinate of the current cell
            x (int): the x coordinate of the current cell

        Returns:
            bool: return True if the cell is surrounded by walls
        """
        return all(grid[y + dy][x + dx] == WALL_CHAR for dx, dy in NEIGHBORS)

    @staticmethod
    def init_displayed_map(width: int, height: int,
                           start: Point, end: Point) -> Grid:
        grid: Grid = [
            [WALL_CHAR] * width if y in (0, height - 1)
            else [WALL_CHAR] + [" "] * (width - 2) + [WALL_CHAR]
            for y in range(height)
        ]
        sx, sy = to_grid(*start)
        ex, ey = to_grid(*end)
        grid[sy][sx] = START_CHAR
        grid[ey][ex] = END_CHAR
        return grid

    def clean_map(self, grid: Grid) -> Grid:
        for y in range(1, len(grid) - 1):
            for x in range(1, len(grid[y]) - 1):
                if grid[y][x] in (WALL_CHAR, START_CHAR, END_CHAR):
                    continue
                if self.is_surrounded_by_walls(grid, x, y):
                    grid[y][x] = WALL_CHAR
        return grid

    @staticmethod
    def fill_map(grid: Grid, hints: list[list[Cell]]) -> Grid:
        for y, row in enumerate(hints):
            for x, hint in enumerate(row):
                cx, cy = to_grid(x, y)

                # Côtés
                for name, (dx, dy) in OFFSETS.items():
                    if hint[name]:
                        grid[cy + dy][cx + dx] = WALL_CHAR

                # Diagonales
                for a, b in CORNERS:
                    if hint[a] and hint[b]:
                        dx = OFFSETS[a][0] + OFFSETS[b][0]
                        dy = OFFSETS[a][1] + OFFSETS[b][1]
                        grid[cy + dy][cx + dx] = WALL_CHAR
        return grid

    @staticmethod
    def draw_motif(grid: Grid, motif_coords: list[Point]) -> Grid:
        for x, y in motif_coords:
            cx, cy = to_grid(x, y)
            for dx, dy in AROUND:
                grid[cy + dy][cx + dx] = MOTIF_CHAR
        return grid

    def display_map(self, filename: str, start: Point, end: Point,
                    motif_coords: list[Point]) -> None:
        with open(filename, "r") as f:
            hints = self.parse_file(f)

        height = len(hints) * 2 + 1
        width = len(hints[0]) * 2 + 1
        grid = self.init_displayed_map(width, height, start, end)
        grid = self.fill_map(grid, hints)
        grid = self.clean_map(grid)
        grid = self.draw_motif(grid, motif_coords)
        for row in grid:
            print("".join(row))
