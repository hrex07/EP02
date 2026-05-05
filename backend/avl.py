"""Árvore AVL para armazenar chaves de estados visitados na busca.

Implementa um conjunto ordenado sem duplicados: inserção e busca em tempo
O(log n) no pior caso, com balanceamento por rotações após cada inserção.
As chaves são comparáveis (ex.: tuplas derivadas do tabuleiro em ``board.to_key``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AVLNode:
    """Nó interno da árvore AVL.

    Attributes:
        key: Chave ordenável armazenada neste nó.
        height: Altura da subárvore enraizada neste nó (folhas = 1).
        left: Filho à esquerda ou ``None``.
        right: Filho à direita ou ``None``.
    """

    key: Any
    height: int = 1
    left: Optional[AVLNode] = None
    right: Optional[AVLNode] = None


def _height(node: Optional[AVLNode]) -> int:
    """Retorna a altura armazenada do nó ou 0 se for ``None``.

    Args:
        node: Nó da árvore ou subárvore vazia.

    Returns:
        Altura do nó; 0 para árvore vazia.
    """
    # Pseudocódigo:
    # 1. SE nó é vazio ENTÃO retornar 0
    # 2. SENÃO retornar node.height
    return node.height if node else 0


def _balance_factor(node: AVLNode) -> int:
    """Calcula o fator de balanceamento AVL do nó.

    Args:
        node: Nó não nulo.

    Returns:
        altura(esquerda) - altura(direita).
    """
    # Pseudocódigo:
    # 1. obter altura da subárvore esquerda
    # 2. obter altura da subárvore direita
    # 3. retornar (esquerda - direita)
    return _height(node.left) - _height(node.right)


def _update_height(node: AVLNode) -> None:
    """Atualiza ``node.height`` com base nas alturas dos filhos.

    Args:
        node: Nó cuja altura será recalculada.
    """
    # Pseudocódigo:
    # 1. h_esq <- altura do filho esquerdo (0 se None)
    # 2. h_dir <- altura do filho direito (0 se None)
    # 3. node.height <- 1 + max(h_esq, h_dir)
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_right(y: AVLNode) -> AVLNode:
    """Rotação simples à direita em torno de ``y`` (LL case).

    Args:
        y: Nó desbalanceado com subárvore esquerda mais alta.

    Returns:
        Nova raiz da subárvore após a rotação.

    Raises:
        AssertionError: Se ``y.left`` for ``None`` (uso interno inconsistente).
    """
    # Pseudocódigo:
    # 1. x <- y.esquerda
    # 2. T2 <- x.direita
    # 3. x.direita <- y
    # 4. y.esquerda <- T2
    # 5. atualizar altura de y, depois de x
    # 6. retornar x como nova raiz local
    x = y.left
    assert x is not None
    t2 = x.right
    x.right = y
    y.left = t2
    _update_height(y)
    _update_height(x)
    return x


def _rotate_left(x: AVLNode) -> AVLNode:
    """Rotação simples à esquerda em torno de ``x`` (RR case).

    Args:
        x: Nó desbalanceado com subárvore direita mais alta.

    Returns:
        Nova raiz da subárvore após a rotação.

    Raises:
        AssertionError: Se ``x.right`` for ``None`` (uso interno inconsistente).
    """
    # Pseudocódigo:
    # 1. y <- x.direita
    # 2. T2 <- y.esquerda
    # 3. y.esquerda <- x
    # 4. x.direita <- T2
    # 5. atualizar altura de x, depois de y
    # 6. retornar y como nova raiz local
    y = x.right
    assert y is not None
    t2 = y.left
    y.left = x
    x.right = t2
    _update_height(x)
    _update_height(y)
    return y


def _balance(node: AVLNode) -> AVLNode:
    """Rebalanceia o nó se o fator AVL sair do intervalo [-1, 1].

    Args:
        node: Nó potencialmente desbalanceado.

    Returns:
        Raiz da subárvore balanceada (pode ser o próprio ``node`` ou um filho após rotação).
    """
    # Pseudocódigo:
    # 1. atualizar altura de node
    # 2. bf <- fator de balanceamento de node
    # 3. SE bf > 1 (pesado à esquerda):
    #       SE filho esquerdo está "quebrado" para direita: rotação esquerda no filho esquerdo
    #       rotação direita em node
    # 4. SE bf < -1 (pesado à direita):
    #       SE filho direito está "quebrado" para esquerda: rotação direita no filho direito
    #       rotação esquerda em node
    # 5. SENÃO retornar node
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
    """Insere ``key`` na subárvore enraizada em ``node``, mantendo AVL.

    Args:
        node: Raiz atual ou ``None``.
        key: Chave a inserir; duplicatas não são permitidas.

    Returns:
        Tupla ``(nova_raiz, inseriu)`` onde ``inseriu`` é ``False`` se ``key`` já existia.
    """
    # Pseudocódigo:
    # 1. SE node é None ENTÃO criar folha com key; retornar (folha, True)
    # 2. SE key < node.key ENTÃO
    #        node.esquerda, ok <- _insert(node.esquerda, key)
    #        SE não ok ENTÃO retornar (node, False)
    #        retornar (_balance(node), True)
    # 3. SE key > node.key ENTÃO (simétrico à direita)
    # 4. SENÃO chave duplicada: retornar (node, False)
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
    """Busca ``key`` na subárvore enraizada em ``node``.

    Args:
        node: Raiz atual ou ``None``.
        key: Chave procurada.

    Returns:
        ``True`` se ``key`` existe; caso contrário ``False``.
    """
    # Pseudocódigo:
    # 1. SE node é None ENTÃO retornar False
    # 2. SE key == node.key ENTÃO retornar True
    # 3. SE key < node.key ENTÃO retornar busca(node.esquerda, key)
    # 4. SENÃO retornar busca(node.direita, key)
    if node is None:
        return False
    if key == node.key:
        return True
    if key < node.key:
        return _search(node.left, key)
    return _search(node.right, key)


def _size(node: Optional[AVLNode]) -> int:
    """Conta nós na subárvore (uso interno / verificação).

    Args:
        node: Raiz ou ``None``.

    Returns:
        Número de nós.
    """
    # Pseudocódigo:
    # 1. SE node é None ENTÃO retornar 0
    # 2. retornar 1 + tamanho(esquerda) + tamanho(direita)
    if node is None:
        return 0
    return 1 + _size(node.left) + _size(node.right)


class AVLTree:
    """Árvore AVL como conjunto ordenado de chaves únicas.

    Attributes:
        _root: Raiz interna ou ``None`` se vazia.
        _count: Número de chaves distintas armazenadas.
    """

    def __init__(self) -> None:
        """Inicializa árvore vazia."""
        self._root: Optional[AVLNode] = None
        self._count = 0

    def insert(self, key: Any) -> bool:
        """Insere uma chave na árvore.

        Args:
            key: Valor comparável; duplicatas são ignoradas.

        Returns:
            ``True`` se a chave foi inserida; ``False`` se já existia.
        """
        # Pseudocódigo:
        # 1. (_root, inseriu) <- _insert(_root, key)
        # 2. SE inseriu ENTÃO incrementar _count
        # 3. retornar inseriu
        self._root, ins = _insert(self._root, key)
        if ins:
            self._count += 1
        return ins

    def search(self, key: Any) -> bool:
        """Verifica se ``key`` está na árvore.

        Args:
            key: Chave procurada.

        Returns:
            ``True`` se existir; caso contrário ``False``.
        """
        # Pseudocódigo:
        # 1. retornar _search(_root, key)
        return _search(self._root, key)

    def __len__(self) -> int:
        """Número de chaves armazenadas."""
        return self._count

    def size_verify(self) -> int:
        """Conta nós percorrendo a árvore (útil para testes).

        Returns:
            Contagem recursiva de nós a partir da raiz.
        """
        # Pseudocódigo:
        # 1. retornar _size(_root)
        return _size(self._root)
