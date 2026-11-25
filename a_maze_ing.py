from sys import argv, exit, stderr
from display import Display
from maze import MazeGenerator
from ansi_code import get_ansi, get_error
from time import sleep

class UsageError(Exception):
    def __init__(self):
        super().__init__(get_error("Usage: python3 a_maze_ing.py <config_file>"))

def display_menu():
    txt = get_ansi("\nNow that the maze just displays, you can choose further options:\n",
                   "bold", "underline", "magenta")
    txt += get_ansi("1 - Re-generate a new maze and display it\n",
                    "bright_magenta")
    txt += get_ansi("2 - Show/Hide a valid shortest path from the entrance to the exit\n",
                    "bright_magenta")
    txt += get_ansi("3 - Change maze wall colours\n",
                    "bright_magenta")
    txt += get_ansi("4 - Set specific colours to display the “42” pattern\n",
                    "bright_magenta")
    txt += get_ansi("0 - Stop the program properly\n",
                    "bright_magenta")
    txt += get_ansi("# add more if needed and wanted\n",
                    "red")
    print(txt)

def main(chars: dict[str, str]):
    motif = ["#.#.###", "#.#...#", "###.###", "..#.#..", "..#.###"]
    try:
        maze = MazeGenerator()
        maze.parse_config(argv[1])
        maze.grid_gen(motif)
        maze.check_entry_exit()
        # maze.entry_and_exit()
        motif_coords = maze.get_motif_coords
        maze.path_gen()
        if not maze.perfect_mode:
            maze.braid()
        maze.close_motif()
        maze.write_in_file()
        path_str = maze.write_eof()

        START_POS = maze.get_start_pos
        END_POS = maze.get_end_pos
        displayer = Display(maze.get_file, START_POS, END_POS,
                            motif_coords, path_str, chars)
        rowed_map = displayer.get_map()
        for row in rowed_map:
            print(row)
            sleep(0.05)

    except (OSError, ValueError) as e:
        print(get_error(f"Error: {e}"), file=stderr)
        exit(1)
    except UsageError as e:
        print(get_error(e), file=stderr)
        exit(1)


if __name__ == "__main__":
    default_chars = {
        "BORDER_CHAR": get_ansi("#", "black"),
        "WALL_CHAR": get_ansi("@", "black"),
        "MOTIF_CHAR": get_ansi("@", "red"),
        "PATH_CHAR": get_ansi("○", "blue"),
        "START_CHAR": get_ansi("S", "green"),
        "END_CHAR": get_ansi("E", "green")
    }
    try:
        if len(argv) != 2:
            raise UsageError()
        print(get_ansi("Welcome to our Amazing A-Maze-Ing!\n",
                       "blink",
                       "bold",
                       "green"))
        while (True):
            sleep(2)
            main(default_chars)
            sleep(1)
            display_menu()
            choice = int(input(get_ansi("Which choice have you made?",
                                        "blue")))
            if choice == 0:
                break
    except KeyboardInterrupt:
        print(get_error("\n\nUser manually stop the program."))
    except Exception as e:
        print(get_error(e))
