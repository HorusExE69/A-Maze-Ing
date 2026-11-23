from typing import IO
from constants import ANSI_CODE


def parse_hex(nb: str) -> dict[str, bool]:
    txt = bin(int(nb, 16))[2:]
    while (len(txt)) < 4:
        txt = "0" + txt
    wall_positions = {
        "north": bool(int(txt[0])),
        "east": bool(int(txt[1])),
        "south": bool(int(txt[2])),
        "west": bool(int(txt[3])),
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


def init_displayed_map(width, height) -> list[list[str]]:
    displayed_map: list[list[str]] = []
    for i in range(height):
        if i == 0 or i == height - 1:
            displayed_map.append(["#" for _ in range(width)])
        else:
            displayed_map.append(["#"] +
                                 [" " for _ in range(width - 2)] +
                                 ["#"])
    return displayed_map


def fill_map(displayed_map: list[list[str]], hints: list[list[dict[str, bool]]]):
    return displayed_map


def display_map(filename: str) -> None:
    with open(filename, "r") as f:
        hints = parse_file(f)

    height = len(hints) * 2 + 1
    width = len(hints[0]) * 2 + 1
    displayed_map = init_displayed_map(width, height)
    displayed_map = fill_map(displayed_map, hints)
    for row in displayed_map:
        print(''.join(row))


if __name__ == "__main__":
    display_map("test.txt")
