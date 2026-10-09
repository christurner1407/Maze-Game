"""Run with:  python -m maze_game   (add --solve-test 100 to test the solver)"""
import argparse

from .game import WON, Game
from .gui import main
from .solver import solve

parser = argparse.ArgumentParser()
parser.add_argument("--width", type=int, default=20)
parser.add_argument("--height", type=int, default=20)
parser.add_argument("--lives", type=int, default=5)
parser.add_argument("--solve-test", type=int, default=0,
                    help="run the solver on this many random mazes")
args = parser.parse_args()

if args.solve_test:
    wins = 0
    total_steps = 0
    for seed in range(args.solve_test):
        game = Game.new(args.width, args.height, lives=args.lives, seed=seed)
        total_steps += solve(game)
        if game.status == WON:
            wins += 1
    print("Solved", wins, "of", args.solve_test, "mazes")
    print("Average steps:", total_steps // args.solve_test)
else:
    main(width=args.width, height=args.height, lives=args.lives)
