# beartype public behavior graph (specified stage)

| behavior | public API | observable contract | hidden-test boundary |
| --- | --- | --- | --- |
| decorator accepts valid calls | `beartype.beartype` | decorated callable remains callable and returns its own result for values satisfying annotations | assert return value and call success, not generated wrapper internals |
| decorator rejects invalid parameters | `beartype.beartype`, `beartype.roar.BeartypeCallHintParamViolation` | wrong argument type raises the documented violation family | assert exception family, not message/frames |
| decorator rejects invalid returns | `beartype.beartype`, `beartype.roar.BeartypeCallHintReturnViolation` | wrong return type raises the documented violation family | assert exception family, not message/frames |
| DOOR predicate | `beartype.door.is_bearable` | returns bool-like truth for object against a supported hint | use supported public hints and stable truth value |
| DOOR assertion | `beartype.door.die_if_unbearable` | returns None when valid and raises a DOOR violation when invalid | assert success/exception class |
| hint wrapper | `beartype.door.TypeHint` | exposes `hint`, `args`, bearability and subhint relations | avoid concrete private subclasses |
| validators | `beartype.vale.Is`, `IsAttr`, `IsEqual`, `IsInstance`, `IsSubclass` | public subscription builds a usable validation hint | assert accepted/rejected values, not factory internals |
| configuration | `beartype.BeartypeConf` and enums | public configuration values are immutable and selectable by decorator | assert documented property values only |
| compatibility typing | `beartype.typing` | public typing names can be imported and used in annotations | assert imports and annotation use, not exact alias implementation |
