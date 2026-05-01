## ADDED Requirements

### Requirement: AVL node structure
Each AVL node SHALL store a key (tuple), height (int), left child (node or None), and right child (node or None).

#### Scenario: Leaf node
- **WHEN** a node is created with a key and no children
- **THEN** height is 1, left and right are None

### Requirement: Insert key into AVL tree
The system SHALL insert a key maintaining BST order and AVL balance. Duplicate keys SHALL be ignored.

#### Scenario: Insert into empty tree
- **WHEN** a key is inserted into an empty tree
- **THEN** the key becomes the root with height 1

#### Scenario: Insert duplicate key
- **WHEN** a key already present in the tree is inserted again
- **THEN** the tree remains unchanged

#### Scenario: Insert triggers rebalancing
- **WHEN** three keys are inserted in ascending order (causing right-heavy imbalance)
- **THEN** a left rotation occurs and the tree height is 2

### Requirement: Search key in AVL tree
The system SHALL search for a key and return True if found, False otherwise, in O(log n) time.

#### Scenario: Key exists
- **WHEN** searching for a key that was previously inserted
- **THEN** True is returned

#### Scenario: Key does not exist
- **WHEN** searching for a key not in the tree
- **THEN** False is returned

### Requirement: AVL rotations maintain balance
The tree SHALL apply single (LL, RR) and double (LR, RL) rotations to maintain balance factor in {-1, 0, +1} for every node after insertion.

#### Scenario: Left-Left case (LL)
- **WHEN** a node has balance factor +2 and its left child has balance factor >= 0
- **THEN** a single right rotation is performed

#### Scenario: Right-Right case (RR)
- **WHEN** a node has balance factor -2 and its right child has balance factor <= 0
- **THEN** a single left rotation is performed

#### Scenario: Left-Right case (LR)
- **WHEN** a node has balance factor +2 and its left child has balance factor < 0
- **THEN** a left rotation on the left child followed by a right rotation on the node is performed

#### Scenario: Right-Left case (RL)
- **WHEN** a node has balance factor -2 and its right child has balance factor > 0
- **THEN** a right rotation on the right child followed by a left rotation on the node is performed

### Requirement: Report tree size
The system SHALL report the number of keys stored in the AVL tree.

#### Scenario: Size after insertions
- **WHEN** 5 distinct keys are inserted
- **THEN** size returns 5
