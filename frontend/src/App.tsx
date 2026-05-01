import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

/** Must stay aligned with backend `MAX_BOARD_DIM` default (40). */
const MAX_BOARD_DIM = 40

function clampBoardDim(n: number): number {
  const x = Math.floor(Number(n))
  if (!Number.isFinite(x)) return 1
  return Math.min(Math.max(1, x), MAX_BOARD_DIM)
}

type PieceInfo = {
  name: string
  id: number
  color: string
  orientations: number[][][]
}

type SolveStats = {
  time_ms: number
  states_explored: number
  states_in_avl: number
  states_pruned: number
  timed_out: boolean
}

function piecePreviewCells(orient: number[][]) {
  if (!orient.length) return { w: 1, h: 1, cells: new Set<string>() }
  let maxR = 0
  let maxC = 0
  for (const [r, c] of orient) {
    maxR = Math.max(maxR, r)
    maxC = Math.max(maxC, c)
  }
  const cells = new Set(orient.map(([r, c]) => `${r},${c}`))
  return { w: maxC + 1, h: maxR + 1, cells }
}

function PieceGlyph({
  orient,
  color,
  dimmed,
  selected,
  onClick,
}: {
  orient: number[][]
  color: string
  dimmed?: boolean
  selected?: boolean
  onClick?: () => void
}) {
  const { w, h, cells } = useMemo(() => piecePreviewCells(orient), [orient])
  const cell = 10
  const pad = 2
  return (
    <button
      type="button"
      className={`piece-glyph${selected ? ' selected' : ''}${dimmed ? ' dimmed' : ''}`}
      onClick={onClick}
      aria-label="Select piece"
    >
      <svg width={w * cell + pad * 2} height={h * cell + pad * 2}>
        {Array.from({ length: h }).map((_, r) =>
          Array.from({ length: w }).map((_, c) => (
            <rect
              key={`${r}-${c}`}
              x={pad + c * cell}
              y={pad + r * cell}
              width={cell - 1}
              height={cell - 1}
              rx={2}
              fill={cells.has(`${r},${c}`) ? color : 'var(--empty)'}
              stroke="var(--border)"
              strokeWidth={0.5}
            />
          )),
        )}
      </svg>
    </button>
  )
}

