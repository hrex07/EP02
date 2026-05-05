"""Testes de fumaça do solucionador DFS/BFS e poda por ilhas."""

from board import create
from solver import solve


def test_solve_small_dfs():
    b = create(5, 4)
    sols, stats = solve(b, algorithm="dfs", find_all=False, island_pruning=True, timeout_sec=30)
    assert len(sols) == 1
    assert sum(v != 0 for row in sols[0] for v in row) == 20
    assert stats.states_explored > 0


def test_bfs_finds_solution_small():
    b = create(5, 4)
    sols, stats = solve(b, algorithm="bfs", island_pruning=True, timeout_sec=60)
    assert len(sols) == 1
    assert sum(v != 0 for row in sols[0] for v in row) == 20
    assert stats.states_explored > 0


def test_solve_6x10_dfs_one_solution():
    b = create(6, 10)
    sols, stats = solve(b, algorithm="dfs", find_all=False, island_pruning=True, timeout_sec=120)
    assert len(sols) == 1
    assert not stats.timed_out
