## Context

Projeto greenfield — não há código existente. O sistema será um jogo de pentaminós com backend Python (FastAPI) e frontend React (TypeScript/Vite). É um trabalho acadêmico focado em estruturas de dados: grafos implícitos, BFS, DFS e árvore AVL.

O tabuleiro padrão é 6×10 (60 células, 12 peças de 5 células cada). O espaço de estados é exponencial — decisões de poda e representação impactam diretamente a viabilidade da execução.

## Goals / Non-Goals

**Goals:**
- Implementar as 4 estruturas de dados obrigatórias (grafo implícito, DFS, BFS, AVL) de forma didática e demonstrável
- Separar claramente representação de estado, geração de vizinhos, estratégia de busca e estrutura de dados (AVL)
- Permitir comparação empírica entre DFS e BFS com métricas concretas
- Poda por ilhas como opção configurável (habilitada/desabilitada pelo usuário)
- Interface funcional para jogar e resolver

**Non-Goals:**
- Performance otimizada para produção (é trabalho acadêmico)
- Persistência em banco de dados
- Autenticação ou multi-usuário
- Visualização animada em tempo real dos estados do solver

## Decisions

### 1. Representação das peças: offsets normalizados

Cada orientação de uma peça é uma tupla de 5 pares `(row, col)` com mínimo em `(0,0)`, ordenados lexicograficamente.

**Alternativa considerada:** Bitmask em inteiro — mais compacto, mas dificulta a visualização e depuração. Para contexto acadêmico, a clareza da tupla é preferível.

### 2. Geração de orientações: algorítmica a partir de definição canônica

Cada peça é definida uma vez como lista de strings (`"##.", ".#."`, etc.). Rotações (4×) e reflexões (2×) são geradas por transformação de coordenadas, com deduplicação por normalização.

**Alternativa considerada:** Listar todas as 63 orientações manualmente — propenso a erros e não demonstra compreensão algorítmica.

### 3. Estado do tabuleiro: tupla achatada como chave da AVL

`to_key()` retorna `tuple(tuple(row) for row in board)`. Comparação lexicográfica nativa do Python serve diretamente para a AVL (`<`, `>`, `==`).

**Alternativa considerada:** Zobrist hashing — O(1) para comparar, mas introduz risco de colisão e não oferece ordem natural para a AVL (precisaria de chave adicional).

### 4. Grafo implícito com estratégia de primeira célula vazia

Em vez de testar todas as posições livres, o solver localiza a primeira célula vazia (esquerda→direita, cima→baixo) e só tenta peças que cobrem essa célula. Isso reduz drasticamente o branching factor e garante falha rápida.

**Alternativa considerada:** Testar todas as posições livres — branching factor centenas de vezes maior, inviável para tabuleiros reais.

### 5. AVL implementada manualmente

O requisito acadêmico exige implementação própria. A AVL expõe apenas `inserir(chave)`, `buscar(chave)` e `tamanho()`. Internamente implementa rotações LL, RR, LR, RL.

**Alternativa considerada:** `set` do Python (hash table, O(1)) — mais eficiente, mas não atende o requisito. Será usada na comparação empírica do relatório.

### 6. Poda por ilhas como opção

Após posicionar uma peça, verificar se existem regiões desconectadas de células vazias com tamanho não múltiplo de 5. Se sim, o estado é descartado sem consultar a AVL. Essa verificação usa BFS/flood-fill nas células vazias.

A poda é **configurável**: o usuário escolhe se quer ativá-la ou não. Isso permite comparar o impacto da heurística nos resultados e no relatório.

### 7. Arquitetura: monorepo com backend/ e frontend/

```
EP02/
├── backend/
│   ├── pentominoes.py
│   ├── board.py
│   ├── avl.py
│   ├── solver.py
│   ├── api.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── docs/
```

### 8. Comunicação: REST puro

Sem WebSocket — o solver retorna o resultado final. Endpoints REST stateless para o modo jogar (estado do jogo mantido em memória no servidor, identificado por game_id).

## Risks / Trade-offs

- **BFS inviável para 6×10 completo** → Documentar no relatório. Demonstrar BFS com tabuleiros menores (5×4, 4 peças). Incluir timeout configurável.
- **AVL mais lenta que hash table** → Esperado e desejado para análise comparativa. O overhead é O(log n) × O(k) por operação, onde k=60 (tamanho da chave).
- **Solver síncrono bloqueia o server** → Para escopo acadêmico é aceitável. Se necessário, rodar em thread separada com `asyncio.to_thread`.
- **Estado do jogo em memória** → Reinicia se o server cair. Aceitável para o escopo.
