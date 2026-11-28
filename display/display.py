from ansi_code import get_error
from typedefs import Cell, Point
from .constants import WALL_BITS, OFFSETS, OPPOSITE


class Display:
    """
    Base class of the maze displays: reads and validates a maze seed.

    Attributes:
        filename: Seed filename.
        start: Start coordinates.
        end: End coordinates.
        motif_coords: Motif coordinates.
        hints: Parsed seed.
        path: Maze solution path.
    """

    def __init__(
        self,
        filename: str,
        start: Point | list[int],
        end: Point | list[int],
        motif_coords: list[Point],
        path: str
    ) -> None:
        self.filename = filename
        self.start = start
        self.end = end
        self.motif_coords = motif_coords
        self.hints: list[list[Cell]] = []
        self.path = path

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
