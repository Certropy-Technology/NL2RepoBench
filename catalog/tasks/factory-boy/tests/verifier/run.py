from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: dict[str, object]) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok}
    if observed.ok:
        actual["value"] = observed.value
    else:
        actual["exception_type"] = observed.exception_type
    status = "passed" if actual == expected else "failed"
    result: dict[str, object] = {"status": status}
    if status == "failed":
        result["message"] = json.dumps(
            {"actual": actual, "expected": expected}, sort_keys=True
        )
    return result


CASES: list[tuple[str, str, dict[str, object]]] = [
    (
        "exports-and-version",
        "import factory\nfrom factory import random\nresult = [factory.__version__, factory.Factory.__module__, all(hasattr(factory, n) for n in ['Factory', 'Faker', 'Sequence', 'Trait', 'build']), hasattr(random, 'reseed_random')]",
        {"ok": True, "value": ["3.3.4.dev0", "factory.base", True, True]},
    ),
    (
        "make-factory",
        "import factory\nclass User:\n def __init__(self, name=None, age=None): self.name=name; self.age=age\nF=factory.make_factory(User, name='alice', age=7)\nu=F()\nresult=[type(F).__name__, F.__name__, u.name, u.age]",
        {"ok": True, "value": ["FactoryMetaClass", "UserFactory", "alice", 7]},
    ),
    (
        "helpers-build-batch",
        "import factory\nclass Item:\n def __init__(self, value=None): self.value=value\nitems=factory.build_batch(Item, 3, value='x')\nresult=[[x.value for x in items], type(factory.build(Item, value='y')).__name__]",
        {"ok": True, "value": [["x", "x", "x"], "Item"]},
    ),
    (
        "abstract-factory-errors",
        "import factory\ndef check(fn):\n try: fn()\n except Exception as e: return type(e).__module__+'.'+type(e).__name__\n return None\nclass F(factory.Factory): pass\nresult=[F._meta.abstract, check(F.build), check(F.create)]",
        {"ok": True, "value": [True, "factory.errors.FactoryError", "factory.errors.FactoryError"]},
    ),
    (
        "lazy-declarations",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n a=factory.LazyFunction(lambda: 3)\n b=factory.LazyAttribute(lambda o: o.a*2)\n c=factory.LazyAttributeSequence(lambda o,n: [o.b,n])\nresult=F()",
        {"ok": True, "value": {"a": 3, "b": 6, "c": [6, 0]}},
    ),
    (
        "subfactory-selfattribute",
        "import factory\nclass Child:\n def __init__(self, value=None): self.value=value\nclass Parent:\n def __init__(self, child=None, copied=None): self.child=child; self.copied=copied\nclass CF(factory.Factory):\n class Meta: model=Child\n value=factory.Sequence(lambda n: n+10)\nclass PF(factory.Factory):\n class Meta: model=Parent\n child=factory.SubFactory(CF)\n copied=factory.SelfAttribute('child.value')\nresult=[PF().child.value, PF(child__value=99).copied]",
        {"ok": True, "value": [10, 99]},
    ),
    (
        "iterator-cycle",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n value=factory.Iterator(['a','b'])\nresult=[F()['value'], F()['value'], F()['value']]",
        {"ok": True, "value": ["a", "b", "a"]},
    ),
    (
        "traits-and-maybe",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n name='base'\n value=factory.Maybe('enabled', yes_declaration='yes', no_declaration='no')\n class Params:\n  enabled=False\n  loud=factory.Trait(name='LOUD')\nresult=[F()['name'], F()['value'], F(loud=True)['name'], F(enabled=True)['value']]",
        {"ok": True, "value": ["base", "no", "LOUD", "yes"]},
    ),
    (
        "transformer",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n value=factory.Transformer('abc', transform=str.upper)\nresult=[F()['value'], F(value=factory.Transformer.Force('raw'))['value']]",
        {"ok": True, "value": ["ABC", "raw"]},
    ),
    (
        "dict-and-list-declarations",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n payload=factory.Dict({'a': 1, 'b': factory.Sequence(lambda n: n)})\n items=factory.List([factory.LazyFunction(lambda: 'x'), 2])\nresult=F(payload__a=9, items__1=4)",
        {"ok": True, "value": {"payload": {"a": 9, "b": 0}, "items": ["x", 4]}},
    ),
    (
        "post-generation",
        "import factory\ncalls=[]\ndef hook(obj, create, extracted, **kwargs): calls.append([obj['value'], create, extracted, sorted(kwargs.items())])\nclass F(factory.Factory):\n class Meta: model=dict\n value=1\n done=factory.PostGeneration(hook)\nresult=[F(done='arg', done__flag=2), calls]",
        {"ok": True, "value": [{"value": 1}, [[1, True, "arg", [["flag", 2]]]]]},
    ),
    (
        "post-generation-method",
        "import factory\nclass Box:\n def __init__(self): self.calls=[]\n def add(self, value): self.calls.append(value)\nclass F(factory.Factory):\n class Meta: model=Box\n add=factory.PostGenerationMethodCall('add', 'default')\nresult=F().calls",
        {"ok": True, "value": ["default"]},
    ),
    (
        "helpers-stub",
        "import factory\nclass User:\n def __init__(self, name=None): self.name=name\ns=factory.stub(User, name='stub')\nresult=[s.name, type(s).__name__, hasattr(s, 'name')]",
        {"ok": True, "value": ["stub", "StubObject", True]},
    ),
    (
        "helpers-generate",
        "import factory\nclass Item:\n def __init__(self, value=None): self.value=value\na=factory.generate(Item, factory.BUILD_STRATEGY, value='a')\nb=factory.simple_generate(Item, False, value='b')\nresult=[a.value, b.value]",
        {"ok": True, "value": ["a", "b"]},
    ),
    (
        "fuzzy-integer",
        "from factory import fuzzy, random\nrandom.reseed_random(42)\na=[fuzzy.FuzzyInteger(2, 5, step=1).fuzz() for _ in range(20)]\nresult=[all(2<=x<=5 for x in a), sorted(set(a)), len(a)]",
        {"ok": True, "value": [True, [2, 3, 4, 5], 20]},
    ),
    (
        "fuzzy-text-choice",
        "from factory import fuzzy, random\nrandom.reseed_random(7)\nt=fuzzy.FuzzyText(prefix='pre-', suffix='-end', length=5).fuzz()\nc=fuzzy.FuzzyChoice(['red','blue']).fuzz()\nresult=[t.startswith('pre-'), t.endswith('-end'), len(t), c in ['red','blue']]",
        {"ok": True, "value": [True, True, 13, True]},
    ),
    (
        "fuzzy-decimal-float",
        "from factory import fuzzy, random\nrandom.reseed_random(3)\nd=fuzzy.FuzzyDecimal(1, 2, precision=2).fuzz()\nf=fuzzy.FuzzyFloat(1, 2).fuzz()\nresult=[type(d).__name__, 1<=d<=2, type(f).__name__, 1<=f<=2]",
        {"ok": True, "value": ["Decimal", True, "float", True]},
    ),
    (
        "fuzzy-dates",
        "import datetime\nfrom factory import fuzzy\nd=fuzzy.FuzzyDate(datetime.date(2020,1,1), datetime.date(2020,1,3)).fuzz()\nn=fuzzy.FuzzyNaiveDateTime(datetime.datetime(2020,1,1), datetime.datetime(2020,1,2)).fuzz()\nresult=[type(d).__name__, datetime.date(2020,1,1)<=d<=datetime.date(2020,1,3), n.tzinfo is None]",
        {"ok": True, "value": ["date", True, True]},
    ),
    (
        "random-state",
        "from factory import random\nrandom.reseed_random(11)\nstate=random.get_random_state()\na=random.randgen.randint(1,100)\nrandom.set_random_state(state)\nb=random.randgen.randint(1,100)\nresult=[a,b,a==b]",
        {"ok": True, "value": [58, 58, True]},
    ),
    (
        "faker-declaration",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n word=factory.Faker('pystr', min_chars=4, max_chars=4)\nresult=[isinstance(F()['word'], str), len(F()['word'])==4]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "utils-import-object",
        "from factory import utils\nimport datetime\nresult=[utils.import_object('datetime','date') is datetime.date]\ntry: utils.import_object('datetime','missing')\nexcept Exception as e: result.append(type(e).__module__+'.'+type(e).__name__)",
        {"ok": True, "value": [True, "builtins.AttributeError"]},
    ),
    (
        "debug-context",
        "import io, logging\nfrom factory import helpers\nstream=io.StringIO()\nlogger=logging.getLogger('factory')\nwith helpers.debug(stream=stream): logger.debug('hello')\nresult=[stream.getvalue(), logger.level, len(logger.handlers)]",
        {"ok": True, "value": ["hello\n", 0, 0]},
    ),
    (
        "sequence-reset",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n n=factory.Sequence(lambda n: n)\na=F()['n']; b=F()['n']; F.reset_sequence(0); c=F()['n']\nresult=[a,b,c]",
        {"ok": True, "value": [0, 1, 0]},
    ),
    (
        "nested-overrides",
        "import factory\nclass Child:\n def __init__(self, value=None): self.value=value\nclass Parent:\n def __init__(self, child=None): self.child=child\nclass C(factory.Factory):\n class Meta: model=Child\n value='one'\nclass P(factory.Factory):\n class Meta: model=Parent\n child=factory.SubFactory(C)\nresult=[P().child.value, P(child__value='two').child.value]",
        {"ok": True, "value": ["one", "two"]},
    ),
    (
        "factory-options",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n class Params: enabled=True\nresult=[F._meta.model.__name__, F._meta.abstract, sorted(F._meta.parameters)]",
        {"ok": True, "value": ["dict", False, ["enabled"]]},
    ),
    (
        "factory-create-hook",
        "import factory\nclass Item:\n def __init__(self, value=None): self.value=value\nclass F(factory.Factory):\n class Meta: model=Item\n @classmethod\n def _create(cls, model_class, *args, **kwargs): return ['created', model_class.__name__, kwargs]\nresult=F.create(value=4)",
        {"ok": True, "value": ["created", "Item", {"value": 4}]},
    ),
    (
        "list-factory",
        "import factory\nclass F(factory.ListFactory):\n x=factory.Sequence(lambda n: n)\nresult=[F(), F()]",
        {"ok": True, "value": [[0], [1]]},
    ),
    (
        "container-attribute",
        "import factory\nclass F(factory.Factory):\n class Meta: model=dict\n value=factory.ContainerAttribute(lambda obj, chain: [obj.__class__.__name__, len(chain)], strict=False)\nresult=F()['value']",
        {"ok": True, "value": ["Resolver", 0]},
    ),
    (
        "error-contracts",
        "import factory\ndef kind(fn):\n try: fn()\n except Exception as e: return type(e).__module__+'.'+type(e).__name__\n return 'none'\nclass F(factory.Factory):\n class Meta: model=dict\n it=factory.Iterator([1], cycle=False)\nresult=[kind(lambda: F()), kind(lambda: F())]",
        {"ok": True, "value": ["none", "builtins.StopIteration"]},
    ),
    (
        "deterministic-repeat",
        "import factory\nfrom factory import random\nclass F(factory.Factory):\n class Meta: model=dict\n n=factory.Sequence(lambda n: n)\nrandom.reseed_random(99)\nfirst=[F()['n'] for _ in range(3)]\nF.reset_sequence(0)\nsecond=[F()['n'] for _ in range(3)]\nresult=[first, second]",
        {"ok": True, "value": [[0, 1, 2], [0, 1, 2]]},
    ),
]


def main() -> None:
    leaves = []
    for case_id, source, expected in CASES:
        outcome = _run(source, expected)
        leaf = {"id": case_id, "status": outcome["status"]}
        if outcome["status"] == "failed":
            leaf["message"] = outcome["message"]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
