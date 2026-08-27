from __future__ import annotations

from collections.abc import Hashable, Mapping, Sequence, Set as AbstractSet
from importlib import metadata
from pathlib import Path
import pickle

import pytest

import pyrsistent
from pyrsistent import (
    CheckedKeyTypeError,
    CheckedPMap,
    CheckedPSet,
    CheckedPVector,
    CheckedValueTypeError,
    InvariantException,
    PBag,
    PClass,
    PDeque,
    PList,
    PMap,
    PRecord,
    PSet,
    PTypeError,
    PVector,
    b,
    discard,
    dq,
    field,
    freeze,
    get_in,
    immutable,
    inc,
    l,
    m,
    mutant,
    ny,
    optional,
    pbag,
    pdeque,
    plist,
    pmap,
    pmap_field,
    pset,
    pset_field,
    pvector,
    pvector_field,
    rex,
    s,
    thaw,
    v,
)


class PointRecord(PRecord):
    x = field(type=int, mandatory=True)
    y = field(type=int, initial=0)


class PositiveRecord(PRecord):
    __invariant__ = lambda self: (self.high >= self.low, "high below low")
    low = field(type=int, invariant=lambda value: (value >= 0, "negative low"))
    high = field(type=int)


class ChildRecord(PRecord):
    value = field(type=int, factory=lambda value: int(value))


class ParentRecord(PRecord):
    child = field(type=ChildRecord)


class CollectionsRecord(PRecord):
    numbers = pvector_field(int)
    names = pset_field(str)
    scores = pmap_field(str, int)


class PersonClass(PClass):
    name = field(type=str, mandatory=True)
    age = field(type=int, initial=0)


class IntVector(CheckedPVector):
    __type__ = int


class StrIntMap(CheckedPMap):
    __key_type__ = str
    __value_type__ = int


class PositiveSet(CheckedPSet):
    __type__ = int
    __invariant__ = lambda value: (value >= 0, "negative")


def test_distribution_metadata_and_version():
    assert metadata.version("pyrsistent") == "0.21.0"
    assert metadata.requires("pyrsistent") in (None, [])


def test_package_surface_is_explicit():
    expected = {
        "pmap", "m", "PMap", "pvector", "v", "PVector", "pset", "s", "PSet",
        "pbag", "b", "PBag", "plist", "l", "PList", "pdeque", "dq", "PDeque",
        "CheckedPMap", "CheckedPVector", "CheckedPSet", "InvariantException",
        "CheckedKeyTypeError", "CheckedValueTypeError", "CheckedType", "optional",
        "PRecord", "field", "pset_field", "pmap_field", "pvector_field", "PClass",
        "PClassMeta", "immutable", "freeze", "thaw", "mutant", "get_in", "inc",
        "discard", "rex", "ny",
    }
    assert set(pyrsistent.__all__) == expected
    assert pyrsistent.PTypeError is PTypeError


def test_pep561_package_data():
    package_root = Path(pyrsistent.__file__).resolve().parent
    assert (package_root / "py.typed").is_file()
    assert (package_root / "__init__.pyi").is_file()
    assert (package_root / "typing.pyi").is_file()


def test_typing_module_surface():
    from pyrsistent import typing

    assert typing.PVector is not None
    assert typing.PMap is not None
    assert typing.PSet is not None
    assert typing.PDeque is not None


@pytest.mark.parametrize(
    ("factory", "arguments", "expected_type", "expected"),
    [
        (v, (1, 2, 3), PVector, [1, 2, 3]),
        (m, (), PMap, {}),
        (s, (1, 2, 2), PSet, {1, 2}),
        (b, (1, 2, 2), PBag, {1: 1, 2: 2}),
        (l, (1, 2, 3), PList, [1, 2, 3]),
        (dq, (1, 2, 3), PDeque, [1, 2, 3]),
    ],
)
def test_variadic_aliases(factory, arguments, expected_type, expected):
    result = factory(*arguments)
    assert isinstance(result, expected_type)
    if isinstance(result, PBag):
        assert {value: result.count(value) for value in set(result)} == expected
    elif isinstance(expected, set):
        assert set(result) == expected
    elif isinstance(expected, dict):
        assert dict(result) == expected
    else:
        assert list(result) == expected


