"""
Lógica pura de "fusão estilo 2048".

Mantida sem dependência do Streamlit para ser testável isoladamente e
reaproveitável em qualquer tema de peças (aqui, funções DAX).
"""

import random
from typing import List, Optional, Tuple

from game.constants import SIZE, NEW_TILE_FOUR_CHANCE, WIN_VALUE

Grid = List[List[int]]
MaskGrid = List[List[bool]]


def new_grid(size: int = SIZE, rng: Optional[random.Random] = None) -> Grid:
    grid = [[0] * size for _ in range(size)]
    add_random_tile(grid, rng)
    add_random_tile(grid, rng)
    return grid


def add_random_tile(grid: Grid, rng: Optional[random.Random] = None) -> None:
    rng = rng or random
    empty = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 0]
    if not empty:
        return
    r, c = rng.choice(empty)
    grid[r][c] = 4 if rng.random() < NEW_TILE_FOUR_CHANCE else 2


def compress(row: List[int]) -> List[int]:
    new_row = [v for v in row if v != 0]
    new_row += [0] * (len(row) - len(new_row))
    return new_row


def merge(row: List[int], score: int) -> Tuple[List[int], int]:
    row = row[:]
    for i in range(len(row) - 1):
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
    return all(a[r][c] == b[r][c] for r in range(len(a)) for c in range(len(a[0])))


def can_move(grid: Grid) -> bool:
    n = len(grid)
    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                return True
            if c + 1 < n and grid[r][c] == grid[r][c + 1]:
                return True
            if r + 1 < n and grid[r][c] == grid[r + 1][c]:
                return True
    return False


def has_won(grid: Grid) -> bool:
    return any(v >= WIN_VALUE for row in grid for v in row)


def max_value(grid: Grid) -> int:
    return max(v for row in grid for v in row)


# --------------------------------------------------------------------------
# Versões que também retornam quais peças foram fruto de uma fusão nesta
# jogada (usadas só para destacar visualmente a peça, sem afetar a lógica
# de pontuação/movimento acima, que permanece coberta pelos testes).
# --------------------------------------------------------------------------
def _merge_track(row: List[int]) -> Tuple[List[int], List[bool]]:
    row = row[:]
    mask = [False] * len(row)
    for i in range(len(row) - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            mask[i] = True
            row[i + 1] = 0
    return row, mask


def _move_row_left_track(row: List[int]) -> Tuple[List[int], List[bool]]:
    nz = [v for v in row if v != 0]
    nz += [0] * (len(row) - len(nz))
    values, merged = _merge_track(nz)
    combined = [(v, m) for v, m in zip(values, merged) if v != 0]
    combined += [(0, False)] * (len(values) - len(combined))
    return [v for v, _ in combined], [m for _, m in combined]


def move_left_mask(grid: Grid) -> Tuple[Grid, MaskGrid]:
    new_grid, masks = [], []
    for row in grid:
        nr, m = _move_row_left_track(row)
        new_grid.append(nr)
        masks.append(m)
    return new_grid, masks


def move_right_mask(grid: Grid) -> Tuple[Grid, MaskGrid]:
    new_grid, masks = [], []
    for row in grid:
        nr, m = _move_row_left_track(row[::-1])
        new_grid.append(nr[::-1])
        masks.append(m[::-1])
    return new_grid, masks


def move_up_mask(grid: Grid) -> Tuple[Grid, MaskGrid]:
    t = transpose(grid)
    nt, m = move_left_mask(t)
    return transpose(nt), transpose(m)


def move_down_mask(grid: Grid) -> Tuple[Grid, MaskGrid]:
    t = transpose(grid)
    nt, m = move_right_mask(t)
    return transpose(nt), transpose(m)
