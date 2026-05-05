# Pentaminós (EP02)

Jogo de pentaminós com interface web em React e motor de solução em Python (FastAPI). O backend expõe uma API REST e um solucionador com busca em profundidade ou em largura, poda por ilhas opcional e limite de tempo.

## Documentação

- **[Relatório técnico](docs/Relatorio_Tecnico.md)** — formulação do problema como grafo de estados, DFS/BFS, árvore AVL para estados visitados, poda e notas de desempenho.

## Arquitetura

| Parte | Stack | Entrada principal |
|-------|--------|-------------------|
| `frontend/` | React 19, TypeScript, Vite | `src/main.tsx` |
| `backend/` | Python, FastAPI | `api.py` (servidor em `http://localhost:8000`) |
| `openspec/` | Especificações | alterações em `changes/` |

## Pré-requisitos

- **Node.js** (para o frontend) e **npm**
- **Python 3** com ambiente virtual recomendado em `backend/.venv`

## Configuração rápida

1. **Backend:** criar/ativar o virtualenv em `backend/`, instalar dependências com `pip install -r requirements.txt`, depois executar o servidor.
2. **Frontend:** em `frontend/`, executar `npm install`.
3. **Variáveis de ambiente (opcional):** em Windows/PowerShell, `.\backend\setup_env.ps1` define origens CORS e variáveis relacionadas ao Firestore.

## Comandos

### Frontend (diretório `frontend/`)

```bash
npm run dev      # http://localhost:5173
npm run build
npm run lint
```

### Backend (diretório `backend/`)

No Windows, ative o ambiente antes de correr o servidor e os testes:

```powershell
.\backend\.venv\Scripts\Activate.ps1
uvicorn api:app --reload
pytest
```

Em sistemas Unix, use o `activate` correspondente à sua pasta `.venv`.

## Notas

- Para trabalho no backend, prefira o virtualenv em **`backend/.venv`** (pode existir também um `.venv` na raiz).
- O solucionador suporta algoritmos `dfs` e `bfs`, com `island_pruning` configurável na API.
