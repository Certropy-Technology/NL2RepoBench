from __future__ import annotations

import importlib
import io
import json
import os
import sys
import types
import unittest


CANDIDATE_SITE = os.environ.get("NL2REPO_SIX_CANDIDATE_SITE", "/tmp/candidate-site")
if CANDIDATE_SITE not in sys.path:
    sys.path.insert(0, CANDIDATE_SITE)

import six


def error_name(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except Exception as exc:
        return type(exc).__name__
    return None


def package_identity():
    return {
        "version": six.__version__,
        "flags": [six.PY2, six.PY3, six.PY34],
        "types": [
            [item.__name__ for item in six.string_types],
            [item.__name__ for item in six.integer_types],
            [item.__name__ for item in six.class_types],
            six.text_type.__name__,
            six.binary_type.__name__,
        ],
        "maxsize": six.MAXSIZE,
        "package_path": list(six.__path__),
    }


def byte_literals():
    return {
        "b_hex": six.b("\xff").hex(),
        "u": six.u("hi \u0439"),
        "unichr": six.unichr(0x1234),
        "int2byte": six.int2byte(3).hex(),
        "int2byte_error": error_name(six.int2byte, 256),
        "byte2int": six.byte2int(b"\x03\x04"),
        "byte2int_empty_error": error_name(six.byte2int, b""),
        "indexbytes": six.indexbytes(b"hello", 3),
        "iterbytes": list(six.iterbytes(b"hi")),
    }


def ensure_conversions():
    emoji = "\U0001f600"
    encoded = emoji.encode("utf-8")
    return {
        "binary_from_text": six.ensure_binary(emoji).hex(),
        "binary_identity": six.ensure_binary(encoded) is encoded,
        "str_from_binary": six.ensure_str(encoded),
        "str_identity": six.ensure_str(emoji) is emoji,
        "text_from_binary": six.ensure_text(encoded),
        "text_identity": six.ensure_text(emoji) is emoji,
        "ignore": six.ensure_binary(emoji, "latin-1", "ignore").hex(),
        "strict_error": error_name(six.ensure_binary, emoji, "latin-1", "strict"),
        "type_errors": [
            error_name(six.ensure_binary, 8),
            error_name(six.ensure_str, 8),
            error_name(six.ensure_text, 8),
        ],
    }


def io_aliases():
    text = six.StringIO()
    text.write("hello")
    binary = six.BytesIO()
    binary.write(b"hello")
    return {
        "text": text.getvalue(),
        "binary": binary.getvalue().hex(),
        "types": [type(text).__name__, type(binary).__name__],
        "wrong_write": error_name(text.write, b"bad"),
    }


def dictionary_helpers():
    mapping = {"a": 1, "b": 2}
    keys = six.viewkeys(mapping)
    values = six.viewvalues(mapping)
    items = six.viewitems(mapping)
    mapping["c"] = 3

    class Multi:
        def __init__(self):
            self.seen = None

        def lists(self, **kwargs):
            self.seen = kwargs
            return [("a", [1, 2])]

    multi = Multi()
    lists = list(six.iterlists(multi, marker=42))
    return {
        "iterkeys": list(six.iterkeys(mapping)),
        "itervalues": list(six.itervalues(mapping)),
        "iteritems": [list(item) for item in six.iteritems(mapping)],
        "views": [sorted(keys), sorted(values), [list(item) for item in sorted(items)]],
        "iterlists": [[key, value] for key, value in lists],
        "kwargs": multi.seen,
    }


def function_accessors():
    marker = 42

    def sample(first, second=3):
        return marker + first + second

    class Holder:
        def method(self, value):
            return value + 1

    holder = Holder()
    closure = six.get_function_closure(sample)
    return {
        "defaults": list(six.get_function_defaults(sample)),
        "code_name": six.get_function_code(sample).co_name,
        "globals_name": six.get_function_globals(sample)["__name__"],
        "closure": [cell.cell_contents for cell in closure],
        "method_function": six.get_method_function(holder.method).__name__,
        "method_self_class": type(six.get_method_self(holder.method)).__name__,
        "unbound_name": six.get_unbound_function(Holder.method).__name__,
        "missing_method_error": error_name(six.get_method_self, 42),
    }


def iterator_helpers():
    class Portable(six.Iterator):
        def __next__(self):
            return 13

    iterator = iter([1, 2])
    values = [six.next(iterator), six.advance_iterator(iterator)]
    return {
        "alias": six.next is six.advance_iterator,
        "values": values,
        "exhausted": error_name(six.next, iterator),
        "portable": six.advance_iterator(Portable()),
        "callable": [
            six.callable(Portable),
            six.callable(Portable()),
            six.callable(lambda: None),
            six.callable(4),
        ],
    }


def method_constructors():
    class Holder:
        def __init__(self, value):
            self.value = value

    def read(self):
        return self.value

    holder = Holder(17)
    bound = six.create_bound_method(read, holder)
    unbound = six.create_unbound_method(read, Holder)
    return {
        "bound_type": type(bound).__name__,
        "bound_value": bound(),
        "bound_self": bound.__self__ is holder,
        "unbound_value": unbound(holder),
        "unbound_error": error_name(unbound),
    }


def exec_namespaces():
    first = {}
    six.exec_("x = 42", first)
    glob = {}
    local = {}
    six.exec_("global y; y = 42; x = 12", glob, local)
    return {
        "first": first["x"],
        "global_y": glob["y"],
        "global_has_x": "x" in glob,
        "local_x": local["x"],
        "local_has_y": "y" in local,
    }


def print_function():
    normal = six.StringIO()
    six.print_("Hello,", "person!", file=normal)
    custom = six.StringIO()
    six.print_("a", "b", file=custom, sep="X", end="!")

    class Flushable(six.StringIO):
        def __init__(self):
            super().__init__()
            self.flushed = False

        def flush(self):
            self.flushed = True

    flushable = Flushable()
    six.print_("ok", file=flushable, flush=True)
    return {
        "normal": normal.getvalue(),
        "custom": custom.getvalue(),
        "flushed": flushable.flushed,
        "errors": [
            error_name(six.print_, "x", file=io.StringIO(), sep=3),
            error_name(six.print_, "x", file=io.StringIO(), end=3),
        ],
    }


def exception_helpers():
    original = ValueError("original")
    try:
        raise original
    except ValueError:
        tp, value, traceback = sys.exc_info()
    try:
        six.reraise(tp, value, traceback)
    except Exception as reraised:
        reraise_result = [type(reraised).__name__, str(reraised), reraised is original]

    context = None
    try:
        try:
            raise KeyError("context")
        except KeyError as exc:
            context = exc
            six.raise_from(RuntimeError("outer"), None)
    except Exception as chained:
        chain_result = {
            "type": type(chained).__name__,
            "message": str(chained),
            "cause_is_none": chained.__cause__ is None,
            "context_preserved": chained.__context__ is context,
            "suppressed": chained.__suppress_context__,
        }
    return {"reraise": reraise_result, "raise_from": chain_result}


def with_metaclass_helper():
    class Prepared(dict):
        pass

    class Meta(type):
        @classmethod
        def __prepare__(cls, name, bases):
            return Prepared(meta_name=cls.__name__, base_names=[base.__name__ for base in bases])

    class Base:
        pass

    class Built(six.with_metaclass(Meta, Base)):
        marker = 7

    return {
        "meta": type(Built).__name__,
        "bases": [base.__name__ for base in Built.__bases__],
        "mro": [item.__name__ for item in Built.__mro__],
        "prepared_type": type(Built.__dict__).__name__,
        "prepared_values": [Built.meta_name, Built.base_names],
        "marker": Built().marker,
    }


def add_metaclass_helper():
    class Meta(type):
        marker = "meta"

    class Base:
        base = "base"

    @six.add_metaclass(Meta)
    class Built(Base):
        "kept doc"

    @six.add_metaclass(Meta)
    class Slotted:
        __slots__ = ("value",)

    instance = Slotted()
    instance.value = 9
    return {
        "meta": type(Built).__name__,
        "bases": [base.__name__ for base in Built.__bases__],
        "doc": Built.__doc__,
        "qualname_suffix": Built.__qualname__.endswith("add_metaclass_helper.<locals>.Built"),
        "slots": list(Slotted.__slots__),
        "slot_value": instance.value,
        "dict_error": error_name(setattr, instance, "other", 1),
        "attributes": [Built.marker, Built.base],
    }


def unicode_decorator():
    @six.python_2_unicode_compatible
    class Value:
        def __str__(self):
            return "hello"

        def __bytes__(self):
            return b"hello"

    value = Value()
    return {"str": str(value), "bytes": bytes(value).hex(), "class": type(value).__name__}


def wraps_helper():
    def original():
        "original doc"

    original.marker = 43
    original.settings = {"original": 1}

    def wrapper():
        return 42

    wrapper.settings = {"wrapper": 2}
    decorated = six.wraps(
        original,
        assigned=("__name__", "__doc__", "marker"),
        updated=("settings",),
    )(wrapper)
    missing_error = error_name(six.wraps(original, (), ("missing",)), lambda: None)
    return {
        "name": decorated.__name__,
        "doc": decorated.__doc__,
        "marker": decorated.marker,
        "settings": decorated.settings,
        "wrapped_identity": decorated.__wrapped__ is original,
        "call": decorated(),
        "missing_error": missing_error,
    }


def unittest_aliases():
    case = unittest.TestCase()
    six.assertCountEqual(case, [1, 2, 2], [2, 1, 2])
    six.assertRegex(case, "hello", r"^he")
    six.assertNotRegex(case, "hello", r"xyz")
    with six.assertRaisesRegex(case, ValueError, r"bad value"):
        raise ValueError("bad value")
    return {
        "success": True,
        "count_error": error_name(six.assertCountEqual, case, [1], [2]),
        "regex_error": error_name(six.assertRegex, case, "hello", r"^x"),
        "not_regex_error": error_name(six.assertNotRegex, case, "hello", r"ell"),
    }


def moves_modules():
    from six.moves import builtins, cPickle, collections_abc, configparser, html_parser, queue
    from six.moves.configparser import ConfigParser
    from six.moves.queue import Queue

    return {
        "module_names": [
            builtins.__name__,
            cPickle.__name__,
            collections_abc.__name__,
            configparser.__name__,
            html_parser.__name__,
            queue.__name__,
        ],
        "classes": [ConfigParser.__name__, Queue.__name__],
        "dir_entries": all(
            name in dir(six.moves)
            for name in ("builtins", "configparser", "queue", "html_parser", "urllib_parse")
        ),
    }


def moves_iterables():
    from six.moves import filter, filterfalse, map, range, reduce, zip, zip_longest

    return {
        "filter": list(filter(lambda item: item % 2, range(6))),
        "filterfalse": list(filterfalse(lambda item: item % 3, range(7))),
        "map": list(map(lambda item: item + 1, range(3))),
        "range": list(range(2, 5)),
        "reduce": reduce(lambda left, right: left + right, [1, 2, 3]),
        "zip": [list(item) for item in zip(range(2), range(2, 4))],
        "zip_longest": [list(item) for item in zip_longest(range(2), range(1))],
    }


def urllib_moves():
    from six.moves import urllib_error, urllib_parse, urllib_request, urllib_response
    from six.moves.urllib import error, parse, request, response, robotparser
    from six.moves.urllib.parse import urljoin

    parsed = parse.urlparse("https://example.test/a?x=1")
    return {
        "parsed": [parsed.scheme, parsed.netloc, parsed.path, parsed.query],
        "joined": urljoin("https://example.test/a/", "../b"),
        "quoted": urllib_parse.quote("a b/"),
        "module_aliases": [
            parse is urllib_parse,
            error is urllib_error,
            request is urllib_request,
            response is urllib_response,
        ],
        "types": [
            urllib_error.URLError.__name__,
            urllib_request.Request.__name__,
            urllib_response.addinfourl.__name__,
            robotparser.RobotFileParser.__name__,
        ],
    }


def custom_moves():
    module_move = six.MovedModule("contract_json", "json", "json")
    six.add_move(module_move)
    imported_module = six.moves.contract_json
    module_result = [imported_module.__name__, imported_module.loads("{\"x\": 2}")["x"]]
    six.remove_move("contract_json")

    attribute_move = six.MovedAttribute(
        "contract_decoder", "json", "json", "JSONDecoder", "JSONDecoder"
    )
    six.add_move(attribute_move)
    decoder = six.moves.contract_decoder
    attribute_result = [decoder.__name__, decoder().decode("{\"y\": 3}")["y"]]
    six.remove_move("contract_decoder")
    return {
        "module": module_result,
        "attribute": attribute_result,
        "removed": [
            hasattr(six.moves, "contract_json"),
            hasattr(six.moves, "contract_decoder"),
        ],
        "missing_error": error_name(six.remove_move, "contract_missing"),
    }


def import_protocol():
    direct = importlib.import_module("six.moves.urllib_parse")
    nested = importlib.import_module("six.moves.urllib.parse")
    queue_module = importlib.import_module("six.moves.queue")
    return {
        "parse_identity": direct is nested,
        "parse_name": direct.__name__,
        "queue_name": queue_module.__name__,
        "spec_names": [direct.__spec__.name, nested.__spec__.name, queue_module.__spec__.name],
        "paths": [list(six.__path__), list(six.moves.__path__)],
    }


OPERATIONS = {
    "package_identity": package_identity,
    "byte_literals": byte_literals,
    "ensure_conversions": ensure_conversions,
    "io_aliases": io_aliases,
    "dictionary_helpers": dictionary_helpers,
    "function_accessors": function_accessors,
    "iterator_helpers": iterator_helpers,
    "method_constructors": method_constructors,
    "exec_namespaces": exec_namespaces,
    "print_function": print_function,
    "exception_helpers": exception_helpers,
    "with_metaclass_helper": with_metaclass_helper,
    "add_metaclass_helper": add_metaclass_helper,
    "unicode_decorator": unicode_decorator,
    "wraps_helper": wraps_helper,
    "unittest_aliases": unittest_aliases,
    "moves_modules": moves_modules,
    "moves_iterables": moves_iterables,
    "urllib_moves": urllib_moves,
    "custom_moves": custom_moves,
    "import_protocol": import_protocol,
}


def main():
    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
            operation = request["operation"]
            result = OPERATIONS[operation]()
            response = {"id": request["id"], "ok": True, "result": result}
        except Exception as exc:
            response = {
                "id": request.get("id") if isinstance(request, dict) else None,
                "ok": False,
                "error": type(exc).__name__,
            }
        print(json.dumps(response, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
