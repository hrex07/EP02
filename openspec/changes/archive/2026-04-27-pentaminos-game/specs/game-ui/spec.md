## ADDED Requirements

### Requirement: Board grid display
The UI SHALL render the board as a colored grid where each piece has a distinct color and empty cells are visually distinct.

#### Scenario: Empty board
- **WHEN** a new game is started
- **THEN** all cells are rendered in the empty color

#### Scenario: Board with pieces
- **WHEN** pieces are placed on the board
- **THEN** each piece's cells are rendered in that piece's assigned color

### Requirement: Piece selection panel
The UI SHALL display all 12 pieces in a side panel. Used pieces are visually dimmed. The user selects a piece by clicking it.

#### Scenario: Select a piece
- **WHEN** user clicks on piece "T" in the panel
- **THEN** piece "T" is highlighted as selected and its current orientation is shown

#### Scenario: Already used piece
- **WHEN** piece "T" is already on the board
- **THEN** it appears dimmed and cannot be selected

### Requirement: Orientation control
The UI SHALL provide a button to rotate the selected piece through its available orientations.

#### Scenario: Rotate piece
- **WHEN** user clicks the rotate button
- **THEN** the preview shows the next orientation of the selected piece

### Requirement: Place piece by clicking the board
The UI SHALL place the selected piece at the cell the user clicks (using that cell as the piece's top-left anchor).

#### Scenario: Click to place
- **WHEN** user has piece "L" selected in orientation 2 and clicks cell (1, 3)
- **THEN** the system attempts to place piece "L" orientation 2 at row=1, col=3

### Requirement: Mode selector
The UI SHALL allow switching between Play mode and Solve mode.

#### Scenario: Switch to Solve mode
- **WHEN** user selects Solve mode
- **THEN** the solver configuration panel is shown (algorithm, find_all, island_pruning)

### Requirement: Solver configuration panel
The UI SHALL provide controls for: algorithm (DFS/BFS), find all solutions (checkbox), and island pruning (checkbox).

#### Scenario: Configure and run solver
- **WHEN** user selects DFS, enables island pruning, disables find_all, and clicks Solve
- **THEN** the solver request is sent with those parameters

### Requirement: Metrics display
The UI SHALL display solver results: number of solutions found, elapsed time, states explored, and states in AVL.

#### Scenario: Solver completes
- **WHEN** solver returns results
- **THEN** all four metrics are displayed alongside the solution board

### Requirement: Board dimension configuration
The UI SHALL allow the user to set board rows and columns before starting a game or solving.

#### Scenario: Set custom dimensions
- **WHEN** user sets rows=5, cols=12
- **THEN** the board is rendered as 5×12 and the solver uses those dimensions
