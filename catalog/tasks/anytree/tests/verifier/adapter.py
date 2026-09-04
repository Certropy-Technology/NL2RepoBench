#!/usr/bin/env python3
"""Child-side, fixed-scenario adapter for the anytree public API.

Only a scenario token and a candidate site path cross the trusted boundary.
Callbacks are defined here and all node objects stay inside this process.
"""

from __future__ import annotations

import argparse
import io
import json
import tempfile
import traceback
from pathlib import Path


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect(exc_type: type[BaseException], function, message: str) -> None:
    try:
        function()
    except exc_type:
        return
    except BaseException as exc:
        raise AssertionError(
            f"{message}: expected {exc_type.__name__}, got {type(exc).__name__}"
        ) from exc
    raise AssertionError(f"{message}: expected {exc_type.__name__}")


def names(nodes) -> list[str]:
    return [str(node.name) for node in nodes]


def paths(nodes) -> list[str]:
    return [node.separator.join(str(part.name) for part in node.path) for node in nodes]


def make_tree():
    from anytree import Node

    root = Node("root")
    left = Node("left", root, rank=1)
    right = Node("right", root, rank=2)
    Node("left-a", left, rank=3)
    Node("left-b", left, rank=4)
    Node("right-a", right, rank=5)
    Node("right-b", right, rank=6)
    return root, left, right


def api_surface() -> None:
    import anytree
    from anytree import (
        AnyNode,
        LevelGroupOrderIter,
        LevelOrderGroupIter,
        LevelOrderIter,
        Node,
        PreOrderIter,
        RenderTree,
        Resolver,
        SymlinkNode,
    )
    from anytree.exporter import DictExporter, JsonExporter, MermaidExporter
    from anytree.importer import DictImporter, JsonImporter
    from anytree.iterators import AbstractIter, PostOrderIter, ZigZagGroupIter
    from anytree.node import NodeMixin, TreeError
    from anytree.util import commonancestors, leftsibling, rightsibling

    required = {
        "Node": Node,
        "AnyNode": AnyNode,
        "LevelOrderIter": LevelOrderIter,
        "PreOrderIter": PreOrderIter,
        "PostOrderIter": PostOrderIter,
        "RenderTree": RenderTree,
        "Resolver": Resolver,
        "SymlinkNode": SymlinkNode,
        "DictExporter": DictExporter,
        "JsonExporter": JsonExporter,
        "MermaidExporter": MermaidExporter,
        "DictImporter": DictImporter,
        "JsonImporter": JsonImporter,
        "AbstractIter": AbstractIter,
        "NodeMixin": NodeMixin,
        "TreeError": TreeError,
        "commonancestors": commonancestors,
        "leftsibling": leftsibling,
        "rightsibling": rightsibling,
    }
    check(all(value is not None for value in required.values()), "missing public symbol")
    check(LevelGroupOrderIter is LevelOrderGroupIter, "legacy iterator alias changed")
    check(all(name in dir(anytree) for name in required if name in {"Node", "AnyNode", "LevelOrderIter", "PreOrderIter", "PostOrderIter", "RenderTree", "Resolver", "SymlinkNode", "NodeMixin", "TreeError"}), "root package lost a public symbol")
    check(isinstance(anytree.__version__, str), "version metadata is absent")
    check(isinstance(anytree.__url__, str) and anytree.__url__, "source URL metadata is absent")


def node_relationships() -> None:
    from anytree import Node

    root, left, right = make_tree()
    check(root.children == (left, right), "children order changed")
    check(left.parent is root and left.root is root, "parent/root relation failed")
    check(left.path == (root, left), "path relation failed")
    check(tuple(left.iter_path_reverse()) == (left, root), "reverse path failed")
    check(
        names(root.descendants)
        == ["left", "left-a", "left-b", "right", "right-a", "right-b"],
        "descendants order failed",
    )
    check(names(root.leaves) == ["left-a", "left-b", "right-a", "right-b"], "leaves failed")
    check(left.siblings == (right,), "siblings failed")
    check(root.is_root and not root.is_leaf, "root/leaf flags failed")
    check(left.height == 1 and left.depth == 1 and root.height == 2, "height/depth failed")
    check(root.size == 7 and left.size == 3, "subtree size failed")
    check(repr(root) == "Node('/root')", "node repr failed")
    check(repr(left) == "Node('/root/left', rank=1)", "attribute repr failed")
    check(root.separator == "/", "default separator changed")


