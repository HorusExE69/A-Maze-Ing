from sys import argv, exit, stderr
from display import Display
from maze import MazeGenerator


class UsageError(Exception):
    def __init__(self):
        super().__init__("Usage: python3 a_maze_ing.py <config_file>")


motif = ["#.#.###", "#.#...#", "###.###", "..#.#..", "..#.###"]
try:
    if len(argv) != 2:
        raise UsageError()
    maze = MazeGenerator()
    maze.parse_config(argv[1])
    maze.grid_gen(motif)
    maze.check_entry_exit()
    # maze.entry_and_exit()
    motif_coords = maze.get_motif_coords()
    maze.path_gen()
    if not maze.perfect_mode:
        maze.braid()
    maze.close_motif()
    maze.write_in_file()
    path_str = maze.write_eof()

    START_POS = (0, 0)
    END_POS = (maze.get_width() - 1, maze.get_height() - 1)
    displayer = Display(maze.get_file,
                        START_POS,
                        END_POS,
                        motif_coords,
                        path_str)
    displayer.display_map()

except (OSError, ValueError) as e:
    print(f"Error: {e}", file=stderr)
    exit(1)
except UsageError as e:
    print(e, file=stderr)
    exit(1)
