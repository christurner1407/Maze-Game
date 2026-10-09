"""Maze generator using randomized Kruskal's algorithm.

The maze is a grid of tiles with size (2*height+1) x (2*width+1).
Cells sit on odd (row, col) positions and the tiles between them are
either walls or passages.
"""
import random

WALL = 1
FLOOR = 0
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def find(parent, item):
    """Find the root of a set (union-find)."""
    while parent[item] != item:
        parent[item] = parent[parent[item]]
        item = parent[item]
    return item


def generate_maze(width, height, loop_chance=0.08, rng=None):
    """Make a maze. A loop_chance above 0 knocks down extra walls so the
    maze has loops."""
    if rng is None:
        rng = random.Random()

    grid = []
    for row in range(2 * height + 1):
        grid.append([WALL] * (2 * width + 1))
    for y in range(height):
        for x in range(width):
            grid[2 * y + 1][2 * x + 1] = FLOOR

    # every wall between two neighboring cells
    walls = []
    for y in range(height):
        for x in range(width):
            if x + 1 < width:
                walls.append((x, y, x + 1, y))
            if y + 1 < height:
                walls.append((x, y, x, y + 1))
    rng.shuffle(walls)

    parent = list(range(width * height))
    for x1, y1, x2, y2 in walls:
        root1 = find(parent, y1 * width + x1)
        root2 = find(parent, y2 * width + x2)
        if root1 != root2:
            # cells not connected yet, so remove the wall
            parent[root2] = root1
            grid[y1 + y2 + 1][x1 + x2 + 1] = FLOOR
        elif rng.random() < loop_chance:
            # already connected, so this makes a loop
            grid[y1 + y2 + 1][x1 + x2 + 1] = FLOOR
    return grid


def floor_neighbors(grid, pos):
    """List the tiles next to pos that you can walk on."""
    result = []
    for d_row, d_col in DIRECTIONS:
        new_row = pos[0] + d_row
        new_col = pos[1] + d_col
        if grid[new_row][new_col] == FLOOR:
            result.append((new_row, new_col))
    return result


def count_loops(grid):
    """Count loops in the maze (0 means a perfect maze).
    For a connected graph, loops = edges - nodes + 1."""
    nodes = 0
    edge_ends = 0
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == FLOOR:
                nodes += 1
                edge_ends += len(floor_neighbors(grid, (row, col)))
    return edge_ends // 2 - nodes + 1
