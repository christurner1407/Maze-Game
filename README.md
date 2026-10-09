# Maze Game

ECEN4293 midterm project. A maze game where you can only see down the
corridors you are standing in, plus a solver that plays with the same
limited view.

## Run

    python -m maze_game                  # play the game
    python -m maze_game --solve-test 100 # try the solver on 100 mazes
    python -m pytest                     # run the tests

Only Python 3 (with tkinter) is needed to play. pytest is needed for tests.

## How to play

- Move with the arrow keys or WASD.
- Find the gold goal tile. You can't see it from where you start.
- Stand on the blue tile and press **M** to open the map. It shows the maze,
  the traps (red) and a path to the goal (green) from a random spot (orange).
- Hidden traps cost a life (you start with 5). They show up red once found.
- Press **P** to watch the solver play. Press any move key to take over.
- When the game ends, press **Y** to play again or **N** to quit.

## Files

- `maze_game/generator.py` - randomized Kruskal maze generator (can make loops)
- `maze_game/game.py` - rules, limited vision, map, traps
- `maze_game/solver.py` - solver that only uses what the player can see
- `maze_game/pathfinding.py` - breadth first search
- `maze_game/gui.py` - tkinter window
- `tests/test_maze.py` - pytest tests

The tile layout (cells on odd positions with wall tiles between) comes from
the Lab 3 maze code.
