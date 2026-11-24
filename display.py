from typing import IO
from ansi_code import get_ansi
from constants import WALL_CHAR


def is_surrounded_by_walls(displayed_map, x, y):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue

            if displayed_map[y + dy][x + dx] != WALL_CHAR:
                return False

    return True


def parse_hex(nb: str) -> dict[str, bool]:
    value = int(nb, 16)

    wall_positions = {
        "north": bool(value & 1),
        "east": bool(value & 2),
        "south": bool(value & 4),
        "west": bool(value & 8),
    }

    return wall_positions


def parse_file(file: IO) -> list[list[dict[str, bool]]]:
    data: list[list[dict[str, bool]]] = []
    for line in file:
        data_line: list[dict[str, bool]] = []
        for char in line:
            if char == '#':
                break
            if (char != '\n'):
                data_line.append(parse_hex(char))
        if (len(data_line) > 0):
            data.append(data_line)
    return data


def init_displayed_map(width, height, start, end) -> list[list[str]]:
    displayed_map: list[list[str]] = []
    for i in range(height):
        if i == 0 or i == height - 1:
            displayed_map.append([WALL_CHAR for _ in range(width)])
        else:
            displayed_map.append([WALL_CHAR] +
                                 [' ' for _ in range(width - 2)] +
                                 [WALL_CHAR])
    displayed_map[start[1] * 2 + 1][start[0] * 2 + 1] = get_ansi('S', "green")
    displayed_map[end[1] * 2 + 1][end[0] * 2 + 1] = get_ansi('E', "green")
    return displayed_map


def clean_map(displayed_map: list[list[str]]) -> list[list[str]]:
    for y in range(1, len(displayed_map) - 1):
        for x in range(1, len(displayed_map[y]) - 1):
            if displayed_map[y][x] == WALL_CHAR:
                continue
            if displayed_map[y][x] in (get_ansi('S', "green"),
                                       get_ansi('E', "green")):
                continue
            if is_surrounded_by_walls(displayed_map, x, y):
                displayed_map[y][x] = WALL_CHAR
    return displayed_map


def fill_map(displayed_map: list[list[str]],
             hints: list[list[dict[str, bool]]]):
    for y in range(len(hints)):
        for x in range(len(hints[y])):
            current_pos = {"x": x * 2 + 1, "y": y * 2 + 1}
            current_hint = hints[y][x]

            # Sides
            if (current_hint["north"]):
                displayed_map[
                    current_pos["y"] - 1][
                    current_pos["x"]] = WALL_CHAR
            if (current_hint["east"]):
                displayed_map[
                    current_pos["y"]][
                    current_pos["x"] + 1] = WALL_CHAR
            if (current_hint["south"]):
                displayed_map[
                    current_pos["y"] + 1][
                    current_pos["x"]] = WALL_CHAR
            if (current_hint["west"]):
                displayed_map[
                    current_pos["y"]][
                    current_pos["x"] - 1] = WALL_CHAR

            # Diagonales
            if (current_hint["north"] and current_hint["east"]):
                displayed_map[
                    current_pos["y"] - 1][
                    current_pos["x"] + 1] = WALL_CHAR
            if (current_hint["east"] and current_hint["south"]):
                displayed_map[
                    current_pos["y"] + 1][
                    current_pos["x"] + 1] = WALL_CHAR
            if (current_hint["south"] and current_hint["west"]):
                displayed_map[
                    current_pos["y"] + 1][
                    current_pos["x"] - 1] = WALL_CHAR
            if (current_hint["west"] and current_hint["north"]):
                displayed_map[
                    current_pos["y"] - 1][
                    current_pos["x"] - 1] = WALL_CHAR
    return clean_map(displayed_map)


def display_map(filename: str,
                start: tuple[int, int],
                end: tuple[int, int]) -> None:
    with open(filename, "r") as f:
        hints = parse_file(f)

    height = len(hints) * 2 + 1
    width = len(hints[0]) * 2 + 1
    displayed_map = init_displayed_map(width, height, start, end)
    displayed_map = fill_map(displayed_map, hints)
    for row in displayed_map:
        print(''.join(row))


if __name__ == "__main__":
    display_map("test.txt", (0, 0), (9, 9))
