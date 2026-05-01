## 1. Project Setup

- [x] 1.1 Create backend/ directory with requirements.txt (fastapi, uvicorn, pydantic)
- [x] 1.2 Create frontend/ directory with Vite + React + TypeScript scaffold
- [x] 1.3 Configure CORS in FastAPI to allow frontend requests

## 2. Pentomino Pieces (pentominoes.py)

- [x] 2.1 Define the 12 canonical pieces as string grids
- [x] 2.2 Implement parse function to convert string grid to list of (row, col) coordinates
- [x] 2.3 Implement normalize function (shift to min 0,0 + sort → tuple)
- [x] 2.4 Implement rotate_90 and reflect transformations
- [x] 2.5 Implement all_orientations generator (4 rotations × 2 reflections, deduplicated)
- [x] 2.6 Build PIECES dict mapping piece name → list of orientation tuples
- [x] 2.7 Define PIECE_COLORS dict mapping piece name → hex color
- [x] 2.8 Verify total unique orientations (55 D4-normalized; see tests and pentominoes.py)

## 3. Board State (board.py)

- [x] 3.1 Implement Board class with create(rows, cols), validate dimensions (area ≥ 5)
- [x] 3.2 Implement place_piece(board, piece_id, orientation, row, col) with bounds and overlap validation
- [x] 3.3 Implement remove_piece(board, piece_id) — reset cells to 0
- [x] 3.4 Implement find_first_empty(board) — left-to-right, top-to-bottom scan
- [x] 3.5 Implement to_key(board) — convert matrix to tuple of tuples
- [x] 3.6 Implement detect_islands(board) — BFS/flood-fill on empty cells, check each region size % 5 == 0

## 4. AVL Tree (avl.py)

- [x] 4.1 Implement AVLNode class (key, height, left, right)
- [x] 4.2 Implement height and balance_factor helper functions
- [x] 4.3 Implement right rotation (LL case)
- [x] 4.4 Implement left rotation (RR case)
- [x] 4.5 Implement balance function (handles LL, RR, LR, RL)
- [x] 4.6 Implement insert (recursive, with rebalancing on return)
- [x] 4.7 Implement search (recursive BST search)
- [x] 4.8 Implement AVLTree wrapper class with public insert, search, size methods

## 5. Solver Engine (solver.py)

- [x] 5.1 Implement generate_neighbors — find first empty cell, try all unused pieces/orientations at offsets covering that cell
- [x] 5.2 Implement DFS solver with AVL for visited states, support find_all flag
- [x] 5.3 Implement BFS solver with FIFO queue and AVL for visited states
- [x] 5.4 Add island pruning as optional flag — check before AVL insertion
- [x] 5.5 Implement SolverStats dataclass (time_ms, states_explored, states_in_avl, states_pruned)
- [x] 5.6 Add timeout mechanism to prevent infinite runs

## 6. Game API (api.py)

- [x] 6.1 Implement GET /pieces — return all pieces with orientations and colors
- [x] 6.2 Implement POST /game/new — create game session, return game_id and empty board
- [x] 6.3 Implement GET /game/{id} — return current board, placed pieces, available pieces
- [x] 6.4 Implement POST /game/{id}/place — validate and place piece, return updated state
- [x] 6.5 Implement POST /game/{id}/undo — remove last placed piece
- [x] 6.6 Implement POST /solve — run DFS or BFS with config, return solutions and stats

## 7. Frontend — Layout and Board

- [x] 7.1 Create main layout: board area (left), side panel (right)
- [x] 7.2 Implement board grid component rendering m×n cells with piece colors
- [x] 7.3 Implement board dimension inputs (rows, cols) with validation
- [x] 7.4 Implement mode selector (Play / Solve)

## 8. Frontend — Play Mode

- [x] 8.1 Implement piece selection panel showing all 12 pieces, dimming used ones
- [x] 8.2 Implement orientation control (rotate button with visual preview)
- [x] 8.3 Implement click-to-place: click cell → send place request → update board
- [x] 8.4 Implement undo button
- [x] 8.5 Display validation feedback (valid/invalid placement messages)

## 9. Frontend — Solve Mode

- [x] 9.1 Implement solver config panel (algorithm dropdown, find_all checkbox, island_pruning checkbox)
- [x] 9.2 Implement solve button that sends config to POST /solve
- [x] 9.3 Display solution board(s) on completion
- [x] 9.4 Display metrics panel (time, states explored, states in AVL, states pruned)

## 10. Integration and Testing

- [x] 10.1 Test pentomino piece generation (count orientations per piece and total)
- [x] 10.2 Test AVL tree operations (insert, search, rotations, balance)
- [x] 10.3 Test solver on small board (5×4 with subset of pieces)
- [x] 10.4 End-to-end test: solve 6×10 with DFS + island pruning
