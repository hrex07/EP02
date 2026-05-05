# Relatório Técnico: Jogo dos Pentaminós

Este relatório aborda a implementação técnica do jogo Pentaminós, com ênfase na modelagem de busca em grafos, nos algoritmos de solução e nas estruturas de dados avançadas.

**Nota sobre o código:** os pastas em `backend/` tiveram suas funções e classes documentadas em **português (Brasil)**. Em `solver.py` e `avl.py`, cada função inclui ainda **comentários de pseudocódigo passo a passo** (numerados) no corpo, alinhados à lógica implementada. Os pedaços de código abaixo reproduzem esses comentários; as referências `início:fim:caminho` apontam para o repositório.
---

## 1. Formulação do Problema

O desafio de cobrir um tabuleiro com Pentaminós foi representado como uma busca em um grafo de estados.

* **Estado dos Vértices (Representação dos Estados):** cada nó ilustra uma configuração do tabuleiro (`Board`: matriz de inteiros, 0 = vazio). A chave imutável para deduplicação é `to_key`, documentada no próprio módulo.

```python - 67:76:backend/board.py
def to_key(board: Board) -> Tuple[Tuple[int, ...], ...]:
    """Converte o tabuleiro numa tupla imutável para usar como chave (ex.: AVL).

    Args:
        board: Grade atual.

    Returns:
        Tupla de tuplas de inteiros, comparável e hashable.
    """
    return tuple(tuple(row) for row in board)
```

* **Representação de Mudanças (Conexões):** os vizinhos são gerados por `generate_neighbors`, com pseudocódigo no ficheiro que descreve a âncora na primeira célula vazia.
Isso foi necessário para manter uma memória mais limpa sem precisar guardar todas as jogadas possíveis na memória. Desta forma, a cada jogada o código gera seus vizinhos
para determinar quais as próximas jogadas possíveis para o `solver` realizar.

```python - 40:74:backend/solver.py
def generate_neighbors(board: Board) -> List[Board]:
    """Gera todos os tabuleiros vizinhos por uma jogada na primeira célula vazia.
    ...
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
    ...
    return out
```

* **Estratégia de Crescimento:** preenchimento <canónico> pelo “primeiro espaço vazio” (varredura em ordem de linha).
* <canónico>: único critério determinístico (primeiro espaço vazio na ordem de linha)

```python - 79:91:backend/board.py
def find_first_empty(board: Board) -> Optional[Tuple[int, int]]:
    """Encontra a primeira célula vazia na ordem de tradicional de leitura (cima→baixo, esq→dir).
    ...
    """
    for r, row in enumerate(board):
        for c, v in enumerate(row):
            if v == 0:
                return r, c
    return None
```

## 2. Busca

Duas estratégias de travessia no grafo de estados foram implementadas:

* **Busca em Profundidade (DFS):** Retrocesso com conjunto de visitados em AVL; a função interna `dfs` documenta o pseudocódigo e comentários inline no encerramento de `solve_dfs`.

```python - 102:139:backend/solver.py
    def dfs(board: Board) -> None:
        """Visita recursivamente ``board`` (fechamento DFS interno a ``solve_dfs``).

        Pseudocódigo:
            1. SE tempo esgotou ENTÃO marcar timed_out e SAIR
            2. key <- to_key(board)
            3. SE key já na AVL (Arvore binária de busca) ENTÃO SAIR
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
```

    * **Referência da função completa:** `solve_dfs` — `backend/solver.py`, linhas 77–151 (inclui comentário `# Pseudocódigo (solve_dfs):` antes de medir o tempo).

* **Busca em Largura (BFS):** fila `deque`; o bloco comentado resume o algoritmo antes do laço principal.

```python - 173:215:backend/solver.py
    # Pseudocódigo:
    # 1. AVL <- vazia; inserir to_key(initial); fila Q <- [initial]
    # 2. ENQUANTO Q não vazia:
    #        SE timeout ENTÃO marcar timed_out e SAIR do laço
    #        board <- desenfileirar Q; incrementar states_explored
    #        ...
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
            ...
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
```

    * **Referência:** `solve_bfs` — linhas 154–220; despacho em `solve`:

```python - 223:258:backend/solver.py
def solve(
    initial: Board,
    *,
    algorithm: str,
    find_all: bool = False,
    island_pruning: bool = False,
    timeout_sec: float = 120.0,
) -> Tuple[List[Board], SolverStats]:
    """Despacha para DFS ou BFS conforme o nome do algoritmo.
    ...
    """
    # Pseudocódigo:
    # 1. algo <- minúsculas(algorithm)
    # 2. SE algo == "dfs" ENTÃO retornar solve_dfs(...)
    # 3. SE algo == "bfs" ENTÃO SE find_all ENTÃO erro SENÃO retornar solve_bfs(...)
    # 4. SENÃO levantar ValueError
    algo = algorithm.lower()
    if algo == "dfs":
        return solve_dfs(initial, find_all=find_all, island_pruning=island_pruning, timeout_sec=timeout_sec)
    ...
```

* **Diferenças notadas:** DFS adequada a CSP com solução nas folhas; BFS pode explodir memória/tempo em tabuleiros maiores.

## 3. Estruturas de Dados: Árvore AVL

A árvore AVL (`backend/avl.py`) serve como conjunto ordenado de chaves visitadas. As operações públicas incluem pseudocódigo em comentários.

```python - 241:283:backend/avl.py
class AVLTree:
    """Árvore AVL como conjunto ordenado de chaves únicas.
    ...
    """

    def insert(self, key: Any) -> bool:
        """Insere uma chave na árvore.
        ...
        """
        # Pseudocódigo:
        # 1. (_root, inseriu) <- _insert(_root, key)
        # 2. SE inseriu ENTÃO incrementar _count
        # 3. retornar inseriu
        self._root, ins = _insert(self._root, key)
        ...

    def search(self, key: Any) -> bool:
        """Verifica se ``key`` está na árvore.
        ...
        """
        # Pseudocódigo:
        # 1. retornar _search(_root, key)
        return _search(self._root, key)
```

