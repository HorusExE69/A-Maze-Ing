from time import sleep
from ansi_code import get_ansi
from maze import MazeGenerator
from typedefs import Grid, Point
from .constants import OFFSETS, AROUND, NEIGHBORS, to_grid
from .display import Display


def get_chars(
    is_path_visible: bool,
    wall_color: str,
    motif_color: str,
    path_color: str
) -> dict[str, str]:

    return {
        "BORDER_CHAR": get_ansi("#", wall_color),
        "WALL_CHAR": get_ansi("@", wall_color),
        "SPACE_CHAR": get_ansi(" "),
        "PATH_CHAR": get_ansi("○", path_color) if is_path_visible else " ",
        "MOTIF_CHAR": get_ansi("@", motif_color),
        "START_CHAR": get_ansi("S", "green"),
        "END_CHAR": get_ansi("E", "green")
    }


class TerminalDisplay(Display):
    """
    Render a maze seed in the terminal.

    Attributes:
        grid: Display grid.
        chars: Characters (with ANSI colors) used to draw the maze.
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
        super().__init__(filename, start, end, motif_coords, path)
        self.grid: Grid = []
        self.chars = chars

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
            else [self.chars["BORDER_CHAR"]] +
                 [self.chars["SPACE_CHAR"]] * (width - 2) +
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


def display_maze(
    maze: MazeGenerator,
    motif_coords: list[tuple[int, int]],
    path_str: str,
    chars: dict[str, str]
) -> list[str]:

    displayer = TerminalDisplay(
        maze.get_file,
        maze.get_start_pos,
        maze.get_end_pos,
        motif_coords,
        path_str,
        chars
    )

    rowed_map = displayer.get_map()

    for row in rowed_map:
        print(row)
        sleep(0.05)

    return (rowed_map)
