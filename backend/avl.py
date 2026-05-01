"""AVL tree for visited state keys (order-statistic BST, no duplicates)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AVLNode:
    key: Any
    height: int = 1
    left: Optional[AVLNode] = None
    right: Optional[AVLNode] = None


def _height(node: Optional[AVLNode]) -> int:
    return node.height if node else 0


def _balance_factor(node: AVLNode) -> int:
    return _height(node.left) - _height(node.right)


def _update_height(node: AVLNode) -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_right(y: AVLNode) -> AVLNode:
    x = y.left
    assert x is not None
    t2 = x.right
    x.right = y
    y.left = t2
    _update_height(y)
    _update_height(x)
    return x


def _rotate_left(x: AVLNode) -> AVLNode:
    y = x.right
    assert y is not None
    t2 = y.left
    y.left = x
    x.right = t2
    _update_height(x)
    _update_height(y)
    return y


def _balance(node: AVLNode) -> AVLNode:
    _update_height(node)
    bf = _balance_factor(node)
    if bf > 1:
        assert node.left is not None
        if _balance_factor(node.left) < 0:
            node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if bf < -1:
        assert node.right is not None
        if _balance_factor(node.right) > 0:
            node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


def _insert(node: Optional[AVLNode], key: Any) -> tuple[Optional[AVLNode], bool]:
    """Returns (new_root, inserted) where inserted is False if duplicate."""
    if node is None:
        return AVLNode(key=key), True
    if key < node.key:
        node.left, ins = _insert(node.left, key)
        if not ins:
            return node, False
        return _balance(node), True
    if key > node.key:
        node.right, ins = _insert(node.right, key)
        if not ins:
            return node, False
        return _balance(node), True
    return node, False


def _search(node: Optional[AVLNode], key: Any) -> bool:
    if node is None:
        return False
    if key == node.key:
        return True
    if key < node.key:
        return _search(node.left, key)
    return _search(node.right, key)


def _size(node: Optional[AVLNode]) -> int:
    if node is None:
        return 0
    return 1 + _size(node.left) + _size(node.right)


class AVLTree:
    def __init__(self) -> None:
        self._root: Optional[AVLNode] = None
        self._count = 0

    def insert(self, key: Any) -> bool:
        """Insert key. Returns True if inserted, False if duplicate."""
        self._root, ins = _insert(self._root, key)
        if ins:
            self._count += 1
        return ins

    def search(self, key: Any) -> bool:
        return _search(self._root, key)

    def __len__(self) -> int:
        return self._count

    def size_verify(self) -> int:
        return _size(self._root)
