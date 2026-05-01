## ADDED Requirements

### Requirement: Create a new game session
The API SHALL provide `POST /game/new` accepting `rows` and `cols`, returning a `game_id` and empty board.

#### Scenario: Create 6x10 game
- **WHEN** POST /game/new with {"rows": 6, "cols": 10}
- **THEN** response contains a game_id and a 6×10 board of zeros

### Requirement: Place a piece in game mode
The API SHALL provide `POST /game/{id}/place` accepting piece name, orientation index, row, and col. Returns updated board or validation error.

#### Scenario: Valid placement
- **WHEN** POST /game/{id}/place with {"piece": "F", "orientation": 0, "row": 0, "col": 0}
- **THEN** response contains the updated board with piece placed

#### Scenario: Invalid placement
- **WHEN** the placement would overlap or go out of bounds
- **THEN** response contains an error message and the board is unchanged

### Requirement: Undo last placement
The API SHALL provide `POST /game/{id}/undo` to remove the last placed piece.

#### Scenario: Undo with history
- **WHEN** POST /game/{id}/undo and at least one piece has been placed
- **THEN** the last piece is removed and the updated board is returned

#### Scenario: Undo with empty board
- **WHEN** POST /game/{id}/undo and no pieces have been placed
- **THEN** response contains an error indicating nothing to undo

### Requirement: Get game state
The API SHALL provide `GET /game/{id}` returning current board, placed pieces, and available pieces.

#### Scenario: Retrieve game state
- **WHEN** GET /game/{id}
- **THEN** response contains board matrix, list of placed pieces, and list of available pieces with their orientations

### Requirement: Solve the puzzle
The API SHALL provide `POST /solve` accepting rows, cols, algorithm ("dfs" or "bfs"), find_all (bool), and island_pruning (bool). Returns solutions and metrics.

#### Scenario: Solve with DFS
- **WHEN** POST /solve with {"rows": 6, "cols": 10, "algorithm": "dfs", "find_all": false, "island_pruning": true}
- **THEN** response contains the solution board and stats

#### Scenario: Solve with BFS
- **WHEN** POST /solve with {"algorithm": "bfs"}
- **THEN** response contains the solution (if found within limits) and stats

### Requirement: List available pieces and orientations
The API SHALL provide `GET /pieces` returning all 12 pieces with their orientations.

#### Scenario: Get pieces catalog
- **WHEN** GET /pieces
- **THEN** response contains 12 pieces, each with name, orientations count, and orientation shapes
