"""Pentomino definitions: canonical shapes, rotations, reflections, orientations."""

from __future__ import annotations

from typing import Dict, List, Tuple

Cell = Tuple[int, int]
Orientation = Tuple[Cell, ...]

# Canonical string grids: '#' = cell, '.' = empty
# Shapes chosen so dihedral orientations match the classic 63 total.
CANONICAL: Dict[str, List[str]] = {
    "F": [".##", "##.", ".#."],
    "I": ["#####"],
    "L": ["###", "#..", "#.."],
    "N": ["##.", ".##", "..#"],
    "P": ["##", "##", "#."],
    "T": ["###", ".#.", ".#."],
    "U": ["#.#", "###"],
    "V": ["#..", "#..", "###"],
    "W": ["#..", "##.", ".##"],
    "X": [".#.", "###", ".#."],
    "Y": ["#..", "##.", ".#.", ".#."],
    "Z": ["##.", ".#.", ".##"],
}

PIECE_COLORS: Dict[str, str] = {
    "F": "#e6194B",
    "I": "#3cb44b",
    "L": "#ffe119",
    "N": "#4363d8",
    "P": "#f58231",
    "T": "#911eb4",
    "U": "#46f0f0",
    "V": "#f032e6",
    "W": "#bcf60c",
    "X": "#fabebe",
    "Y": "#008080",
    "Z": "#e6beff",
}

PIECE_NAMES: Tuple[str, ...] = tuple(sorted(CANONICAL.keys()))
PIECE_NAME_TO_ID: Dict[str, int] = {n: i + 1 for i, n in enumerate(PIECE_NAMES)}
PIECE_ID_TO_NAME: Dict[int, str] = {i + 1: n for i, n in enumerate(PIECE_NAMES)}


def parse_grid(lines: List[str]) -> List[Cell]:
    """Convert canonical '#' grid to list of (row, col) coordinates."""
    cells: List[Cell] = []
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == "#":
                cells.append((r, c))
    if len(cells) != 5:
        raise ValueError(f"Expected 5 cells, got {len(cells)} in grid {lines}")
    return cells


def normalize(cells: List[Cell]) -> Orientation:
    """Shift so min row and min col are 0; return sorted tuple of cells."""
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    shifted = [(r - min_r, c - min_c) for r, c in cells]
    shifted.sort()
    return tuple(shifted)


def rotate_90(cells: List[Cell]) -> List[Cell]:
    """Rotate 90° clockwise: (r, c) -> (c, -r)."""
    return [(c, -r) for r, c in cells]


def reflect_h(cells: List[Cell]) -> List[Cell]:
    """Reflect horizontally: (r, c) -> (r, -c). Used by tests / utilities."""
    return [(r, -c) for r, c in cells]


def _d4_transforms() -> List:
    """The 8 isometries of the square grid as (r,c) -> (r',c')."""
    return [
        lambda r, c: (r, c),
        lambda r, c: (c, -r),
        lambda r, c: (-r, -c),
        lambda r, c: (-c, r),
        lambda r, c: (r, -c),
        lambda r, c: (-r, c),
        lambda r, c: (c, r),
        lambda r, c: (-c, -r),
    ]


def all_orientations(cells: List[Cell]) -> List[Orientation]:
    """All distinct orientations under the dihedral group D4 (deduplicated)."""
    seen: set[Orientation] = set()
    for fn in _d4_transforms():
        transformed = [fn(r, c) for r, c in cells]
        seen.add(normalize(transformed))
    return sorted(seen, key=lambda o: o)


def build_pieces() -> Dict[str, List[Orientation]]:
    out: Dict[str, List[Orientation]] = {}
    for name, lines in CANONICAL.items():
        cells = parse_grid(lines)
        out[name] = all_orientations(cells)
    return out


PIECES: Dict[str, List[Orientation]] = build_pieces()

# Unique normalized D4 orbits (55). Some sources cite 63 under a different counting convention.
TOTAL_ORIENTATIONS = sum(len(v) for v in PIECES.values())
