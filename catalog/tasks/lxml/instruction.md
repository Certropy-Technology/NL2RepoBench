# Build `lxml`

Create a complete, installable Python project named `lxml` from an empty
workspace. It is an XML and HTML processing library whose public runtime
interfaces are available from `lxml.etree` and `lxml.html`. The project may
use CPython extension modules and the system `libxml2` and `libxslt`
libraries; normal runtime behavior must work without network access.

## Supports

- Support CPython 3.12 on Linux x86_64. Use a standard `pyproject.toml` build
  configuration and make `pip install .` succeed without build isolation when
  Cython, setuptools, wheel, a C compiler, `pkg-config`, libxml2, libxslt, and
  zlib development headers are already available.
- Install the `lxml` distribution and expose the `lxml.etree` and `lxml.html`
  modules. Do not depend on a preinstalled copy of `lxml`, package indexes,
  network services, subprocesses, or local files for the documented runtime
  operations.
- Preserve XML input as Unicode or bytes according to the caller's requested
  encoding. UTF-8 XML bytes are supported.
- Raise `lxml.etree.XMLSyntaxError` for malformed XML passed to
  `etree.fromstring`.

## API Usage Guide

### `lxml.etree`

- `fromstring(text, parser=None, *, base_url=None)` parses an XML document or
  fragment and returns its root element. Elements expose `.tag`, `.text`,
  `.get(name, default=None)`, `.getparent()`, `.nsmap`, sequence-style child
  access, `insert(index, element)`, and `remove(element)`.
- `XML(text, parser=None, *, base_url=None)` is an XML parsing convenience
  function with equivalent element behavior for ordinary XML input.
- `Element(tag, attrib=None, nsmap=None, **extra)` creates an element.
  Attribute keyword arguments and the optional mapping set element attributes.
  `SubElement(parent, tag, attrib=None, nsmap=None, **extra)` creates, appends,
  and returns a child element.
- `tostring(element_or_tree, encoding=None, method="xml", *, pretty_print=False, xml_declaration=None, with_tail=True, ...)`
  serializes an element. With `encoding="unicode"` it returns `str`; with the
  default byte encoding it returns `bytes`. XML serialization preserves child
  order and attributes. `pretty_print=True` emits indentation and a trailing
  newline for the nested XML documents shown below.
- `Element.xpath(path, namespaces=None, **variables)` evaluates XPath. It
  supports child/descendant navigation, attribute selections, predicates,
  string conversion, and numeric `count()`. Namespace prefixes in a path are
  resolved through the caller-provided `namespaces` mapping.

Examples:

```python
from lxml import etree

root = etree.fromstring(b"<root><item rank='2'>b</item><item rank='1'>a</item></root>")
assert root.xpath("//item/@rank") == ["2", "1"]
assert root.xpath("string(//item[@rank='1'])") == "a"
assert root.xpath("count(//item)") == 2.0
```

```python
from lxml import etree

root = etree.Element("root", version="1")
child = etree.SubElement(root, "child")
child.text = "hello"
assert etree.tostring(root, encoding="unicode") == '<root version="1"><child>hello</child></root>'
```

### `lxml.html`

- `fromstring(html, parser=None, base_url=None, **kw)` parses an HTML fragment
  and returns an element that supports the same `.xpath()` element query API.
  For example, parsing `<div><p class="note">hello</p></div>` lets callers
  retrieve `"hello"` through `string(.//p)` and select the paragraph with
  `.//p[@class="note"]`.

## Implementation Notes

- Treat element construction and parsed elements consistently: both preserve
  child order, support parent lookup after insertion, and serialize valid XML.
- XML namespaces use Clark-style element tags where applicable and expose the
  declared prefix-to-URI mapping through `.nsmap`. XPath namespace resolution
  is an explicit caller input, not an implicit global setting.
- The finished package needs only the interfaces described above. Full XSLT,
  DTD, RelaxNG, XMLSchema, objectify, incremental parser, custom resolver,
  CSS-selector, HTTP, catalog, and C API compatibility are outside this
  deterministic task scope.
- The task is deterministic and offline. Do not build features around external
  URLs or remote entity loading.

## Deterministic Verification Scope

The fixed denominator is eight offline behavior scenarios: parsing and byte
serialization, XPath text and attribute queries, constructed elements,
namespaces, tree mutation and parent lookup, parse errors, pretty printing,
and HTML fragment XPath queries. Every scenario corresponds to a behavior
specified above.