def test_pvector_constructor_sequence_hash_and_repr():
    vector = pvector(x * 2 for x in range(3))
    assert isinstance(vector, Sequence)
    assert isinstance(vector, Hashable)
    assert list(vector) == [0, 2, 4]
    assert repr(vector) == "pvector([0, 2, 4])"
    assert hash(vector) == hash(pvector([0, 2, 4]))


def test_pvector_updates_preserve_original():
    original = v(1, 2, 3)
    updated = original.append(4).set(1, 20).extend([5, 6])
    assert list(original) == [1, 2, 3]
    assert list(updated) == [1, 20, 3, 4, 5, 6]


def test_pvector_slicing_and_negative_index():
    vector = v(0, 1, 2, 3, 4)
    assert vector[-1] == 4
    assert vector[1:4] == v(1, 2, 3)
    assert vector[::-2] == v(4, 2, 0)


def test_pvector_set_append_index_rules():
    vector = v(1, 2)
    assert vector.set(-1, 9) == v(1, 9)
    assert vector.set(2, 3) == v(1, 2, 3)
    with pytest.raises(IndexError):
        vector.set(3, 4)


def test_pvector_delete_single_and_slice():
    vector = v(0, 1, 2, 3, 4)
    assert vector.delete(1) == v(0, 2, 3, 4)
    assert vector.delete(1, 4) == v(0, 4)


def test_pvector_mset_count_index_remove():
    vector = v(1, 2, 1, 3)
    assert vector.mset(0, 9, 3, 8) == v(9, 2, 1, 8)
    assert vector.count(1) == 2
    assert vector.index(3) == 3
    assert vector.remove(1) == v(2, 1, 3)
    with pytest.raises(ValueError):
        vector.remove(99)


def test_pvector_add_and_multiply():
    assert v(1, 2) + v(3) == v(1, 2, 3)
    assert v(1, 2) * 3 == v(1, 2, 1, 2, 1, 2)


def test_pvector_evolver_transaction():
    original = v(1, 2, 3)
    evolver = original.evolver()
    assert evolver.is_dirty() is False
    evolver[1] = 20
    evolver.append(4).extend([5])
    assert evolver.is_dirty() is True
    assert list(original) == [1, 2, 3]
    assert evolver.persistent() == v(1, 20, 3, 4, 5)
    assert evolver.is_dirty() is False


def test_pmap_constructor_mapping_protocol_and_hash():
    mapping = pmap([("a", 1), ("b", 2)])
    assert isinstance(mapping, Mapping)
    assert isinstance(mapping, Hashable)
    assert dict(mapping) == {"a": 1, "b": 2}
    assert hash(mapping) == hash(pmap({"b": 2, "a": 1}))


def test_pmap_updates_preserve_original():
    original = m(a=1, b=2)
    updated = original.set("a", 10).set("c", 3)
    assert dict(original) == {"a": 1, "b": 2}
    assert dict(updated) == {"a": 10, "b": 2, "c": 3}


def test_pmap_remove_and_discard():
    mapping = m(a=1, b=2)
    assert mapping.remove("a") == m(b=2)
    assert mapping.discard("missing") is mapping
    with pytest.raises(KeyError):
        mapping.remove("missing")


def test_pmap_update_precedence_and_add():
    mapping = m(a=1, b=2)
    assert mapping.update({"a": 3}, {"c": 4}) == m(a=3, b=2, c=4)
    assert mapping + m(b=7, d=8) == m(a=1, b=7, d=8)


def test_pmap_update_with():
    mapping = m(a=1, b=2)
    result = mapping.update_with(lambda old, new: old + new, {"a": 4, "c": 10})
    assert result == m(a=5, b=2, c=10)


def test_pmap_views_and_attribute_access():
    mapping = m(alpha=1, beta=2)
    assert set(mapping.keys()) == {"alpha", "beta"}
    assert set(mapping.values()) == {1, 2}
    assert set(mapping.items()) == {("alpha", 1), ("beta", 2)}
    assert mapping.alpha == 1
    with pytest.raises(AttributeError):
        _ = mapping.missing


def test_pmap_evolver_transaction():
    original = m(a=1)
    evolver = original.evolver()
    evolver["a"] = 2
    evolver["b"] = 3
    assert evolver.is_dirty() is True
    assert evolver.persistent() == m(a=2, b=3)
    assert original == m(a=1)


def test_pset_constructor_protocol_and_hash():
    persistent = pset([1, 2, 1])
    assert isinstance(persistent, AbstractSet)
    assert isinstance(persistent, Hashable)
    assert set(persistent) == {1, 2}
    assert hash(persistent) == hash(pset([2, 1]))


