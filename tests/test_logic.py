"""
Testes unitários para game/logic.py

Execute com:
    pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from game.logic import (
    compress,
    merge,
    move_left,
    move_right,
    move_up,
    move_down,
    can_move,
    has_won,
    grids_equal,
    add_random_tile,
    max_value,
)


def test_compress_pushes_values_left():
    assert compress([0, 2, 0, 4]) == [2, 4, 0, 0]
    assert compress([2, 4, 8, 16]) == [2, 4, 8, 16]
    assert compress([0, 0, 0, 0]) == [0, 0, 0, 0]


def test_merge_combines_adjacent_equal_pairs():
    row, score = merge([2, 2, 4, 4], 0)
    assert row == [4, 0, 8, 0]
    assert score == 12


def test_merge_does_not_chain_triples():
    row, score = merge([2, 2, 2, 0], 0)
    assert row == [4, 0, 2, 0]
    assert score == 4


def test_move_left_basic():
    grid = [
        [2, 2, 0, 0],
        [0, 4, 4, 0],
        [2, 0, 2, 2],
        [0, 0, 0, 0],
    ]
    new_grid, score = move_left(grid, 0)
    assert new_grid == [
        [4, 0, 0, 0],
        [8, 0, 0, 0],
        [4, 2, 0, 0],
        [0, 0, 0, 0],
    ]
    assert score == 4 + 8 + 4


def test_move_right_basic():
    grid = [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    new_grid, score = move_right(grid, 0)
    assert new_grid[0] == [0, 0, 0, 4]
    assert score == 4


def test_move_up_and_down_are_transposes_of_left_right():
    grid = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [4, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    new_grid, score = move_up(grid, 0)
    assert new_grid[0][0] == 4
    assert new_grid[1][0] == 4
    assert score == 4

    new_grid, score = move_down(grid, 0)
    assert new_grid[3][0] == 4
    assert new_grid[2][0] == 4
    assert score == 4


def test_can_move_false_when_board_full_and_no_merges():
    grid = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2],
    ]
    assert can_move(grid) is False


def test_can_move_true_when_empty_cell_exists():
    grid = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 0],
    ]
    assert can_move(grid) is True


def test_has_won_detects_2048_tile():
    grid = [[0] * 4 for _ in range(4)]
    assert has_won(grid) is False
    grid[1][2] = 2048
    assert has_won(grid) is True


def test_add_random_tile_fills_only_one_empty_cell():
    grid = [[0] * 4 for _ in range(4)]
    add_random_tile(grid)
    non_zero = sum(1 for row in grid for v in row if v != 0)
    assert non_zero == 1


def test_grids_equal():
    a = [[1, 2, 0, 0], [3, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    b = [[1, 2, 0, 0], [3, 4, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    c = [[1, 2, 0, 0], [3, 5, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    assert grids_equal(a, b) is True
    assert grids_equal(a, c) is False


def test_max_value():
    grid = [[2, 4, 0, 0], [0, 32, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    assert max_value(grid) == 32
