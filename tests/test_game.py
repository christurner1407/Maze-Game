"""Tests for the game rules: vision, placement, the map, traps, winning."""
from helpers import small_game
from maze_game.game import (LOST, PLAYING, WON, Game, line_of_sight,
                            view_tiles)
from maze_game.generator import FLOOR, WALL, floor_neighbors


# --- limited vision ----------------------------------------------------

def test_cannot_see_through_walls():
    grid = [[WALL] * 5 for _ in range(5)]
    grid[1][1] = FLOOR
    grid[1][2] = FLOOR
    grid[1][3] = FLOOR
    grid[2][3] = FLOOR          # a turn going down at column 3
    grid[3][3] = FLOOR
    seen = line_of_sight(grid, (1, 1))
    assert (1, 3) in seen
    assert (3, 3) not in seen   # around the corner


def test_view_includes_side_openings():
    game = small_game()
    game.grid[0][3] = FLOOR     # opening above the middle tile
    assert (0, 3) in view_tiles(game.grid, game.player)


def test_observation_only_has_nearby_tiles():
    for seed in range(10):
        game = Game.new(seed=seed)
        obs = game.observation()
        assert set(obs["visible"]) == view_tiles(game.grid, game.player)
        assert len(obs["visible"]) < 100


# --- placement ---------------------------------------------------------

def test_goal_not_visible_from_start():
    for seed in range(50):
        game = Game.new(seed=seed)
        assert game.goal not in line_of_sight(game.grid, game.player)


def test_player_goal_and_map_are_different_places():
    for seed in range(50):
        game = Game.new(seed=seed)
        assert len({game.player, game.goal, game.map_pos}) == 3


# --- the map -----------------------------------------------------------

def test_map_only_available_on_map_tile():
    game = small_game()
    assert game.get_map() is None
    game.move(0, 1)
    game.move(0, 1)
    assert game.on_map()
    assert game.get_map() is not None


def test_map_path_is_valid_and_ends_at_goal():
    for seed in range(20):
        game = Game.new(seed=seed)
        path = game.map_path()
        assert path[0] == game.map_path_start
        assert path[-1] == game.goal
        for a, b in zip(path, path[1:]):
            assert b in floor_neighbors(game.grid, a)
        for tile in path:
            assert tile not in game.traps


# --- winning, losing, and walls ----------------------------------------

def test_cannot_walk_through_walls():
    game = small_game()
    assert game.move(-1, 0) is False
    assert game.player == (1, 1)


def test_reaching_goal_wins():
    game = small_game()
    for i in range(4):
        game.move(0, 1)
    assert game.status == WON
    assert "escaped" in game.message


def test_no_moving_after_game_ends():
    game = small_game()
    for i in range(4):
        game.move(0, 1)
    assert game.move(0, -1) is False


def test_trap_costs_a_life_and_is_revealed():
    game = small_game(traps={(1, 2)})
    game.move(0, 1)
    assert game.lives == 2
    assert (1, 2) in game.revealed_traps
    assert game.status == PLAYING


def test_losing_all_lives_loses_game():
    game = small_game(traps={(1, 2)}, lives=1)
    game.move(0, 1)
    assert game.status == LOST


def test_hidden_traps_look_like_floor():
    game = small_game(traps={(1, 2)})
    assert game.tile_kind((1, 2)) == "floor"


def test_traps_never_block_the_safe_path():
    for seed in range(30):
        game = Game.new(seed=seed)
        assert game.player not in game.traps
        assert game.goal not in game.traps
        assert game.map_pos not in game.traps
        assert game.map_path() is not None


def test_play_again_makes_a_new_game():
    first = Game.new(seed=1)
    second = Game.new(seed=2)
    assert first.grid != second.grid or first.goal != second.goal


def test_tiny_maze_gives_clear_error():
    try:
        Game.new(1, 1)
        assert False, "should have raised ValueError"
    except ValueError:
        pass
