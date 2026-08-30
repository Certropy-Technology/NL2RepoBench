#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/typing_inspection
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["hatchling==1.28.0"]
build-backend = "hatchling.build"

[project]
name = "typing-inspection"
version = "0.4.4"
requires-python = ">=3.10"
dependencies = ["typing-extensions>=4.15.0"]
TOML

cat > /workspace/typing_inspection/__init__.py <<'PY'
PY

cat > /workspace/typing_inspection/introspection.py <<'PY'
__all__ = [
    "AnnotationSource", "ForbiddenQualifier", "InspectedAnnotation", "Qualifier",
    "get_literal_values", "inspect_annotation", "is_union_origin",
]

def is_union_origin(obj, /):
    return False

def get_literal_values(annotation, /, *, type_check=False, unpack_type_aliases="eager"):
    return iter(())

def inspect_annotation(annotation, /, *, annotation_source, unpack_type_aliases="skip"):
    return None
PY

cat > /workspace/typing_inspection/typing_objects.py <<'PY'
__all__ = [
    "DEPRECATED_ALIASES", "DEPRECATED_ALIASES_IDS", "NoneType", "is_annotated", "is_any",
    "is_classvar", "is_concatenate", "is_deprecated", "is_final", "is_forwardref",
    "is_generic", "is_literal", "is_literalstring", "is_namedtuple", "is_never",
    "is_newtype", "is_nodefault", "is_noextraitems", "is_noreturn", "is_notrequired",
    "is_paramspec", "is_paramspecargs", "is_paramspeckwargs", "is_readonly", "is_required",
    "is_self", "is_typealias", "is_typealiastype", "is_typeguard", "is_typeis", "is_typevar",
    "is_typevartuple", "is_union", "is_unpack",
]
NoneType = type(None)
DEPRECATED_ALIASES = {}
DEPRECATED_ALIASES_IDS = {}

def _false(obj, /):
    return False

for _name in __all__:
    if _name.startswith("is_"):
        globals()[_name] = _false
PY

touch /workspace/typing_inspection/py.typed
