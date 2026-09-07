# Project Description

Create a complete, installable Python project named `lxml` from an empty
workspace. It is an XML and HTML processing library whose public runtime
interfaces are available from `lxml.etree` and `lxml.html`. The project may
use CPython extension modules and the system `libxml2`, `libxslt`, and zlib
libraries. The documented runtime operations are local and must work without
network access.

# Natural Language Instruction

Create the `lxml` project from an empty `workspace/`. Implement the bounded
`lxml.etree` and `lxml.html` behavior below: parse XML and HTML, construct and
mutate elements, serialize trees, expose parent and namespace information, and
evaluate the stated XPath forms. Ensure malformed XML raises
`lxml.etree.XMLSyntaxError` and that Unicode/bytes encoding behavior is
preserved.

This task intentionally covers a deterministic core rather than all of lxml.
Do not add network-dependent entity loading, remote URLs, or undocumented
features merely to broaden the surface. The package must be installable from
the declared native build environment and usable from an installed target,
not only from the source directory.

# Supports

- Support CPython `3.12.14` on Linux x86_64, Debian-based system libraries,
  and the pinned base image digest recorded in task metadata.
- Use a standard `pyproject.toml` build configuration. `pip install .` must
  succeed without build isolation when Cython, setuptools, wheel, a C
  compiler, `pkg-config`, libxml2, libxslt, and zlib development headers are
  already available.
- Install the `lxml` distribution and expose `lxml.etree` and `lxml.html`.
  Build requirements are Cython `3.3.0`, packaging `26.3`, setuptools
  `84.0.0`, and wheel `0.48.0` from the locked build environment; do not add
  runtime package-index requirements.
- Candidate and verifier execution is NoNetwork. Do not depend on a
  preinstalled lxml copy, package indexes, network services, subprocesses, or
  files outside the installed package for documented operations.
- Support XML Unicode and UTF-8 bytes. Native compilation may use only the
  declared system libraries and must not fetch source or dependencies at run
  time.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── lxml/
│   ├── __init__.py
│   ├── etree.pyx
│   └── html/
│       └── __init__.py
```

The build metadata must install the `lxml` distribution and map the public
imports to the installed `lxml` package. `lxml/etree.py` or the corresponding
native extension provides parsing, elements, serialization, and XPath;
`lxml/html` provides HTML fragment parsing. Include only the build sources,
package resources, and configuration needed for these public modules. Do not
list protected test directories, verifier adapters, reports, or private source
archives as agent-owned files.

# API Usage Guide

## `lxml.etree` parsing and construction

- `fromstring(text, parser=None, *, base_url=None)` accepts an XML string or
  bytes and returns its root element. `XML(text, parser=None, *, base_url=None)`
  is the equivalent convenience parser. Malformed XML raises
  `lxml.etree.XMLSyntaxError`.
- `Element(tag, attrib=None, nsmap=None, **extra)` creates an element.
  `SubElement(parent, tag, attrib=None, nsmap=None, **extra)` creates, appends,
  and returns a child. Tags, attribute mappings, namespace maps, and keyword
  attributes follow the documented element shapes.
- Elements expose `.tag`, `.text`, `.get(name, default=None)`, `.getparent()`,
  `.nsmap`, and sequence-style child access. `insert(index, element)` inserts
  at the requested child position; `remove(element)` removes that child.
  Construction, insertion, and removal preserve child order and update parent
  lookup.

## Serialization

```python
tostring(
    element_or_tree,
    encoding=None,
    method="xml",
    *,
    pretty_print=False,
    xml_declaration=None,
    with_tail=True,
    ...,
) -> bytes | str
```

Serialize an element or tree while preserving child order and attributes. The
default byte encoding returns `bytes`; `encoding="unicode"` returns `str`.
`pretty_print=True` emits indentation and a trailing newline for the nested
documents shown in this specification. `method="xml"` is the required deterministic
mode, and `with_tail` controls tail-text inclusion where applicable.

## XPath

```python
element.xpath(path, namespaces=None, **variables)
```

Evaluate child/descendant navigation, attribute selections, predicates, string
conversion, and numeric `count()`. Namespace prefixes in `path` resolve only
through the caller-provided `namespaces` mapping. Return node lists, strings,
or numeric values according to the expression; `count()` returns a float as in
the public API.

## `lxml.html`

```python
lxml.html.fromstring(html, parser=None, base_url=None, **kw)
```

Parse an HTML fragment and return an element supporting the same `.xpath()`
query API. For `<div><p class="note">hello</p></div>`, callers can select
`.//p[@class="note"]` and obtain its text with `string(.//p)`.

# Implementation Notes

- Treat constructed and parsed elements consistently: preserve child order,
  support parent lookup after insertion, and serialize valid XML.
- XML namespaces use Clark-style element tags where applicable; `.nsmap`
  exposes the declared prefix-to-URI mapping. XPath namespace resolution is
  explicit caller input, never an implicit global setting.
- Native extension behavior must remain deterministic and local. Do not load
  external entities or remote resources, and do not build features around
  external URLs.
- Full XSLT, DTD, RelaxNG, XMLSchema, objectify, incremental parser, custom
  resolver, CSS selector, HTTP, catalog, and C API compatibility are outside
  the required contract.

# Examples

```python
from lxml import etree

root = etree.fromstring(b"<root><item rank='2'>b</item><item rank='1'>a</item></root>")
root.xpath("//item/@rank")  # ["2", "1"]
root.xpath("string(//item[@rank='1'])")  # "a"
root.xpath("count(//item)")  # 2.0
```

```python
from lxml import etree

root = etree.Element("root", version="1")
child = etree.SubElement(root, "child")
child.text = "hello"
etree.tostring(root, encoding="unicode")
expected: '<root version="1"><child>hello</child></root>'
```

# Error Handling and Boundary Conditions

- `etree.fromstring` and `etree.XML` must raise `XMLSyntaxError` for malformed
  XML rather than returning a partial tree. UTF-8 bytes and Unicode strings
  remain distinct according to the selected serialization encoding.
- Empty elements, missing attributes, and absent XPath matches return the
  normal empty/`None`/empty-list forms of the public element API. Element
  insertion and removal must preserve deterministic order and parent links.
- Namespace-prefixed XPath requires an explicit caller mapping. Do not infer
  namespaces from global state or access remote namespace resources.
- HTML parsing is local fragment parsing only. Do not load external URLs,
  execute scripts, access files outside the package, or consult network,
  registry, DNS, clock, or random state.

The fixed offline behavior scope covers parsing and byte serialization, XPath
text and attribute queries, constructed elements, namespaces, tree mutation
and parent lookup, parse errors, pretty printing, and HTML fragment XPath
queries. The public sections above specify those behaviors without exposing
private test contents.
