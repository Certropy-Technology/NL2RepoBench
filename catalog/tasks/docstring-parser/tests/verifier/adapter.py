import argparse
import importlib
import json
import sys


def encode_meta(meta):
    value = {"kind": type(meta).__name__, "args": list(meta.args), "description": meta.description}
    for name in ("arg_name", "type_name", "is_optional", "default", "is_generator", "return_name", "version", "snippet"):
        if hasattr(meta, name):
            value[name] = getattr(meta, name)
    return value


def encode_doc(doc):
    return {
        "short_description": doc.short_description,
        "long_description": doc.long_description,
        "blank_after_short_description": doc.blank_after_short_description,
        "blank_after_long_description": doc.blank_after_long_description,
        "style": doc.style.name if doc.style is not None else None,
        "meta": [encode_meta(item) for item in doc.meta],
    }


def style(name):
    from docstring_parser.common import DocstringStyle
    return getattr(DocstringStyle, name)


def rendering(name):
    from docstring_parser.common import RenderingStyle
    return getattr(RenderingStyle, name)


def decode_doc(value):
    from docstring_parser.common import (
        Docstring, DocstringDeprecated, DocstringExample, DocstringMeta,
        DocstringParam, DocstringRaises, DocstringReturns,
    )
    doc = Docstring(style=style(value["style"]) if value.get("style") else None)
    doc.short_description = value.get("short_description")
    doc.long_description = value.get("long_description")
    doc.blank_after_short_description = bool(value.get("blank_after_short_description"))
    doc.blank_after_long_description = bool(value.get("blank_after_long_description"))
    for item in value.get("meta", []):
        kind = item["kind"]
        args = list(item.get("args", []))
        description = item.get("description")
        if kind == "DocstringParam":
            meta = DocstringParam(args, description, item["arg_name"], item.get("type_name"), item.get("is_optional"), item.get("default"))
        elif kind == "DocstringReturns":
            meta = DocstringReturns(args, description, item.get("type_name"), bool(item.get("is_generator")), item.get("return_name"))
        elif kind == "DocstringRaises":
            meta = DocstringRaises(args, description, item.get("type_name"))
        elif kind == "DocstringDeprecated":
            meta = DocstringDeprecated(args, description, item.get("version"))
        elif kind == "DocstringExample":
            meta = DocstringExample(args, item.get("snippet"), description)
        else:
            meta = DocstringMeta(args, description)
        doc.meta.append(meta)
    return doc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    request = json.loads(args.request)
    operation = request["operation"]
    if operation == "api":
        import docstring_parser as package
        from docstring_parser.common import DocstringStyle, RenderingStyle
        names = ["parse", "parse_from_object", "combine_docstrings", "compose", "ParseError", "Docstring", "DocstringMeta", "DocstringParam", "DocstringRaises", "DocstringReturns", "DocstringDeprecated", "DocstringStyle", "RenderingStyle", "Style"]
        value = {"root_exports": [name for name in names if hasattr(package, name)], "style_members": [item.name for item in DocstringStyle], "rendering_members": [item.name for item in RenderingStyle], "style_alias": package.Style is DocstringStyle}
    else:
        selected = style(request.get("style", "AUTO"))
        if operation == "parse":
            value = encode_doc(importlib.import_module("docstring_parser").parse(request.get("text"), selected))
        elif operation == "dialect_parse":
            module = importlib.import_module("docstring_parser." + request["dialect"])
            value = encode_doc(module.parse(request.get("text")))
        elif operation == "parse_compose":
            module = importlib.import_module("docstring_parser")
            doc = module.parse(request.get("text"), selected)
            value = module.compose(doc, style=selected, rendering_style=rendering(request["rendering"]), indent=request.get("indent", "    "))
        elif operation == "dialect_parse_compose":
            module = importlib.import_module("docstring_parser." + request["dialect"])
            doc = module.parse(request.get("text"))
            value = module.compose(doc, rendering_style=rendering(request["rendering"]), indent=request.get("indent", "    "))
        elif operation == "compose_model":
            module = importlib.import_module("docstring_parser" if request.get("dialect") == "root" else "docstring_parser." + request["dialect"])
            doc = decode_doc(request["doc"])
            if request.get("dialect") == "root":
                value = module.compose(doc, style=selected, rendering_style=rendering(request["rendering"]), indent=request.get("indent", "    "))
            else:
                value = module.compose(doc, rendering_style=rendering(request["rendering"]), indent=request.get("indent", "    "))
        else:
            raise ValueError("unknown operation")
    print(json.dumps({"ok": True, "value": value}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


try:
    main()
except BaseException as exc:
    print(json.dumps({"ok": False, "exception_type": type(exc).__module__ + "." + type(exc).__qualname__, "exception_message": str(exc)}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
