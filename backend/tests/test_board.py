"""Testes de criação do tabuleiro, primeira célula vazia e poda por ilhas."""

import pytest

from board import BoardError, create, find_first_empty, islands_valid, place_piece
from pentominoes import PIECES, PIECE_NAME_TO_ID


def test_create_rejects_small_area():
    with pytest.raises(BoardError):
        create(2, 2)


def test_find_first_empty():
    b = create(2, 3)
    assert find_first_empty(b) == (0, 0)


def test_islands_valid_empty():
    b = create(2, 5)
    assert islands_valid(b) is True


def test_islands_invalid_split():
    b = create(3, 3)
    pid = PIECE_NAME_TO_ID["P"]
    orient = PIECES["P"][0]
    b = place_piece(b, pid, orient, 0, 0)
    assert islands_valid(b) is False


def test_place_piece():
    b = create(6, 10)
    pid = PIECE_NAME_TO_ID["F"]
    orient = PIECES["F"][0]
    nb = place_piece(b, pid, orient, 0, 0)
    assert sum(v != 0 for row in nb for v in row) == 5