* **Balanceamento:** `_balance` documenta os casos LL/RR e rotações duplas em pseudocódigo.

```python - 133:164:backend/avl.py
def _balance(node: AVLNode) -> AVLNode:
    """Rebalanceia o nó se o fator AVL sair do intervalo [-1, 1].
    ...
    """
    # Pseudocódigo:
    # 1. atualizar altura de node
    # 2. bf <- fator de balanceamento de node
    # 3. SE bf > 1 (pesado à esquerda):
    #       ...
    _update_height(node)
    bf = _balance_factor(node)
    if bf > 1:
        ...
    return node
```

* **Complexidade:** busca e inserção \(O(\log n)\) no número de chaves armazenadas.

## 4. Análise de Performance

1. **Tempo de resolução / poda por ilhas:** `islands_valid` está documentada em português; a BFS interna por componente vazia mede o tamanho de cada ilha.

```python - 190:224:backend/board.py
def islands_valid(board: Board) -> bool:
    """Verifica se cada componente conexo de células vazias tem tamanho múltiplo de 5.
    ...
    """
    rows, cols = len(board), len(board[0])
    seen = [[False] * cols for _ in range(rows)]

    def bfs(sr: int, sc: int) -> int:
        """Conta células vazias na componente que contém ``(sr, sc)``."""
        ...
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 0 and not seen[r][c]:
                size = bfs(r, c)
                if size % 5 != 0:
                    return False
    return True
```

Uso no solver: condição `island_pruning and not islands_valid(nb)` em `solver.py` (por exemplo, linhas 131–134 na DFS). Na API, o cliente activa a poda com `SolveBody`:

```python - 85:94:backend/api.py
class SolveBody(BaseModel):
    """Parâmetros do solucionador (dimensões, algoritmo, poda, tempo máximo, tabuleiro opcional)."""

    rows: int = Field(6, ge=1, le=_MAX_BOARD_DIM)
    cols: int = Field(10, ge=1, le=_MAX_BOARD_DIM)
    algorithm: str = Field("dfs")
    find_all: bool = False
    island_pruning: bool = False
    timeout_sec: float = Field(120.0, gt=0, le=_SOLVE_TIMEOUT_SEC_MAX)
    board: Optional[List[List[int]]] = None
```

2. **Estados visitados:** métricas na dataclass `SolverStats` e no JSON de resposta de `/solve`.

```python - 20:37:backend/solver.py
@dataclass
class SolverStats:
    """Métricas agregadas de uma execução do solucionador.

    Attributes:
        time_ms: Tempo de CPU gasto na busca, em milissegundos.
        states_explored: Contagem de expansões de estado ...
        ...
    """

    time_ms: float = 0.0
    states_explored: int = 0
    states_in_avl: int = 0
    states_pruned: int = 0
    timed_out: bool = False
```

```python - 236:245:backend/api.py
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
```

3. **Comparação:** DFS com AVL e poda é prática em tabuleiros médios; BFS mantém-se principalmente para referência didáctica.

## 5. Dificuldades e Possíveis Resoluções

* **Gestão de memória:** cópias de linhas e chaves imutáveis — ver `clone` e `to_key`.

```python - 55:76:backend/board.py
def clone(board: Board) -> Board:
    """Copia superficial do tabuleiro (cada linha é nova lista).
    ...
    """
    return [row[:] for row in board]


def to_key(board: Board) -> Tuple[Tuple[int, ...], ...]:
    """Converte o tabuleiro numa tupla imutável para usar como chave (ex.: AVL).
    ...
    """
    return tuple(tuple(row) for row in board)
```

* **Deploy e CORS:** origens permitidas via ambiente; middleware documentado no módulo `api`.

```python - 24:36:backend/api.py
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
```

* **Estado em memória e workers:** jogos activos em `_games`; convém um único worker de processo quando o estado não é partilhado entre processos.

```python - 38:51:backend/api.py
_games: OrderedDict[str, BoardState] = OrderedDict()


def _store_game(game_id: str, state: BoardState) -> None:
    """Armazena ou atualiza o estado do jogo e aplica eviction LRU se necessário.
    ...
    """
    _games[game_id] = state
    _games.move_to_end(game_id)
    while len(_games) > _MAX_ACTIVE_GAMES:
        _games.popitem(last=False)
```

## 6. Emprego de IA

O projeto foi elaborado com o suporte da ferramenta Gemini, atuando como um assistente de programação (*pair programming*):

* **Arquitetura:** separação entre motor Python/FastAPI e interface React.
* **Geração de código:** orientações diedrais das peças (`_d4_transforms`, `all_orientations`), agora documentadas em português.

```python - 113:144:backend/pentominoes.py
def _d4_transforms() -> List:
    """Lista das 8 isometrias da malha quadrada como funções ``(r,c) -> (r',c')``.
    ...
    """
    return [
        lambda r, c: (r, c),
        lambda r, c: (c, -r),
        ...
    ]


def all_orientations(cells: List[Cell]) -> List[Orientation]:
    """Todas as orientações distintas sob D4, normalizadas e sem duplicados.
    ...
    """
    seen: set[Orientation] = set()
    for fn in _d4_transforms():
        transformed = [fn(r, c) for r, c in cells]
        seen.add(normalize(transformed))
    return sorted(seen, key=lambda o: o)
```

* **Resolução de problemas:** Docker, rede e configuração em nuvem.
