from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


SCENARIO = r'''
import json

from referencing import Anchor, Registry, Resource, Specification
from referencing import exceptions
from referencing import jsonschema
from referencing.retrieval import to_cached_resource

results = []


def check(identifier, callback):
    try:
        callback()
    except BaseException as error:
        results.append({"id": identifier, "passed": False, "message": f"{type(error).__name__}: {error}"})
    else:
        results.append({"id": identifier, "passed": True})


def raises(expected, callback):
    try:
        callback()
    except expected:
        return
    raise AssertionError(f"expected {expected.__name__}")


D2020 = "https://json-schema.org/draft/2020-12/schema"
D2019 = "https://json-schema.org/draft/2019-09/schema"


check("exports", lambda: (
    __import__("referencing").__all__ == ["Anchor", "Registry", "Resource", "Specification"]
    or (_ for _ in ()).throw(AssertionError("root exports"))
))


def resource_id_and_detection():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:root#", "value": 3})
    assert resource.id() == "urn:root"
    assert resource.contents["value"] == 3


check("resource-detection-and-id", resource_id_and_detection)


def opaque_resource():
    resource = Resource.opaque({"value": 3})
    assert resource.id() is None
    assert list(resource.subresources()) == []
    assert list(resource.anchors()) == []


check("opaque-resource", opaque_resource)


def registry_immutability():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:one"})
    original = Registry()
    extended = original.with_resource("urn:one#", resource)
    assert len(original) == 0
    assert extended.contents("urn:one") == resource.contents
    assert extended["urn:one#"] is resource


check("registry-immutability-and-fragment-normalization", registry_immutability)


def rmatmul_and_no_id():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:one"})
    assert (resource @ Registry()).contents("urn:one") == resource.contents
    raises(exceptions.NoInternalID, lambda: Resource.opaque({}) @ Registry())


check("registry-matmul", rmatmul_and_no_id)


def pointer_escaping():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:pointer", "a/b": {"~": [7]}})
    resolved = Registry().with_resource("urn:pointer", resource).resolver().lookup("urn:pointer#/a~1b/~0/0")
    assert resolved.contents == 7


check("json-pointer-and-escaping", pointer_escaping)


def missing_pointer():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:pointer", "example": []})
    resolver = Registry().with_resource("urn:pointer", resource).resolver()
    raises(exceptions.PointerToNowhere, lambda: resolver.lookup("urn:pointer#/example/0"))


check("missing-pointer", missing_pointer)


def named_anchor():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:anchor", "$anchor": "top", "value": 8})
    resolver = Registry().with_resource("urn:anchor", resource).resolver()
    assert resolver.lookup("urn:anchor#top").contents["value"] == 8


check("named-anchor", named_anchor)


def anchor_errors():
    resource = Resource.from_contents({"$schema": D2020, "$id": "urn:anchor"})
    resolver = Registry().with_resource("urn:anchor", resource).resolver()
    raises(exceptions.NoSuchAnchor, lambda: resolver.lookup("urn:anchor#missing"))
    raises(exceptions.InvalidAnchor, lambda: resolver.lookup("urn:anchor#bad/name"))


check("anchor-errors", anchor_errors)


def nested_subresource():
    root = Resource.from_contents({
        "$schema": D2020,
        "$id": "https://example.test/root",
        "$defs": {"child": {"$id": "child", "answer": 42}},
    })
    registry = Registry().with_resource("https://example.test/root", root).crawl()
    assert registry.contents("https://example.test/child")["answer"] == 42
    assert registry.resolver().lookup("https://example.test/child").contents["answer"] == 42


check("subresource-crawl-and-relative-id", nested_subresource)


def remove_and_combine():
    left = Registry().with_contents([("urn:left", {"$schema": D2020, "$id": "urn:left"})])
    right = Registry().with_contents([("urn:right", {"$schema": D2020, "$id": "urn:right"})])
    combined = left.combine(right)
    assert combined.contents("urn:left")["$id"] == "urn:left"
    assert combined.remove("urn:left").contents("urn:right")["$id"] == "urn:right"
    raises(exceptions.NoSuchResource, lambda: combined.remove("urn:missing"))


check("registry-remove-and-combine", remove_and_combine)


def retrieval_behavior():
    calls = []
    def retrieve(uri):
        calls.append(uri)
        return Resource.from_contents({"$schema": D2020, "$id": uri, "uri": uri})
    first = Registry(retrieve=retrieve).get_or_retrieve("urn:remote")
    second = first.registry.get_or_retrieve("urn:remote")
    assert first.value.contents == second.value.contents
    assert calls == ["urn:remote"]


check("registry-retrieval", retrieval_behavior)


def retrieval_errors():
    registry = Registry(retrieve=lambda uri: (_ for _ in ()).throw(RuntimeError("offline")))
    raises(exceptions.Unretrievable, lambda: registry.get_or_retrieve("urn:remote"))
    raises(exceptions.Unresolvable, lambda: registry.resolver().lookup("urn:remote"))


check("retrieval-errors", retrieval_errors)


def cached_retrieval():
    calls = []
    @to_cached_resource()
    def retrieve(uri):
        calls.append(uri)
        return json.dumps({"$schema": D2020, "$id": uri, "uri": uri})
    assert retrieve("urn:cached").contents["uri"] == "urn:cached"
    assert retrieve("urn:cached").contents["uri"] == "urn:cached"
    assert calls == ["urn:cached"]


check("cached-retrieval-helper", cached_retrieval)


def custom_retrieval_hooks():
    loaded = []
    def loads(value):
        loaded.append(value)
        return {"$schema": D2020, "$id": "urn:custom"}
    wrapped = to_cached_resource(cache=lambda function: function, loads=loads)(lambda uri: "payload")
    assert wrapped("urn:custom").id() == "urn:custom"
    assert loaded == ["payload"]


check("custom-retrieval-hooks", custom_retrieval_hooks)


def dialect_selection():
    spec = jsonschema.specification_with(D2020 + "#")
    assert spec is jsonschema.DRAFT202012
    assert jsonschema.specification_with("urn:unknown", default=Specification.OPAQUE) is Specification.OPAQUE
    raises(jsonschema.UnknownDialect, lambda: jsonschema.specification_with("urn:unknown"))


check("dialect-selection", dialect_selection)


def exception_value_identity():
    one = exceptions.NoSuchResource(ref="urn:missing")
    two = exceptions.NoSuchResource(ref="urn:missing")
    assert one == two and hash(one) == hash(two)
    assert one != exceptions.Unretrievable(ref="urn:missing")


check("exception-value-identity", exception_value_identity)


def dynamic_anchor():
    resource = jsonschema.DRAFT202012.create_resource({"$dynamicAnchor": "top", "value": "dynamic"})
    resolver = Registry().with_resource("urn:dynamic", resource).resolver()
    assert resolver.lookup("urn:dynamic#top").contents["value"] == "dynamic"


check("dynamic-anchor", dynamic_anchor)


def recursive_reference():
    resource = jsonschema.DRAFT201909.create_resource({"$recursiveAnchor": True, "value": "recursive"})
    resolver = Registry().with_resource("urn:recursive", resource).resolver()
    resolved = jsonschema.lookup_recursive_ref(resolver.lookup("urn:recursive").resolver)
    assert resolved.contents["value"] == "recursive"


check("recursive-reference", recursive_reference)


def resolver_subresource_base():
    child = Resource.from_contents({"$schema": D2020, "$id": "child", "value": 5})
    resolver = Registry().with_resource("https://example.test/root/child", child).resolver(
        base_uri="https://example.test/root/"
    ).in_subresource(child)
    assert resolver.lookup("#").contents["value"] == 5
    assert resolver.in_subresource(Resource.opaque({})) is resolver


check("resolver-subresource-base", resolver_subresource_base)


result = results
'''


