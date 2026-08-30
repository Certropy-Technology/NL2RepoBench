from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=3.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {"status": "passed" if actual == expected else "failed", "actual": actual}


CASES: list[tuple[str, str, object]] = [
    (
        "package-metadata",
        "from importlib.metadata import version\n"
        "from importlib.resources import files\n"
        "import typing_inspection\n"
        "result = [version('typing-inspection'), "
        "files('typing_inspection').joinpath('py.typed').is_file(), typing_inspection.__name__]",
        {"ok": True, "value": ["0.4.4", True, "typing_inspection"]},
    ),
    (
        "module-exports",
        "from typing_inspection import introspection, typing_objects\n"
        "result = [list(introspection.__all__), list(typing_objects.__all__)]",
        {
            "ok": True,
            "value": [
                [
                    "AnnotationSource",
                    "ForbiddenQualifier",
                    "InspectedAnnotation",
                    "Qualifier",
                    "get_literal_values",
                    "inspect_annotation",
                    "is_union_origin",
                ],
                [
                    "DEPRECATED_ALIASES",
                    "DEPRECATED_ALIASES_IDS",
                    "NoneType",
                    "is_annotated",
                    "is_any",
                    "is_classvar",
                    "is_concatenate",
                    "is_deprecated",
                    "is_final",
                    "is_forwardref",
                    "is_generic",
                    "is_literal",
                    "is_literalstring",
                    "is_namedtuple",
                    "is_never",
                    "is_newtype",
                    "is_nodefault",
                    "is_noextraitems",
                    "is_noreturn",
                    "is_notrequired",
                    "is_paramspec",
                    "is_paramspecargs",
                    "is_paramspeckwargs",
                    "is_readonly",
                    "is_required",
                    "is_self",
                    "is_typealias",
                    "is_typealiastype",
                    "is_typeguard",
                    "is_typeis",
                    "is_typevar",
                    "is_typevartuple",
                    "is_union",
                    "is_unpack",
                ],
            ],
        },
    ),
    (
        "union-origins",
        "import types, typing\n"
        "from typing_inspection.introspection import is_union_origin\n"
        "items = [typing.Union, typing.get_origin(typing.Union[int, str]), "
        "typing.get_origin(int | str), types.UnionType, int]\n"
        "result = [is_union_origin(item) for item in items]",
        {"ok": True, "value": [True, True, True, True, False]},
    ),
    (
        "literal-basic",
        "from typing import Literal\n"
        "from typing_inspection.introspection import get_literal_values\n"
        "result = [repr(value) for value in "
        "get_literal_values(Literal[1, 'x', True, b'b', None])]",
        {"ok": True, "value": ["1", "'x'", "True", "b'b'", "None"]},
    ),
    (
        "literal-none-deduplication",
        "from typing import Literal\n"
        "from typing_inspection.introspection import get_literal_values\n"
        "result = [repr(value) for value in "
        "get_literal_values(Literal[None, type(None), None])]",
        {"ok": True, "value": ["None"]},
    ),
    (
        "literal-enum-type-check",
        "from enum import Enum\n"
        "from typing import Literal\n"
        "from typing_inspection.introspection import get_literal_values\n"
        "class Color(Enum):\n"
        "    RED = 1\n"
        "value = list(get_literal_values(Literal[Color.RED], type_check=True))[0]\n"
        "result = [type(value).__name__, value.name, value.value]",
        {"ok": True, "value": ["Color", "RED", 1]},
    ),
    (
        "literal-type-check-error",
        "from typing import Literal\n"
        "from typing_inspection.introspection import get_literal_values\n"
        "try:\n"
        "    list(get_literal_values(Literal[1.5], type_check=True))\n"
        "except Exception as exc:\n"
        "    result = [type(exc).__module__ + '.' + type(exc).__name__, str(exc)]",
        {
            "ok": True,
            "value": [
                "builtins.TypeError",
                "1.5 is not a valid literal value, must be one of: int, bytes, str, Enum, None.",
            ],
        },
    ),
    (
        "literal-unhashable-values",
        "from typing import Literal\n"
        "from typing_inspection.introspection import get_literal_values\n"
        "result = [repr(value) for value in get_literal_values(Literal[[1], [1]])]",
        {"ok": True, "value": ["[1]", "[1]"]},
    ),
    (
        "annotation-source-members",
        "from typing_inspection.introspection import AnnotationSource\n"
        "result = [[source.name, source.value, sorted(source.allowed_qualifiers)] "
        "for source in AnnotationSource]",
        {
            "ok": True,
            "value": [
                ["ASSIGNMENT_OR_VARIABLE", 1, ["final"]],
                ["CLASS", 2, ["class_var", "final"]],
                ["DATACLASS", 3, ["class_var", "final", "init_var"]],
                ["TYPED_DICT", 4, ["not_required", "read_only", "required"]],
                ["NAMED_TUPLE", 5, []],
                ["FUNCTION", 6, []],
                [
                    "ANY",
                    7,
                    ["class_var", "final", "init_var", "not_required", "read_only", "required"],
                ],
                ["BARE", 8, []],
            ],
        },
    ),
    (
        "unknown-sentinel",
        "from typing_inspection.introspection import UNKNOWN\n"
        "result = [str(UNKNOWN), repr(UNKNOWN), UNKNOWN is UNKNOWN]",
        {"ok": True, "value": ["UNKNOWN", "<UNKNOWN>", True]},
    ),
    (
        "inspected-annotation-shape",
        "from typing_inspection.introspection import InspectedAnnotation\n"
        "item = InspectedAnnotation(int, {'final'}, ['meta'])\n"
        "result = [list(item._fields), item.type.__name__, sorted(item.qualifiers), item.metadata, len(item)]",
        {"ok": True, "value": [["type", "qualifiers", "metadata"], "int", ["final"], ["meta"], 3]},
    ),
    (
        "inspect-simple",
        "from typing_inspection.introspection import AnnotationSource, inspect_annotation\n"
        "item = inspect_annotation(int, annotation_source=AnnotationSource.BARE)\n"
        "result = [item.type.__name__, sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": ["int", [], []]},
    ),
    (
        "inspect-annotated",
        "from typing import Annotated\n"
        "from typing_inspection.introspection import AnnotationSource, inspect_annotation\n"
        "item = inspect_annotation(Annotated[int, 'inner', 42], annotation_source=AnnotationSource.BARE)\n"
        "result = [item.type.__name__, sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": ["int", [], ["inner", 42]]},
    ),
    (
        "inspect-nested-metadata",
        "from typing import Annotated\n"
        "from typing_inspection.introspection import AnnotationSource, inspect_annotation\n"
        "annotation = Annotated[Annotated[int, 'inner'], 'outer']\n"
        "item = inspect_annotation(annotation, annotation_source=AnnotationSource.BARE)\n"
        "result = [item.type.__name__, sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": ["int", [], ["inner", "outer"]]},
    ),
    (
        "inspect-class-qualifiers",
        "from typing_extensions import Annotated, ClassVar, Final\n"
        "from typing_inspection.introspection import AnnotationSource, inspect_annotation\n"
        "item = inspect_annotation(Final[Annotated[ClassVar[int], 'meta']], "
        "annotation_source=AnnotationSource.CLASS)\n"
        "result = [item.type.__name__, sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": ["int", ["class_var", "final"], ["meta"]]},
    ),
    (
        "inspect-dataclass-initvar",
        "from dataclasses import InitVar\n"
        "from typing_inspection.introspection import AnnotationSource, inspect_annotation\n"
        "item = inspect_annotation(InitVar[int], annotation_source=AnnotationSource.DATACLASS)\n"
        "result = [item.type.__name__, sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": ["int", ["init_var"], []]},
    ),
    (
        "inspect-typed-dict-qualifiers",
        "from typing import NotRequired\n"
        "from typing_extensions import ReadOnly\n"
        "from typing_inspection.introspection import AnnotationSource, inspect_annotation\n"
        "item = inspect_annotation(ReadOnly[NotRequired[str]], "
        "annotation_source=AnnotationSource.TYPED_DICT)\n"
        "result = [item.type.__name__, sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": ["str", ["not_required", "read_only"], []]},
    ),
    (
        "inspect-bare-final",
        "from typing import Final\n"
        "from typing_inspection.introspection import AnnotationSource, UNKNOWN, inspect_annotation\n"
        "item = inspect_annotation(Final, annotation_source=AnnotationSource.ASSIGNMENT_OR_VARIABLE)\n"
        "result = [item.type is UNKNOWN, repr(item.type), sorted(item.qualifiers), item.metadata]",
        {"ok": True, "value": [True, "<UNKNOWN>", ["final"], []]},
    ),
    (
        "forbidden-qualifier",
        "from typing import Final\n"
        "from typing_inspection.introspection import AnnotationSource, ForbiddenQualifier, inspect_annotation\n"
        "try:\n"
        "    inspect_annotation(Final[int], annotation_source=AnnotationSource.FUNCTION)\n"
        "except ForbiddenQualifier as exc:\n"
        "    result = [type(exc).__name__, exc.qualifier, str(exc)]",
        {"ok": True, "value": ["ForbiddenQualifier", "final", "final"]},
    ),
    (
        "typing-basic-forms",
        "import typing\n"
        "from typing_inspection import typing_objects as objects\n"
        "pairs = [('annotated', objects.is_annotated, typing.Annotated), "
        "('any', objects.is_any, typing.Any), ('classvar', objects.is_classvar, typing.ClassVar), "
        "('concatenate', objects.is_concatenate, typing.Concatenate), "
        "('final', objects.is_final, typing.Final), ('generic', objects.is_generic, typing.Generic), "
        "('literal', objects.is_literal, typing.Literal)]\n"
        "result = [[name, check(value)] for name, check, value in pairs]",
        {
            "ok": True,
            "value": [
                ["annotated", True],
                ["any", True],
                ["classvar", True],
                ["concatenate", True],
                ["final", True],
                ["generic", True],
                ["literal", True],
            ],
        },
    ),
    (
        "union-member-distinction",
        "import types, typing\n"
        "from typing_inspection.typing_objects import is_union\n"
        "result = [is_union(value) for value in "
        "[typing.Union, types.UnionType, typing.get_origin(int | str), int]]",
        {"ok": True, "value": [True, False, False, False]},
    ),
    (
        "type-variable-objects",
        "import typing\n"
        "from typing_inspection import typing_objects as objects\n"
        "P = typing.ParamSpec('P')\nT = typing.TypeVar('T')\nTs = typing.TypeVarTuple('Ts')\n"
        "result = [objects.is_paramspec(P), objects.is_typevar(T), objects.is_typevartuple(Ts), "
        "objects.is_paramspecargs(P.args), objects.is_paramspeckwargs(P.kwargs), "
        "objects.is_forwardref(typing.ForwardRef('X'))]",
        {"ok": True, "value": [True, True, True, True, True, True]},
    ),
    (
        "stdlib-special-forms",
        "import typing\n"
        "from typing_inspection import typing_objects as objects\n"
        "result = [objects.is_literalstring(typing.LiteralString), objects.is_never(typing.Never), "
        "objects.is_noreturn(typing.NoReturn), objects.is_required(typing.Required), "
        "objects.is_notrequired(typing.NotRequired), objects.is_self(typing.Self), "
        "objects.is_typealias(typing.TypeAlias), objects.is_typeguard(typing.TypeGuard), "
        "objects.is_unpack(typing.Unpack)]",
        {"ok": True, "value": [True, True, True, True, True, True, True, True, True]},
    ),
    (
        "extensions-special-forms",
        "import typing_extensions as extensions\n"
        "from typing_inspection import typing_objects as objects\n"
        "result = [objects.is_readonly(extensions.ReadOnly), objects.is_typeis(extensions.TypeIs), "
        "objects.is_nodefault(extensions.NoDefault), objects.is_noextraitems(extensions.NoExtraItems)]",
        {"ok": True, "value": [True, True, True, True]},
    ),
    (
        "namedtuple-detection",
        "import collections, typing\n"
        "from typing_inspection.typing_objects import is_namedtuple\n"
        "class TypingTuple(typing.NamedTuple):\n    value: int\n"
        "CollectionsTuple = collections.namedtuple('CollectionsTuple', 'value')\n"
        "result = [is_namedtuple(TypingTuple), is_namedtuple(CollectionsTuple), "
        "is_namedtuple(tuple), is_namedtuple(TypingTuple(1))]",
        {"ok": True, "value": [True, True, False, False]},
    ),
    (
        "newtype-detection",
        "from typing import NewType\n"
        "from typing_inspection.typing_objects import is_newtype\n"
        "UserId = NewType('UserId', int)\n"
        "result = [is_newtype(UserId), is_newtype(int), is_newtype(UserId(1))]",
        {"ok": True, "value": [True, False, False]},
    ),
    (
        "type-alias-type",
        "from typing_extensions import TypeAliasType\n"
        "from typing_inspection.typing_objects import is_typealiastype\n"
        "Alias = TypeAliasType('Alias', int)\n"
        "result = [is_typealiastype(Alias), is_typealiastype(int)]",
        {"ok": True, "value": [True, False]},
    ),
    (
        "deprecated-marker",
        "from typing_extensions import deprecated\n"
        "from typing_inspection.typing_objects import is_deprecated\n"
        "marker = deprecated('use something else')\n"
        "result = [is_deprecated(marker), is_deprecated(deprecated), is_deprecated(int)]",
        {"ok": True, "value": [True, False, False]},
    ),
    (
        "negative-predicate-table",
        "from typing_inspection import typing_objects as objects\n"
        "names = [name for name in objects.__all__ if name.startswith('is_')]\n"
        "probe = object()\n"
        "result = [name for name in names if getattr(objects, name)(probe)]",
        {"ok": True, "value": []},
    ),
    (
        "deprecated-alias-maps",
        "import re, typing\n"
        "from typing_inspection.typing_objects import DEPRECATED_ALIASES, DEPRECATED_ALIASES_IDS\n"
        "pairs = [(typing.List, list), (typing.Dict, dict), (typing.Pattern, re.Pattern), "
        "(typing.Match, re.Match)]\n"
        "result = [[DEPRECATED_ALIASES.get(old) is new, "
        "DEPRECATED_ALIASES_IDS.get(id(old)) is new] for old, new in pairs]",
        {"ok": True, "value": [[True, True], [True, True], [True, True], [True, True]]},
    ),
    (
        "positional-only-contract",
        "import typing\n"
        "from typing_inspection import introspection, typing_objects\n"
        "calls = [(typing_objects.is_any, {'obj': typing.Any}), "
        "(introspection.is_union_origin, {'obj': typing.Union}), "
        "(introspection.get_literal_values, {'annotation': typing.Literal[1]}), "
        "(introspection.inspect_annotation, "
        "{'annotation': int, 'annotation_source': introspection.AnnotationSource.BARE})]\n"
        "result = []\n"
        "for function, kwargs in calls:\n"
        "    try:\n        function(**kwargs)\n"
        "    except TypeError as exc:\n"
        "        result.append(['TypeError', 'positional-only' in str(exc)])",
        {"ok": True, "value": [["TypeError", True]] * 4},
    ),
    (
        "repeat-determinism",
        "from typing import Annotated, Literal\n"
        "from typing_inspection.introspection import AnnotationSource, get_literal_values, inspect_annotation\n"
        "def run():\n"
        "    literals = list(get_literal_values(Literal[1, 2, 1]))\n"
        "    item = inspect_annotation(Annotated[int, 'meta'], annotation_source=AnnotationSource.BARE)\n"
        "    return [literals, item.type.__name__, sorted(item.qualifiers), item.metadata]\n"
        "result = [run(), run(), run()]",
        {
            "ok": True,
            "value": [[[1, 2], "int", [], ["meta"]]] * 3,
        },
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        outcome = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": outcome["status"]}
        if outcome["status"] == "failed":
            leaf["message"] = json.dumps(outcome["actual"], sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
