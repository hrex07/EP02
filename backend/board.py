"""Board representation, placement, state keys, island detection."""

from __future__ import annotations

from collections import deque
from typing import List, Optional, Tuple

from pentominoes import Orientation, PIECE_NAME_TO_ID, PIECE_NAMES

Board = List[List[int]]


class BoardError(ValueError):
    """Invalid board operation."""


def validate_dimensions(rows: int, cols: int) -> None:
    if rows < 1 or cols < 1:
        raise BoardError("Dimensions must be positive")
    if rows * cols < 5:
        raise BoardError("Board area must be at least 5")


def create(rows: int, cols: int) -> Board:
    validate_dimensions(rows, cols)
    return [[0 for _ in range(cols)] for _ in range(rows)]


def clone(board: Board) -> Board:
    return [row[:] for row in board]


def to_key(board: Board) -> Tuple[Tuple[int, ...], ...]:
    return tuple(tuple(row) for row in board)


def find_first_empty(board: Board) -> Optional[Tuple[int, int]]:
    for r, row in enumerate(board):
        for c, v in enumerate(row):
            if v == 0:
                return r, c
    return None


def can_place(board: Board, piece_id: int, orientation: Orientation, row: int, col: int) -> bool:
    rows, cols = len(board), len(board[0])
    for dr, dc in orientation:
        rr, cc = row + dr, col + dc
        if rr < 0 or rr >= rows or cc < 0 or cc >= cols:
            return False
        if board[rr][cc] != 0:
            return False
    return True


def place_piece(board: Board, piece_id: int, orientation: Orientation, row: int, col: int) -> Board:
    if not can_place(board, piece_id, orientation, row, col):
        raise BoardError("Invalid placement: out of bounds or overlap")
    out = clone(board)
    for dr, dc in orientation:
        out[row + dr][col + dc] = piece_id
    return out


def remove_piece(board: Board, piece_id: int) -> Board:
    out = clone(board)
    for r, row in enumerate(out):
        for c, v in enumerate(row):
            if v == piece_id:
                out[r][c] = 0
    return out


def placed_piece_ids(board: Board) -> set[int]:
    ids: set[int] = set()
    for row in board:
        for v in row:
            if v != 0:
                ids.add(v)
    return ids


def remaining_piece_names(board: Board) -> List[str]:
    used = placed_piece_ids(board)
    return [n for n in PIECE_NAMES if PIECE_NAME_TO_ID[n] not in used]


def islands_valid(board: Board) -> bool:
    """True if every empty connected region has size divisible by 5."""
    rows, cols = len(board), len(board[0])
    seen = [[False] * cols for _ in range(rows)]

    def bfs(sr: int, sc: int) -> int:
        q = deque([(sr, sc)])
        seen[sr][sc] = True
        count = 0
        while q:
            r, c = q.popleft()
            count += 1
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc] and board[nr][nc] == 0:
                    seen[nr][nc] = True
                    q.append((nr, nc))
        return count

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 0 and not seen[r][c]:
                size = bfs(r, c)
                if size % 5 != 0:
                    return False
    return True


class BoardState:
    """Mutable game board with undo stack for interactive play."""

    def __init__(self, rows: int, cols: int) -> None:
        validate_dimensions(rows, cols)
        self.rows = rows
        self.cols = cols
        self.grid: Board = create(rows, cols)
        self._undo: List[Tuple[str, int, int, int, int]] = []

    def place(self, piece_name: str, orientation_index: int, row: int, col: int, orientations: List[Orientation]) -> None:
        if piece_name not in PIECE_NAME_TO_ID:
            raise BoardError("Unknown piece")
        pid = PIECE_NAME_TO_ID[piece_name]
        if any(v == pid for row_ in self.grid for v in row_):
            raise BoardError("Piece already placed")
        if orientation_index < 0 or orientation_index >= len(orientations):
            raise BoardError("Invalid orientation index")
        orient = orientations[orientation_index]
        if not can_place(self.grid, pid, orient, row, col):
            raise BoardError("Invalid placement: out of bounds or overlap")
        self.grid = place_piece(self.grid, pid, orient, row, col)
        self._undo.append((piece_name, orientation_index, row, col, pid))

    def undo(self) -> None:
        if not self._undo:
            raise BoardError("Nothing to undo")
        piece_name, _oi, _r, _c, pid = self._undo.pop()
        self.grid = remove_piece(self.grid, pid)
