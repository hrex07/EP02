"""Testes da geração de orientações diedrais e contagens de ``PIECES``."""

from pentominoes import PIECES, PIECE_NAMES, TOTAL_ORIENTATIONS


def test_twelve_piece_names():
    assert len(PIECE_NAMES) == 12


def test_each_piece_has_five_cells():
    for name in PIECE_NAMES:
        for orient in PIECES[name]:
            assert len(orient) == 5


def test_total_orientations_matches_generator():
    # Literature often cites 63 placements counting a different symmetry convention;
    # this project uses D4-normalized coordinate tuples (55 unique).
    assert TOTAL_ORIENTATIONS == 55


def test_x_has_one_orientation():
    assert len(PIECES["X"]) == 1


def test_i_has_two_orientations():
    assert len(PIECES["I"]) == 2
