# Build `anytree`

Create a complete, installable Python package named `anytree` from an empty
workspace. It is a pure-Python tree data structure library. The package must
work without network access and without any preinstalled copy of `anytree`.

The scored behavior is the deterministic, local tree API described below. The
package must not require a third-party runtime dependency. An optional cache
accelerator may be detected, but the standard-library path must be complete.

## Project Description

`anytree` models ordered rooted trees. A node has at most one parent and an
ordered tuple of children. The library provides concrete nodes, mixins for
adding tree behavior to user classes, symbolic links, depth-first and
level-order traversal, path lookup, searches, walking between nodes, text
rendering, JSON/dictionary import-export, and Mermaid text export.

The tree is mutable. Attaching a node updates both sides of the relationship;
detaching it makes it a root of its own tree. The implementation must preserve
child insertion order and must reject cycles and duplicate children without
leaving a partially modified tree.

The source revision used for this candidate is the behavior reference. Do not
copy source files or upstream tests into the generated project, and do not
implement a generic tree with a superficially similar API. Implement the
observable contracts in this document.

## Supports

- Support CPython `>=3.9.2,<4.0` using only the Python standard library at
  runtime.
- Provide an installable package layout whose import package is `anytree`.
- Import and use the package with an empty site-packages directory. The
  optional `fastcache` accelerator is not a required dependency; cached search
  functions must fall back to correct uncached behavior when it is absent.
- Keep ordinary tree construction, traversal, searching, rendering, and
  JSON/dictionary operations local. They must not contact a network or service
  and must not invoke a subprocess.
- Use deterministic behavior for fixed node construction, fixed child order,
  fixed callbacks, and fixed serializer options. Do not sort children unless a
  caller explicitly supplies a sorting child iterator.
- Make source-only builds reproducible without requiring a `.git` directory.
  Do not make runtime behavior depend on a mutable branch, network metadata,
  or an unavailable SCM checkout.

### Explicit Graphviz boundary

Graphviz is excluded from this task. Do not require the `dot` executable, a
Python Graphviz binding, or any system Graphviz package. The following source
surface is outside the contract and need not be implemented or re-exported:

- `anytree.exporter.DotExporter`;
- `anytree.exporter.UniqueDotExporter`;
- `anytree.dotexport.RenderTreeGraph`;
- DOT text/file behavior; and
- `to_picture()`, which would create a temporary DOT file and invoke the
  external `dot` subprocess.

The safe exporter surface is `DictExporter`, `JsonExporter`, and
`MermaidExporter`. A package import of those safe classes must not fail merely
because Graphviz is absent.

## Public API Usage Guide

### Package exports

The root package must expose these names. `LevelGroupOrderIter` is a legacy
alias of `LevelOrderGroupIter`.

```text
AbstractStyle, AnyNode, AsciiStyle, ChildResolverError,
ContRoundStyle, ContStyle, CountError, DoubleStyle,
LevelGroupOrderIter, LevelOrderGroupIter, LevelOrderIter,
LightNodeMixin, LoopError, Node, NodeMixin, PostOrderIter, PreOrderIter,
RenderTree, Resolver, ResolverError, RootResolverError, SymlinkNode,
SymlinkNodeMixin, TreeError, WalkError, Walker, ZigZagGroupIter,
cachedsearch, find, find_by_attr, findall, findall_by_attr, util
```

The root also exposes the source metadata constants `__version__`,
`__author__`, `__author_email__`, `__description__`, and `__url__`. Metadata
must not be obtained by contacting the network. The distribution metadata and
the runtime constant must be internally consistent for the chosen deterministic
build configuration.

The following submodule exports are required:

- `anytree.node`: `AnyNode`, `LightNodeMixin`, `LoopError`, `Node`,
  `NodeMixin`, `SymlinkNode`, `SymlinkNodeMixin`, `TreeError`;
- `anytree.iterators`: `AbstractIter`, `LevelOrderGroupIter`,
  `LevelOrderIter`, `PostOrderIter`, `PreOrderIter`, `ZigZagGroupIter`;
- `anytree.exporter`: `DictExporter`, `JsonExporter`, `MermaidExporter`;
- `anytree.importer`: `DictImporter`, `JsonImporter`; and
- `anytree.util`: `commonancestors`, `leftsibling`, `rightsibling`.

