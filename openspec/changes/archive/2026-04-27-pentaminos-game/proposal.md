## Why

Trabalho acadêmico do mestrado em Computação Aplicada (IPT) — disciplina de Estruturas de Dados e Análise de Algoritmos. O objetivo é exercitar grafos, BFS, DFS e árvores AVL através de um sistema que resolve e permite jogar o puzzle de pentaminós.

## What Changes

- Criar backend Python (FastAPI) com solver de pentaminós usando grafo implícito, DFS, BFS e árvore AVL para controle de estados visitados
- Criar frontend React com interface para modo Jogar (interativo) e modo Resolver (automático)
- Tabuleiro padrão 6×10 com as 12 peças clássicas (63 orientações via rotações e reflexões)
- Poda por ilhas (regiões desconectadas com tamanho não múltiplo de 5) como opção configurável, não obrigatória
- Métricas de desempenho: tempo de execução, estados explorados, estados na AVL
- Comparação DFS vs BFS

## Capabilities

### New Capabilities
- `pentomino-pieces`: Definição das 12 peças, geração de todas as orientações (rotações e reflexões), representação como offsets normalizados
- `board-state`: Representação do tabuleiro como matriz, validação de posicionamento de peças, geração de chave de estado, detecção de ilhas
- `avl-tree`: Implementação própria de árvore AVL com inserção, busca e rebalanceamento para armazenar estados visitados
- `solver-engine`: Grafo implícito, DFS (uma ou todas as soluções), BFS (menor profundidade), poda por ilhas opcional, coleta de métricas
- `game-api`: Endpoints REST — criar jogo, posicionar peça, desfazer jogada, resolver tabuleiro
- `game-ui`: Interface React — grid interativo, painel de peças com seleção e rotação, painel de configuração e métricas

### Modified Capabilities

## Impact

- Novo projeto: backend Python com FastAPI, frontend React com TypeScript
- Dependências backend: fastapi, uvicorn, pydantic
- Dependências frontend: react, typescript, vite
- Sem banco de dados — estado mantido em memória durante a sessão
