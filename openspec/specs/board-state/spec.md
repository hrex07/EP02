## ADDED Requirements

### Requirement: Create board with arbitrary dimensions
The system SHALL create a board as a 2D matrix of integers with configurable rows and columns. Value 0 represents an empty cell; values 1-12 represent placed pieces.

#### Scenario: Create 6x10 board
- **WHEN** a board is created with rows=6, cols=10
- **THEN** a 6×10 matrix of zeros is returned

#### Scenario: Reject invalid dimensions
- **WHEN** a board is created with area < 5
- **THEN** the system SHALL reject with a validation error

### Requirement: Place a piece on the board
The system SHALL place a piece orientation at a given position (row, col) on the board, writing the piece ID into the covered cells.

#### Scenario: Valid placement
- **WHEN** piece "F" (id=1) orientation 0 is placed at (0,0) on an empty 6×10 board
- **THEN** the 5 cells covered by the orientation are set to 1 and the updated board is returned

#### Scenario: Placement out of bounds
- **WHEN** a piece orientation would extend beyond board boundaries
- **THEN** the placement SHALL be rejected

#### Scenario: Placement overlaps existing piece
- **WHEN** a piece orientation would cover a cell already occupied (value > 0)
- **THEN** the placement SHALL be rejected

### Requirement: Remove a piece from the board
The system SHALL remove a piece by resetting its cells to 0.

#### Scenario: Undo placement
- **WHEN** piece with id=1 is removed from the board
- **THEN** all cells with value 1 are set to 0

### Requirement: Find first empty cell
The system SHALL locate the first empty cell scanning left-to-right, top-to-bottom.

#### Scenario: Partially filled board
- **WHEN** rows 0-1 columns 0-4 are filled
- **THEN** first empty cell returned is (0, 5)

#### Scenario: Full board
- **WHEN** no empty cells exist
- **THEN** None is returned (board is complete)

### Requirement: Generate state key for AVL
The system SHALL convert the board matrix into a tuple of tuples suitable as an AVL key with lexicographic comparison.

#### Scenario: Key uniqueness
- **WHEN** two boards differ by at least one cell
- **THEN** their keys SHALL be different

#### Scenario: Key consistency
- **WHEN** the same board is converted to key twice
- **THEN** both keys SHALL be identical

### Requirement: Detect islands (optional pruning)
The system SHALL detect disconnected regions of empty cells and verify each region's size is a multiple of 5. This check is only executed when the user enables island pruning.

#### Scenario: Board with valid regions
- **WHEN** island detection runs on a board where all empty regions have sizes that are multiples of 5
- **THEN** the board is considered valid

#### Scenario: Board with invalid region
- **WHEN** island detection runs on a board with an empty region of size 3
- **THEN** the board is considered invalid (unprunable)

#### Scenario: Island pruning disabled
- **WHEN** island pruning is disabled in solver configuration
- **THEN** island detection is NOT executed
