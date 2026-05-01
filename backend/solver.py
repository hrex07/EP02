"""Pentomino solver: implicit graph, DFS, BFS, AVL visited set."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Tuple

from avl import AVLTree
from board import Board, clone, find_first_empty, islands_valid, place_piece, remaining_piece_names, to_key, can_place
from pentominoes import PIECES, PIECE_NAME_TO_ID


@dataclass
class SolverStats:
    time_ms: float = 0.0
    states_explored: int = 0
    states_in_avl: int = 0
    states_pruned: int = 0
    timed_out: bool = False


def generate_neighbors(board: Board) -> List[Board]:
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
    avl = AVLTree()
    solutions: List[Board] = []
    stats = SolverStats()
    deadline = time.monotonic() + timeout_sec
    timed_out = False

    def dfs(board: Board) -> None:
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
    algo = algorithm.lower()
    if algo == "dfs":
        return solve_dfs(initial, find_all=find_all, island_pruning=island_pruning, timeout_sec=timeout_sec)
    if algo == "bfs":
        if find_all:
            raise ValueError("BFS find_all is not supported")
        return solve_bfs(initial, island_pruning=island_pruning, timeout_sec=timeout_sec)
    raise ValueError("algorithm must be 'dfs' or 'bfs'")
