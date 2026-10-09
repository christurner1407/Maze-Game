"""Maze solver that only uses what the player could see.

It remembers every tile it has seen. If it sees the goal it walks to it,
otherwise it walks to the closest unexplored spot. If it finds the map it
reads the whole layout. It avoids traps it already knows about.
"""
from .game import PLAYING
from .generator import DIRECTIONS
from .pathfinding import shortest_path


class Solver:
    def __init__(self):
        self.known = {}   # tile -> "wall", "floor", "goal" or "map"
        self.traps = set()
        self.goal = None
        self.map_pos = None
        self.got_map = False

    def remember(self, obs):
        """Add what we can see to our memory."""
        for pos, kind in obs["visible"].items():
            if kind == "trap":
                self.traps.add(pos)
                kind = "floor"
            self.known[pos] = kind
            if kind == "goal":
                self.goal = pos
            elif kind == "map":
                self.map_pos = pos

        info = obs["map"]
        if info is not None:
            self.got_map = True
            self.goal = info["goal"]
            self.traps |= info["traps"]
            for row in range(len(info["grid"])):
                for col in range(len(info["grid"][0])):
                    if info["grid"][row][col] == 1:
                        self.known[(row, col)] = "wall"
                    else:
                        self.known[(row, col)] = "floor"

    def get_neighbors(self, pos, avoid_traps):
        result = []
        for d_row, d_col in DIRECTIONS:
            nxt = (pos[0] + d_row, pos[1] + d_col)
            if self.known.get(nxt, "wall") == "wall":
                continue
            if avoid_traps and nxt in self.traps:
                continue
            result.append(nxt)
        return result

    def is_frontier(self, pos):
        """A tile we know is floor but that has an unseen neighbor."""
        if self.known.get(pos) == "wall":
            return False
        for d_row, d_col in DIRECTIONS:
            if (pos[0] + d_row, pos[1] + d_col) not in self.known:
                return True
        return False

    def find_path(self, start, is_target):
        # try to avoid traps first, then allow them if there's no choice
        for avoid_traps in (True, False):
            path = shortest_path(
                start, is_target,
                lambda p: self.get_neighbors(p, avoid_traps))
            if path:
                return path
        return None

    def next_move(self, obs):
        """Return (d_row, d_col) for the next step, or None if stuck."""
        self.remember(obs)
        if self.goal is not None:
            path = self.find_path(obs["pos"], lambda p: p == self.goal)
        elif self.map_pos is not None and not self.got_map:
            path = self.find_path(obs["pos"], lambda p: p == self.map_pos)
        else:
            path = self.find_path(obs["pos"], self.is_frontier)

        if path is None or len(path) < 2:
            return None
        return path[1][0] - path[0][0], path[1][1] - path[0][1]


def solve(game, max_steps=10000):
    """Let the solver play a whole game. Returns the number of steps."""
    solver = Solver()
    steps = 0
    while game.status == PLAYING and steps < max_steps:
        move = solver.next_move(game.observation())
        if move is None:
            break
        game.move(move[0], move[1])
        steps += 1
    return steps