def test_pset_updates_preserve_original():
    original = s(1, 2)
    assert original.add(3) == s(1, 2, 3)
    assert original.remove(1) == s(2)
    assert original.discard(9) is original
    assert original == s(1, 2)
    with pytest.raises(KeyError):
        original.remove(9)


def test_pset_standard_operations():
    left = s(1, 2, 3)
    right = s(3, 4)
    assert left | right == s(1, 2, 3, 4)
    assert left & right == s(3)
    assert left - right == s(1, 2)
    assert left ^ right == s(1, 2, 4)
    assert s(1, 2) < left


def test_pset_named_operations():
    left = s(1, 2, 3)
    assert left.union([3, 4]) == s(1, 2, 3, 4)
    assert left.intersection([2, 3, 9]) == s(2, 3)
    assert left.difference([2]) == s(1, 3)
    assert left.symmetric_difference([3, 4]) == s(1, 2, 4)
    assert left.isdisjoint([8, 9]) is True


def test_pset_evolver_transaction():
    original = s(1, 2)
    evolver = original.evolver()
    evolver.add(3)
    evolver.remove(1)
    assert evolver.persistent() == s(2, 3)
    assert original == s(1, 2)


def test_pbag_count_and_updates():
    bag = pbag([1, 1, 2])
    assert len(bag) == 3
    assert bag.count(1) == 2
    assert bag.count(9) == 0
    assert bag.add(2).count(2) == 2
    assert bag.update([1, 3]).count(1) == 3


def test_pbag_remove_and_errors():
    bag = b(1, 1, 2)
    assert bag.remove(1) == b(1, 2)
    with pytest.raises(KeyError):
        bag.remove(9)


def test_pbag_multiset_arithmetic():
    left = b(1, 2, 2)
    right = b(2, 3, 3)
    assert left + right == b(1, 2, 2, 2, 3, 3)
    assert (left + right) - b(2, 3, 3, 9) == b(1, 2, 2)
    assert left | right == b(1, 2, 2, 3, 3)
    assert left & right == b(2)


def test_pbag_value_equality_hash_and_comparison_rules():
    assert b(1, 2, 1) == b(2, 1, 1)
    assert hash(b(1, 2, 1)) == hash(b(2, 1, 1))
    with pytest.raises(TypeError):
        _ = b(1) == [1]
    with pytest.raises(TypeError):
        _ = b(1) < b(2)


def test_plist_construction_and_links():
    linked = plist([1, 2, 3])
    assert list(linked) == [1, 2, 3]
    assert linked.first == 1
    assert linked.rest.first == 2
    assert linked.rest.rest == l(3)


def test_plist_cons_mcons_and_original():
    original = l(1, 2)
    assert original.cons(3) == l(3, 1, 2)
    assert original.mcons([3, 4]) == l(4, 3, 1, 2)
    assert original == l(1, 2)


def test_plist_index_slice_and_reverse():
    linked = l(0, 1, 2, 3)
    assert linked[-1] == 3
    assert linked[1:] == l(1, 2, 3)
    assert linked[::2] == l(0, 2)
    assert linked.reverse() == l(3, 2, 1, 0)
    assert reversed(linked) == l(3, 2, 1, 0)


def test_plist_split_remove_and_errors():
    linked = l(1, 2, 3, 2)
    assert linked.split(2) == (l(1, 2), l(3, 2))
    assert linked.remove(2) == l(1, 3, 2)
    with pytest.raises(ValueError):
        linked.remove(9)
    with pytest.raises(IndexError):
        _ = linked[99]


def test_empty_plist_contract():
    empty = plist()
    assert not empty
    assert len(empty) == 0
    assert empty.rest is empty
    with pytest.raises(AttributeError):
        _ = empty.first


def test_pdeque_construction_tips_and_hash():
    queue = pdeque([1, 2, 3])
    assert list(queue) == [1, 2, 3]
    assert queue.left == 1
    assert queue.right == 3
    assert hash(queue) == hash(pdeque([1, 2, 3]))


def test_pdeque_appends_preserve_original():
    original = dq(1, 2)
    assert original.append(3) == dq(1, 2, 3)
    assert original.appendleft(0) == dq(0, 1, 2)
    assert original.extend([3, 4]) == dq(1, 2, 3, 4)
    assert original.extendleft([3, 4]) == dq(4, 3, 1, 2)
    assert original == dq(1, 2)


