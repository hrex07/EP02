"""Motor de solução de pentaminós por busca em grafo implícito.

Modela o tabuleiro como vértice e cada colocação válida na primeira célula vazia
como aresta. Implementa DFS com retrocesso e BFS com fila; ambos usam
``AVLTree`` para memorizar estados já visitados e podem aplicar poda por ilhas.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple

from avl import AVLTree
from board import Board, clone, find_first_empty, islands_valid, place_piece, remaining_piece_names, to_key, can_place
from pentominoes import PIECES, PIECE_NAME_TO_ID


@dataclass
class SolverStats:
    """Métricas agregadas de uma execução do solucionador.

    Attributes:
        time_ms: Tempo de CPU gasto na busca, em milissegundos.
        states_explored: Contagem de expansões de estado (DFS: ao entrar no nó;
            BFS: ao desenfileirar e ao enfileirar vizinho novo — ver implementação).
        states_in_avl: Quantidade de chaves distintas na árvore AVL ao terminar.
        states_pruned: Vizinhos descartados pela poda por ilhas.
        timed_out: ``True`` se o limite de tempo foi atingido antes do fim da busca.
    """

    time_ms: float = 0.0
    states_explored: int = 0
    states_in_avl: int = 0
    states_pruned: int = 0
    timed_out: bool = False


def generate_neighbors(board: Board) -> List[Board]:
    """Gera todos os tabuleiros vizinhos por uma jogada na primeira célula vazia.

    Para cada peça ainda não usada e cada orientação, tenta ancorar a peça de modo
    que a primeira célula vazia (varredura linha a linha) fique ocupada.

    Args:
        board: Estado atual do tabuleiro.

    Returns:
        Lista de novos tabuleiros após colocações válidas; vazia se não houver célula vazia.
    """
    # Pseudocódigo:
    # 1. (er, ec) <- primeira célula com valor 0; SE não existir retornar lista vazia
    # 2. vizinhos <- lista vazia
    # 3. PARA cada nome em peças restantes:
    #       PARA cada orientação da peça:
    #           PARA cada célula (dr,dc) da orientação:
    #               âncora <- (er - dr, ec - dc)
    #               SE cabe no tabuleiro SEM sobreposição ENTÃO
    #                   adicionar tabuleiro após place_piece
    # 4. retornar vizinhos
    fe = find_first_empty(board)
    if fe is None:
        return []
    er, ec = fe
    out: List[Board] = []
    for name in remaining_piece_names(board):
        pid = PIECE_NAME_TO_ID[name]
        for orient in PIECES[name]:
            for dr, dc in orient:
                row, col = er - dr, ec - dc
                if can_place(board, pid, orient, row, col):
                    out.append(place_piece(board, pid, orient, row, col))
    return out


def solve_dfs(
    initial: Board,
    *,
    find_all: bool = False,
    island_pruning: bool = False,
    timeout_sec: float = 120.0,
) -> Tuple[List[Board], SolverStats]:
    """Resolve por busca em profundidade (retrocesso) com conjunto de visitados AVL.

    Args:
        initial: Tabuleiro inicial (parcialmente preenchido ou vazio).
        find_all: Se ``True``, continua até enumerar todas as soluções (respeitando timeout).
        island_pruning: Se ``True``, não expande estados onde alguma ilha vazia tem
            tamanho não múltiplo de 5.
        timeout_sec: Limite de tempo da busca em segundos (relógio monotónico).

    Returns:
        Tupla ``(soluções, estatísticas)``. Lista vazia se não houver solução ou timeout sem achado.
    """
    avl = AVLTree()
    solutions: List[Board] = []
    stats = SolverStats()
    deadline = time.monotonic() + timeout_sec
    timed_out = False

    def dfs(board: Board) -> None:
        """Visita recursivamente ``board`` (fechamento DFS interno a ``solve_dfs``).

        Pseudocódigo:
            1. SE tempo esgotou ENTÃO marcar timed_out e SAIR
            2. key <- to_key(board)
            3. SE key já na AVL ENTÃO SAIR
            4. inserir key na AVL; incrementar states_explored
            5. SE não há célula vazia ENTÃO guardar clone em solutions e SAIR
            6. PARA cada vizinho nb de generate_neighbors(board):
                   SE poda por ilhas e nb inválido ENTÃO incrementar pruned; CONTINUAR
                   dfs(nb)
                   SE timed_out ENTÃO SAIR
                   SE há solução e não é find_all ENTÃO SAIR
        """
        nonlocal timed_out
        if time.monotonic() > deadline:
            timed_out = True
            return
        key = to_key(board)
        if avl.search(key):
            return
        avl.insert(key)
        stats.states_explored += 1

        if find_first_empty(board) is None:
            solutions.append(clone(board))
            return

        for nb in generate_neighbors(board):
            if island_pruning and not islands_valid(nb):
                stats.states_pruned += 1
                continue
            dfs(nb)
            if timed_out:
                return
            if solutions and not find_all:
                return

    # Pseudocódigo (solve_dfs):
    # 1. inicializar AVL, lista solutions, stats, deadline
    # 2. dfs(initial)
    # 3. preencher time_ms, states_in_avl, timed_out em stats
    # 4. retornar (solutions, stats)
    t0 = time.perf_counter()
    dfs(initial)
    stats.time_ms = (time.perf_counter() - t0) * 1000
    stats.states_in_avl = len(avl)
    stats.timed_out = timed_out
    return solutions, stats


def solve_bfs(
    initial: Board,
    *,
    island_pruning: bool = False,
    timeout_sec: float = 120.0,
) -> Tuple[List[Board], SolverStats]:
    """Resolve por busca em largura: primeira solução completa mais rasa (em número de peças).

    Args:
        initial: Tabuleiro inicial.
        island_pruning: Se ``True``, aplica a mesma poda por ilhas que na DFS.
        timeout_sec: Limite de tempo em segundos.

    Returns:
        Tupla com lista contendo uma solução ou lista vazia, e estatísticas.

    Note:
        Não suporta enumerar todas as soluções; usar apenas a primeira encontrada.
    """
    # Pseudocódigo:
    # 1. AVL <- vazia; inserir to_key(initial); fila Q <- [initial]
    # 2. ENQUANTO Q não vazia:
    #        SE timeout ENTÃO marcar timed_out e SAIR do laço
    #        board <- desenfileirar Q; incrementar states_explored
    #        SE board completo ENTÃO retornar [clone(board)], stats preenchidos
    #        PARA cada nb em generate_neighbors(board):
    #             SE poda ilhas e nb inválido ENTÃO pruned++; CONTINUAR
    #             k <- to_key(nb)
    #             SE k na AVL ENTÃO CONTINUAR
    #             inserir k; incrementar states_explored; enfileirar nb
    # 3. retornar [], stats (sem solução ou timeout)
    avl = AVLTree()
    stats = SolverStats()
    deadline = time.monotonic() + timeout_sec
    timed_out = False

    avl.insert(to_key(initial))
    q: deque[Board] = deque([initial])

    t0 = time.perf_counter()
    while q:
        if time.monotonic() > deadline:
            timed_out = True
            break
        board = q.popleft()
        stats.states_explored += 1
        if find_first_empty(board) is None:
            stats.time_ms = (time.perf_counter() - t0) * 1000
            stats.states_in_avl = len(avl)
            stats.timed_out = timed_out
            return [clone(board)], stats

        for nb in generate_neighbors(board):
            if island_pruning and not islands_valid(nb):
                stats.states_pruned += 1
                continue
            k = to_key(nb)
            if avl.search(k):
                continue
            avl.insert(k)
            stats.states_explored += 1
            q.append(nb)

    stats.time_ms = (time.perf_counter() - t0) * 1000
    stats.states_in_avl = len(avl)
    stats.timed_out = timed_out
    return [], stats


def solve(
    initial: Board,
    *,
    algorithm: str,
    find_all: bool = False,
    island_pruning: bool = False,
    timeout_sec: float = 120.0,
) -> Tuple[List[Board], SolverStats]:
    """Despacha para DFS ou BFS conforme o nome do algoritmo.

    Args:
        initial: Tabuleiro inicial.
        algorithm: Valores ``"dfs"`` ou ``"bfs"`` (sem distinção de maiúsculas).
        find_all: Apenas para DFS; se ``True`` enumera soluções até timeout.
        island_pruning: Ativa poda por ilhas em ambos os modos suportados.
        timeout_sec: Limite de tempo em segundos.

    Returns:
        Lista de soluções e estatísticas da execução.

    Raises:
        ValueError: Se o algoritmo não for reconhecido ou se ``find_all`` for usado com BFS.
    """
    # Pseudocódigo:
    # 1. algo <- minúsculas(algorithm)
    # 2. SE algo == "dfs" ENTÃO retornar solve_dfs(...)
    # 3. SE algo == "bfs" ENTÃO SE find_all ENTÃO erro SENÃO retornar solve_bfs(...)
    # 4. SENÃO levantar ValueError
    algo = algorithm.lower()
    if algo == "dfs":
        return solve_dfs(initial, find_all=find_all, island_pruning=island_pruning, timeout_sec=timeout_sec)
    if algo == "bfs":
        if find_all:
            raise ValueError("BFS find_all is not supported")
        return solve_bfs(initial, island_pruning=island_pruning, timeout_sec=timeout_sec)
    raise ValueError("algorithm must be 'dfs' or 'bfs'")
