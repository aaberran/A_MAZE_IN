import sys
import os
from mazegen.maze_generator import MazeGenerator


def parse_config(filename: str) -> dict:
    """Parse the configuration file and return a dictionary.

    Args:
        filename: path to the config file

    Returns:
        dictionary containing all config values
    """
    config = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key_value: list = line.split('=', 1)
                try:
                    if len(key_value) == 1 or key_value[1] == "":
                        raise ValueError(
                            f"missing value for key '{key_value[0]}'"
                            )
                except ValueError as e:
                    print(f"Error : {e}")
                    sys.exit(1)
                try:
                    key = key_value[0].upper()
                    if key in ["WIDTH", "HEIGHT", "SEED"]:
                        value = int(key_value[1])
                    elif key in ["ENTRY", "EXIT"]:
                        try:
                            parts = key_value[1].split(',')
                            if len(parts) > 2 or parts[1] == "":
                                raise ValueError("Invalid Information Format")
                            value = (int(parts[0]), int(parts[1]))
                        except ValueError as e:
                            print(f"Error : {e}")
                            sys.exit(1)
                    elif key == "PERFECT":
                        value = key_value[1].strip()
                        value = value.upper()
                        if value == 'TRUE' or value == '1':
                            value = True
                        elif value == 'FALSE' or value == '0':
                            value = False
                            print(value)
                        else:
                            raise ValueError(
                                "PERFECT must be True/False or 1/0"
                                )
                    elif key == "OUTPUT_FILE":
                        value = key_value[1].strip()
                    else:
                        value = key_value[1].strip()
                except ValueError as e:
                    print(e)
                    sys.exit(1)
                config[key] = value
            if "SEED" not in config:
                config["SEED"] = 42
            keys = [
                "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
                ]
            try:
                for key in keys:
                    if key not in config:
                        raise ValueError(f"missing key '{key}' in config file")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            try:
                if config["WIDTH"] <= 0 or config["HEIGHT"] <= 0:
                    raise ValueError("width and height must be greater than 0")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            try:
                ix = config["ENTRY"][0]
                iy = config["ENTRY"][1]
                ox = config["EXIT"][0]
                oy = config["EXIT"][1]
                if ix < 0 or iy < 0:
                    raise ValueError(
                        f"entry coordinates cannot "
                        f"be negative, got ({ix}, {iy})"
                        )
                if ox < 0 or oy < 0:
                    raise ValueError(f"exit coordinates cannot "
                                     f"be negative, got ({ox}, {oy})")
                if ix == ox and iy == oy:
                    raise ValueError("entry and exit cannot be the same cell")
                if ix >= config["WIDTH"] or iy >= config["HEIGHT"]:
                    raise ValueError("entry is outside the maze bounds")
                if ox >= config["WIDTH"] or oy >= config["HEIGHT"]:
                    raise ValueError("exit is outside the maze bounds")
            except ValueError as e:
                print(f"Error : {e}")
                sys.exit(1)
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found")
        sys.exit(1)
    return config


def write_output(maze: MazeGenerator,
                 entry: tuple[int, int],
                 end: tuple[int, int],
                 output_file: str) -> None:
    """Write maze data to output file.

    Args:
        maze: MazeGenerator object containing grid and solution
        entry: entry coordinates (x, y)
        end: exit coordinates (x, y)
        output_file: path to output file
    """
    try:
        with open(output_file, "w") as f:
            for row in maze.grid:
                line = ""
                for col in row:
                    line += format(col, 'X')
                f.write(f"{line}\n")
            f.write('\n')
            sx, sy = entry
            ex, ey = end
            f.write(f"{sx},{sy}\n")
            f.write(f"{ex},{ey}\n")
            solution = ''
            for s in maze.solution:
                solution += s
            f.write(f"{solution}\n")
    except IOError:
        print(f"Error: cannot write to file '{output_file}'")
        sys.exit(1)


def display_maze(
    maze: MazeGenerator,
    entry: tuple[int, int],
    end: tuple[int, int],
    show_solution: bool,
    wall_color: str
) -> None:
    """Display the maze in the terminal.

    Args:
        maze: MazeGenerator object
        entry: entry coordinates (x, y)
        end: exit coordinates (x, y)
        show_solution: whether to show solution path
        wall_color: ANSI color code for walls
    """
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    solutions: set[tuple[int, int]] = set()
    if show_solution:
        cx, cy = entry
        solutions.add((cx, cy))
        for side in maze.solution:
            if side == 'N':
                cy -= 1
            elif side == 'E':
                cx += 1
            elif side == 'S':
                cy += 1
            elif side == 'W':
                cx -= 1
            solutions.add((cx, cy))
    for y in range(maze.height):
        for x in range(maze.width):
            print(wall_color + "█" + RESET, end="")
            if maze.grid[y][x] & 1:
                print(wall_color + "██" + RESET, end="")
            else:
                print("  ", end="")
        print(wall_color + "█" + RESET)
        for x in range(maze.width):
            if maze.grid[y][x] & 8:
                print(wall_color + "█" + RESET, end="")
            else:
                print(" ", end="")

            if (x, y) == entry:
                print(GREEN + "👮" + RESET, end="")
            elif (x, y) == end:
                print(RED + "😈" + RESET, end="")
            elif show_solution and (x, y) in solutions:
                print(BLUE + "██" + RESET, end="")
            else:
                print("  ", end="")
        print(wall_color + "█" + RESET)
    print(wall_color + "█" * (maze.width * 3 + 1) + RESET)


def main() -> None:
    """Main entry point of the program."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    filename = sys.argv[1]
    config = parse_config(filename)

    maze = MazeGenerator(
        width=config["WIDTH"],
        height=config["HEIGHT"],
        seed=config["SEED"],
        p_flag=config["PERFECT"]
    )

    maze.generate(config["ENTRY"], config["EXIT"])
    maze.get_solution(config["ENTRY"], config["EXIT"])

    write_output(
        maze,
        config["ENTRY"],
        config["EXIT"],
        config["OUTPUT_FILE"]
    )

    show_solution: bool = False
    wall_color: str = "\033[37m"
    colors: list[str] = [
        "\033[37m",
        "\033[32m",
        "\033[33m",
        "\033[35m",
    ]
    color_index: int = 0

    os.system("clear")
    display_maze(maze, config["ENTRY"],
                 config["EXIT"], show_solution,
                 wall_color)

    while True:
        print("\n==== A-Maze-ing ====")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path")
        print("3. Change wall color")
        print("4. Quit")
        try:
            choice = input("Choice (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "1":
            config["SEED"] += 1
            maze = MazeGenerator(
                width=config["WIDTH"],
                height=config["HEIGHT"],
                seed=config["SEED"],
                p_flag=config["PERFECT"]
            )
            maze.generate(config["ENTRY"], config["EXIT"])
            maze.get_solution(config["ENTRY"], config["EXIT"])
            write_output(
                maze,
                config["ENTRY"],
                config["EXIT"],
                config["OUTPUT_FILE"]
            )
            os.system("clear")
            display_maze(maze, config["ENTRY"],
                         config["EXIT"], show_solution,
                         wall_color)

        elif choice == "2":
            show_solution = not show_solution
            os.system("clear")
            display_maze(maze, config["ENTRY"],
                         config["EXIT"], show_solution,
                         wall_color)

        elif choice == "3":
            color_index = (color_index + 1) % len(colors)
            wall_color = colors[color_index]
            os.system("clear")
            display_maze(maze, config["ENTRY"],
                         config["EXIT"], show_solution,
                         wall_color)

        elif choice == "4":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
