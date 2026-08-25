"""Generic JSON probe executed only in the unprivileged candidate process."""

from __future__ import annotations

import json
import sys


def result_view(value):
    if value is None:
        return None
    if hasattr(value, "evaluate_result"):
        value = value.evaluate_result()
    return {"fixed": list(value.fixed), "named": value.named}


def execute(request):
    sys.path.insert(0, "/tmp/candidate-site")
    sys.path.insert(1, "/opt/candidate-dependencies/site")
    import parse

    action = request["action"]
    if action in {"parse", "search"}:
        value = getattr(parse, action)(*request["args"], **request.get("kwargs", {}))
        return result_view(value)
    if action == "findall":
        value = parse.findall(*request["args"], **request.get("kwargs", {}))
        return [result_view(item) for item in value]
    if action == "parser":
        parser = parse.compile(request["format"], case_sensitive=request.get("case_sensitive", False))
        operation = request["operation"]
        if operation == "fields":
            return {
                "format": parser.format,
                "fixed_fields": parser.fixed_fields,
                "named_fields": parser.named_fields,
            }
        value = getattr(parser, operation)(*request["args"], **request.get("kwargs", {}))
        if operation == "findall":
            return [result_view(item) for item in value]
        return result_view(value)
    if action == "result":
        result = parse.Result(tuple(request["fixed"]), request["named"], request.get("spans"))
        operation = request["operation"]
        if operation == "get":
            return result[request["key"]]
        if operation == "slice":
            key = slice(*request["slice"])
            return list(result[key])
        if operation == "contains":
            return request["key"] in result
        if operation == "shape":
            return {"fixed": list(result.fixed), "named": result.named, "spans": result.spans}
    raise ValueError("unsupported probe action")


def main():
    request = json.load(sys.stdin)
    try:
        response = {"ok": True, "value": execute(request)}
    except BaseException as exc:
        response = {
            "ok": False,
            "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "exception_message": str(exc)[:512],
        }
    print(json.dumps(response, ensure_ascii=False, allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
