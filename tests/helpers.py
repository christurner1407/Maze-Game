"""Shared test helper."""
from maze_game.game import Game
from maze_game.generator import FLOOR, WALL


def small_game(**changes):
    """A hand made 3 cell corridor so tests are predictable:
    #######
    #S . G#   (row 1, cols 1, 3, 5)
    #######
    """
    grid = [[WALL] * 7 for _ in range(3)]
    for col in range(1, 6):
        grid[1][col] = FLOOR
    options = dict(grid=grid, player=(1, 1), goal=(1, 5), map_pos=(1, 3),
                   map_path_start=(1, 1), traps=set(), lives=3)
    options.update(changes)
    return Game(**options)
