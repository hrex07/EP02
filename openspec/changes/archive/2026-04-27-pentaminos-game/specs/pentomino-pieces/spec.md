## ADDED Requirements

### Requirement: Define the 12 canonical pentomino pieces
The system SHALL define each of the 12 pentominoes (F, I, L, N, P, T, U, V, W, X, Y, Z) as a list of strings where `#` represents a filled cell.

#### Scenario: All 12 pieces are defined
- **WHEN** the pieces module is loaded
- **THEN** exactly 12 pieces are available, keyed by their letter name

### Requirement: Generate all orientations via rotation and reflection
The system SHALL generate all distinct orientations for each piece by applying 4 rotations (0°, 90°, 180°, 270°) and horizontal reflection, then deduplicating via normalization.

#### Scenario: Total orientation count
- **WHEN** all orientations are generated for all 12 pieces
- **THEN** the total count SHALL be 63

#### Scenario: Symmetric piece produces fewer orientations
- **WHEN** orientations are generated for piece "X"
- **THEN** exactly 1 orientation is produced

#### Scenario: Asymmetric piece produces 8 orientations
- **WHEN** orientations are generated for piece "F"
- **THEN** exactly 8 orientations are produced

### Requirement: Normalize orientation representation
Each orientation SHALL be represented as a sorted tuple of 5 `(row, col)` offsets with minimum row and column shifted to 0.

#### Scenario: Normalization produces consistent output
- **WHEN** two equivalent sets of cells are normalized (same shape, different absolute positions)
- **THEN** both produce the identical tuple

### Requirement: Rotation transforms coordinates correctly
Rotation 90° clockwise SHALL map `(r, c)` to `(c, -r)`, followed by normalization.

#### Scenario: Rotating a horizontal I-piece
- **WHEN** piece "I" in horizontal orientation `((0,0),(0,1),(0,2),(0,3),(0,4))` is rotated 90°
- **THEN** the result after normalization is `((0,0),(1,0),(2,0),(3,0),(4,0))`

### Requirement: Reflection transforms coordinates correctly
Horizontal reflection SHALL map `(r, c)` to `(r, -c)`, followed by normalization.

#### Scenario: Reflecting an asymmetric piece
- **WHEN** piece "F" is reflected
- **THEN** the result is a distinct orientation not present in rotations alone
