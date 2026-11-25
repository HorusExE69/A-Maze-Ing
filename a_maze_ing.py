
from sys import argv, exit, stderr
from display import Display
from maze import MazeGenerator
from ansi_code import get_ansi, get_error
from time import sleep


COLORS = [
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
    def __init__(self):
        super().__init__(
            get_error("Usage: python3 a_maze_ing.py <config_file>")
        )


# -------------------------
# Characters and colors
# -------------------------

def get_chars(
    is_path_visible: bool,
    wall_color: str,
    motif_color: str
) -> dict[str, str]:

    return {
        "BORDER_CHAR": get_ansi("#", wall_color),
        "WALL_CHAR": get_ansi("@", wall_color),
        "PATH_CHAR": get_ansi("○", "blue") if is_path_visible else " ",
        "MOTIF_CHAR": get_ansi("@", motif_color),
        "START_CHAR": get_ansi("S", "green"),
        "END_CHAR": get_ansi("E", "green")
    }


# -------------------------
# Maze generation
# -------------------------

def generate_maze(config_file: str):
    motif = [
        "#.#.###",
        "#.#...#",
        "###.###",
        "..#.#..",
        "..#.###"
    ]

    maze = MazeGenerator()
    maze.parse_config(config_file)
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

def display_maze(maze, motif_coords, path_str, chars):
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
    motif_color: str
):
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
    motif_color: str
) -> tuple[str, bool, str, str]:

    while True:
        display_menu(is_path_visible, wall_color, motif_color)

        choice = input(
            get_ansi("Which choice have you made?\t\t", "blue")
        ).strip()

        print()

        if choice == "0":
            print(get_ansi(
                "Thanks for using our program! See you soon!",
                "green", "bold"
            ))

            return "quit", is_path_visible, wall_color, motif_color

        elif choice == "1":
            return "regenerate", is_path_visible, wall_color, motif_color

        elif choice == "2":
            is_path_visible = not is_path_visible

            print(get_ansi(
                f"The path is now "
                f"{'visible' if is_path_visible else 'invisible'}",
                "green", "bold"
            ))

            return "redraw", is_path_visible, wall_color, motif_color

        elif choice == "3":
            wall_color = choose_color()

            print(get_ansi(
                f"Wall color changed to {wall_color}",
                "green", "bold"
            ))

            return "redraw", is_path_visible, wall_color, motif_color

        elif choice == "4":
            motif_color = choose_color()

            print(get_ansi(
                f"42 pattern color changed to {motif_color}",
                "green", "bold"
            ))

            return "redraw", is_path_visible, wall_color, motif_color

        else:
            print(get_error("Invalid choice. Please choose between 0 and 4."))


# -------------------------
# Other utilities
# -------------------------

def print_rerun():
    print(get_ansi("The program will rerun", "green", "bold"), end="")

    for _ in range(3):
        print(get_ansi(".", "green", "bold"), end="")

    print()


# -------------------------
# Main
# -------------------------

def main():
    if len(argv) != 2:
        raise UsageError()

    is_path_visible = True
    wall_color = "black"
    motif_color = "red"

    print(get_ansi(
        "Welcome to our Amazing A-Maze-Ing!\n",
        "bold", "green"
    ))

    # Generate the maze only once initially
    maze, motif_coords, path_str = generate_maze(argv[1])

    while True:

        # Rebuild the display using the existing maze
        chars = get_chars(
            is_path_visible,
            wall_color,
            motif_color
        )

        display_maze(maze, motif_coords, path_str, chars)

        sleep(1)

        action, is_path_visible, wall_color, motif_color = parse_menu(
            is_path_visible,
            wall_color,
            motif_color
        )

        if action == "quit":
            break

        elif action == "regenerate":
            print_rerun()

            maze, motif_coords, path_str = generate_maze(argv[1])


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
