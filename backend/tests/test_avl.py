"""AVL tree."""

import random

from avl import AVLTree


def test_insert_search():
    t = AVLTree()
    assert t.insert(5) is True
    assert t.search(5) is True
    assert t.search(3) is False


def test_duplicate_insert():
    t = AVLTree()
    assert t.insert(1) is True
    assert t.insert(1) is False
    assert len(t) == 1


def test_many_integers():
    t = AVLTree()
    keys = list(range(100))
    random.shuffle(keys)
    for k in keys:
        t.insert(k)
    assert len(t) == 100
    for k in keys:
        assert t.search(k) is True


def test_tuple_keys():
    t = AVLTree()
    a = ((0, 0), (0, 1))
    b = ((0, 0), (1, 0))
    assert t.insert(a) is True
    assert t.insert(b) is True
    assert t.search(a) is True
    assert len(t) == 2