def mutation_and_cycles() -> None:
    from anytree import Node
    from anytree.node import LoopError, TreeError

    root = Node("root")
    first = Node("first", root)
    second = Node("second", root)
    moved = Node("moved", first)
    moved.parent = second
    check(first.children == () and second.children == (moved,), "reparenting failed")
    before = second.children
    expect(LoopError, lambda: setattr(root, "parent", moved), "cycle was accepted")
    check(second.children == before and root.parent is None, "cycle changed the tree")
    expect(TreeError, lambda: Node("dup", children=[first, first]), "duplicate children accepted")
    check(first.parent is root, "duplicate-child rejection detached node")
    second.children = [Node("new-a"), Node("new-b")]
    check(names(second.children) == ["new-a", "new-b"], "children replacement failed")
    del second.children
    check(second.children == (), "children deletion failed")
    first.parent = None
    check(first.is_root and first.children == (), "detach failed")


def anynode_attributes() -> None:
    from anytree import AnyNode

    root = AnyNode(kind="root", priority=2)
    child = AnyNode(parent=root, kind="child", priority=1)
    check(root.kind == "root" and child.parent is root, "AnyNode attributes failed")
    check(repr(root) == "AnyNode(kind='root', priority=2)", "AnyNode repr failed")
    check(root.__dict__["kind"] == "root", "ordinary attributes were not retained")


def mixins() -> None:
    from anytree import LightNodeMixin, NodeMixin

    class Custom(NodeMixin):
        def __init__(self, label, parent=None):
            self.label = label
            self.parent = parent

        def __repr__(self):
            return f"Custom({self.label!r})"

    root = Custom("root")
    child = Custom("child", root)
    check(child.root is root and root.children == (child,), "NodeMixin relation failed")
    check(child.ancestors == (root,), "NodeMixin ancestors failed")
    check(child.anchestors == child.ancestors, "deprecated ancestor alias failed")

    class Slotted(LightNodeMixin):
        __slots__ = ("label",)

        def __init__(self, label, parent=None):
            self.label = label
            self.parent = parent

    slotted_root = Slotted("root")
    slotted_child = Slotted("child", slotted_root)
    check(slotted_child.parent is slotted_root, "LightNodeMixin relation failed")
    check(slotted_root.children == (slotted_child,), "LightNodeMixin children failed")


def symlink_nodes() -> None:
    from anytree import Node, SymlinkNode

    root = Node("root", color="blue")
    target = Node("target", root, value=7)
    link = SymlinkNode(target, root)
    check(link.target is target and link.parent is root, "symlink relation failed")
    check(link.value == 7, "symlink attribute forwarding failed")
    link.value = 9
    check(target.value == 9, "symlink assignment forwarding failed")
    check(link.children == (), "symlink children should be local")
    check("SymlinkNode" in repr(link) and "target" in repr(link), "symlink repr failed")


def iterator_depth() -> None:
    from anytree import PostOrderIter, PreOrderIter

    root, left, _ = make_tree()
    check(
        names(PreOrderIter(root))
        == ["root", "left", "left-a", "left-b", "right", "right-a", "right-b"],
        "preorder failed",
    )
    check(
        names(PostOrderIter(root))
        == ["left-a", "left-b", "left", "right-a", "right-b", "right", "root"],
        "postorder failed",
    )
    check(names(PreOrderIter(root, maxlevel=2)) == ["root", "left", "right"], "maxlevel failed")
    check(names(PreOrderIter(root, maxlevel=0)) == [], "zero maxlevel failed")
    check(
        names(PreOrderIter(root, filter_=lambda node: node.name.endswith("-a")))
        == ["left-a", "right-a"],
        "filter failed",
    )
    check(
        names(PreOrderIter(root, stop=lambda node: node is left))
        == ["root", "right", "right-a", "right-b"],
        "stop failed",
    )
    iterator = PreOrderIter(root)
    check(iter(iterator) is iterator and next(iterator) is root, "iterator state protocol failed")


