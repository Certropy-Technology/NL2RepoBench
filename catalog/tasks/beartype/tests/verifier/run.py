"""Private deterministic scenarios for the beartype 0.22.9 public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/beartype/beartype,
version 0.22.9, revision 9430c6515af3b158acacdc47fe7b1adb646f6624). The
candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=30.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


# Test cases organized by module/API surface
# Each tuple: (id, source_code, expected_result)
CASES: list[tuple[str, str, object]] = [
    (
        'beartype-import',
        'import beartype\nresult = callable(beartype.beartype)',
        {"ok": True, "value": True},
    ),
    (
        'beartype-version',
        'import beartype\nresult = beartype.__version__',
        {"ok": True, "value": "0.22.9"},
    ),
    (
        'beartype-version-info',
        'import beartype\nresult = beartype.__version_info__',
        {"ok": True, "value": [0, 22, 9]},
    ),
    (
        'beartype-decorator-int-pass',
        'import beartype as _be\n@_be.beartype\ndef f(x: int) -> int:\n    return x * 2\nresult = f(5)',
        {"ok": True, "value": 10},
    ),
    (
        'beartype-decorator-int-fail',
        "import beartype as _be\nimport beartype.roar\n@_be.beartype\ndef f(x: int) -> int:\n    return x * 2\ntry:\n    f('string')\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintParamViolation:\n    result = 'param-violation'",
        {"ok": True, "value": "param-violation"},
    ),
    (
        'beartype-decorator-str-pass',
        "import beartype as _be\n@_be.beartype\ndef greet(name: str) -> str:\n    return 'Hello, ' + name\nresult = greet('World')",
        {"ok": True, "value": "Hello, World"},
    ),
    (
        'beartype-decorator-str-fail',
        "import beartype as _be\nimport beartype.roar\n@_be.beartype\ndef greet(name: str) -> str:\n    return 'Hello, ' + str(name)\ntry:\n    greet(42)\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintParamViolation:\n    result = 'param-violation'",
        {"ok": True, "value": "param-violation"},
    ),
    (
        'beartype-decorator-return-fail',
        "import beartype as _be\nimport beartype.roar\n@_be.beartype\ndef bad() -> int:\n    return 'string'\ntry:\n    bad()\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintReturnViolation:\n    result = 'return-violation'",
        {"ok": True, "value": "return-violation"},
    ),
    (
        'beartype-decorator-list-int-pass',
        'import beartype as _be\n@_be.beartype\ndef sum_list(items: list[int]) -> int:\n    return sum(items)\nresult = sum_list([1, 2, 3, 4, 5])',
        {"ok": True, "value": 15},
    ),
    (
        'beartype-decorator-list-int-empty',
        'import beartype as _be\n@_be.beartype\ndef sum_list(items: list[int]) -> int:\n    return sum(items)\nresult = sum_list([])',
        {"ok": True, "value": 0},
    ),
    (
        'beartype-decorator-dict-pass',
        "import beartype as _be\n@_be.beartype\ndef get_val(d: dict[str, int], k: str) -> int:\n    return d.get(k, 0)\nresult = get_val({'a': 1, 'b': 2}, 'a')",
        {"ok": True, "value": 1},
    ),
    (
        'beartype-decorator-optional-none',
        "import beartype as _be\nfrom typing import Optional\n@_be.beartype\ndef maybe_upper(s: Optional[str]) -> str:\n    return s.upper() if s else 'NONE'\nresult = maybe_upper(None)",
        {"ok": True, "value": "NONE"},
    ),
    (
        'beartype-decorator-optional-str',
        "import beartype as _be\nfrom typing import Optional\n@_be.beartype\ndef maybe_upper(s: Optional[str]) -> str:\n    return s.upper() if s else 'NONE'\nresult = maybe_upper('hello')",
        {"ok": True, "value": "HELLO"},
    ),
    (
        'beartype-decorator-union',
        "import beartype as _be\nfrom typing import Union\n@_be.beartype\ndef process(val: Union[int, str]) -> str:\n    return str(val)\nresult = [process(42), process('text')]",
        {"ok": True, "value": ["42", "text"]},
    ),
    (
        'beartype-decorator-tuple-fixed',
        "import beartype as _be\n@_be.beartype\ndef pair(t: tuple[int, str]) -> str:\n    return f'{t[0]}:{t[1]}'\nresult = pair((1, 'a'))",
        {"ok": True, "value": "1:a"},
    ),
    (
        'beartype-decorator-tuple-variable',
        "import beartype as _be\n@_be.beartype\ndef join_ints(t: tuple[int, ...]) -> str:\n    return ','.join(map(str, t))\nresult = join_ints((1, 2, 3))",
        {"ok": True, "value": "1,2,3"},
    ),
    (
        'beartype-decorator-no-annotation',
        'import beartype as _be\n@_be.beartype\ndef plain(x):\n    return x + 1\nresult = plain(5)',
        {"ok": True, "value": 6},
    ),
    (
        'beartype-decorator-class',
        'import beartype as _be\n@_be.beartype\nclass Point:\n    def __init__(self, x: int, y: int):\n        self.x = x\n        self.y = y\np = Point(1, 2)\nresult = [p.x, p.y]',
        {"ok": True, "value": [1, 2]},
    ),
    (
        'beartype-decorator-method',
        'import beartype as _be\nclass Calculator:\n    @_be.beartype\n    def add(self, a: int, b: int) -> int:\n        return a + b\nc = Calculator()\nresult = c.add(3, 4)',
        {"ok": True, "value": 7},
    ),
    (
        'beartype-literal-pass',
        "import beartype as _be\nfrom typing import Literal\n@_be.beartype\ndef mode(m: Literal['read', 'write']) -> str:\n    return m.upper()\nresult = mode('read')",
        {"ok": True, "value": "READ"},
    ),
    (
        'conf-import',
        'from beartype import BeartypeConf\nresult = BeartypeConf is not None',
        {"ok": True, "value": True},
    ),
    (
        'conf-default-construct',
        'from beartype import BeartypeConf\nc = BeartypeConf()\nresult = c is not None',
        {"ok": True, "value": True},
    ),
    (
        'conf-strategy-import',
        "from beartype import BeartypeStrategy\nresult = hasattr(BeartypeStrategy, 'O1')",
        {"ok": True, "value": True},
    ),
    (
        'conf-strategy-members',
        'from beartype import BeartypeStrategy\nresult = sorted([s.name for s in BeartypeStrategy])',
        {"ok": True, "value": ["O0", "O1", "Ologn", "On"]},
    ),
    (
        'conf-verbosity-import',
        "from beartype import BeartypeViolationVerbosity\nresult = hasattr(BeartypeViolationVerbosity, 'DEFAULT')",
        {"ok": True, "value": True},
    ),
    (
        'conf-verbosity-members',
        'from beartype import BeartypeViolationVerbosity\nresult = sorted([v.name for v in BeartypeViolationVerbosity])',
        {"ok": True, "value": ["DEFAULT", "MAXIMAL", "MINIMAL"]},
    ),
    (
        'conf-decor-place-import',
        "from beartype import BeartypeDecorPlace\nresult = hasattr(BeartypeDecorPlace, 'FIRST')",
        {"ok": True, "value": True},
    ),
    (
        'conf-with-strategy',
        'from beartype import BeartypeConf, BeartypeStrategy\nc = BeartypeConf(strategy=BeartypeStrategy.O0)\nresult = c.strategy == BeartypeStrategy.O0',
        {"ok": True, "value": True},
    ),
    (
        'conf-with-verbosity',
        'from beartype import BeartypeConf, BeartypeViolationVerbosity\nc = BeartypeConf(violation_verbosity=BeartypeViolationVerbosity.MINIMAL)\nresult = c.violation_verbosity == BeartypeViolationVerbosity.MINIMAL',
        {"ok": True, "value": True},
    ),
    (
        'conf-is-debug-default',
        'from beartype import BeartypeConf\nc = BeartypeConf()\nresult = c.is_debug',
        {"ok": True, "value": False},
    ),
    (
        'conf-is-debug-true',
        'from beartype import BeartypeConf\nc = BeartypeConf(is_debug=True)\nresult = c.is_debug',
        {"ok": True, "value": True},
    ),
    (
        'conf-decorator-with-conf',
        'import beartype as _be\nfrom beartype import BeartypeConf, BeartypeStrategy\nc = BeartypeConf(strategy=BeartypeStrategy.O1)\n@_be.beartype(conf=c)\ndef f(x: int) -> int:\n    return x * 2\nresult = f(3)',
        {"ok": True, "value": 6},
    ),
    (
        'conf-equality-same',
        'from beartype import BeartypeConf\nc1 = BeartypeConf()\nc2 = BeartypeConf()\nresult = c1 == c2',
        {"ok": True, "value": True},
    ),
    (
        'conf-equality-different',
        'from beartype import BeartypeConf\nc1 = BeartypeConf(is_debug=False)\nc2 = BeartypeConf(is_debug=True)\nresult = c1 == c2',
        {"ok": True, "value": False},
    ),
    (
        'conf-hash-stable',
        'from beartype import BeartypeConf\nc1 = BeartypeConf()\nc2 = BeartypeConf()\nresult = hash(c1) == hash(c2)',
        {"ok": True, "value": True},
    ),
    (
        'conf-repr',
        "from beartype import BeartypeConf\nc = BeartypeConf()\nresult = 'BeartypeConf' in repr(c)",
        {"ok": True, "value": True},
    ),
    (
        'conf-kwargs-property',
        'from beartype import BeartypeConf\nc = BeartypeConf(is_debug=True)\nresult = isinstance(c.kwargs, dict)',
        {"ok": True, "value": True},
    ),
    (
        'conf-is-pep484-tower-default',
        'from beartype import BeartypeConf\nc = BeartypeConf()\nresult = c.is_pep484_tower',
        {"ok": True, "value": False},
    ),
    (
        'conf-claw-is-pep526-default',
        'from beartype import BeartypeConf\nc = BeartypeConf()\nresult = c.claw_is_pep526',
        {"ok": True, "value": True},
    ),
    (
        'door-import-is-bearable',
        'from beartype.door import is_bearable\nresult = callable(is_bearable)',
        {"ok": True, "value": True},
    ),
    (
        'door-import-die-if-unbearable',
        'from beartype.door import die_if_unbearable\nresult = callable(die_if_unbearable)',
        {"ok": True, "value": True},
    ),
    (
        'door-import-is-subhint',
        'from beartype.door import is_subhint\nresult = callable(is_subhint)',
        {"ok": True, "value": True},
    ),
    (
        'door-import-typehint',
        'from beartype.door import TypeHint\nresult = TypeHint is not None',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-int-true',
        'from beartype.door import is_bearable\nresult = is_bearable(42, int)',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-int-false',
        "from beartype.door import is_bearable\nresult = is_bearable('string', int)",
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-str-true',
        "from beartype.door import is_bearable\nresult = is_bearable('hello', str)",
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-str-false',
        'from beartype.door import is_bearable\nresult = is_bearable(123, str)',
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-list-int-true',
        'from beartype.door import is_bearable\nresult = is_bearable([1, 2, 3], list[int])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-list-int-false',
        "from beartype.door import is_bearable\nresult = is_bearable(['a', 'b'], list[int])",
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-list-int-empty',
        'from beartype.door import is_bearable\nresult = is_bearable([], list[int])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-dict-str-int-true',
        "from beartype.door import is_bearable\nresult = is_bearable({'a': 1, 'b': 2}, dict[str, int])",
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-dict-str-int-false',
        "from beartype.door import is_bearable\nresult = is_bearable({'a': 'x'}, dict[str, int])",
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-dict-empty',
        'from beartype.door import is_bearable\nresult = is_bearable({}, dict[str, int])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-tuple-fixed-true',
        "from beartype.door import is_bearable\nresult = is_bearable((1, 'a'), tuple[int, str])",
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-tuple-fixed-false',
        'from beartype.door import is_bearable\nresult = is_bearable((1, 2), tuple[int, str])',
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-tuple-variable-true',
        'from beartype.door import is_bearable\nresult = is_bearable((1, 2, 3), tuple[int, ...])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-tuple-variable-empty',
        'from beartype.door import is_bearable\nresult = is_bearable((), tuple[int, ...])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-optional-none',
        'from beartype.door import is_bearable\nfrom typing import Optional\nresult = is_bearable(None, Optional[int])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-optional-value',
        'from beartype.door import is_bearable\nfrom typing import Optional\nresult = is_bearable(42, Optional[int])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-optional-wrong',
        "from beartype.door import is_bearable\nfrom typing import Optional\nresult = is_bearable('string', Optional[int])",
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-union-first',
        'from beartype.door import is_bearable\nfrom typing import Union\nresult = is_bearable(42, Union[int, str])',
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-union-second',
        "from beartype.door import is_bearable\nfrom typing import Union\nresult = is_bearable('hello', Union[int, str])",
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-union-neither',
        'from beartype.door import is_bearable\nfrom typing import Union\nresult = is_bearable([1, 2], Union[int, str])',
        {"ok": True, "value": False},
    ),
    (
        'door-is-bearable-literal-match',
        "from beartype.door import is_bearable\nfrom typing import Literal\nresult = is_bearable('read', Literal['read', 'write'])",
        {"ok": True, "value": True},
    ),
    (
        'door-is-bearable-literal-no-match',
        "from beartype.door import is_bearable\nfrom typing import Literal\nresult = is_bearable('append', Literal['read', 'write'])",
        {"ok": True, "value": False},
    ),
    (
        'door-die-if-unbearable-pass',
        "from beartype.door import die_if_unbearable\ndie_if_unbearable(42, int)\nresult = 'passed'",
        {"ok": True, "value": "passed"},
    ),
    (
        'door-die-if-unbearable-fail',
        "from beartype.door import die_if_unbearable\nimport beartype.roar\ntry:\n    die_if_unbearable('string', int)\n    result = 'no-error'\nexcept beartype.roar.BeartypeDoorHintViolation:\n    result = 'door-violation'",
        {"ok": True, "value": "door-violation"},
    ),
    (
        'door-die-if-unbearable-list-pass',
        "from beartype.door import die_if_unbearable\ndie_if_unbearable([1, 2, 3], list[int])\nresult = 'passed'",
        {"ok": True, "value": "passed"},
    ),
    (
        'door-die-if-unbearable-list-fail',
        "from beartype.door import die_if_unbearable\nimport beartype.roar\ntry:\n    die_if_unbearable(['a', 'b'], list[int])\n    result = 'no-error'\nexcept beartype.roar.BeartypeDoorHintViolation:\n    result = 'door-violation'",
        {"ok": True, "value": "door-violation"},
    ),
    (
        'door-is-subhint-int-int',
        'from beartype.door import is_subhint\nresult = is_subhint(int, int)',
        {"ok": True, "value": True},
    ),
    (
        'door-is-subhint-int-object',
        'from beartype.door import is_subhint\nresult = is_subhint(int, object)',
        {"ok": True, "value": True},
    ),
    (
        'typehint-construct-int',
        'from beartype.door import TypeHint\nt = TypeHint(int)\nresult = t.hint == int',
        {"ok": True, "value": True},
    ),
    (
        'typehint-construct-list',
        'from beartype.door import TypeHint\nt = TypeHint(list[int])\nresult = t.hint == list[int]',
        {"ok": True, "value": True},
    ),
    (
        'typehint-args-simple',
        'from beartype.door import TypeHint\nt = TypeHint(int)\nresult = isinstance(t.args, tuple)',
        {"ok": True, "value": True},
    ),
    (
        'typehint-args-generic',
        'from beartype.door import TypeHint\nt = TypeHint(list[int])\nresult = [isinstance(t.args, tuple), len(t.args) >= 0]',
        {"ok": True, "value": [True, True]},
    ),
    (
        'typehint-is-ignorable-int',
        'from beartype.door import TypeHint\nt = TypeHint(int)\nresult = t.is_ignorable',
        {"ok": True, "value": False},
    ),
    (
        'typehint-is-bearable-int-true',
        'from beartype.door import TypeHint\nt = TypeHint(int)\nresult = t.is_bearable(42)',
        {"ok": True, "value": True},
    ),
    (
        'typehint-is-bearable-int-false',
        "from beartype.door import TypeHint\nt = TypeHint(int)\nresult = t.is_bearable('string')",
        {"ok": True, "value": False},
    ),
    (
        'typehint-is-bearable-list-true',
        'from beartype.door import TypeHint\nt = TypeHint(list[int])\nresult = t.is_bearable([1, 2, 3])',
        {"ok": True, "value": True},
    ),
    (
        'typehint-is-bearable-list-false',
        "from beartype.door import TypeHint\nt = TypeHint(list[int])\nresult = t.is_bearable(['two'])",
        {"ok": True, "value": False},
    ),
    (
        'typehint-die-if-unbearable-pass',
        "from beartype.door import TypeHint\nt = TypeHint(int)\nt.die_if_unbearable(42)\nresult = 'passed'",
        {"ok": True, "value": "passed"},
    ),
    (
        'typehint-die-if-unbearable-fail',
        "from beartype.door import TypeHint\nimport beartype.roar\nt = TypeHint(int)\ntry:\n    t.die_if_unbearable('string')\n    result = 'no-error'\nexcept beartype.roar.BeartypeDoorHintViolation:\n    result = 'door-violation'",
        {"ok": True, "value": "door-violation"},
    ),
    (
        'typehint-is-subhint-same',
        'from beartype.door import TypeHint\nt1 = TypeHint(int)\nt2 = TypeHint(int)\nresult = t1.is_subhint(t2)',
        {"ok": True, "value": True},
    ),
    (
        'typehint-is-subhint-sub',
        'from beartype.door import TypeHint\nt1 = TypeHint(int)\nt2 = TypeHint(object)\nresult = t1.is_subhint(t2)',
        {"ok": True, "value": True},
    ),
    (
        'typehint-is-superhint-same',
        'from beartype.door import TypeHint\nt1 = TypeHint(int)\nt2 = TypeHint(int)\nresult = t1.is_superhint(t2)',
        {"ok": True, "value": True},
    ),
    (
        'typehint-is-superhint-super',
        'from beartype.door import TypeHint\nt1 = TypeHint(object)\nt2 = TypeHint(int)\nresult = t1.is_superhint(t2)',
        {"ok": True, "value": True},
    ),
    (
        'vale-import-is',
        'from typing import Annotated\nfrom beartype.vale import Is\nresult = Is is not None',
        {"ok": True, "value": True},
    ),
    (
        'vale-import-isattr',
        'from typing import Annotated\nfrom beartype.vale import IsAttr\nresult = IsAttr is not None',
        {"ok": True, "value": True},
    ),
    (
        'vale-import-isequal',
        'from typing import Annotated\nfrom beartype.vale import IsEqual\nresult = IsEqual is not None',
        {"ok": True, "value": True},
    ),
    (
        'vale-import-isinstance',
        'from typing import Annotated\nfrom beartype.vale import IsInstance\nresult = IsInstance is not None',
        {"ok": True, "value": True},
    ),
    (
        'vale-import-issubclass',
        'from typing import Annotated\nfrom beartype.vale import IsSubclass\nresult = IsSubclass is not None',
        {"ok": True, "value": True},
    ),
    (
        'vale-is-positive',
        'from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import Is\nPositive = Annotated[int, Is[lambda x: x > 0]]\n@_be.beartype\ndef square(x: Positive) -> int:\n    return x * x\nresult = square(4)',
        {"ok": True, "value": 16},
    ),
    (
        'vale-is-positive-fail',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import Is\nimport beartype.roar\nPositive = Annotated[int, Is[lambda x: x > 0]]\n@_be.beartype\ndef square(x: Positive) -> int:\n    return x * x\ntry:\n    square(-1)\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintParamViolation:\n    result = 'param-violation'",
        {"ok": True, "value": "param-violation"},
    ),
    (
        'vale-isequal-pass',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import IsEqual\nExpected = Annotated[str, IsEqual['ready']]\n@_be.beartype\ndef check(status: Expected) -> str:\n    return 'OK'\nresult = check('ready')",
        {"ok": True, "value": "OK"},
    ),
    (
        'vale-isequal-fail',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import IsEqual\nimport beartype.roar\nExpected = Annotated[str, IsEqual['ready']]\n@_be.beartype\ndef check(status: Expected) -> str:\n    return 'OK'\ntry:\n    check('waiting')\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintParamViolation:\n    result = 'param-violation'",
        {"ok": True, "value": "param-violation"},
    ),
    (
        'vale-isinstance-pass',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import IsInstance\nDictType = Annotated[object, IsInstance[dict]]\n@_be.beartype\ndef process(d: DictType) -> int:\n    return len(d)\nresult = process({'a': 1, 'b': 2})",
        {"ok": True, "value": 2},
    ),
    (
        'vale-isinstance-fail',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import IsInstance\nimport beartype.roar\nDictType = Annotated[object, IsInstance[dict]]\n@_be.beartype\ndef process(d: DictType) -> int:\n    return len(d)\ntry:\n    process([1, 2])\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintParamViolation:\n    result = 'param-violation'",
        {"ok": True, "value": "param-violation"},
    ),
    (
        'vale-issubclass-pass',
        'from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import IsSubclass\nExcType = Annotated[type, IsSubclass[BaseException]]\n@_be.beartype\ndef handle(exc_cls: ExcType) -> str:\n    return exc_cls.__name__\nresult = handle(ValueError)',
        {"ok": True, "value": "ValueError"},
    ),
    (
        'vale-issubclass-fail',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import IsSubclass\nimport beartype.roar\nExcType = Annotated[type, IsSubclass[BaseException]]\n@_be.beartype\ndef handle(exc_cls: ExcType) -> str:\n    return exc_cls.__name__\ntry:\n    handle(int)\n    result = 'no-error'\nexcept beartype.roar.BeartypeCallHintParamViolation:\n    result = 'param-violation'",
        {"ok": True, "value": "param-violation"},
    ),
    (
        'vale-is-even',
        'from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import Is\nEven = Annotated[int, Is[lambda x: x % 2 == 0]]\n@_be.beartype\ndef half(x: Even) -> int:\n    return x // 2\nresult = half(10)',
        {"ok": True, "value": 5},
    ),
    (
        'vale-is-length',
        "from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import Is\nShortStr = Annotated[str, Is[lambda s: len(s) <= 5]]\n@_be.beartype\ndef label(s: ShortStr) -> str:\n    return s.upper()\nresult = label('hi')",
        {"ok": True, "value": "HI"},
    ),
    (
        'roar-import-exception',
        'from beartype.roar import BeartypeException\nresult = issubclass(BeartypeException, Exception)',
        {"ok": True, "value": True},
    ),
    (
        'roar-import-door-exception',
        'from beartype.roar import BeartypeDoorException\nresult = issubclass(BeartypeDoorException, Exception)',
        {"ok": True, "value": True},
    ),
    (
        'roar-import-door-violation',
        'from beartype.roar import BeartypeDoorHintViolation\nresult = issubclass(BeartypeDoorHintViolation, Exception)',
        {"ok": True, "value": True},
    ),
    (
        'roar-import-call-violation',
        'from beartype.roar import BeartypeCallHintViolation\nresult = issubclass(BeartypeCallHintViolation, Exception)',
        {"ok": True, "value": True},
    ),
    (
        'roar-import-param-violation',
        'from beartype.roar import BeartypeCallHintParamViolation\nresult = issubclass(BeartypeCallHintParamViolation, Exception)',
        {"ok": True, "value": True},
    ),
    (
        'roar-import-return-violation',
        'from beartype.roar import BeartypeCallHintReturnViolation\nresult = issubclass(BeartypeCallHintReturnViolation, Exception)',
        {"ok": True, "value": True},
    ),
    (
        'roar-import-warning',
        'from beartype.roar import BeartypeWarning\nresult = issubclass(BeartypeWarning, Warning)',
        {"ok": True, "value": True},
    ),
    (
        'roar-door-hierarchy',
        'from beartype.roar import BeartypeDoorException, BeartypeDoorHintViolation\nresult = issubclass(BeartypeDoorHintViolation, BeartypeDoorException)',
        {"ok": True, "value": False},
    ),
    (
        'roar-call-hierarchy',
        'from beartype.roar import BeartypeCallHintViolation, BeartypeCallHintParamViolation\nresult = issubclass(BeartypeCallHintParamViolation, BeartypeCallHintViolation)',
        {"ok": True, "value": True},
    ),
    (
        'roar-return-hierarchy',
        'from beartype.roar import BeartypeCallHintViolation, BeartypeCallHintReturnViolation\nresult = issubclass(BeartypeCallHintReturnViolation, BeartypeCallHintViolation)',
        {"ok": True, "value": True},
    ),
    (
        'roar-catch-param',
        "import beartype as _be\nfrom beartype.roar import BeartypeCallHintParamViolation\n@_be.beartype\ndef f(x: int) -> int:\n    return x\ntry:\n    f('string')\n    result = 'no-error'\nexcept BeartypeCallHintParamViolation:\n    result = 'caught'",
        {"ok": True, "value": "caught"},
    ),
    (
        'roar-catch-return',
        "import beartype as _be\nfrom beartype.roar import BeartypeCallHintReturnViolation\n@_be.beartype\ndef f() -> int:\n    return 'string'\ntry:\n    f()\n    result = 'no-error'\nexcept BeartypeCallHintReturnViolation:\n    result = 'caught'",
        {"ok": True, "value": "caught"},
    ),
    (
        'roar-catch-call-base',
        "import beartype as _be\nfrom beartype.roar import BeartypeCallHintViolation\n@_be.beartype\ndef f(x: int) -> int:\n    return x\ntry:\n    f('string')\n    result = 'no-error'\nexcept BeartypeCallHintViolation:\n    result = 'caught'",
        {"ok": True, "value": "caught"},
    ),
    (
        'roar-catch-door-base',
        "from beartype.door import die_if_unbearable\nfrom beartype.roar import BeartypeDoorHintViolation\ntry:\n    die_if_unbearable('string', int)\n    result = 'no-error'\nexcept BeartypeDoorHintViolation:\n    result = 'caught'",
        {"ok": True, "value": "caught"},
    ),
    (
        'typing-import-any',
        'from beartype.typing import Any\nresult = Any is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-optional',
        'from beartype.typing import Optional\nresult = Optional is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-union',
        'from beartype.typing import Union\nresult = Union is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-literal',
        'from beartype.typing import Literal\nresult = Literal is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-annotated',
        'from beartype.typing import Annotated\nresult = Annotated is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-callable',
        'from beartype.typing import Callable\nresult = Callable is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-typevar',
        'from beartype.typing import TypeVar\nresult = callable(TypeVar)',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-generic',
        'from beartype.typing import Generic\nresult = Generic is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-typeddict',
        'from beartype.typing import TypedDict\nresult = TypedDict is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-namedtuple',
        'from beartype.typing import NamedTuple\nresult = NamedTuple is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-cast',
        'from beartype.typing import cast\nresult = callable(cast)',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-get-args',
        'from beartype.typing import get_args\nresult = callable(get_args)',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-get-origin',
        'from beartype.typing import get_origin\nresult = callable(get_origin)',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-get-type-hints',
        'from beartype.typing import get_type_hints\nresult = callable(get_type_hints)',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-final',
        'from beartype.typing import Final\nresult = Final is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-import-classvar',
        'from beartype.typing import ClassVar\nresult = ClassVar is not None',
        {"ok": True, "value": True},
    ),
    (
        'typing-use-optional',
        'import beartype as _be\nfrom beartype.typing import Optional\n@_be.beartype\ndef f(x: Optional[int]) -> int:\n    return x if x else 0\nresult = [f(None), f(5)]',
        {"ok": True, "value": [0, 5]},
    ),
    (
        'typing-use-union',
        "import beartype as _be\nfrom beartype.typing import Union\n@_be.beartype\ndef f(x: Union[int, str]) -> str:\n    return str(x)\nresult = [f(42), f('text')]",
        {"ok": True, "value": ["42", "text"]},
    ),
    (
        'typing-use-literal',
        "import beartype as _be\nfrom beartype.typing import Literal\n@_be.beartype\ndef f(mode: Literal['a', 'b']) -> str:\n    return mode.upper()\nresult = f('a')",
        {"ok": True, "value": "A"},
    ),
    (
        'typing-typevar-create',
        "from beartype.typing import TypeVar\nT = TypeVar('T')\nresult = T.__name__",
        {"ok": True, "value": "T"},
    ),
    (
        'cave-import',
        'import beartype.cave\nresult = beartype.cave is not None',
        {"ok": True, "value": True},
    ),
    (
        'cave-anytype',
        'from beartype.cave import AnyType\nresult = isinstance(AnyType, type)',
        {"ok": True, "value": True},
    ),
    (
        'cave-booltype',
        'from beartype.cave import BoolType\nresult = BoolType == bool',
        {"ok": True, "value": False},
    ),
    (
        'cave-inttype',
        'from beartype.cave import IntType\nresult = IntType == int',
        {"ok": True, "value": False},
    ),
    (
        'cave-strtype',
        'from beartype.cave import StrType\nresult = StrType == str',
        {"ok": True, "value": True},
    ),
    (
        'beartype-nested-list',
        'import beartype as _be\n@_be.beartype\ndef f(x: list[list[int]]) -> int:\n    return sum(sum(row) for row in x)\nresult = f([[1, 2], [3, 4]])',
        {"ok": True, "value": 10},
    ),
    (
        'beartype-nested-dict',
        "import beartype as _be\n@_be.beartype\ndef f(x: dict[str, dict[str, int]]) -> int:\n    return sum(sum(v.values()) for v in x.values())\nresult = f({'a': {'b': 1, 'c': 2}, 'd': {'e': 3}})",
        {"ok": True, "value": 6},
    ),
    (
        'beartype-unicode',
        "import beartype as _be\n@_be.beartype\ndef greet(name: str) -> str:\n    return f'Hello, {name}!'\nresult = greet('世界')",
        {"ok": True, "value": "Hello, 世界!"},
    ),
    (
        'door-unicode',
        "from beartype.door import is_bearable\nresult = is_bearable('Привет', str)",
        {"ok": True, "value": True},
    ),
    (
        'beartype-bool',
        'import beartype as _be\n@_be.beartype\ndef negate(b: bool) -> bool:\n    return not b\nresult = negate(True)',
        {"ok": True, "value": False},
    ),
    (
        'beartype-float',
        'import beartype as _be\n@_be.beartype\ndef double(f: float) -> float:\n    return f * 2.0\nresult = double(3.5)',
        {"ok": True, "value": 7.0},
    ),
    (
        'beartype-none-type',
        'import beartype as _be\n@_be.beartype\ndef identity(x: None) -> None:\n    return x\nresult = identity(None)',
        {"ok": True, "value": None},
    ),
    (
        'beartype-any-hint',
        "import beartype as _be\nfrom typing import Any\n@_be.beartype\ndef pass_through(x: Any) -> Any:\n    return x\nresult = [pass_through(1), pass_through('a'), pass_through([1, 2])]",
        {"ok": True, "value": [1, "a", [1, 2]]},
    ),
    (
        'beartype-set',
        'import beartype as _be\n@_be.beartype\ndef size(s: set[int]) -> int:\n    return len(s)\nresult = size({1, 2, 3})',
        {"ok": True, "value": 3},
    ),
    (
        'beartype-frozenset',
        "import beartype as _be\n@_be.beartype\ndef size(s: frozenset[str]) -> int:\n    return len(s)\nresult = size(frozenset(['a', 'b']))",
        {"ok": True, "value": 2},
    ),
    (
        'beartype-bytes',
        "import beartype as _be\n@_be.beartype\ndef length(b: bytes) -> int:\n    return len(b)\nresult = length(b'hello')",
        {"ok": True, "value": 5},
    ),
    (
        'beartype-multiple-params',
        'import beartype as _be\n@_be.beartype\ndef add(a: int, b: int, c: int) -> int:\n    return a + b + c\nresult = add(1, 2, 3)',
        {"ok": True, "value": 6},
    ),
    (
        'beartype-keyword-args',
        "import beartype as _be\n@_be.beartype\ndef greet(name: str, greeting: str = 'Hello') -> str:\n    return f'{greeting}, {name}!'\nresult = greet('Alice', greeting='Hi')",
        {"ok": True, "value": "Hi, Alice!"},
    ),
    (
        'beartype-varargs',
        'import beartype as _be\n@_be.beartype\ndef sum_all(*args: int) -> int:\n    return sum(args)\nresult = sum_all(1, 2, 3, 4, 5)',
        {"ok": True, "value": 15},
    ),
    (
        'beartype-kwargs',
        "import beartype as _be\n@_be.beartype\ndef build(**kwargs: str) -> dict:\n    return kwargs\nresult = build(a='1', b='2')",
        {"ok": True, "value": {"a": "1", "b": "2"}},
    ),
    (
        'door-complex-nested',
        "from beartype.door import is_bearable\nresult = is_bearable({'users': [{'name': 'Alice', 'age': 30}]}, dict[str, list[dict[str, object]]])",
        {"ok": True, "value": True},
    ),
    (
        'vale-is-range',
        'from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import Is\nPercent = Annotated[int, Is[lambda x: 0 <= x <= 100]]\n@_be.beartype\ndef scale(p: Percent) -> float:\n    return p / 100.0\nresult = scale(50)',
        {"ok": True, "value": 0.5},
    ),
    (
        'conf-multiple-options',
        'from beartype import BeartypeConf, BeartypeStrategy, BeartypeViolationVerbosity\nc = BeartypeConf(strategy=BeartypeStrategy.O0, violation_verbosity=BeartypeViolationVerbosity.MINIMAL, is_debug=True)\nresult = [c.strategy == BeartypeStrategy.O0, c.violation_verbosity == BeartypeViolationVerbosity.MINIMAL, c.is_debug]',
        {"ok": True, "value": [True, True, True]},
    ),
    (
        'beartype-callable-simple',
        'import beartype as _be\nfrom typing import Callable\n@_be.beartype\ndef apply(f: Callable[[int], int], x: int) -> int:\n    return f(x)\nresult = apply(lambda n: n * 2, 5)',
        {"ok": True, "value": 10},
    ),
    (
        'door-callable',
        'from beartype.door import is_bearable\nfrom typing import Callable\nresult = is_bearable(lambda x: x, Callable)',
        {"ok": True, "value": True},
    ),
    (
        'typing-get-args-list',
        'from beartype.typing import get_args\nresult = get_args(list[int])',
        {"ok": True, "value": ["<class 'int'>"]},
    ),
    (
        'typing-get-origin-list',
        'from beartype.typing import get_origin\nresult = get_origin(list[int]) == list',
        {"ok": True, "value": True},
    ),
    (
        'beartype-chain-decorators',
        'import beartype as _be\n@_be.beartype\n@_be.beartype\ndef f(x: int) -> int:\n    return x * 2\nresult = f(3)',
        {"ok": True, "value": 6},
    ),
    (
        'beartype-lambda-wrapped',
        'import beartype as _be\nf = _be.beartype(lambda x: x * 2)\nresult = f(5)',
        {"ok": True, "value": 10},
    ),
    (
        'beartype-staticmethod',
        'import beartype as _be\nclass Math:\n    @staticmethod\n    @_be.beartype\n    def add(a: int, b: int) -> int:\n        return a + b\nresult = Math.add(2, 3)',
        {"ok": True, "value": 5},
    ),
    (
        'beartype-classmethod',
        'import beartype as _be\nclass Counter:\n    count = 0\n    @classmethod\n    @_be.beartype\n    def inc(cls, n: int) -> int:\n        cls.count += n\n        return cls.count\nresult = Counter.inc(5)',
        {"ok": True, "value": 5},
    ),
    (
        'door-none',
        'from beartype.door import is_bearable\nresult = is_bearable(None, type(None))',
        {"ok": True, "value": True},
    ),
    (
        'door-any',
        "from beartype.door import is_bearable\nfrom typing import Any\nresult = [is_bearable(1, Any), is_bearable('a', Any), is_bearable(None, Any)]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        'typehint-str',
        "from beartype.door import TypeHint\nt = TypeHint(str)\nresult = [t.is_bearable('hello'), t.is_bearable(123)]",
        {"ok": True, "value": [True, False]},
    ),
    (
        'typehint-bool',
        'from beartype.door import TypeHint\nt = TypeHint(bool)\nresult = [t.is_bearable(True), t.is_bearable(False), t.is_bearable(1)]',
        {"ok": True, "value": [True, True, False]},
    ),
    (
        'vale-is-nonempty',
        'from typing import Annotated\nimport beartype as _be\nfrom beartype.vale import Is\nNonempty = Annotated[list, Is[lambda x: len(x) > 0]]\n@_be.beartype\ndef first(s: Nonempty) -> object:\n    return s[0]\nresult = first([1, 2, 3])',
        {"ok": True, "value": 1},
    ),
    (
        'beartype-dict-get',
        "import beartype as _be\n@_be.beartype\ndef lookup(d: dict[str, int], key: str) -> int:\n    return d[key]\nresult = lookup({'x': 10, 'y': 20}, 'x')",
        {"ok": True, "value": 10},
    ),
    (
        'beartype-tuple-unpack',
        'import beartype as _be\n@_be.beartype\ndef swap(pair: tuple[int, int]) -> tuple[int, int]:\n    a, b = pair\n    return (b, a)\nresult = swap((1, 2))',
        {"ok": True, "value": [2, 1]},
    ),
    (
        'beartype-property',
        'import beartype as _be\nclass Box:\n    def __init__(self, value: int):\n        self._value = value\n    @property\n    @_be.beartype\n    def value(self) -> int:\n        return self._value\nbox = Box(42)\nresult = box.value',
        {"ok": True, "value": 42},
    ),
    (
        'frozendict-import',
        'from beartype import FrozenDict\nresult = FrozenDict is not None',
        {"ok": True, "value": True},
    ),
    (
        'door-list-str',
        "from beartype.door import is_bearable\nresult = is_bearable(['a', 'b', 'c'], list[str])",
        {"ok": True, "value": True},
    ),
    (
        'door-set-int',
        'from beartype.door import is_bearable\nresult = is_bearable({1, 2, 3}, set[int])',
        {"ok": True, "value": True},
    ),
    (
        'beartype-ellipsis-tuple',
        "import beartype as _be\n@_be.beartype\ndef count(items: tuple[str, ...]) -> int:\n    return len(items)\nresult = count(('a', 'b', 'c', 'd'))",
        {"ok": True, "value": 4},
    ),
    (
        'beartype-mixed-tuple',
        "import beartype as _be\n@_be.beartype\ndef describe(t: tuple[str, int, bool]) -> str:\n    return f'{t[0]}: {t[1]} ({t[2]})'\nresult = describe(('item', 5, True))",
        {"ok": True, "value": "item: 5 (True)"},
    ),
    (
        'door-annotated',
        "from beartype.door import is_bearable\nfrom typing import Annotated\nresult = is_bearable(42, Annotated[int, 'positive'])",
        {"ok": True, "value": True},
    ),
    (
        'typing-newtype',
        "from beartype.typing import NewType\nUserId = NewType('UserId', int)\nresult = UserId(42)",
        {"ok": True, "value": 42},
    ),
    (
        'typing-no-type-check',
        'from beartype.typing import no_type_check\n@no_type_check\ndef f(x):\n    return x\nresult = callable(f)',
        {"ok": True, "value": True},
    ),
]

assert len(CASES) == 182, f"Expected 182 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
