"""API HTTP FastAPI para jogo interativo e solucionador de pentaminós.

Expõe rotas para criar jogos em memória, colocar peças, desfazer e resolver o
tabuleiro. Configura CORS via ``ALLOWED_ORIGINS`` e limites via variáveis de ambiente.
"""

from __future__ import annotations

import os
import uuid
from collections import OrderedDict
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from board import BoardError, BoardState, create, remaining_piece_names
from pentominoes import PIECES, PIECE_COLORS, PIECE_NAME_TO_ID, PIECE_NAMES
from solver import solve

app = FastAPI(title="Pentaminós API", version="0.1.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

_MAX_BOARD_DIM = int(os.getenv("MAX_BOARD_DIM", "40"))
_MAX_ACTIVE_GAMES = int(os.getenv("MAX_ACTIVE_GAMES", "500"))
_SOLVE_TIMEOUT_SEC_MAX = float(os.getenv("SOLVE_TIMEOUT_SEC_MAX", "300"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_games: OrderedDict[str, BoardState] = OrderedDict()


def _store_game(game_id: str, state: BoardState) -> None:
    """Armazena ou atualiza o estado do jogo e aplica eviction LRU se necessário.

    Args:
        game_id: Identificador único da partida.
        state: Estado mutável do tabuleiro.
    """
    _games[game_id] = state
    _games.move_to_end(game_id)
    while len(_games) > _MAX_ACTIVE_GAMES:
        _games.popitem(last=False)


def _get_game(game_id: str) -> Optional[BoardState]:
    """Obtém o estado da partida e atualiza ordem LRU.

    Args:
        game_id: ID da partida.

    Returns:
        ``BoardState`` se existir; caso contrário ``None``.
    """
    state = _games.get(game_id)
    if state is not None:
        _games.move_to_end(game_id)
    return state


class NewGameBody(BaseModel):
    """Corpo JSON para criar tabuleiro vazio."""

    rows: int = Field(6, ge=1, le=_MAX_BOARD_DIM)
    cols: int = Field(10, ge=1, le=_MAX_BOARD_DIM)


class PlaceBody(BaseModel):
    """Corpo JSON para colocar uma peça numa orientação e posição."""

    piece: str
    orientation: int = Field(ge=0)
    row: int = Field(ge=0)
    col: int = Field(ge=0)


class SolveBody(BaseModel):
    """Parâmetros do solucionador (dimensões, algoritmo, poda, tempo máximo, tabuleiro opcional)."""

    rows: int = Field(6, ge=1, le=_MAX_BOARD_DIM)
    cols: int = Field(10, ge=1, le=_MAX_BOARD_DIM)
    algorithm: str = Field("dfs")
    find_all: bool = False
    island_pruning: bool = False
    timeout_sec: float = Field(120.0, gt=0, le=_SOLVE_TIMEOUT_SEC_MAX)
    board: Optional[List[List[int]]] = None


def _serialize_board(board: List[List[int]]) -> List[List[int]]:
    """Converte linhas do tabuleiro em listas mutáveis para JSON.

    Args:
        board: Grade interna (lista de listas).

    Returns:
        Cópia superficial adequada para serialização Pydantic/JSON.
    """
    return [list(row) for row in board]


def _pieces_catalog() -> List[dict]:
    """Monta catálogo de peças com nome, id, cor e todas as orientações.

    Returns:
        Lista de dicionários consumidos pelo frontend.
    """
    out = []
    for name in PIECE_NAMES:
        out.append(
            {
                "name": name,
                "id": PIECE_NAME_TO_ID[name],
                "color": PIECE_COLORS[name],
                "orientations": [list(map(list, o)) for o in PIECES[name]],
            }
        )
    return out


@app.get("/pieces")
def get_pieces() -> dict:
    """Lista todas as peças e suas orientações."""
    return {"pieces": _pieces_catalog()}


@app.post("/game/new")
def game_new(body: NewGameBody) -> dict:
    """Cria nova partida com tabuleiro vazio e devolve ``game_id``.

    Raises:
        HTTPException: 400 se dimensões inválidas segundo ``BoardState``.
    """
    try:
        gid = str(uuid.uuid4())
        st = BoardState(body.rows, body.cols)
        _store_game(gid, st)
    except BoardError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"game_id": gid, "board": _serialize_board(st.grid), "rows": st.rows, "cols": st.cols}


@app.get("/game/{game_id}")
def game_get(game_id: str) -> dict:
    """Consulta estado atual: grade, peças colocadas e disponíveis.

    Raises:
        HTTPException: 404 se ``game_id`` não existir.
    """
    st = _get_game(game_id)
    if st is None:
        raise HTTPException(status_code=404, detail="Unknown game_id")
    rem = remaining_piece_names(st.grid)
    placed = [n for n in PIECE_NAMES if n not in rem]
    return {
        "board": _serialize_board(st.grid),
        "placed_pieces": placed,
        "available_pieces": rem,
        "rows": st.rows,
        "cols": st.cols,
    }


@app.post("/game/{game_id}/place")
def game_place(game_id: str, body: PlaceBody) -> dict:
    """Coloca peça na partida indicada.

    Raises:
        HTTPException: 404 partida inexistente; 400 peça ou jogada inválida.
    """
    st = _get_game(game_id)
    if st is None:
        raise HTTPException(status_code=404, detail="Unknown game_id")
    try:
        orientations = PIECES[body.piece]
        st.place(body.piece, body.orientation, body.row, body.col, orientations)
    except KeyError as e:
        raise HTTPException(status_code=400, detail="Unknown piece") from e
    except BoardError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"ok": True, "board": _serialize_board(st.grid)}


@app.post("/game/{game_id}/undo")
def game_undo(game_id: str) -> dict:
    """Desfaz última colocação na partida.

    Raises:
        HTTPException: 404 ou 400 conforme existência da partida e pilha de undo.
    """
    st = _get_game(game_id)
    if st is None:
        raise HTTPException(status_code=404, detail="Unknown game_id")
    try:
        st.undo()
    except BoardError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"ok": True, "board": _serialize_board(st.grid)}


@app.post("/solve")
def solve_endpoint(body: SolveBody) -> dict:
    """Executa o solucionador sobre tabuleiro vazio ou parcial enviado no corpo.

    Raises:
        HTTPException: 400 por dimensões inconsistentes, tabuleiro inválido ou parâmetros do solver.
    """
    try:
        if body.board is not None:
            board = [list(row) for row in body.board]
            if len(board) != body.rows or any(len(row) != body.cols for row in board):
                raise HTTPException(status_code=400, detail="board dimensions mismatch")
        else:
            board = create(body.rows, body.cols)
    except BoardError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        solutions, stats = solve(
            board,
            algorithm=body.algorithm,
            find_all=body.find_all,
            island_pruning=body.island_pruning,
            timeout_sec=body.timeout_sec,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "solutions": [_serialize_board(s) for s in solutions],
        "stats": {
            "time_ms": round(stats.time_ms, 3),
            "states_explored": stats.states_explored,
            "states_in_avl": stats.states_in_avl,
            "states_pruned": stats.states_pruned,
            "timed_out": stats.timed_out,
        },
    }


@app.get("/health")
def health() -> dict:
    """Verificação simples de disponibilidade do serviço."""
    return {"status": "ok"}
