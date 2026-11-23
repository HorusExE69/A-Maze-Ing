from typing import IO


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


def init_displayed_map(width, height) -> list[list[None | str]]:
    displayed_map: list[list[None | str]] = []
    for _ in range(width):
        displayed_map.append([None for _ in range(height)])
    return displayed_map


def main() -> None:
    with open("test.txt", "r") as f:
        parsed_file = parse_file(f)
    for line in parsed_file:
        for dico in line:
            print(dico)
        print()


if __name__ == "__main__":
    main()
