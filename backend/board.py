"""Representação do tabuleiro, colocação de peças, chaves de estado e poda por ilhas.

Tipos e funções utilitárias usados pelo solucionador e pela API HTTP. O tabuleiro é
uma matriz de inteiros: 0 indica célula vazia; valores positivos identificam peças
via ``PIECE_NAME_TO_ID`` em ``pentominoes``.
"""

from __future__ import annotations

from collections import deque
from typing import List, Optional, Tuple

from pentominoes import Orientation, PIECE_NAME_TO_ID, PIECE_NAMES

Board = List[List[int]]


class BoardError(ValueError):
    """Exceção para operações inválidas sobre o tabuleiro ou dimensões."""


def validate_dimensions(rows: int, cols: int) -> None:
    """Garante dimensões positivas e área mínima para pelo menos um pentaminó.

    Args:
        rows: Número de linhas.
        cols: Número de colunas.

    Raises:
        BoardError: Se ``rows`` ou ``cols`` forem inválidos ou a área for menor que 5.
    """
    if rows < 1 or cols < 1:
        raise BoardError("Dimensions must be positive")
    if rows * cols < 5:
        raise BoardError("Board area must be at least 5")


def create(rows: int, cols: int) -> Board:
    """Cria um tabuleiro vazio com todas as células em 0.

    Args:
        rows: Linhas.
        cols: Colunas.

    Returns:
        Nova matriz ``rows x cols`` preenchida com zeros.

    Raises:
        BoardError: Se as dimensões forem inválidas.
    """
    validate_dimensions(rows, cols)
    return [[0 for _ in range(cols)] for _ in range(rows)]


def clone(board: Board) -> Board:
    """Copia superficial do tabuleiro (cada linha é nova lista).

    Args:
        board: Estado a copiar.

    Returns:
        Cópia independente das linhas; estrutura nova, valores iguais.
    """
    return [row[:] for row in board]


def to_key(board: Board) -> Tuple[Tuple[int, ...], ...]:
    """Converte o tabuleiro numa tupla imutável para usar como chave (ex.: AVL).

    Args:
        board: Grade atual.

    Returns:
        Tupla de tuplas de inteiros, comparável e hashable.
    """
    return tuple(tuple(row) for row in board)


def find_first_empty(board: Board) -> Optional[Tuple[int, int]]:
    """Encontra a primeira célula vazia na ordem linha-major (cima→baixo, esq→dir).

    Args:
        board: Tabuleiro.

    Returns:
        Par ``(linha, coluna)`` ou ``None`` se estiver completo.
    """
    for r, row in enumerate(board):
        for c, v in enumerate(row):
            if v == 0:
                return r, c
    return None


def can_place(board: Board, piece_id: int, orientation: Orientation, row: int, col: int) -> bool:
    """Verifica se a peça cabe inteira no tabuleiro sem sair dos limites nem sobrepor.

    Args:
        board: Estado atual.
        piece_id: Identificador numérico da peça.
        orientation: Lista de deslocamentos ``(dr, dc)`` relativos à âncora ``(row, col)``.
        row: Linha da âncora.
        col: Coluna da âncora.

    Returns:
        ``True`` se todas as células alvo estiverem dentro do tabuleiro e forem 0.
    """
    rows, cols = len(board), len(board[0])
    for dr, dc in orientation:
        rr, cc = row + dr, col + dc
        if rr < 0 or rr >= rows or cc < 0 or cc >= cols:
            return False
        if board[rr][cc] != 0:
            return False
    return True


def place_piece(board: Board, piece_id: int, orientation: Orientation, row: int, col: int) -> Board:
    """Devolve um novo tabuleiro com a peça colocada na posição indicada.

    Args:
        board: Estado base (não é mutado).
        piece_id: ID da peça.
        orientation: Deslocamentos da peça.
        row: Linha âncora.
        col: Coluna âncora.

    Returns:
        Novo ``Board`` com células da peça preenchidas com ``piece_id``.

    Raises:
        BoardError: Se a colocação for inválida.
    """
    if not can_place(board, piece_id, orientation, row, col):
        raise BoardError("Invalid placement: out of bounds or overlap")
    out = clone(board)
    for dr, dc in orientation:
        out[row + dr][col + dc] = piece_id
    return out


def remove_piece(board: Board, piece_id: int) -> Board:
    """Remove todas as células que contenham ``piece_id``, voltando-as a 0.

    Args:
        board: Estado atual.
        piece_id: ID a remover.

    Returns:
        Novo tabuleiro sem ocorrências desse ID.
    """
    out = clone(board)
    for r, row in enumerate(out):
        for c, v in enumerate(row):
            if v == piece_id:
                out[r][c] = 0
    return out


def placed_piece_ids(board: Board) -> set[int]:
    """Conjunto de IDs de peça já presentes no tabuleiro (células não zero).

    Args:
        board: Estado atual.

    Returns:
        Conjunto de inteiros ``piece_id``.
    """
    ids: set[int] = set()
    for row in board:
        for v in row:
            if v != 0:
                ids.add(v)
    return ids


def remaining_piece_names(board: Board) -> List[str]:
    """Lista nomes de pentaminós ainda não colocados.

    Args:
        board: Estado atual.

    Returns:
        Nomes em ``PIECE_NAMES`` cujo ID não aparece no tabuleiro.
    """
    used = placed_piece_ids(board)
    return [n for n in PIECE_NAMES if PIECE_NAME_TO_ID[n] not in used]


def islands_valid(board: Board) -> bool:
    """Verifica se cada componente conexo de células vazias tem tamanho múltiplo de 5.

    Usado na poda: regiões vazias que não podem ser cobertas por pentaminós são inválidas.

    Args:
        board: Estado a inspecionar.

    Returns:
        ``True`` se todas as ilhas vazias tiverem cardinalidade divisível por 5.
    """
    rows, cols = len(board), len(board[0])
    seen = [[False] * cols for _ in range(rows)]

    def bfs(sr: int, sc: int) -> int:
        """Conta células vazias na componente que contém ``(sr, sc)``."""
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
    """Tabuleiro mutável para jogo interativo com pilha de desfazer.

    Attributes:
        rows: Altura do tabuleiro.
        cols: Largura do tabuleiro.
        grid: Grade atual (mutável entre jogadas).
    """

    def __init__(self, rows: int, cols: int) -> None:
        """Inicializa estado vazio com dimensões válidas.

        Args:
            rows: Linhas.
            cols: Colunas.

        Raises:
            BoardError: Se as dimensões forem inválidas.
        """
        validate_dimensions(rows, cols)
        self.rows = rows
        self.cols = cols
        self.grid: Board = create(rows, cols)
        self._undo: List[Tuple[str, int, int, int, int]] = []

    def place(self, piece_name: str, orientation_index: int, row: int, col: int, orientations: List[Orientation]) -> None:
        """Coloca uma peça pela orientação e âncora dadas.

        Args:
            piece_name: Letra da peça (ex.: ``"F"``).
            orientation_index: Índice na lista de orientações pré-calculadas.
            row: Linha âncora.
            col: Coluna âncora.
            orientations: Lista de orientações da peça (geralmente ``PIECES[piece_name]``).

        Raises:
            BoardError: Peça desconhecida, já colocada, índice inválido ou sobreposição/fora.
        """
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
        """Desfaz a última colocação registrada na pilha interna.

        Raises:
            BoardError: Se não houver jogadas para desfazer.
        """
        if not self._undo:
            raise BoardError("Nothing to undo")
        piece_name, _oi, _r, _c, pid = self._undo.pop()
        self.grid = remove_piece(self.grid, pid)
