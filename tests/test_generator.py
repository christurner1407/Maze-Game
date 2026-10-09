"""Tests for the maze generator."""
import random

from maze_game.generator import (FLOOR, WALL, count_loops, floor_neighbors,
                                 generate_maze)
from maze_game.pathfinding import distances


# --- maze generation ---------------------------------------------------

def test_maze_size_and_border():
    grid = generate_maze(10, 8, rng=random.Random(1))
    assert len(grid) == 17
    assert len(grid[0]) == 21
    for col in range(21):
        assert grid[0][col] == WALL and grid[16][col] == WALL
    for row in range(17):
        assert grid[row][0] == WALL and grid[row][20] == WALL


def test_every_cell_reachable():
    grid = generate_maze(12, 12, rng=random.Random(2))
    reachable = distances((1, 1), lambda p: floor_neighbors(grid, p))
    floors = sum(row.count(FLOOR) for row in grid)
    assert len(reachable) == floors


def test_maze_can_have_loops():
    grid = generate_maze(12, 12, loop_chance=0.3, rng=random.Random(3))
    assert count_loops(grid) > 0


def test_no_loops_when_loop_chance_is_zero():
    grid = generate_maze(12, 12, loop_chance=0, rng=random.Random(3))
    assert count_loops(grid) == 0
