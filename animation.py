import os
import time
from mazegen.maze_generator import MazeGenerator


class Animation:
    """Handles maze generation animation."""

    def __init__(
        self,
        maze: MazeGenerator,
        entry: tuple[int, int],
        end: tuple[int, int],
        speed: float,
        wall_color: str
    ) -> None:
        """Initialize the Animation.

        Args:
            maze: MazeGenerator object
            entry: entry coordinates (x, y)
            end: exit coordinates (x, y)
            speed: delay in seconds between each step
            wall_color: ANSI color code for walls
        """
        self.maze = maze
        self.entry = entry
        self.end = end
        self.speed = speed
        self.wall_color = wall_color

    def animate(self) -> None:
        """Clear terminal, display current maze state and sleep."""
        try:
            os.system("clear")
            from a_maze_ing import display_maze
            display_maze(
                self.maze,
                self.entry,
                self.end,
                False,
                self.wall_color
            )
            time.sleep(self.speed)
        except (Exception, KeyboardInterrupt):
            pass
