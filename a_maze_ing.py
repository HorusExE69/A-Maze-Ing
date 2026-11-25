
from sys import argv, exit, stderr
from display import Display
from maze import MazeGenerator
from ansi_code import get_ansi, get_error
from time import sleep


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


class UsageError(Exception):
    def __init__(self) -> None:
        super().__init__(
            get_error("Usage: python3 a_maze_ing.py <config_file>")
        )


# -------------------------
# Characters and colors
# -------------------------

def get_chars(
    is_path_visible: bool,
    wall_color: str,
    motif_color: str,
    path_color: str
) -> dict[str, str]:

    return {
        "BORDER_CHAR": get_ansi("#", wall_color),
        "WALL_CHAR": get_ansi("@", wall_color),
        "PATH_CHAR": get_ansi("○", path_color) if is_path_visible else " ",
        "MOTIF_CHAR": get_ansi("@", motif_color),
        "START_CHAR": get_ansi("S", "green"),
        "END_CHAR": get_ansi("E", "green")
    }


# -------------------------
# Maze generation
# -------------------------

def generate_maze(
    config_file: str,
    reset_seed: int
) -> tuple[MazeGenerator, list[tuple[int, int]], str]:

    motif = [
        "#.#.###",
        "#.#...#",
        "###.###",
        "..#.#..",
        "..#.###"
    ]

    maze = MazeGenerator()
    maze.parse_config(config_file)
    if reset_seed:
        maze.randomize_seed()
    maze.grid_gen(motif)
    maze.check_entry_exit()

    motif_coords = maze.get_motif_coords

    maze.path_gen()

    if not maze.perfect_mode:
        maze.braid()

    maze.close_motif()
    maze.write_in_file()

    path_str = maze.write_eof()

    return maze, motif_coords, path_str


# -------------------------
# Maze display
# -------------------------

def display_maze(
    maze: MazeGenerator,
    motif_coords: list[tuple[int, int]],
    path_str: str,
    chars: dict[str, str]
) -> None:

    displayer = Display(
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


# -------------------------
# Menu
# -------------------------

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

        else:
            print(get_error("Invalid choice. Please choose between 0 and 4."))


# -------------------------
# Other utilities
# -------------------------

def print_rerun() -> None:
    print(get_ansi("The program will rerun", "green", "bold"), end="")

    for _ in range(3):
        print(get_ansi(".", "green", "bold"), end="")

    print()


# -------------------------
# Main
# -------------------------

def main() -> None:
    if len(argv) != 2:
        raise UsageError()

    is_path_visible = True
    wall_color = "black"
    motif_color = "red"
    path_color = "blue"

    print(get_ansi(
        "Welcome to our Amazing A-Maze-Ing!\n",
        "bold", "green"
    ))

    # Generate the maze only once initially
    maze, motif_coords, path_str = generate_maze(argv[1], 0)

    while True:

        # Rebuild the display using the existing maze
        chars = get_chars(
            is_path_visible,
            wall_color,
            motif_color,
            path_color
        )

        display_maze(maze, motif_coords, path_str, chars)

        sleep(1)

        action, is_path_visible, wall_color, motif_color, path_color = parse_menu(
            is_path_visible,
            wall_color,
            motif_color,
            path_color
        )

        if action == "quit":
            break

        elif action == "regenerate":
            print_rerun()

            maze, motif_coords, path_str = generate_maze(argv[1], 1)


if __name__ == "__main__":
    try:
        main()

    except UsageError as e:
        print(get_error(e), file=stderr)
        exit(1)

    except (OSError, ValueError) as e:
        print(get_error(f"Error: {e}"), file=stderr)
        exit(1)

    except KeyboardInterrupt:
        print(get_error("\n\nUser manually stopped the program."))

    except Exception as e:
        print(get_error(e), file=stderr)
        exit(1)