def test_pdeque_pop_and_popleft_counts():
    queue = dq(1, 2, 3, 4)
    assert queue.pop() == dq(1, 2, 3)
    assert queue.pop(2) == dq(1, 2)
    assert queue.popleft() == dq(2, 3, 4)
    assert queue.popleft(2) == dq(3, 4)
    assert queue.pop(-1) == dq(2, 3, 4)


def test_pdeque_bounded_behavior():
    queue = pdeque([1, 2, 3, 4], maxlen=3)
    assert list(queue) == [2, 3, 4]
    assert queue.maxlen == 3
    assert list(queue.append(5)) == [3, 4, 5]
    assert list(queue.appendleft(1)) == [1, 2, 3]
    with pytest.raises(ValueError):
        pdeque([], maxlen=-1)
    with pytest.raises(TypeError):
        pdeque([], maxlen="3")


def test_pdeque_sequence_remove_reverse_rotate():
    queue = dq(1, 2, 3, 2)
    assert queue[0] == 1
    assert queue[-1] == 2
    assert list(queue[1:3]) == [2, 3]
    assert queue.remove(2) == dq(1, 3, 2)
    assert queue.reverse() == dq(2, 3, 2, 1)
    assert queue.rotate(1) == dq(2, 1, 2, 3)
    assert queue.rotate(-1) == dq(2, 3, 2, 1)


def test_pdeque_empty_tips_and_remove_errors():
    empty = pdeque()
    assert empty.pop() is not None and list(empty.pop()) == []
    with pytest.raises(IndexError):
        _ = empty.left
    with pytest.raises(IndexError):
        _ = empty.right
    with pytest.raises(ValueError):
        dq(1, 2).remove(9)


def test_freeze_and_thaw_nested_builtins():
    source = {"items": [1, {"tags": {"a", "b"}}], "pair": (2, [3])}
    frozen = freeze(source)
    assert isinstance(frozen, PMap)
    assert isinstance(frozen["items"], PVector)
    assert isinstance(frozen["items"][1]["tags"], PSet)
    assert isinstance(frozen["pair"], tuple)
    assert thaw(frozen) == source


def test_freeze_and_thaw_strict_flags():
    nested_vector = v(1, [2, 3])
    assert isinstance(freeze(nested_vector)[1], PVector)
    assert isinstance(freeze(nested_vector, strict=False)[1], list)
    nested_list = [v(1, 2)]
    assert thaw(nested_list) == [[1, 2]]
    assert isinstance(thaw(nested_list, strict=False)[0], PVector)


def test_mutant_freezes_arguments_and_result():
    @mutant
    def operation(values, *, config):
        assert isinstance(values, PVector)
        assert isinstance(config, PMap)
        return [values[0] + 1], {"enabled": config["enabled"]}

    result, config = operation([1], config={"enabled": True})
    assert result == v(2)
    assert config == m(enabled=True)


def test_get_in_defaults_and_errors():
    nested = freeze({"a": [{"b": 3}]})
    assert get_in(["a", 0, "b"], nested) == 3
    assert get_in(["a", 9], nested) is None
    assert get_in(["a", 9], nested, "missing") == "missing"
    with pytest.raises(IndexError):
        get_in(["a", 9], nested, no_default=True)


def test_immutable_set_and_frozen_members():
    Point = immutable("x, y, id_", name="Point")
    point = Point(1, 2, id_=10)
    assert point.set(x=3) == Point(3, 2, id_=10)
    assert point.set() is point
    with pytest.raises(AttributeError):
        point.set(id_=11)
    with pytest.raises(AttributeError):
        point.set(z=4)


def test_transform_nested_path_and_identity():
    original = freeze({"items": [{"score": 1}, {"score": 2}]})
    updated = original.transform(["items", 1, "score"], inc)
    assert thaw(updated) == {"items": [{"score": 1}, {"score": 3}]}
    assert original.transform([lambda key: key == "missing"], inc) is original


def test_transform_matchers_and_discard():
    scores = freeze({"John": 10, "Joseph": 20, "Sara": 30})
    updated = scores.transform([rex("^Jo")], 0)
    assert updated == m(John=0, Joseph=0, Sara=30)
    removed = updated.transform([ny], discard)
    assert removed == pmap()
    assert ny(object()) is True


