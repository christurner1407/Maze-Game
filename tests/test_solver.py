"""Tests for the solver."""
from helpers import small_game
from maze_game.game import WON, Game
from maze_game.generator import FLOOR
from maze_game.solver import Solver, solve


# --- solver ------------------------------------------------------------

def test_solver_solves_most_mazes():
    wins = 0
    for seed in range(40):
        game = Game.new(seed=seed)
        solve(game)
        if game.status == WON:
            wins += 1
    assert wins >= 36   # hidden traps can sometimes kill it


def test_solver_solves_maze_without_traps():
    for seed in range(20):
        game = Game.new(seed=seed, trap_density=0)
        solve(game)
        assert game.status == WON


def test_solver_avoids_known_traps():
    game = small_game()
    # a loop: two ways around, one has a known trap
    game.grid[0][1] = FLOOR
    game.grid[0][2] = FLOOR
    game.grid[0][3] = FLOOR
    solver = Solver()
    solver.traps.add((1, 2))
    game.traps = {(1, 2)}
    solver.remember(game.observation())
    move = solver.next_move(game.observation())
    assert move == (-1, 0)      # goes around through row 0