def iterator_breadth() -> None:
    from anytree import LevelGroupOrderIter, LevelOrderGroupIter, LevelOrderIter, ZigZagGroupIter

    root, _, _ = make_tree()
    check(
        names(LevelOrderIter(root))
        == ["root", "left", "right", "left-a", "left-b", "right-a", "right-b"],
        "level order failed",
    )
    check(
        [names(group) for group in LevelOrderGroupIter(root)]
        == [["root"], ["left", "right"], ["left-a", "left-b", "right-a", "right-b"]],
        "level groups failed",
    )
    check(LevelGroupOrderIter is LevelOrderGroupIter, "group alias failed")
    check(
        [names(group) for group in ZigZagGroupIter(root)]
        == [["root"], ["right", "left"], ["left-a", "left-b", "right-a", "right-b"]],
        "zigzag groups failed",
    )


def render_tree() -> None:
    from anytree import AsciiStyle, ContRoundStyle, ContStyle, DoubleStyle, Node, RenderTree

    root = Node("root", lines=["first", "second"])
    Node("left", root)
    Node("right", root)
    check(
        AsciiStyle().vertical == "|   "
        and AsciiStyle().cont == "|-- "
        and AsciiStyle().end == "+-- ",
        "ASCII style failed",
    )
    check(ContStyle().vertical == "│   " and ContRoundStyle().end == "╰── ", "Unicode style failed")
    check(DoubleStyle().end == "╚══ ", "double style failed")
    rows = list(RenderTree(root))
    check(rows[0].node is root and rows[1].node.name == "left", "render rows lost nodes")
    check(str(RenderTree(root)) == "Node('/root', lines=['first', 'second'])\n├── Node('/root/left')\n└── Node('/root/right')", "render text failed")
    by_lines = str(RenderTree(root).by_attr("lines"))
    check(by_lines == "first\nsecond\n├── \n└── ", "multiline rendering failed")
    check("Node('/root'" in repr(RenderTree(root)), "render repr failed")


def search() -> None:
    from anytree import find, find_by_attr, findall, findall_by_attr
    from anytree.search import CountError

    root, _, _ = make_tree()
    matches = findall(root, filter_=lambda node: "a" in node.name)
    check(names(matches) == ["left-a", "right-a"], "findall failed")
    check(find(root, filter_=lambda node: node.name == "right").name == "right", "find failed")
    check(find_by_attr(root, 4, name="rank").name == "left-b", "find_by_attr failed")
    check(names(findall_by_attr(root, 5, name="rank")) == ["right-a"], "findall_by_attr failed")
    expect(
        CountError,
        lambda: find(root, filter_=lambda node: node.name.startswith("left")),
        "find count guard failed",
    )
    expect(
        CountError,
        lambda: findall(root, filter_=lambda node: True, maxcount=2),
        "findall maxcount guard failed",
    )
    expect(
        CountError,
        lambda: findall(root, filter_=lambda node: False, mincount=1),
        "findall mincount guard failed",
    )
    check(findall_by_attr(root, "missing", name="unknown") == (), "missing attribute should not match")


def cached_search() -> None:
    from anytree import cachedsearch, findall

    root, _, _ = make_tree()
    uncached = names(findall(root, filter_=lambda node: node.name.endswith("-b")))
    cached = names(cachedsearch.findall(root, filter_=lambda node: node.name.endswith("-b")))
    check(cached == uncached, "cached search differs from uncached search")
    check(cachedsearch.find_by_attr(root, 6, name="rank").name == "right-b", "cached attr search failed")