### Nodes and relationships

#### `Node`

```python
Node(name, parent=None, children=None, **kwargs)
```

`name` is the node identifier used in paths and representations. `parent` is
an optional `NodeMixin` or `LightNodeMixin`. `children` is an optional
iterable of node objects. Other keyword arguments become ordinary instance
attributes. The constructor attaches the node after storing its attributes.

`repr(Node("root"))` is `"Node('/root')"`; a descendant path joins the string
form of each name with the node separator `/`, for example
`Node('/root/child')`. Additional attributes appear as `key=value` repr pairs
in lexicographic key order. `str(node)` follows the normal object
representation for this class.

#### `AnyNode`

```python
AnyNode(parent=None, children=None, **kwargs)
```

`AnyNode` has no required `name`; all keyword arguments become ordinary
attributes. Its repr is `AnyNode(...)` with public attributes rendered in
lexicographic key order. The tree relationship behavior is the same as for
`Node`.

#### `NodeMixin` and `LightNodeMixin`

These mixins add tree behavior to a user class. `NodeMixin` stores relationship
state in ordinary instance storage. `LightNodeMixin` provides the same public
tree operations while using slots for its relationship state; a user class
using it must provide compatible slots for its own attributes.

The relationship properties and methods are:

```text
parent                 get/set one parent or None
children               get a tuple; set/delete an iterable of children
path                   tuple from root to this node, inclusive
iter_path_reverse()    generator from this node to its root
ancestors              tuple of parents from root down to the parent
descendants            tuple of all descendants in preorder
root                   root node of this tree
siblings               tuple of other children of the same parent
leaves                 tuple of leaf descendants, including self if leaf
is_leaf                whether children is empty
is_root                whether parent is None
height                 maximum edge distance from this node to a leaf
depth                  edge distance from the root
size                   number of nodes in the subtree rooted here
```

The legacy misspelling `anchestors` is a deprecated alias of `ancestors` and
may emit `DeprecationWarning`. The class attribute `separator` defaults to
`"/"`; subclasses may override it for path and repr formatting.

Setting `node.parent` detaches the node from its old parent before attaching it
to the new parent. Setting it to `None` makes the node a root. Setting
`node.children` replaces all current children atomically; deleting it detaches
all children. A child may occur at most once in a parent's children. A node
cannot be its own parent, and an ancestor cannot become a descendant. Invalid
parent/child objects and cycles raise `TreeError` or `LoopError` with the
corresponding operation rejected.

The attach/detach hook methods are callable extension points and execute in
the order implied by their names:

```text
_pre_detach(parent)       _post_detach(parent)
_pre_attach(parent)       _post_attach(parent)
_pre_detach_children(children)  _post_detach_children(children)
_pre_attach_children(children)  _post_attach_children(children)
```

They receive the affected parent or child tuple and do not change the
relationship semantics.

#### `SymlinkNode` and `SymlinkNodeMixin`

```python
SymlinkNode(target, parent=None, children=None, **kwargs)
```

The target is another tree node. A symlink has its own parent and children, but
ordinary non-tree attribute access and assignment is forwarded to `target`.
Constructor keyword attributes are stored on the target. Its representation
identifies the target as `SymlinkNode(<target repr>)`.

`SymlinkNodeMixin` provides the same forwarding behavior to a user class that
defines a `target` attribute. Access to `target`, `parent`, and `children`
remains local to the symlink.

### Exceptions

Provide these exception classes at the indicated import paths:

```text
anytree.node.TreeError
anytree.node.LoopError             subclass of TreeError
anytree.search.CountError          subclass of RuntimeError
anytree.resolver.ResolverError     subclass of RuntimeError
anytree.resolver.RootResolverError subclass of ResolverError
anytree.resolver.ChildResolverError subclass of ResolverError
anytree.walker.WalkError           subclass of RuntimeError
```

`ResolverError` instances expose the relevant `node` and `child` attributes.
`CountError` reports the requested count and the observed matching tuple.

### Iterators

Each iterator is stateful and supports `iter(iterator) is iterator` and
`next(iterator)`. The common constructor contract is:

