## ADDED Requirements

### Requirement: Generate neighbors via implicit graph
The system SHALL generate neighbor states by finding the first empty cell and trying all unused pieces in all orientations at offsets that cover that cell. Each valid placement yields a new state (edge in the implicit graph).

#### Scenario: Generate neighbors for partially filled board
- **WHEN** a board has 2 pieces placed and 10 remaining
- **THEN** neighbors are generated only for placements covering the first empty cell

#### Scenario: No valid neighbors
- **WHEN** no remaining piece fits at the first empty cell
- **THEN** zero neighbors are generated (dead end)

### Requirement: DFS solver
The system SHALL implement depth-first search via recursive backtracking over the implicit graph, using the AVL tree to track visited states.

#### Scenario: Find one solution
- **WHEN** DFS runs with find_all=false on a solvable board
- **THEN** the first solution found is returned along with stats (time, states explored)

#### Scenario: Find all solutions
- **WHEN** DFS runs with find_all=true
- **THEN** all distinct solutions are returned along with stats

#### Scenario: No solution exists
- **WHEN** DFS runs on an unsolvable board configuration
- **THEN** an empty result is returned with stats

### Requirement: BFS solver
The system SHALL implement breadth-first search over the implicit graph using a FIFO queue, with the AVL tree to track visited states. BFS finds the solution at minimum depth.

#### Scenario: Find solution at minimum depth
- **WHEN** BFS runs on a solvable board
- **THEN** the first solution found is at the shallowest depth

#### Scenario: BFS on large board
- **WHEN** BFS runs on a 6×10 board with all 12 pieces
- **THEN** the system MAY timeout due to memory/time constraints (expected behavior, document in metrics)

### Requirement: Collect solver metrics
The system SHALL track and return: elapsed time (ms), number of states explored, number of states stored in the AVL tree, and number of states pruned.

#### Scenario: Metrics returned on completion
- **WHEN** a solver run completes (DFS or BFS)
- **THEN** all four metrics are present in the response

### Requirement: Optional island pruning
The system SHALL accept a configuration flag to enable/disable island pruning. When enabled, states with empty regions whose size is not a multiple of 5 are discarded before AVL insertion.

#### Scenario: Island pruning enabled
- **WHEN** solver runs with island_pruning=true
- **THEN** states with invalid empty regions are skipped and counted as pruned

#### Scenario: Island pruning disabled
- **WHEN** solver runs with island_pruning=false
- **THEN** no island check is performed; all valid placements are explored