EXPECTED = [
    "exports",
    "resource-detection-and-id",
    "opaque-resource",
    "registry-immutability-and-fragment-normalization",
    "registry-matmul",
    "json-pointer-and-escaping",
    "missing-pointer",
    "named-anchor",
    "anchor-errors",
    "subresource-crawl-and-relative-id",
    "registry-remove-and-combine",
    "registry-retrieval",
    "retrieval-errors",
    "cached-retrieval-helper",
    "custom-retrieval-hooks",
    "dialect-selection",
    "exception-value-identity",
    "dynamic-anchor",
    "recursive-reference",
    "resolver-subresource-base",
]


def main() -> None:
    observation = execute_script(SCENARIO, timeout_sec=30.0)
    if not observation.ok or not isinstance(observation.value, list):
        leaves = [
            {
                "id": identifier,
                "status": "failed",
                "message": observation.exception_message or observation.exception_type or "candidate scenario failed",
            }
            for identifier in EXPECTED
        ]
    else:
        found = {
            item.get("id"): item
            for item in observation.value
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        leaves = []
        for identifier in EXPECTED:
            item = found.get(identifier)
            passed = isinstance(item, dict) and item.get("passed") is True
            leaves.append(
                {
                    "id": identifier,
                    "status": "passed" if passed else "failed",
                    "message": "" if passed else str(item.get("message", "scenario missing")),
                }
            )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