def test_transform_multiple_commands():
    original = freeze({"a": [1, 2], "b": {"x": 3}})
    result = original.transform(["a", 0], inc, ["b", "x"], 9)
    assert thaw(result) == {"a": [2, 2], "b": {"x": 9}}


def test_precord_fields_defaults_mapping_and_updates():
    record = PointRecord(x=1)
    assert record.x == 1 and record.y == 0
    assert record["x"] == 1
    assert dict(record) == {"x": 1, "y": 0}
    assert record.set(x=2) == PointRecord(x=2)
    assert record == PointRecord(x=1)


def test_precord_type_mandatory_and_unknown_errors():
    with pytest.raises(PTypeError):
        PointRecord(x="bad")
    with pytest.raises(InvariantException) as missing:
        PointRecord()
    assert "PointRecord.x" in missing.value.missing_fields
    with pytest.raises(AttributeError):
        PointRecord(x=1).set(unknown=2)


def test_precord_invariant_details():
    with pytest.raises(InvariantException) as field_error:
        PositiveRecord(low=-1, high=2)
    assert "negative low" in field_error.value.invariant_errors
    with pytest.raises(InvariantException) as global_error:
        PositiveRecord(low=3, high=2)
    assert "high below low" in global_error.value.invariant_errors


def test_precord_factories_create_and_ignore_extra():
    parent = ParentRecord.create({"child": {"value": "7"}})
    assert parent == ParentRecord(child=ChildRecord(value=7))
    assert ParentRecord.create({"child": {"value": 2}, "extra": 9}, ignore_extra=True) == ParentRecord(child=ChildRecord(value=2))
    with pytest.raises(AttributeError):
        ParentRecord.create({"child": {"value": 2}, "extra": 9})


def test_precord_collection_fields_and_serialization():
    record = CollectionsRecord(numbers=[1, 2], names={"a", "b"}, scores={"a": 1})
    assert isinstance(record.numbers, CheckedPVector)
    assert isinstance(record.names, CheckedPSet)
    assert isinstance(record.scores, CheckedPMap)
    assert record.serialize() == {"numbers": [1, 2], "names": {"a", "b"}, "scores": {"a": 1}}


def test_pclass_fields_updates_and_immutability():
    person = PersonClass(name="Ada")
    assert person.name == "Ada" and person.age == 0
    assert person.set(age=37) == PersonClass(name="Ada", age=37)
    assert person.remove("age") == PersonClass(name="Ada")
    with pytest.raises(AttributeError):
        person.name = "Grace"


def test_pclass_create_serialize_and_evolver():
    person = PersonClass.create({"name": "Ada", "age": 36})
    assert person.serialize() == {"name": "Ada", "age": 36}
    evolver = person.evolver()
    evolver.age = 37
    assert evolver.persistent() == PersonClass(name="Ada", age=37)


def test_checked_vector_create_updates_serialize_and_errors():
    vector = IntVector.create([1, 2])
    assert vector.append(3) == IntVector([1, 2, 3])
    assert vector.serialize() == [1, 2]
    with pytest.raises(CheckedValueTypeError):
        vector.append("bad")


def test_checked_map_create_updates_serialize_and_errors():
    mapping = StrIntMap.create({"a": 1})
    assert mapping.set("b", 2) == StrIntMap({"a": 1, "b": 2})
    assert mapping.serialize() == {"a": 1}
    with pytest.raises(CheckedKeyTypeError):
        mapping.set(1, 2)
    with pytest.raises(CheckedValueTypeError):
        mapping.set("b", "bad")


def test_checked_set_create_invariant_and_errors():
    values = PositiveSet.create([1, 2])
    assert values.add(3) == PositiveSet([1, 2, 3])
    assert values.serialize() == {1, 2}
    with pytest.raises(CheckedValueTypeError):
        values.add("bad")
    with pytest.raises(InvariantException):
        values.add(-1)


def test_optional_type_helper():
    allowed = optional(int, str)
    assert allowed == (int, str, type(None))
    assert PointRecord(x=1).set(x=2).x == 2


@pytest.mark.parametrize(
    "value",
    [
        v(1, 2, 3),
        m(a=1, b=2),
        s(1, 2, 3),
        b(1, 1, 2),
        l(1, 2, 3),
        dq(1, 2, 3),
        PointRecord(x=1),
        PersonClass(name="Ada"),
    ],
)
def test_pickle_round_trip(value):
    assert pickle.loads(pickle.dumps(value)) == value
