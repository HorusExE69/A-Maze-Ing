from mlx import Mlx
from typedefs import Point
from .display import Display


class MlxDisplay(Display):
    """
    Render a maze seed in a MiniLibX window.

    Attributes:
        mlx: MiniLibX binding.
        mlx_ptr: MiniLibX connection pointer.
        win: Window pointer.
        win_width: Window width in pixels.
        win_height: Window height in pixels.
    """

    def __init__(
        self,
        filename: str,
        start: Point | list[int],
        end: Point | list[int],
        motif_coords: list[Point],
        path: str,
        title: str = "A-Maze-Ing"
    ) -> None:
        super().__init__(filename, start, end, motif_coords, path)
        self.title = title
        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise ValueError("Unable to initialize MiniLibX")
        ret, screen_w, screen_h = self.mlx.mlx_get_screen_size(self.mlx_ptr)
        if ret != 0:
            raise ValueError("Unable to read the screen size")
        self.win_width = int(screen_w * 0.8)
        self.win_height = int(screen_h * 0.8)
        self.win = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_width, self.win_height, self.title
        )
        # 33 = ClientMessage (window close button)
        self.mlx.mlx_hook(self.win, 33, 0, self.close, None)

    def close(self, param: object = None) -> None:
        """Leave the MiniLibX loop (window close button)."""
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        """Start the MiniLibX loop, then free the resources."""
        self.mlx.mlx_loop(self.mlx_ptr)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win)
        self.mlx.mlx_release(self.mlx_ptr)
