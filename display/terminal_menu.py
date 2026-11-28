from ansi_code import get_ansi, get_error
from maze import MazeGenerator


COLORS: list[str] = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white"
]


def display_menu(
    is_path_visible: bool,
    wall_color: str,
    motif_color: str,
    path_color: str
) -> None:

    txt = get_ansi(
        "\nNow that the maze just displays, you can choose further options:\n",
        "bold", "underline", "magenta"
    )

    txt += get_ansi(
        "1 - Re-generate a new maze and display it\n",
        "bright_magenta"
    )

    txt += get_ansi(
        "2 - Show/Hide a valid shortest path from the entrance to the exit\n",
        "bright_magenta"
    )

    txt += get_ansi(
        f"3 - Change maze wall colours (current: {wall_color})\n",
        "bright_magenta"
    )

    txt += get_ansi(
        f"4 - Change the 42 pattern colour (current: {motif_color})\n",
        "bright_magenta"
    )

    txt += get_ansi(
        f"5 - Change the path colour (current: {path_color})\n",
        "bright_magenta"
    )

    txt += get_ansi(
        "6 - Re-generate a maze with a custom configuration\n",
        "bright_magenta"
    )

    txt += get_ansi(
        "7 - Write the maze in a file\n",
        "bright_magenta"
    )

    txt += get_ansi(
        "0 - Stop the program properly\n",
        "bright_magenta"
    )

    print(txt)


def choose_color() -> str:
    print(get_ansi("\nAvailable colors:", "bold", "cyan"))

    for index, color in enumerate(COLORS, start=1):
        print(get_ansi(f"{index} - {color}", color))

    while True:
        choice = input(get_ansi("\nChoose a color: ", "blue")).strip()

        if choice.isdigit():
            index = int(choice) - 1

            if 0 <= index < len(COLORS):
                return COLORS[index]

        if choice in COLORS:
            return choice

        print(get_error("Invalid color. Try again."))


def ask_custom_config(maze: MazeGenerator) -> dict[str, str]:
    start = maze.get_start_pos
    fields = [
        ("WIDTH", "Width", str(maze.get_width)),
        ("HEIGHT", "Height", str(maze.get_height)),
        ("ENTRY", "Entry (x,y)", f"{start[1]},{start[0]}"),
        ("EXIT", "Exit (x,y)", "Width - 1, Height - 1"),
        ("PERFECT", "Perfect (True/False)", str(maze.perfect_mode)),
        ("SEED", "Seed (empty = random)", ""),
    ]

    print(get_ansi("Custom config (empty = keep current value)",
                   "bold", "cyan"))
    overrides: dict[str, str] = {}
    for key, label, current in fields:
        value = input(get_ansi(f"{label} [{current}]: ", "blue")).strip()
        if value:
            overrides[key] = value
    return overrides


def parse_menu(
    is_path_visible: bool,
    wall_color: str,
    motif_color: str,
    path_color: str
) -> tuple[str, bool, str, str, str]:

    while True:
        display_menu(is_path_visible, wall_color, motif_color, path_color)

        choice = input(
            get_ansi("Which choice have you made?\t\t", "blue")
        ).strip()

        print()

        if choice == "0":
            print(get_ansi(
                "Thanks for using our program! See you soon!",
                "green", "bold"
            ))

            return ("quit", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "1":
            return ("regenerate", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "2":
            is_path_visible = not is_path_visible

            print(get_ansi(
                f"The path is now "
                f"{'visible' if is_path_visible else 'invisible'}",
                "green", "bold"
            ))

            return ("redraw", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "3":
            wall_color = choose_color()

            print(get_ansi(
                f"Wall color changed to {wall_color}",
                "green", "bold"
            ))

            return ("redraw", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "4":
            motif_color = choose_color()

            print(get_ansi(
                f"42 pattern color changed to {motif_color}",
                "green", "bold"
            ))

            return ("redraw", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "5":
            path_color = choose_color()

            print(get_ansi(
                f"Path color changed to {path_color}",
                "green", "bold"
            ))

            return ("redraw", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "6":
            return ("custom", is_path_visible,
                    wall_color, motif_color, path_color)

        elif choice == "7":
            return ("write", is_path_visible,
                    wall_color, motif_color, path_color)

        else:
            print(get_error("Invalid choice. Please choose between 0 and 7."))


def print_rerun() -> None:
    print(get_ansi("The program will rerun", "green", "bold"), end="")

    for _ in range(3):
        print(get_ansi(".", "green", "bold"), end="")

    print()


def clean(str_map: list[str]) -> str:
    clean_map: list[str] = []
    for row in str_map:
        clean_row = ""
        splitted_row = row.split(get_ansi(""))
        for char in splitted_row:
            if "@" in char:
                clean_row += "@"
            if "#" in char:
                clean_row += "#"
            if "○" in char:
                clean_row += "○"
            if " " in char:
                clean_row += " "
            if "S" in char:
                clean_row += "S"
            if "E" in char:
                clean_row += "E"
        clean_map.append(clean_row)
    return '\n'.join(clean_map)
