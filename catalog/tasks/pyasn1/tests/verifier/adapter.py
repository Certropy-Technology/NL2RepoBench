from __future__ import annotations

import argparse
import json
import resource
import sys
from typing import Any

RESULT_PREFIX = "NL2REPO_PYASN1_RESULT="


def _limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))


def _error(action: Any) -> dict[str, Any]:
    try:
        action()
    except BaseException as exc:
        return {"message": str(exc), "type": type(exc).__name__}
    return {"message": None, "type": None}


def exercise(name: str) -> Any:
    import pyasn1
    from pyasn1.codec.ber import decoder as ber_decoder
    from pyasn1.codec.ber import encoder as ber_encoder
    from pyasn1.codec.der import decoder as der_decoder
    from pyasn1.codec.der import encoder as der_encoder
    from pyasn1.codec.native import decoder as native_decoder
    from pyasn1.codec.native import encoder as native_encoder
    from pyasn1.type import char, constraint, namedtype, namedval, tag, univ, useful

    if name == "metadata":
        return {"version": pyasn1.__version__}
    if name == "tag-constants":
        return {
            "application": tag.tagClassApplication,
            "constructed": tag.tagFormatConstructed,
            "context": tag.tagClassContext,
            "private": tag.tagClassPrivate,
            "simple": tag.tagFormatSimple,
            "universal": tag.tagClassUniversal,
        }
    if name == "tag-value":
        value = tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3)
        return {
            "items": list(value),
            "properties": [value.tagClass, value.tagFormat, value.tagId],
            "repr": repr(value),
        }
    if name == "tag-operators":
        left = tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 3)
        right = tag.Tag(tag.tagClassApplication, tag.tagFormatConstructed, 7)
        return {"and": list(left & right), "or": list(left | right), "ordered": left > right}
    if name == "tagset-explicit":
        base = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 2))
        value = base.tagExplicitly(tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 4))
        return {"base": list(value.baseTag), "length": len(value), "super": [list(x) for x in value.superTags]}
    if name == "tagset-implicit":
        base = tag.initTagSet(tag.Tag(tag.tagClassUniversal, tag.tagFormatSimple, 2))
        value = base.tagImplicitly(tag.Tag(tag.tagClassContext, tag.tagFormatSimple, 5))
        return {"base": list(value.baseTag), "super": [list(x) for x in value.superTags]}
    if name == "named-values":
        value = namedval.NamedValues(("off", 0), ("on", 1), "auto")
        return {
            "contains": ["on" in value, 2 in value],
            "items": list(value.items()),
            "keys": list(value.keys()),
            "lookups": [value["on"], value[2], value.getName(99), value.getValue("missing")],
            "values": list(value.values()),
        }
    if name == "named-values-add-clone":
        left = namedval.NamedValues(("zero", 0))
        value = (left + namedval.NamedValues(("one", 1))).clone(("two", 2))
        return {"items": list(value.items()), "original": list(left.items())}
    if name == "range-constraint":
        rule = constraint.ValueRangeConstraint(1, 3)
        return {"bad": _error(lambda: rule(4)), "good": _error(lambda: rule(2))}
    if name == "size-constraint":
        rule = constraint.ValueSizeConstraint(2, 4)
        return {"bad": _error(lambda: rule("x")), "good": _error(lambda: rule("abc"))}
    if name == "single-value-constraint":
        rule = constraint.SingleValueConstraint("red", "green")
        return {"bad": _error(lambda: rule("blue")), "good": rule("red")}
    if name == "constraints-composed":
        union = constraint.ConstraintsUnion(constraint.SingleValueConstraint(1), constraint.SingleValueConstraint(3))
        intersection = constraint.ConstraintsIntersection(constraint.ValueRangeConstraint(1, 5), constraint.SingleValueConstraint(2, 4))
        return {"intersection": [_error(lambda: intersection(2)), _error(lambda: intersection(3))], "union": [_error(lambda: union(1)), _error(lambda: union(2))]}
    if name == "integer-basic":
        value = univ.Integer(7)
        return {"arithmetic": [int(value + 2), int(2 + value), int(value * 3)], "bool": bool(value), "clone": int(value.clone(9)), "int": int(value), "pretty": value.prettyPrint()}
    if name == "integer-named":
        schema = univ.Integer(namedValues=namedval.NamedValues(("off", 0), ("on", 1)))
        return {"from_name": int(schema.clone("on")), "named": schema.clone(1).prettyPrint(), "unknown": schema.clone(3).prettyPrint()}
    if name == "boolean":
        return {"false": [bool(univ.Boolean(False)), int(univ.Boolean(False))], "true": [bool(univ.Boolean(True)), int(univ.Boolean(True))]}
    if name == "octet-string":
        value = univ.OctetString("hé", encoding="utf-8")
        return {"bytes": value.asOctets().hex(), "numbers": list(value.asNumbers()), "pretty": value.prettyPrint()}
    if name == "bit-string":
        value = univ.BitString("'10110'B")
        return {"bits": list(value), "binary": value.asBinary(), "integer": value.asInteger(), "length": len(value)}
    if name == "object-identifier":
        value = univ.ObjectIdentifier("1.3.6.1.4.1")
        return {"items": list(value), "pretty": value.prettyPrint(), "prefix": value.isPrefixOf(univ.ObjectIdentifier("1.3.6.1.4.1.9"))}
    if name == "real":
        value = univ.Real((314, 10, -2))
        return {"float": float(value), "tuple": list(value)}
    if name == "null-any":
        return {"any": univ.Any(b"\x02\x01\x05").asOctets().hex(), "null": univ.Null("").prettyPrint()}
    if name == "character-strings":
        utf = char.UTF8String("hé")
        numeric = char.NumericString("12 34")
        return {"numeric": str(numeric), "octets": utf.asOctets().hex(), "utf": str(utf)}
    if name == "generalized-time":
        value = useful.GeneralizedTime("20240102030405.12Z")
        dt = value.asDateTime
        return {"datetime": dt.isoformat(), "pretty": value.prettyPrint()}
    if name == "sequence":
        schema = univ.Sequence(componentType=namedtype.NamedTypes(namedtype.NamedType("id", univ.Integer()), namedtype.OptionalNamedType("label", char.UTF8String())))
        schema["id"] = 5
        schema["label"] = "x"
        return {"id": int(schema["id"]), "keys": list(schema.keys()), "label": str(schema["label"]), "length": len(schema)}
    if name == "sequence-default":
        schema = univ.Sequence(componentType=namedtype.NamedTypes(namedtype.DefaultedNamedType("enabled", univ.Boolean(True)), namedtype.NamedType("id", univ.Integer())))
        schema["id"] = 8
        return {"enabled": bool(schema["enabled"]), "id": int(schema["id"]), "value_items": [(k, v.prettyPrint()) for k, v in schema.items()]}
    if name == "sequence-of":
        value = univ.SequenceOf(componentType=univ.Integer())
        value.extend([3, 1, 2])
        value[1] = 9
        return {"items": [int(x) for x in value], "length": len(value)}
    if name == "set-of":
        value = univ.SetOf(componentType=univ.Integer())
        value.extend([3, 1, 2])
        return {"der": der_encoder.encode(value).hex(), "items": [int(x) for x in value]}
    if name == "choice":
        value = univ.Choice(componentType=namedtype.NamedTypes(namedtype.NamedType("number", univ.Integer()), namedtype.NamedType("text", char.UTF8String())))
        value["text"] = "hello"
        return {"chosen": value.getName(), "text": str(value.getComponent())}
    if name == "ber-scalars":
        values = [univ.Integer(7), univ.Boolean(True), univ.OctetString(b"hi"), univ.Null("")]
        return {type(value).__name__: ber_encoder.encode(value).hex() for value in values}
    if name == "ber-roundtrip-rest":
        substrate = bytes.fromhex("020105ffff")
        value, rest = ber_decoder.decode(substrate, asn1Spec=univ.Integer())
        return {"rest": rest.hex(), "value": int(value)}
    if name == "der-sequence":
        schema = univ.Sequence(componentType=namedtype.NamedTypes(namedtype.NamedType("id", univ.Integer()), namedtype.OptionalNamedType("label", char.UTF8String())))
        schema["id"] = 5
        schema["label"] = "x"
        encoded = der_encoder.encode(schema)
        decoded, rest = der_decoder.decode(encoded, asn1Spec=schema.clone())
        return {"encoded": encoded.hex(), "id": int(decoded["id"]), "label": str(decoded["label"]), "rest": rest.hex()}
    if name == "native-codec":
        schema = univ.Sequence(componentType=namedtype.NamedTypes(namedtype.NamedType("id", univ.Integer()), namedtype.NamedType("data", univ.OctetString())))
        native = {"id": 4, "data": b"ok"}
        decoded = native_decoder.decode(native, asn1Spec=schema)
        encoded = native_encoder.encode(decoded)
        return {"data": encoded["data"].hex(), "id": encoded["id"]}
    if name == "clone-subtype":
        value = univ.Integer(3).subtype(subtypeSpec=constraint.ValueRangeConstraint(0, 10))
        return {"bad": _error(lambda: value.clone(11)), "clone": int(value.clone(8)), "same_type": value.isSameTypeWith(value.clone())}
    if name == "named-types":
        types = namedtype.NamedTypes(namedtype.NamedType("id", univ.Integer()), namedtype.OptionalNamedType("name", char.UTF8String()))
        return {"names": sorted(types.keys()), "positions": [types.getPositionByName("id"), types.getPositionByName("name")], "required": sorted(types.requiredComponents)}
    if name == "decode-errors":
        return {"truncated": _error(lambda: ber_decoder.decode(b"\x02\x02\x01")), "unknown_tag": _error(lambda: ber_decoder.decode(b"\xff\x00"))}
    raise ValueError(f"unknown scenario: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    _limits()
    sys.path[:] = [args.candidate_site] + [p for p in sys.path if p != args.candidate_site]
    try:
        value = exercise(args.scenario)
        result = {"ok": True, "value": value}
    except BaseException as exc:
        result = {"exception_message": str(exc), "exception_type": type(exc).__name__, "ok": False}
    print(RESULT_PREFIX + json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
