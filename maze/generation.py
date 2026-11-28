from .MazeGenerator import MazeGenerator


def generate_maze(
    config_file: str,
    reset_seed: int,
    overrides: dict[str, str] | None = None
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
    if overrides:
        maze.custom_config(**overrides)
    if reset_seed and not (overrides and "SEED" in overrides):
        maze.randomize_seed()
    maze.grid_gen(motif)
    maze.check_entry_exit()

    motif_coords = maze.get_motif_coords

    maze.path_gen()

    if not maze.perfect_mode:
        maze.braid()
        maze.solve()

    maze.close_motif()
    maze.write_in_file()

    path_str = maze.write_eof()

    return maze, motif_coords, path_str