```python
Iterator(node, filter_=None, stop=None, maxlevel=None)
```

`filter_` is called for each visited node and controls whether the node is
returned. `stop` prevents descent below a node for which it returns true.
`maxlevel` limits depth relative to the starting node; level 1 is the start
node and `maxlevel=0` returns no nodes. Child order is the order in
`children`.

Implement these traversal classes:

- `PreOrderIter`: node before descendants, depth-first;
- `PostOrderIter`: descendants before node, depth-first;
- `LevelOrderIter`: breadth-first flat sequence;
- `LevelOrderGroupIter`: breadth-first tuples, one tuple per level;
- `LevelGroupOrderIter`: exact alias of `LevelOrderGroupIter`; and
- `ZigZagGroupIter`: breadth-first tuples with alternating child direction.

`AbstractIter` is the common base exposed from `anytree.iterators`; its
internal `_iter` hook may remain abstract, but the concrete iterators must
honor the shared filtering, stopping, and level rules.

### Rendering

#### Styles

`AbstractStyle(vertical, cont, end)` stores three equal-width strings and
provides an `empty` property consisting of spaces of the same width. Its repr
is `ClassName()`. The no-argument styles have these exact values:

```text
AsciiStyle:     vertical="|   ", cont="|-- ", end="+-- "
ContStyle:      vertical="\u2502   ", cont="\u251c\u2500\u2500 ", end="\u2514\u2500\u2500 "
ContRoundStyle:  vertical="\u2502   ", cont="\u251c\u2500\u2500 ", end="\u2570\u2500\u2500 "
DoubleStyle:    vertical="\u2551   ", cont="\u2560\u2550\u2550 ", end="\u255a\u2550\u2550 "
```

#### `RenderTree`

```python
RenderTree(node, style=ContStyle(), childiter=list, maxlevel=None)
```

Iteration yields a three-field `Row(pre, fill, node)` named tuple. `pre` is
the branch prefix for the first line of a node, `fill` is the prefix for
continuation lines, and `node` is the original object. `childiter` receives a
children tuple and controls order/filtering at each level. `maxlevel` follows
the iterator convention.

`str(RenderTree(root))` joins the repr of every node with the calculated
prefixes and newline separators. `repr(render_tree)` includes the starting
node repr, style repr, and child iterator repr. `by_attr(attrname="name")`
returns the same tree shape using the selected attribute; a callable
`attrname` receives each node. String values use their lines, and a list or
tuple attribute is rendered as multiple lines with `fill` prefixes.

### Search and cached search

```python
findall(node, filter_=None, stop=None, maxlevel=None,
        mincount=None, maxcount=None)
findall_by_attr(node, value, name="name", maxlevel=None,
                mincount=None, maxcount=None)
find(node, filter_=None, stop=None, maxlevel=None)
find_by_attr(node, value, name="name", maxlevel=None)
```

`findall` returns a tuple in preorder. `find` returns the first matching node
or `None`; if more than one node matches it raises `CountError`. The
`mincount` and `maxcount` bounds on `findall` raise `CountError` when violated.
`findall_by_attr` and `find_by_attr` compare the named attribute and treat a
missing attribute as non-matching.

`anytree.cachedsearch` provides the same four operations and signatures. Its
cache is an optional optimization only; results and exceptions must match the
uncached functions, and the no-accelerator path must use the standard library.

### Path resolution

```python
Resolver(pathattr="name", ignorecase=False, relax=False)
Resolver.get(node, path)
Resolver.glob(node, path)
Resolver.is_wildcard(path)
```

`get` resolves relative paths using `/`, `.` and `..`, and absolute paths
starting at the root. `glob` returns a list and additionally supports `*` for
any characters except `/`, `?` for one character except `/`, and `**` for
recursive matching. Matches preserve tree traversal order. `ignorecase=True`
performs case-insensitive matching. `relax=True` returns `None` from `get`
and an empty list from `glob` instead of raising resolution errors.

The root name in an absolute path must match. Going above the root raises
`RootResolverError`; an unknown root or missing child raises
`ResolverError`/`ChildResolverError` unless relaxed. The resolver's bounded
match cache must not change results.

### Walking and utilities

```python
Walker.walk(start, end)
```

