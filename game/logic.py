"""
Lógica pura de "fusão estilo 2048".

Mantida sem dependência do Streamlit para ser testável isoladamente e
reaproveitável em qualquer tema de peças (aqui, funções DAX).
"""

import random
from typing import List, Tuple

from game.constants import SIZE, NEW_TILE_FOUR_CHANCE, WIN_VALUE

Grid = List[List[int]]


def new_grid() -> Grid:
    grid = [[0] * SIZE for _ in range(SIZE)]
    add_random_tile(grid)
    add_random_tile(grid)
    return grid


def add_random_tile(grid: Grid) -> None:
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if grid[r][c] == 0]
    if not empty:
        return
    r, c = random.choice(empty)
    grid[r][c] = 4 if random.random() < NEW_TILE_FOUR_CHANCE else 2


def compress(row: List[int]) -> List[int]:
    new_row = [v for v in row if v != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row


def merge(row: List[int], score: int) -> Tuple[List[int], int]:
    row = row[:]
    for i in range(SIZE - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            score += row[i]
            row[i + 1] = 0
    return row, score


def _move_row_left(row: List[int], score: int) -> Tuple[List[int], int]:
    row = compress(row)
    row, score = merge(row, score)
    row = compress(row)
    return row, score


def move_left(grid: Grid, score: int) -> Tuple[Grid, int]:
    new_grid = []
    for row in grid:
        new_row, score = _move_row_left(row, score)
        new_grid.append(new_row)
    return new_grid, score


def move_right(grid: Grid, score: int) -> Tuple[Grid, int]:
    new_grid = []
    for row in grid:
        reversed_row = row[::-1]
        new_row, score = _move_row_left(reversed_row, score)
        new_grid.append(new_row[::-1])
    return new_grid, score


def transpose(grid: Grid) -> Grid:
    return [list(row) for row in zip(*grid)]


def move_up(grid: Grid, score: int) -> Tuple[Grid, int]:
    t = transpose(grid)
    t, score = move_left(t, score)
    return transpose(t), score


def move_down(grid: Grid, score: int) -> Tuple[Grid, int]:
    t = transpose(grid)
    t, score = move_right(t, score)
    return transpose(t), score


def grids_equal(a: Grid, b: Grid) -> bool:
    return all(a[r][c] == b[r][c] for r in range(SIZE) for c in range(SIZE))


def can_move(grid: Grid) -> bool:
    for r in range(SIZE):
        for c in range(SIZE):
            if grid[r][c] == 0:
                return True
            if c + 1 < SIZE and grid[r][c] == grid[r][c + 1]:
                return True
            if r + 1 < SIZE and grid[r][c] == grid[r + 1][c]:
                return True
    return False


def has_won(grid: Grid) -> bool:
    return any(grid[r][c] >= WIN_VALUE for r in range(SIZE) for c in range(SIZE))


def max_value(grid: Grid) -> int:
    return max(v for row in grid for v in row)