export default function App() {
  const [catalog, setCatalog] = useState<PieceInfo[]>([])
  const [mode, setMode] = useState<'play' | 'solve'>('play')
  const [rows, setRows] = useState(6)
  const [cols, setCols] = useState(10)
  const [gameId, setGameId] = useState<string | null>(null)
  const [board, setBoard] = useState<number[][]>([])
  const [placed, setPlaced] = useState<string[]>([])
  const [available, setAvailable] = useState<string[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [orientIdx, setOrientIdx] = useState(0)
  const [message, setMessage] = useState<string | null>(null)
  const [algorithm, setAlgorithm] = useState<'dfs' | 'bfs'>('dfs')
  const [findAll, setFindAll] = useState(false)
  const [islandPruning, setIslandPruning] = useState(true)
  const [solveBusy, setSolveBusy] = useState(false)
  const [solutions, setSolutions] = useState<number[][][]>([])
  const [stats, setStats] = useState<SolveStats | null>(null)

  const pieceMap = useMemo(() => Object.fromEntries(catalog.map((p) => [p.name, p])), [catalog])

  const loadCatalog = useCallback(async () => {
    const r = await fetch(`${API_BASE}/pieces`)
    if (!r.ok) throw new Error('Failed to load pieces')
    const j = await r.json()
    setCatalog(j.pieces as PieceInfo[])
  }, [])

  useEffect(() => {
    loadCatalog().catch(() => setMessage('Could not reach API. Start backend (uvicorn api:app).'))
  }, [loadCatalog])

  const newGame = useCallback(async () => {
    setMessage(null)
    setSolutions([])
    setStats(null)
    const br = clampBoardDim(rows)
    const bc = clampBoardDim(cols)
    if (br !== rows) setRows(br)
    if (bc !== cols) setCols(bc)
    try {
      const r = await fetch(`${API_BASE}/game/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: br, cols: bc }),
      })
      const j = await r.json()
      if (!r.ok) {
        setMessage(j.detail ?? 'Could not create game')
        return
      }
      setGameId(j.game_id)
      setBoard(j.board)
      setPlaced([])
      setAvailable(catalog.map((p) => p.name).sort())
      setSelected(null)
      setOrientIdx(0)
    } catch {
      setMessage('Network error creating game')
    }
  }, [rows, cols, catalog])

  useEffect(() => {
    if (!catalog.length) return
    void newGame()
  }, [catalog.length]) // eslint-disable-line react-hooks/exhaustive-deps -- initial bootstrap

  const refreshGame = useCallback(async (gid: string) => {
    const r = await fetch(`${API_BASE}/game/${gid}`)
    const j = await r.json()
    if (!r.ok) return
    setBoard(j.board)
    setPlaced(j.placed_pieces)
    setAvailable(j.available_pieces)
  }, [])

  const currentOrients = selected ? pieceMap[selected]?.orientations ?? [] : []
  const orientCoords = useMemo(() => {
    if (!selected || !currentOrients.length) return []
    const o = currentOrients[orientIdx % currentOrients.length]
    return o.map(([r, c]) => [r, c] as [number, number])
  }, [selected, currentOrients, orientIdx])

  const idToColor = useMemo(() => {
    const m: Record<number, string> = {}
    for (const p of catalog) m[p.id] = p.color
    return m
  }, [catalog])

  const applyDims = () => {
    const r = clampBoardDim(rows)
    const c = clampBoardDim(cols)
    if (r !== rows) setRows(r)
    if (c !== cols) setCols(c)
    if (r * c < 5) {
      setMessage('Area must be at least 5')
      return
    }
    void newGame()
  }

  const onCellClick = async (r: number, c: number) => {
    if (mode !== 'play' || !gameId || !selected) return
    setMessage(null)
    const body = {
      piece: selected,
      orientation: orientIdx % Math.max(1, currentOrients.length),
      row: r,
      col: c,
    }
    try {
      const res = await fetch(`${API_BASE}/game/${gameId}/place`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const j = await res.json()
      if (!res.ok) {
        setMessage(typeof j.detail === 'string' ? j.detail : 'Invalid placement')
        return
      }
      setBoard(j.board)
      await refreshGame(gameId)
    } catch {
      setMessage('Network error')
    }
  }

  const undo = async () => {
    if (!gameId) return
    setMessage(null)
    try {
      const res = await fetch(`${API_BASE}/game/${gameId}/undo`, { method: 'POST' })
      const j = await res.json()
      if (!res.ok) {
        setMessage(typeof j.detail === 'string' ? j.detail : 'Undo failed')
        return
      }
      setBoard(j.board)
      await refreshGame(gameId)
    } catch {
      setMessage('Network error')
    }
  }

  const runSolve = async () => {
    const r = clampBoardDim(rows)
    const c = clampBoardDim(cols)
    if (r !== rows) setRows(r)
    if (c !== cols) setCols(c)
    if (r * c < 5) {
      setMessage('Area must be at least 5')
      return
    }
    setSolveBusy(true)
    setMessage(null)
    setSolutions([])
    setStats(null)
    try {
      const res = await fetch(`${API_BASE}/solve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rows: r,
          cols: c,
          algorithm,
          find_all: findAll,
          island_pruning: islandPruning,
          timeout_sec: 120,
        }),
      })
      const j = await res.json()
      if (!res.ok) {
        setMessage(typeof j.detail === 'string' ? j.detail : 'Solve failed')
        setSolveBusy(false)
        return
      }
      setSolutions(j.solutions as number[][][])
      setStats(j.stats as SolveStats)
      if (j.solutions?.length === 0 && !j.stats?.timed_out) {
        setMessage('No solution found')
      }
    } catch {
      setMessage('Network error')
    }
    setSolveBusy(false)
  }

  const displayBoard = mode === 'solve' && solutions.length ? solutions[0] : board

  return (
    <div className="app">
      <header className="header">
        <h1>Pentaminós</h1>
        <div className="mode-toggle">
          <button type="button" className={mode === 'play' ? 'active' : ''} onClick={() => setMode('play')}>
            Jogar
          </button>
          <button type="button" className={mode === 'solve' ? 'active' : ''} onClick={() => setMode('solve')}>
            Resolver
          </button>
        </div>
      </header>

      <div className="layout">
        <section className="board-section">
          <div className="dims">
            <label>
              Linhas
              <input
                type="number"
                min={1}
                max={MAX_BOARD_DIM}
                value={rows}
                onChange={(e) => setRows(Number(e.target.value))}
              />
            </label>
            <label>
              Colunas
              <input
                type="number"
                min={1}
                max={MAX_BOARD_DIM}
                value={cols}
                onChange={(e) => setCols(Number(e.target.value))}
              />
            </label>
            <button type="button" onClick={applyDims}>
              Aplicar tabuleiro
            </button>
          </div>

          {displayBoard.length > 0 && (
            <div
              className="grid"
              style={{
                gridTemplateRows: `repeat(${displayBoard.length}, var(--cell))`,
                gridTemplateColumns: `repeat(${displayBoard[0].length}, var(--cell))`,
              }}
            >
              {displayBoard.map((row, r) =>
                row.map((v, c) => (
                  <button
                    type="button"
                    key={`${r}-${c}`}
                    className="cell"
                    style={{
                      background: v === 0 ? 'var(--empty)' : idToColor[v] ?? '#888',
                    }}
                    onClick={() => void onCellClick(r, c)}
                    disabled={mode !== 'play' || !selected}
                    aria-label={`Cell ${r},${c}`}
                  />
                )),
              )}
            </div>
          )}
        </section>

        <aside className="side">
          {mode === 'play' && (
            <>
              <h2>Peças</h2>
              <div className="piece-list">
                {catalog.map((p) => {
                  const used = !available.includes(p.name)
                  const o = p.orientations[0]?.map(([r, c]) => [r, c]) ?? []
                  return (
                    <PieceGlyph
                      key={p.name}
                      orient={o}
                      color={p.color}
                      dimmed={used}
                      selected={selected === p.name}
                      onClick={() => {
                        if (used) return
                        setSelected(p.name)
                        setOrientIdx(0)
                      }}
                    />
                  )
                })}
              </div>
              {selected && (
                <div className="orient-panel">
                  <div>Orientação</div>
                  <PieceGlyph orient={orientCoords} color={pieceMap[selected]?.color ?? '#888'} />
                  <button
                    type="button"
                    onClick={() =>
                      setOrientIdx((i) => (i + 1) % Math.max(1, currentOrients.length))
                    }
                  >
                    Girar
                  </button>
                </div>
              )}
              <div className="actions">
                <button type="button" onClick={() => void undo()} disabled={!gameId}>
                  Desfazer
                </button>
              </div>
              <p className="hint">Selecione uma peça, gire se precisar, clique na célula âncora (canto mínimo da peça).</p>
            </>
          )}

          {mode === 'solve' && (
            <div className="solve-panel">
              <h2>Solver</h2>
              <label>
                Algoritmo
                <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value as 'dfs' | 'bfs')}>
                  <option value="dfs">DFS</option>
                  <option value="bfs">BFS</option>
                </select>
              </label>
              <label className="check">
                <input type="checkbox" checked={findAll} onChange={(e) => setFindAll(e.target.checked)} disabled={algorithm === 'bfs'} />
                Todas as soluções (DFS)
              </label>
              <label className="check">
                <input
                  type="checkbox"
                  checked={islandPruning}
                  onChange={(e) => setIslandPruning(e.target.checked)}
                />
                Poda por ilhas
              </label>
              <button type="button" disabled={solveBusy} onClick={() => void runSolve()}>
                {solveBusy ? 'Resolvendo…' : 'Resolver'}
              </button>
              {stats && (
                <dl className="metrics">
                  <dt>Tempo (ms)</dt>
                  <dd>{stats.time_ms}</dd>
                  <dt>Estados explorados</dt>
                  <dd>{stats.states_explored}</dd>
                  <dt>Estados na AVL</dt>
                  <dd>{stats.states_in_avl}</dd>
                  <dt>Podados (ilhas)</dt>
                  <dd>{stats.states_pruned}</dd>
                  <dt>Timeout</dt>
                  <dd>{stats.timed_out ? 'sim' : 'não'}</dd>
                  <dt>Soluções</dt>
                  <dd>{solutions.length}</dd>
                </dl>
              )}
            </div>
          )}

          {message && <div className="msg">{message}</div>}
          {mode === 'play' && (
            <p className="meta">No tabuleiro: {placed.length} / {catalog.length} peças</p>
          )}
        </aside>
      </div>
    </div>
  )
}
