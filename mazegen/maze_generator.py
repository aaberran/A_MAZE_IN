import random
from collections import deque
import sys


class MazeGenerator:
    """A maze generator using recursive backtracker algorithm."""
    def __init__(self, width: int, height: int,
                 seed: int, p_flag: bool) -> None:
        """Initialize the MazeGenerator.
        Args:
            width: number of cells horizontally
            height: number of cells vertically
            seed: random seed for reproducibility
            p_flag: if True generate a perfect maze
        """
        self.width = width
        self.height = height
        self.seed = seed
        self.p_flag = p_flag
        self.solution: list[str] = []
        self.grid: list[list[int]] = [
            [0xF] * self.width for _ in range(self.height)
            ]
        random.seed(self.seed)

    def generate(self, entry: tuple[int, int], end: tuple[int, int]) -> None:
        """Generate the maze using recursive backtracker algorithm.

        Carves passages through the grid by removing walls between
        cells until every cell has been visited.

        Returns:
            None
        """
        if self.width < 0 or self.height:
            print("Error")
            sys.exit(1)
        logo = self.draw_42(entry, end) or set()
        stack = [(0, 0)]
        is_visited: list[list[bool]] = [
            [False] * self.width for _ in range(self.height)
            ]
        is_visited[0][0] = True
        while stack:
            sides = []
            x, y = stack[-1]
            if (x > 0
                    and not is_visited[y][x-1]
                    and (x-1, y) not in logo):
                sides.append((x-1, y))
            if (x < self.width - 1
                    and not is_visited[y][x+1]
                    and (x+1, y) not in logo):
                sides.append((x+1, y))
            if y > 0 and not is_visited[y-1][x] and (x, y-1) not in logo:
                sides.append((x, y-1))
            if (y < self.height - 1
                    and not is_visited[y+1][x]
                    and (x, y+1) not in logo):
                sides.append((x, y+1))
            if sides:
                rx, ry = random.choice(sides)
                if rx > x:
                    self.grid[y][x] &= ~0x2
                    self.grid[ry][rx] &= ~0x8
                if rx < x:
                    self.grid[y][x] &= ~0x8
                    self.grid[ry][rx] &= ~0x2
                if ry > y:
                    self.grid[y][x] &= ~0x4
                    self.grid[ry][rx] &= ~0x1
                if ry < y:
                    self.grid[y][x] &= ~0x1
                    self.grid[ry][rx] &= ~0x4
                is_visited[ry][rx] = True
                stack.append((rx, ry))
            else:
                stack.pop()
        for x, y in logo:
            self.grid[y][x] = 0xF

        if not self.p_flag:
            times: int = int(self.height * self.width * 0.15)
            while times:
                rx: int = random.randint(0, self.width - 1)
                ry: int = random.randint(0, self.height - 1)
                sides: list[str] = ['N', 'E', 'S', 'W']
                side: str = random.choice(sides)
                if (ry > 0 and side == 'N'
                        and (rx, ry-1) not in logo
                        and (rx, ry) not in logo):
                    self.grid[ry][rx] &= ~0x1
                    self.grid[ry-1][rx] &= ~0x4
                elif (rx < self.width - 1
                        and side == 'E'
                        and (rx+1, ry) not in logo
                        and (rx, ry) not in logo):
                    self.grid[ry][rx] &= ~0x2
                    self.grid[ry][rx+1] &= ~0x8
                elif (ry < self.height - 1
                      and side == 'S' and (rx, ry+1) not in logo
                      and (rx, ry) not in logo):
                    self.grid[ry][rx] &= ~0x4
                    self.grid[ry+1][rx] &= ~0x1
                elif (rx > 0 and side == 'W'
                      and (rx-1, ry) not in logo
                      and (rx, ry) not in logo):
                    self.grid[ry][rx] &= ~0x8
                    self.grid[ry][rx-1] &= ~0x2
                times -= 1

    def get_solution(self, entry: tuple[int, int],
                     end: tuple[int, int]) -> None:
        """Find shortest path from entry to exit using BFS.

        Args:
            entry: starting cell coordinates (x, y)
            exit: ending cell coordinates (x, y)

        Returns:
            None
        """
        came_from: list[
            list[tuple[int, int] | None]
            ] = [[None] * self.width for _ in range(self.height)]
        queue: deque[tuple[int, int]] = deque()
        x, y = entry
        queue.append(entry)
        came_from[y][x] = "START"

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == end:
                break
            if (cy > 0 and self.grid[cy][cx] & 0x1 == 0
                    and came_from[cy-1][cx] is None):
                queue.append((cx, cy-1))
                came_from[cy-1][cx] = (cx, cy)
            if (cx < self.width - 1
                    and self.grid[cy][cx] & 0x2 == 0
                    and came_from[cy][cx+1] is None):
                queue.append((cx+1, cy))
                came_from[cy][cx+1] = (cx, cy)
            if (cy < self.height - 1
                    and self.grid[cy][cx] & 0x4 == 0
                    and came_from[cy+1][cx] is None):
                queue.append((cx, cy+1))
                came_from[cy+1][cx] = (cx, cy)
            if (cx > 0 and self.grid[cy][cx] & 0x8 == 0
                    and came_from[cy][cx-1] is None):
                queue.append((cx-1, cy))
                came_from[cy][cx-1] = (cx, cy)

        current: tuple[int, int] = end
        cx, cy = current
        path: list[str] = []
        while came_from[cy][cx] != "START":
            pre = came_from[cy][cx]
            px, py = pre
            if px < cx:
                path.append('E')
            elif px > cx:
                path.append('W')
            elif py < cy:
                path.append('S')
            elif py > cy:
                path.append('N')
            cx, cy = px, py

        path.reverse()
        self.solution = path

    def draw_42(self, entry: tuple[int, int], end: tuple[int, int]) -> list:
        """Compute and return the set of cells forming the '42' pattern.

        Args:
            entry: entry coordinates (x, y)
            end: exit coordinates (x, y)

        Returns:
            set of (x, y) maze coordinates for the '42' pattern cells.
        """
        if self.width < 9 or self.height < 7:
            print("error: maze too small to display '42' pattern")
            return
        start_x = (self.width - 7) // 2
        start_y = (self.height - 5) // 2
        four = [
            (0, 0), (0, 1), (0, 2),
            (1, 2), (2, 2), (2, 3),
            (2, 4)
        ]
        two = [
            (4, 0), (5, 0), (6, 0),
            (6, 1), (4, 2), (5, 2),
            (6, 2), (4, 3), (4, 4),
            (5, 4), (6, 4)
        ]
        pattern_cells = {
            (x+start_x, y+start_y) for x, y in four
            } | {(x+start_x, y+start_y) for x, y in two}
        if entry in pattern_cells or end in pattern_cells:
            print("Error: entry or exit is inside the '42' pattern")
            sys.exit(1)
        return pattern_cells