def resolver_paths() -> None:
    from anytree import Node, Resolver
    from anytree.resolver import ChildResolverError, ResolverError, RootResolverError

    root = Node("root")
    left = Node("Left", root)
    leaf = Node("leaf", left)
    resolver = Resolver()
    check(resolver.get(root, "/root/Left/leaf") is leaf, "absolute resolution failed")
    check(resolver.get(leaf, "../") is left, "parent resolution failed")
    check(resolver.get(left, "./leaf") is leaf, "relative resolution failed")
    check(resolver.get(root, "/root") is root, "root resolution failed")
    check(Resolver(ignorecase=True).get(root, "/ROOT/left/LEAF") is leaf, "ignorecase failed")
    expect(RootResolverError, lambda: resolver.get(root, "../../root"), "root escape was accepted")
    expect(ResolverError, lambda: resolver.get(root, "/other"), "unknown root was accepted")
    expect(ChildResolverError, lambda: resolver.get(root, "/root/missing"), "missing child was accepted")
    relaxed = Resolver(relax=True)
    check(relaxed.get(root, "/other") is None and relaxed.glob(root, "/root/nope") == [], "relax mode failed")


def resolver_glob() -> None:
    from anytree import Resolver

    root, _, _ = make_tree()
    resolver = Resolver()
    check(resolver.is_wildcard("/root/*"), "wildcard detection failed")
    check(names(resolver.glob(root, "/root/*")) == ["left", "right"], "single wildcard failed")
    check(names(resolver.glob(root, "/root/*/*-a")) == ["left-a", "right-a"], "segment wildcard failed")
    check(names(resolver.glob(root, "/root/**/right-b")) == ["right-b"], "recursive wildcard failed")
    check(names(resolver.glob(root, "/root/????t")) == ["right"], "question wildcard failed")


def walker_utilities() -> None:
    from anytree import Node, Walker
    from anytree.util import commonancestors, leftsibling, rightsibling
    from anytree.walker import WalkError

    root, left, right = make_tree()
    left_leaf = left.children[1]
    right_leaf = right.children[0]
    upwards, common, downwards = Walker().walk(left_leaf, right_leaf)
    check(names(upwards) == ["left-b", "left"], "walker upwards failed")
    check(common is root and names(downwards) == ["right", "right-a"], "walker path failed")
    check(names(commonancestors(left_leaf, right_leaf)) == ["root"], "common ancestors failed")
    check(leftsibling(right) is left and rightsibling(left) is right, "sibling utilities failed")
    check(leftsibling(left) is None and rightsibling(right) is None, "sibling boundaries failed")
    other = Node("other")
    expect(WalkError, lambda: Walker().walk(left_leaf, other), "cross-root walk was accepted")


def dict_export_import() -> None:
    from anytree import Node
    from anytree.exporter import DictExporter
    from anytree.importer import DictImporter

    root = Node("root", z=2, a=1)
    Node("first", root, value=[1, 2])
    Node("second", root, value=[3])
    exported = DictExporter().export(root)
    check(list(exported) == ["z", "a", "name", "children"], "attribute insertion order changed")
    check(exported["children"][0]["name"] == "first", "dictionary child order changed")
    limited = DictExporter(maxlevel=2).export(root)
    check("children" in limited and "children" not in limited["children"][0], "dictionary maxlevel failed")
    filtered = DictExporter(
        attriter=lambda items: ((key, value) for key, value in items if key != "z")
    ).export(root)
    check("z" not in filtered and filtered["a"] == 1, "dictionary attriter failed")
    imported = DictImporter().import_(exported)
    check(imported.name == "root" and names(imported.children) == ["first", "second"], "dictionary import failed")
    check(imported.children[0].value == [1, 2], "dictionary attributes failed")


def json_roundtrip() -> None:
    from anytree import Node
    from anytree.exporter import JsonExporter
    from anytree.importer import JsonImporter

    root = Node("root", count=2)
    Node("child", root, enabled=True)
    text = JsonExporter(indent=2, sort_keys=True).export(root)
    check('"children"' in text and text.startswith("{"), "JSON export failed")
    restored = JsonImporter().import_(text)
    check(restored.name == "root" and restored.children[0].enabled is True, "JSON import failed")
    buffer = io.StringIO()
    result = JsonExporter().write(root, buffer)
    check(result is None and json.loads(buffer.getvalue())["name"] == "root", "JSON write failed")
    expect(json.JSONDecodeError, lambda: JsonImporter().import_("{"), "invalid JSON was accepted")


