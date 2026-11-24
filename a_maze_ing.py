from sys import argv
from display import Display
from maze import MazeGenerator

motif = ["#.#.###",
         "#.#...#",
         "###.###",
         "..#.#..",
         "..#.###"
         ]

maze = MazeGenerator()
maze.parse_config(argv[1])
maze.grid_gen(motif)
# maze.entry_and_exit()
motif_coords = maze.get_motif_coords()
maze.path_gen()
maze.write_in_file()

START_POS = (0, 0)
END_POS = (maze.get_width() - 1, maze.get_height() - 1)
displayer = Display()
displayer.display_map(maze.get_file(), START_POS, END_POS, motif_coords)

maze.write_eof()
