from typedefs import Point

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
