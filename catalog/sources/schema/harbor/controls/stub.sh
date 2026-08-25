#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/schema
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="schema", version="0.7.8", packages=["schema"])
PY
cat > /workspace/schema/__init__.py <<'PY'
__version__ = "0.7.8"
__all__ = ["Schema", "And", "Or", "Regex", "Optional", "Use", "Forbidden", "Const", "Literal", "SchemaError", "SchemaWrongKeyError", "SchemaMissingKeyError", "SchemaForbiddenKeyError", "SchemaUnexpectedTypeError", "SchemaOnlyOneAllowedError"]
class SchemaError(Exception): pass
SchemaWrongKeyError = SchemaMissingKeyError = SchemaForbiddenKeyError = SchemaUnexpectedTypeError = SchemaOnlyOneAllowedError = SchemaError
class Schema:
    def __init__(self, schema, *args, **kwargs): self.schema = schema
    def validate(self, data, **kwargs): return data
    def is_valid(self, data, **kwargs): return True
    def json_schema(self, schema_id, **kwargs): return {"$id": schema_id}
class And(Schema): args = ()
class Or(And): pass
class Regex(Schema): pattern_str = ""
class Optional(Schema): pass
class Use(Schema): pass
class Forbidden(Schema): pass
class Const(Schema): pass
class Literal(Schema): pass
class Hook(Schema): pass
PY
