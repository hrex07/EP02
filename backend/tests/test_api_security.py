"""Testes de limites da API HTTP e eviction de jogos em memória."""

import pytest
from fastapi.testclient import TestClient

import api


@pytest.fixture(autouse=True)
def reset_games():
    api._games.clear()
    yield
    api._games.clear()


@pytest.fixture
def client():
    return TestClient(api.app)


def test_new_game_rejects_rows_over_limit(client):
    r = client.post("/game/new", json={"rows": 99, "cols": 10})
    assert r.status_code == 422


def test_solve_rejects_timeout_over_limit(client):
    r = client.post(
        "/solve",
        json={
            "rows": 6,
            "cols": 10,
            "algorithm": "dfs",
            "timeout_sec": 99999,
        },
    )
    assert r.status_code == 422


def test_lru_evicts_oldest_game_when_over_cap(client, monkeypatch):
    monkeypatch.setattr(api, "_MAX_ACTIVE_GAMES", 2)
    id1 = client.post("/game/new", json={"rows": 6, "cols": 10}).json()["game_id"]
    id2 = client.post("/game/new", json={"rows": 6, "cols": 10}).json()["game_id"]
    client.post("/game/new", json={"rows": 6, "cols": 10})
    assert client.get(f"/game/{id1}").status_code == 404
    assert client.get(f"/game/{id2}").status_code == 200
