# Specification-to-verifier traceability

The private custom verifier freezes 69 unique leaves. The table records public
behavior groups without disclosing hidden expected-value code.

| Public contract section | Leaf ID family | Leaves | Source evidence |
| --- | --- | ---: | --- |
| Distribution/import contract | `packaging.*` | 3 | `pyproject.toml`; module import |
| Callable argument markers | `markers.*` | 16 | six public marker functions |
| `trait` identity | `trait.*` | 2 | `trait` implementation |
| `mypyc_attr` identity decorator | `mypyc-attr.*` | 3 | `mypyc_attr` implementation |
| `FlexibleAlias` subscriptions | `flexible-alias.*` | 3 | alias helper classes |
| Native integer conversion, type, instance checks, docs | `native-int.<name>.*` | 24 | `i64`, `i32`, `i16`, `u8`; upstream `MypycNativeIntTests` |
| TypedDict functional/class forms and metadata | `typeddict.*` | 15 | upstream `TypedDictTests` and factory/metaclass behavior |
| Deprecated dynamic `NoReturn` | `no-return.*` | 3 | upstream `DeprecationTests`; module `__getattr__` |
| **Total** |  | **69** | fixed denominator |

All verifier observations correspond to behavior stated in `instruction.md`.
The instruction's core API promises are represented in at least one leaf. No
leaf requires private helper names, exact source layout, lint formatting, or
README text.

The 12 upstream unittest methods pass on the frozen source under Python 3.12.14.
The 69-leaf adapter decomposes those broad unittest methods and adds coverage
for public marker/decorator/alias APIs that the upstream test file does not
exercise. It does not claim that 69 is the upstream unittest collection count.
