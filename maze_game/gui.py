"""Tkinter window for the maze game.

The camera always stays centered on the player and anything undiscovered
(or outside the maze) is drawn black, so the edges of the maze never give
away where the player is.
"""
import tkinter as tk

from .game import PLAYING, WON, Game, view_tiles
from .solver import Solver

TILE = 32
RADIUS = 7                      # tiles shown on each side of the player
SIZE = (2 * RADIUS + 1) * TILE

MOVES = {
    "up": (-1, 0), "w": (-1, 0),
    "down": (1, 0), "s": (1, 0),
    "left": (0, -1), "a": (0, -1),
    "right": (0, 1), "d": (0, 1),
}


class App:
    def __init__(self, root, **game_options):
        self.root = root
        self.game_options = game_options
        root.title("Maze Game")

        self.canvas = tk.Canvas(root, width=SIZE, height=SIZE, bg="black",
                                highlightthickness=0)
        self.canvas.pack()
        self.label = tk.Label(root, font=("Arial", 12), wraplength=SIZE)
        self.label.pack(fill="x")
        root.bind("<Key>", self.on_key)

        self.new_game()
        self.autopilot_tick()

    def new_game(self):
        self.game = Game.new(**self.game_options)
        self.solver = Solver()
        self.autopilot = False
        self.show_map = False
        self.draw()

    def on_key(self, event):
        key = event.keysym.lower()   # so caps lock doesn't break the keys
        if self.game.status != PLAYING:
            # game is over, ask to play again
            if key in ("y", "return"):
                self.new_game()
            elif key in ("n", "escape"):
                self.root.destroy()
            return

        if key in MOVES:
            self.autopilot = False
            self.game.move(MOVES[key][0], MOVES[key][1])
        elif key == "m":
            if self.game.on_map():
                self.show_map = not self.show_map
            else:
                self.game.message = "Find the blue map tile first. " \
                                    "You can only open the map standing on it."
        elif key == "p":
            self.autopilot = not self.autopilot
        self.draw()

    def autopilot_tick(self):
        """Let the solver take a step every 80 ms when autopilot is on."""
        if self.autopilot and self.game.status == PLAYING:
            move = self.solver.next_move(self.game.observation())
            if move is None:
                self.autopilot = False
            else:
                self.game.move(move[0], move[1])
            self.draw()
        self.root.after(80, self.autopilot_tick)

    # drawing -----------------------------------------------------------
    def draw(self):
        game = self.game
        self.canvas.delete("all")
        if not game.on_map():
            self.show_map = False

        if self.show_map:
            self.draw_map()
        else:
            self.draw_view()

        text = "Lives: " + str(game.lives)
        if game.on_map() and not self.show_map:
            text += "   You found the map! Press M to view it"
        if game.message:
            text += "   " + game.message
        text += "\nMove: arrows/WASD   Map: M   Autopilot: P"
        self.label.config(text=text)

        if game.status != PLAYING:
            self.draw_end_screen()

    def draw_view(self):
        game = self.game
        player_row, player_col = game.player
        in_sight = view_tiles(game.grid, game.player)

        for d_row in range(-RADIUS, RADIUS + 1):
            for d_col in range(-RADIUS, RADIUS + 1):
                pos = (player_row + d_row, player_col + d_col)
                if pos not in game.discovered:
                    continue
                x = (d_col + RADIUS) * TILE
                y = (d_row + RADIUS) * TILE
                kind = game.tile_kind(pos)
                bright = pos in in_sight

                if kind == "wall":
                    color = "#5b6270" if bright else "#3a3f4a"
                elif kind == "goal":
                    color = "gold"
                elif kind == "map":
                    color = "#4aa3ff"
                elif kind == "trap":
                    color = "#c0392b"
                else:
                    color = "#e8e2d0" if bright else "#8d8a7c"
                self.canvas.create_rectangle(x, y, x + TILE, y + TILE,
                                             fill=color, outline="")

        middle = RADIUS * TILE
        self.canvas.create_oval(middle + 6, middle + 6,
                                middle + TILE - 6, middle + TILE - 6,
                                fill="#2ecc71", outline="black")

    def draw_map(self):
        info = self.game.get_map()
        grid = info["grid"]
        size = SIZE // len(grid)
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                color = "#222" if grid[row][col] == 1 else "#e8e2d0"
                self.draw_square((row, col), size, color)
        for pos in info["path"]:
            self.draw_square(pos, size, "#2ecc71")
        for pos in info["traps"]:
            self.draw_square(pos, size, "#c0392b")
        self.draw_square(info["goal"], size, "gold")
        self.draw_square(info["path_start"], size, "orange")
        self.draw_square(self.game.player, size, "#4aa3ff")

    def draw_square(self, pos, size, color):
        x = pos[1] * size
        y = pos[0] * size
        self.canvas.create_rectangle(x, y, x + size, y + size,
                                     fill=color, outline="")

    def draw_end_screen(self):
        if self.game.status == WON:
            title = "YOU WIN!"
        else:
            title = "YOU LOSE"
        self.canvas.create_rectangle(0, SIZE // 2 - 60, SIZE, SIZE // 2 + 60,
                                     fill="black", stipple="gray50")
        self.canvas.create_text(SIZE // 2, SIZE // 2 - 20, text=title,
                                fill="white", font=("Arial", 32, "bold"))
        self.canvas.create_text(SIZE // 2, SIZE // 2 + 25,
                                text="Play again? (Y / N)",
                                fill="white", font=("Arial", 16))


def main(**game_options):
    root = tk.Tk()
    App(root, **game_options)
    root.mainloop()


