from sys import argv, exit, stderr
from time import sleep
from ansi_code import get_ansi, get_error
from maze import generate_maze
from display.terminal_display import get_chars, display_maze
from display.terminal_menu import (
    parse_menu, print_rerun, clean, ask_custom_config
)


class UsageError(Exception):
    def __init__(self) -> None:
        super().__init__(
            get_error("Usage: python3 a_maze_ing.py <config_file>")
        )


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

        str_map = display_maze(maze, motif_coords, path_str, chars)

        sleep(1)

        (action, is_path_visible,
         wall_color, motif_color, path_color) = parse_menu(
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

        elif action == "write":
            filename = input(get_ansi(
                "In which file do you want to write the maze? ",
                "blue"))

            with open(filename, "w") as f:
                f.write(clean(str_map))

        elif action == "custom":
            overrides = ask_custom_config(maze)
            try:
                maze, motif_coords, path_str = generate_maze(
                    argv[1], 1, overrides
                )
                print_rerun()
            except (OSError, ValueError) as e:
                print(get_error(f"Error: {e}"), file=stderr)


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
