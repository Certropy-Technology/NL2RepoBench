#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, sys
import importlib.util
from pathlib import Path

META_SCHEMAS = {
    "http://json-schema.org/draft-04/schema",
    "http://json-schema.org/draft-04/schema#",
    "http://json-schema.org/draft-06/schema",
    "http://json-schema.org/draft-06/schema#",
    "http://json-schema.org/draft-07/schema",
    "http://json-schema.org/draft-07/schema#",
    "http://json-schema.org/draft-2019-09/schema",
    "http://json-schema.org/draft-2019-09/schema#",
}
REMOTE_ROOT = Path(os.environ.get("FJS_REMOTE_ROOT", "/tests/remotes"))
META_ROOT = Path(os.environ.get("FJS_META_ROOT", "/tests/metaschemas"))
META_FILES = {
    "http://json-schema.org/draft-04/schema": "draft-04.json",
    "http://json-schema.org/draft-04/schema#": "draft-04.json",
    "http://json-schema.org/draft-06/schema": "draft-06.json",
    "http://json-schema.org/draft-06/schema#": "draft-06.json",
    "http://json-schema.org/draft-07/schema": "draft-07.json",
    "http://json-schema.org/draft-07/schema#": "draft-07.json",
}

def formats(names):
    out = {}
    for name, recipe in names.items():
        if recipe == "is_identifier": out[name] = str.isidentifier
        elif recipe == "is_ascii": out[name] = lambda value: isinstance(value, str) and value.isascii()
        else: raise ValueError("unsupported format recipe")
    return out

def run(request, candidate):
    sys.path.insert(0, str(candidate))
    spec = importlib.util.find_spec("fastjsonschema")
    if spec is None or not spec.origin or not Path(spec.origin).resolve().is_relative_to(candidate.resolve()):
        raise ModuleNotFoundError("fastjsonschema is not present in the candidate workspace")
    import fastjsonschema
    operation, schema = request.get("operation"), request.get("schema")
    if operation not in {"validate", "generated"}: raise ValueError("unsupported operation")
    if not isinstance(schema, (dict, bool)): raise TypeError("schema must be an object or boolean")
    schema = json.loads(json.dumps(schema)); draft = request.get("draft")
    if draft and isinstance(schema, dict): schema.setdefault("$schema", draft)
    remotes = request.get("remote_schemas", {})
    def resolve(uri):
        if uri in META_SCHEMAS:
            return json.loads((META_ROOT / META_FILES[uri]).read_text(encoding="utf-8"))
        if uri in remotes:
            return remotes[uri]
        prefix = "http://localhost:1234/"
        base = uri.split("#", 1)[0]
        if not base.startswith(prefix):
            raise ValueError("remote reference is not allowlisted")
        relative = base.removeprefix(prefix)
        path = (REMOTE_ROOT / relative).resolve()
        if not path.is_file() or not path.is_relative_to(REMOTE_ROOT.resolve()):
            raise ValueError("remote reference is not materialized")
        return json.loads(path.read_text(encoding="utf-8"))
    fmt = formats(request.get("formats", {})); handlers = {"http": resolve, "https": resolve}
    if operation == "validate": validator = fastjsonschema.compile(schema, handlers=handlers, formats=fmt)
    else:
        code = fastjsonschema.compile_to_code(schema, handlers=handlers, formats=fmt)
        if not isinstance(code, str) or not code or len(code) > 1000000: raise ValueError("generated code outside bound")
        namespace = {}; exec(compile(code, "<generated>", "exec"), namespace); validator = namespace["validate"]
    try:
        value = validator(request.get("data"), custom_formats=fmt) if operation == "generated" and fmt else validator(request.get("data"))
    except fastjsonschema.JsonSchemaException:
        return {"ok": False}
    json.dumps(value, allow_nan=False)
    return {"ok": True, "value": value}

def main():
    p = argparse.ArgumentParser(); p.add_argument("--candidate", type=Path, required=True); args = p.parse_args()
    for line in sys.stdin:
        try:
            req = json.loads(line, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            if not isinstance(req, dict): raise TypeError("request must be an object")
            response = run(req, args.candidate)
        except Exception as exc:
            response = {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)[:512]}}
        print(json.dumps(response, ensure_ascii=False, allow_nan=False), flush=True)
if __name__ == "__main__": main()
