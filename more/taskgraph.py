from typing import List, Sequence, Tuple


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.parents = []
        self.nodes = {}

    def __str__(self) -> str:
        return self.name

    def add_child(self, node):
        if node not in self.children:
            self.children.append(node)
        if self not in node.parents:
            node.parents.append(self)

    def add_parent(self, node):
        if node not in self.parents:
            self.parents.append(node)
        if self not in node.children:
            node.children.append(self)

    @staticmethod
    def get_or_set(nodeset, name: str):
        "从节点字典中取出指定名称的节点，没有则创建"
        if name in nodeset:
            return nodeset[name]
        node = Node(name)
        nodeset[name] = node
        return node

    @staticmethod
    def get_parentless_nodes(nodeset):
        "获取节点字典中没有父节点的所有节点"
        return [node for node in nodeset.values() if len(node.parents) == 0]

    def bfs(self):
        def list_children(_nodes):
            _children = []
            for _node in _nodes:
                _children = [*_children, *_node.children]
            return _children

        children: List[Node] = [*self.children]
        while len(children) > 0:
            yield children
            children = list_children(children)

    def descendants(self) -> Sequence["Node"]:
        items = []
        for layer_nodes in self.bfs():
            items = [*items, *layer_nodes]
        return items

    @staticmethod
    def get_uniq_root(nodes: Sequence["Node"]):
        root = Node("__ROOT__")
        for node in nodes:
            if len(node.parents) == 0:
                root.add_child(node)
        return root


def sort_dependencies(dependencies: Sequence[Tuple[str, str]]) -> Sequence[str]:
    nodes = {}
    for dep in dependencies:
        prev = Node.get_or_set(nodes, dep[0] or "START")
        next = Node.get_or_set(nodes, dep[1] or "START")
        prev.add_child(next)

    parentless_nodes = Node.get_parentless_nodes(nodes)

    dup_ordered_items = []

    def tree(_nodes):
        _children = []
        for _node in _nodes:
            dup_ordered_items.append(_node.name)
            _children = [*_children, *_node.children]
        if len(_children) == 0:
            return
        tree(_children)

    tree(parentless_nodes)

    ordered_items = []
    for i in dup_ordered_items[::-1]:
        if i not in ordered_items:
            ordered_items.append(i)

    ordered_items = ordered_items[::-1]
    return [i for i in ordered_items if i != "START"]
