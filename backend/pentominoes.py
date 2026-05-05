"""Definições das peças pentaminó: formas canónicas, rotações e reflexões (grupo D4).

Constrói ``PIECES`` com todas as orientações distintas por nome e mapas nome↔id
usados no tabuleiro e na API.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

Cell = Tuple[int, int]
Orientation = Tuple[Cell, ...]

# Grades canónicas em texto: '#' = célula ocupada, '.' = vazio.
# Formas escolhidas para compatibilidade com contagem clássica de orientações diedrais.
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
    """Converte uma grade textual com ``'#'`` em lista de coordenadas ``(linha, coluna)``.

    Args:
        lines: Cada string é uma linha da grade canónica.

    Returns:
        Lista com exatamente 5 células.

    Raises:
        ValueError: Se o número de células ``'#'`` for diferente de 5.
    """
    cells: List[Cell] = []
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == "#":
                cells.append((r, c))
    if len(cells) != 5:
        raise ValueError(f"Expected 5 cells, got {len(cells)} in grid {lines}")
    return cells


def normalize(cells: List[Cell]) -> Orientation:
    """Translada as células para o quadrante mínimo e devolve tupla ordenada.

    Args:
        cells: Cinco coordenadas relativas.

    Returns:
        Forma normalizada imutável, comparável entre orientações equivalentes.
    """
    min_r = min(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    shifted = [(r - min_r, c - min_c) for r, c in cells]
    shifted.sort()
    return tuple(shifted)


def rotate_90(cells: List[Cell]) -> List[Cell]:
    """Roda 90° no sentido horário: ``(r, c) -> (c, -r)``.

    Args:
        cells: Coordenadas da peça.

    Returns:
        Novas coordenadas após rotação (lista mutável).
    """
    return [(c, -r) for r, c in cells]


def reflect_h(cells: List[Cell]) -> List[Cell]:
    """Reflete horizontalmente: ``(r, c) -> (r, -c)``.

    Args:
        cells: Coordenadas da peça.

    Returns:
        Coordenadas refletidas (útil em testes e utilitários).
    """
    return [(r, -c) for r, c in cells]


def _d4_transforms() -> List:
    """Lista das 8 isometrias da malha quadrada como funções ``(r,c) -> (r',c')``.

    Returns:
        Oito lambdas que geram o grupo diedral D4.
    """
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
    """Todas as orientações distintas sob D4, normalizadas e sem duplicados.

    Args:
        cells: Cinco células de uma peça.

    Returns:
        Lista ordenada de orientações (cada uma é tupla de pares).
    """
    seen: set[Orientation] = set()
    for fn in _d4_transforms():
        transformed = [fn(r, c) for r, c in cells]
        seen.add(normalize(transformed))
    return sorted(seen, key=lambda o: o)


def build_pieces() -> Dict[str, List[Orientation]]:
    """Gera o mapa nome → lista de orientações para todas as peças canónicas.

    Returns:
        Dicionário preenchido a partir de ``CANONICAL``.
    """
    out: Dict[str, List[Orientation]] = {}
    for name, lines in CANONICAL.items():
        cells = parse_grid(lines)
        out[name] = all_orientations(cells)
    return out


PIECES: Dict[str, List[Orientation]] = build_pieces()

# Soma das orbitas normalizadas sob D4 (55 orientações únicas no conjunto gerado).
TOTAL_ORIENTATIONS = sum(len(v) for v in PIECES.values())