The result is `(upwards, common, downwards)`. `upwards` is a tuple from
`start` toward, but excluding, the common node; `common` is the lowest common
ancestor; `downwards` is a tuple from below `common` to `end`. Nodes from
different roots raise `WalkError`.

```python
util.commonancestors(*nodes)
util.leftsibling(node)
util.rightsibling(node)
```

`commonancestors` returns common ancestors from root toward the nodes;
zero arguments return `()`. Sibling helpers return the adjacent sibling or
`None` at a boundary or for a root.

### Dictionary and JSON import/export

#### `DictExporter`

```python
DictExporter(dictcls=dict, attriter=None, childiter=list, maxlevel=None)
DictExporter.export(node)
```

Each node becomes a mapping containing its ordinary public instance
attributes. Relationship internals are omitted. A nonempty child list is
stored under `"children"`; child order is preserved. `attriter` can filter or
order `(key, value)` pairs, `childiter` can filter or order children, and
`maxlevel` limits recursion.

#### `JsonExporter`

```python
JsonExporter(dictexporter=None, maxlevel=None, **kwargs)
JsonExporter.export(node)
JsonExporter.write(node, filehandle)
```

It delegates tree conversion to a `DictExporter` and passes `kwargs` to
`json.dumps` or `json.dump`. JSON options such as `indent`, `sort_keys`, and
`ensure_ascii` therefore retain the standard-library meanings. `write`
returns the underlying JSON writer result.

#### `DictImporter` and `JsonImporter`

```python
DictImporter(nodecls=AnyNode)
DictImporter.import_(data)

JsonImporter(dictimporter=None, **kwargs)
JsonImporter.import_(data)
JsonImporter.read(filehandle)
```

Dictionary input is not mutated. Each mapping becomes `nodecls(**attrs)` with
the `children` key removed and recursively attached. JSON import first calls
`json.loads`/`json.load` with the supplied options, then applies the dictionary
importer. Round-tripping a JSON-safe tree through the matching exporter and
importer preserves attributes and child order.

### Mermaid export

```python
MermaidExporter(
    node, graph="graph", name="TD", options=None, indent=0,
    nodenamefunc=None, nodefunc=None, edgefunc=None,
    filter_=None, stop=None, maxlevel=None,
)
MermaidExporter.to_file(filename)
```

Iteration returns Mermaid lines: the graph header, options, node lines, and
edge lines. The default node identifiers are assigned in preorder as `N0`,
`N1`, ... for one exporter instance. The default node text is a quoted node
name and the default edge is `-->`. Callbacks customize names, node text,
edges, filtering, stopping, and depth. `to_file` writes a UTF-8 Markdown
fence containing the same lines. Escaping of quotes and backslashes must be
stable.

## Determinism and Error Boundaries

- Child tuples, preorder traversal, search results, resolver matches, rendered
  rows, and exported children retain insertion order.
- `Node` and `AnyNode` repr attribute keys are sorted by key, while
  `DictExporter` follows instance insertion order unless `attriter` changes
  it. JSON output follows the options passed to the standard library.
- Fixed callbacks and input values produce identical render and export text
  across repeated fresh processes and different `PYTHONHASHSEED` values.
- Do not promise identity, memory addresses, hash values, object pickles, or
  callback behavior across processes. A verifier may use a child-side adapter
  for Python objects and must compare only explicit projections.
- File-writing methods are local filesystem operations. They must not accept
  candidate-controlled commands or invoke external programs.
- Invalid types, invalid relationships, cycles, duplicate children, missing
  resolver paths, count bounds, and JSON decoding failures must raise normal
  Python exceptions rather than silently changing the tree.

## Implementation Notes

Keep the implementation modular across node classes, iterators, renderers,
search/resolver utilities, and import/export modules. Preserve public aliases
and exception identity across re-exports. The public task does not require
Graphviz, DOT output, external renderers, documentation builds, lint tools,
coverage reports, or the upstream development-only `test2ref` helper.

The package must be installable from a source-only candidate workspace. The
upstream revision declares a PDM SCM-dynamic version and falls back to
`0.0.0` when `.git` is absent; resolve that packaging issue deterministically
in the generated repository instead of relying on a VCS checkout.
