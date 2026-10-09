"""Game rules and state: limited vision, a map, and hidden traps."""
import random

from .generator import DIRECTIONS, FLOOR, WALL, floor_neighbors, generate_maze
from .pathfinding import distances, shortest_path

PLAYING = "playing"
WON = "won"
LOST = "lost"


def line_of_sight(grid, pos):
    """Tiles you can see by looking straight down each corridor.
    Each direction stops at the first wall."""
    seen = {pos}
    for d_row, d_col in DIRECTIONS:
        row, col = pos
        while True:
            row += d_row
            col += d_col
            seen.add((row, col))
            if grid[row][col] == WALL:
                break
    return seen


def view_tiles(grid, pos):
    """Line of sight plus the tiles right beside it, so side openings
    and corridor walls show up."""
    seen = line_of_sight(grid, pos)
    for row, col in list(seen):
        if grid[row][col] == FLOOR:
            for d_row, d_col in DIRECTIONS:
                seen.add((row + d_row, col + d_col))
    return seen


class Game:
    def __init__(self, grid, player, goal, map_pos, map_path_start,
                 traps, lives=5):
        self.grid = grid
        self.player = player
        self.goal = goal
        self.map_pos = map_pos
        self.map_path_start = map_path_start
        self.traps = traps
        self.lives = lives
        self.status = PLAYING
        self.message = ""
        self.revealed_traps = set()
        self.discovered = view_tiles(grid, player)

    @classmethod
    def new(cls, width=20, height=20, loop_chance=0.08, lives=5,
            trap_density=0.005, seed=None):
        """Make a new random game."""
        rng = random.Random(seed)
        grid = generate_maze(width, height, loop_chance, rng)

        cells = []
        for y in range(height):
            for x in range(width):
                cells.append((2 * y + 1, 2 * x + 1))

        def neighbors(pos):
            return floor_neighbors(grid, pos)

        # the goal must be out of sight of the start, and fairly far away
        hidden = []
        for attempt in range(100):
            start = rng.choice(cells)
            visible = line_of_sight(grid, start)
            hidden = [c for c in cells if c not in visible]
            if hidden:
                break
        if not hidden:
            raise ValueError("Maze is too small, try at least 4 x 4")
        from_start = distances(start, neighbors)
        farthest = max(from_start[c] for c in hidden)
        far_cells = [c for c in hidden if from_start[c] >= farthest / 2]
        goal = rng.choice(far_cells)

        map_pos = rng.choice([c for c in cells if c != start and c != goal])
        path_start = rng.choice([c for c in cells if c != goal])

        # keep traps off the paths the player and the map rely on
        protected = {start, goal, map_pos}
        for origin in (start, map_pos, path_start):
            path = shortest_path(origin, lambda p: p == goal, neighbors)
            protected.update(path)

        floors = []
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == FLOOR and (row, col) not in protected:
                    floors.append((row, col))
        num_traps = min(len(floors), max(1, int(len(floors) * trap_density)))
        traps = set(rng.sample(floors, num_traps))

        return cls(grid, start, goal, map_pos, path_start, traps, lives)

    def move(self, d_row, d_col):
        """Move the player one tile. Returns True if they moved."""
        if self.status != PLAYING:
            return False
        row = self.player[0] + d_row
        col = self.player[1] + d_col
        if self.grid[row][col] == WALL:
            return False

        self.player = (row, col)
        self.message = ""
        self.discovered |= view_tiles(self.grid, self.player)

        if self.player in self.traps:
            self.revealed_traps.add(self.player)
            self.lives -= 1
            self.message = "You hit a trap!"
            if self.lives <= 0:
                self.status = LOST
                self.message = "You died in a trap. Game over."
        elif self.player == self.goal:
            self.status = WON
            self.message = "You escaped the maze!"
        return True

    def on_map(self):
        return self.player == self.map_pos

    def map_path(self):
        """Shortest trap-free path from the map's start spot to the goal."""
        def neighbors(pos):
            result = []
            for nxt in floor_neighbors(self.grid, pos):
                if nxt not in self.traps:
                    result.append(nxt)
            return result
        return shortest_path(self.map_path_start,
                             lambda p: p == self.goal, neighbors)

    def get_map(self):
        """Top-down map info. Only works while standing on the map."""
        if not self.on_map():
            return None
        return {
            "grid": [row[:] for row in self.grid],
            "goal": self.goal,
            "path_start": self.map_path_start,
            "path": self.map_path(),
            "traps": set(self.traps),
        }

    def tile_kind(self, pos):
        """What a tile looks like. Hidden traps look like floor."""
        row, col = pos
        if self.grid[row][col] == WALL:
            return "wall"
        if pos in self.revealed_traps:
            return "trap"
        if pos == self.goal:
            return "goal"
        if pos == self.map_pos:
            return "map"
        return "floor"

    def observation(self):
        """Only what the player can see right now. The solver uses this."""
        visible = {}
        for pos in view_tiles(self.grid, self.player):
            visible[pos] = self.tile_kind(pos)
        return {
            "pos": self.player,
            "visible": visible,
            "lives": self.lives,
            "map": self.get_map(),
        }