def mermaid() -> None:
    from anytree import Node
    from anytree.exporter import MermaidExporter

    root = Node("root")
    child = Node('say "hi"', root)
    Node("leaf", child)
    exporter = MermaidExporter(root, options={"theme": "forest"})
    lines = list(exporter)
    check(lines[0] == "graph TD", "Mermaid header failed")
    check(any("theme" in line for line in lines), "Mermaid options failed")
    check(any("N0" in line and "root" in line for line in lines), "Mermaid node naming failed")
    check(any("N0-->N1" in line for line in lines), "Mermaid edge failed")
    with tempfile.NamedTemporaryFile(prefix="anytree-mermaid-", suffix=".md") as handle:
        output = Path(handle.name)
    exporter.to_file(output)
    content = output.read_text(encoding="utf-8")
    output.unlink(missing_ok=True)
    check(content.startswith("```mermaid\n") and content.endswith("\n```"), "Mermaid file fence failed")
    filtered = list(MermaidExporter(root, filter_=lambda node: node is not child))
    check(not any("say" in line for line in filtered), "Mermaid filter failed")


def exception_contracts() -> None:
    from anytree import Node
    from anytree.node import LoopError, TreeError
    from anytree.resolver import ChildResolverError, ResolverError, RootResolverError
    from anytree.search import CountError
    from anytree.walker import WalkError

    check(issubclass(LoopError, TreeError), "LoopError hierarchy changed")
    check(issubclass(CountError, RuntimeError), "CountError hierarchy changed")
    check(issubclass(ChildResolverError, ResolverError), "ChildResolverError hierarchy changed")
    check(issubclass(RootResolverError, ResolverError), "RootResolverError hierarchy changed")
    check(issubclass(WalkError, RuntimeError), "WalkError hierarchy changed")
    root = Node("root")

    def assign_invalid() -> None:
        root.children = (root,)

    expect(TreeError, assign_invalid, "invalid children assignment was accepted")


def deterministic_projection() -> None:
    from anytree import Node, PreOrderIter
    from anytree.exporter import JsonExporter

    def snapshot():
        root = Node("root", z=2, a=1)
        Node("b", root, rank=2)
        Node("a", root, rank=1)
        return {
            "paths": paths(PreOrderIter(root)),
            "repr": [repr(node) for node in PreOrderIter(root)],
            "json": JsonExporter(sort_keys=True).export(root),
        }

    first = snapshot()
    second = snapshot()
    check(first == second and json.dumps(first, sort_keys=True), "fresh-process projection changed")


SCENARIOS = {
    "api-surface": api_surface,
    "node-relationships": node_relationships,
    "mutation-and-cycles": mutation_and_cycles,
    "anynode-attributes": anynode_attributes,
    "mixins": mixins,
    "symlink-nodes": symlink_nodes,
    "iterator-depth": iterator_depth,
    "iterator-breadth": iterator_breadth,
    "render-tree": render_tree,
    "search": search,
    "cached-search": cached_search,
    "resolver-paths": resolver_paths,
    "resolver-glob": resolver_glob,
    "walker-utilities": walker_utilities,
    "dict-export-import": dict_export_import,
    "json-roundtrip": json_roundtrip,
    "mermaid": mermaid,
    "exception-contracts": exception_contracts,
    "deterministic-projection": deterministic_projection,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import sys

    sys.path.insert(0, args.candidate_site)
    verdict = {"scenario": args.scenario, "status": "failed"}
    try:
        SCENARIOS[args.scenario]()
    except BaseException:
        verdict["message"] = traceback.format_exc(limit=10)[-2400:]
    else:
        verdict["status"] = "passed"
    args.output.write_text(json.dumps(verdict, sort_keys=True), encoding="utf-8")
    return 0




if __name__ == "__main__":
    raise SystemExit(main())
