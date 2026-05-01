# Project: Pentominoes Game (EP02)

## Architecture

- **frontend/**: React 19 + TypeScript + Vite. Entry point: `src/main.tsx`
- **backend/**: Python + FastAPI. Entry point: `api.py` (runs at `http://localhost:8000`)
- **openspec/**: Spec-driven development with `.openspec.yaml` files in `changes/`

## Commands

### Frontend (from `frontend/`)
```bash
npm run dev      # Dev server at http://localhost:5173
npm run build    # TypeScript build (tsc -b && vite build)
npm run lint     # ESLint
```

### Backend (from `backend/`)
```bash
backend\.venv\Scripts\Activate.ps1   # Activate venv first
# Then run:
uvicorn api:app --reload   # Dev server
pytest                     # All tests
pytest tests/test_solver.py -v  # Single test file
```

### Environment setup (Windows/PowerShell)
```powershell
.\backend\setup_env.ps1   # Sets CORS origins, Firestore env vars
```

## Key Details

- Two Python venvs: root `.venv` and `backend/.venv`. Use `backend/.venv` for backend work.
- CORS is permissive (`allow_origins=["*"]`) in `api.py`
- Solver supports `dfs` and `bfs` algorithms with island pruning
- `openspec/config.yaml` defines spec-driven workflow; use `opsx` commands to propose/archive changes