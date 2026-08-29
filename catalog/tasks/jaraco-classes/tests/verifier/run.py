from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


CASES: list[tuple[str, str, object]] = [
    (
        "ancestry-mro",
        """
from jaraco.classes.ancestry import all_bases, all_classes
class A: pass
class B(A): pass
result = [[item.__name__ for item in all_bases(B)], [item.__name__ for item in all_classes(B)]]
""",
        [["A", "object"], ["B", "A", "object"]],
    ),
    (
        "ancestry-mro-diamond",
        """
from jaraco.classes.ancestry import all_bases, all_classes
class A: pass
class B: pass
class C(A, B): pass
result = [[item.__name__ for item in all_bases(C)], [item.__name__ for item in all_classes(C)]]
""",
        [["A", "B", "object"], ["C", "A", "B", "object"]],
    ),
    (
        "subclass-order",
        """
from jaraco.classes.ancestry import iter_subclasses
class A: pass
class B(A): pass
class C(A): pass
class D(B): pass
result = [item.__name__ for item in iter_subclasses(A)]
""",
        ["B", "D", "C"],
    ),
    (
        "subclass-diamond",
        """
from jaraco.classes.ancestry import iter_subclasses
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
class E(D): pass
result = [item.__name__ for item in iter_subclasses(A)]
""",
        ["B", "D", "E", "C"],
    ),
    (
        "subclass-empty",
        """
from jaraco.classes.ancestry import iter_subclasses
class A: pass
result = list(iter_subclasses(A))
""",
        [],
    ),
    (
        "nondata-basic",
        """
from jaraco.classes.properties import NonDataProperty
class Sample:
    def __init__(self): self.base = 3
    @NonDataProperty
    def value(self): return self.base
item = Sample()
before = item.value
item.value = 9
result = [before, item.value, Sample.value.fget.__name__, vars(item)]
""",
        [3, 9, "value", {"base": 3, "value": 9}],
    ),
    (
        "nondata-class-access",
        """
from jaraco.classes.properties import NonDataProperty
class Sample:
    @NonDataProperty
    def value(self): return 4
descriptor = Sample.value
result = [type(descriptor).__name__, descriptor.fget.__name__, descriptor.__get__(None, Sample) is descriptor]
""",
        ["NonDataProperty", "value", True],
    ),
    (
        "nondata-assertions",
        """
from jaraco.classes.properties import NonDataProperty
errors = []
for value in (None, 3):
    try:
        NonDataProperty(value)
    except Exception as exc:
        errors.append([type(exc).__name__, str(exc)])
result = errors
""",
        [["AssertionError", "fget cannot be none"], ["AssertionError", "fget must be callable"]],
    ),
    (
        "classproperty-meta",
        """
from jaraco.classes.properties import classproperty
class Config(metaclass=classproperty.Meta):
    value = 2
    @classproperty
    def current(cls): return cls.value
    @current.setter
    def current(cls, value): cls.value = value
item = Config()
values = [Config.current, item.current]
Config.current = 4
values.append(item.current)
item.current = 5
result = values + [Config.value, vars(item)]
""",
        [2, 2, 4, 5, {}],
    ),
    (
        "classproperty-method-kinds",
        """
from jaraco.classes.properties import classproperty
class Sample(metaclass=classproperty.Meta):
    @classproperty
    @classmethod
    def class_name(cls): return cls.__name__
    @classproperty
    @staticmethod
    def constant(): return "constant"
result = [Sample.class_name, Sample().class_name, Sample.constant, Sample().constant]
""",
        ["Sample", "Sample", "constant", "constant"],
    ),
    (
        "classproperty-subclass",
        """
from jaraco.classes.properties import classproperty
class Base(metaclass=classproperty.Meta):
    value = "base"
    @classproperty
    def current(cls): return cls.value
class Child(Base):
    value = "child"
result = [Base.current, Child.current, Child().current]
""",
        ["base", "child", "child"],
    ),
    (
        "classproperty-setter-identity",
        """
from jaraco.classes.properties import classproperty
descriptor = classproperty(lambda cls: 1)
same = descriptor.setter(lambda cls, value: None)
result = [same is descriptor, type(descriptor.fget).__name__, type(descriptor.fset).__name__]
""",
        [True, "classmethod", "classmethod"],
    ),
    (
        "classproperty-read-only",
        """
from jaraco.classes.properties import classproperty
class ReadOnly(metaclass=classproperty.Meta):
    @classproperty
    def value(cls): return 1
errors = []
for target in (ReadOnly, ReadOnly()):
    try:
        target.value = 2
    except Exception as exc:
        errors.append([type(exc).__name__, str(exc)])
result = errors
""",
        [["AttributeError", "can't set attribute"], ["AttributeError", "can't set attribute"]],
    ),
    (
        "classproperty-legacy",
        """
from jaraco.classes.properties import classproperty
class Legacy:
    value = 1
    @classproperty
    def current(cls): return cls.value
    @current.setter
    def current(cls, value): cls.value = value
item = Legacy()
initial = item.current
Legacy.current = 4
item.current = 5
result = [initial, Legacy.current, item.current, vars(item)]
""",
        [1, 4, 5, {"current": 5}],
    ),
    (
        "leaf-registry",
        """
from jaraco.classes.meta import LeafClassesMeta
Root = LeafClassesMeta("Root", (), {})
Child = LeafClassesMeta("Child", (Root,), {})
Grandchild = LeafClassesMeta("Grandchild", (Child,), {})
result = sorted(item.__name__ for item in Root._leaf_classes)
""",
        ["Grandchild"],
    ),
    (
        "leaf-independent",
        """
from jaraco.classes.meta import LeafClassesMeta
First = LeafClassesMeta("First", (), {})
Second = LeafClassesMeta("Second", (), {})
FirstChild = LeafClassesMeta("FirstChild", (First,), {})
result = [sorted(item.__name__ for item in First._leaf_classes), sorted(item.__name__ for item in Second._leaf_classes), First._leaf_classes is Second._leaf_classes]
""",
        [["FirstChild"], ["Second"], False],
    ),
    (
        "tag-registry",
        """
from jaraco.classes.meta import TagRegistered
Base = TagRegistered("Base", (), {"tag": "base"})
Child = TagRegistered("Child", (Base,), {"tag": "child"})
result = [Base._registry is Child._registry, sorted((key, value.__name__) for key, value in Base._registry.items())]
""",
        [True, [["base", "Base"], ["child", "Child"]]],
    ),
    (
        "tag-duplicate",
        """
from jaraco.classes.meta import TagRegistered
First = TagRegistered("First", (), {"tag": "same"})
Second = TagRegistered("Second", (First,), {"tag": "same"})
result = [Second._registry["same"] is Second, sorted((key, value.__name__) for key, value in First._registry.items())]
""",
        [True, [["same", "Second"]]],
    ),
    (
        "tag-independent",
        """
from jaraco.classes.meta import TagRegistered
First = TagRegistered("First", (), {"tag": "one"})
Second = TagRegistered("Second", (), {"tag": "two"})
result = [First._registry is Second._registry, sorted(First._registry), sorted(Second._registry)]
""",
        [False, ["one"], ["two"]],
    ),
    (
        "tag-no-tag",
        """
from jaraco.classes.meta import TagRegistered
Untaged = TagRegistered("Untaged", (), {})
result = sorted(Untaged._registry)
""",
        [],
    ),
    (
        "package-imports",
        """
import jaraco.classes
from jaraco.classes import ancestry, meta, properties
result = [jaraco.classes.__name__, ancestry.__name__, meta.__name__, properties.__name__, sorted(["all_bases", "LeafClassesMeta", "NonDataProperty", "classproperty"])]
""",
        ["jaraco.classes", "jaraco.classes.ancestry", "jaraco.classes.meta", "jaraco.classes.properties", ["LeafClassesMeta", "NonDataProperty", "all_bases", "classproperty"]],
    ),
    (
        "package-marker",
        """
from importlib.resources import files
result = files("jaraco.classes").joinpath("py.typed").is_file()
""",
        True,
    ),
    (
        "package-metadata",
        """
from importlib import metadata
dist = metadata.distribution("jaraco.classes")
requires = sorted((item.split(";", 1)[0].strip().lower().replace("_", "-") for item in (dist.requires or []) if "extra ==" not in item))
result = [dist.metadata["Name"].lower(), metadata.version("jaraco.classes"), requires]
""",
        ["jaraco.classes", "0.1.0", ["more-itertools"]],
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        observed = execute_script(source)
        if observed.ok and observed.value == expected:
            leaves.append({"id": case_id, "status": "passed"})
            continue
        if observed.ok:
            message = f"expected {expected!r}, got {observed.value!r}"
        else:
            message = f"{observed.exception_type}: {observed.exception_message}"
        leaves.append({"id": case_id, "status": "failed", "message": message[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
