from __future__ import annotations

import json
from typing import Any

from nl2repobench.verification.candidate_client import execute_script

URIS = [
    "http://json-schema.org/draft-03/schema",
    "http://json-schema.org/draft-04/schema",
    "http://json-schema.org/draft-06/schema",
    "http://json-schema.org/draft-07/schema",
    "https://json-schema.org/draft/2019-09/schema",
    "https://json-schema.org/draft/2019-09/meta/applicator",
    "https://json-schema.org/draft/2019-09/meta/content",
    "https://json-schema.org/draft/2019-09/meta/core",
    "https://json-schema.org/draft/2019-09/meta/format",
    "https://json-schema.org/draft/2019-09/meta/meta-data",
    "https://json-schema.org/draft/2019-09/meta/validation",
    "https://json-schema.org/draft/2020-12/schema",
    "https://json-schema.org/draft/2020-12/meta/applicator",
    "https://json-schema.org/draft/2020-12/meta/content",
    "https://json-schema.org/draft/2020-12/meta/core",
    "https://json-schema.org/draft/2020-12/meta/format-annotation",
    "https://json-schema.org/draft/2020-12/meta/format-assertion",
    "https://json-schema.org/draft/2020-12/meta/meta-data",
    "https://json-schema.org/draft/2020-12/meta/unevaluated",
    "https://json-schema.org/draft/2020-12/meta/validation",
]

IDS = {
    **{uri: uri for uri in URIS[4:]},
    **{uri: f"{uri}#" for uri in URIS[:4]},
}


def _resource_script(uri: str) -> str:
    encoded = json.dumps(uri)
    return f'''\
from collections.abc import Mapping
from jsonschema_specifications import REGISTRY

uri = {encoded}
contents = REGISTRY.contents(uri)
result = [isinstance(contents, Mapping), contents.get("$id", contents.get("id"))]
'''


SCENARIOS: list[tuple[str, str, Any]] = [
    (f"resource/{index:02d}", _resource_script(uri), [True, IDS[uri]])
    for index, uri in enumerate(URIS, 1)
]
SCENARIOS.extend(
    [
        (
            "package/all",
            "from jsonschema_specifications import REGISTRY, __all__\nresult = __all__",
            ["REGISTRY"],
        ),
        (
            "package/size",
            "from jsonschema_specifications import REGISTRY\nresult = len(REGISTRY)",
            20,
        ),
        (
            "package/metadata",
            "import importlib.metadata\n"
            "result = importlib.metadata.requires('jsonschema-specifications')",
            ["referencing>=0.31.0"],
        ),
        (
            "package/data",
            "from jsonschema_specifications import REGISTRY\n"
            "result = all(isinstance(REGISTRY.contents(uri), dict) for uri in REGISTRY)",
            True,
        ),
        (
            "package/version-shape",
            "import importlib.metadata\n"
            "result = (importlib.metadata.version('jsonschema-specifications').count('.') >= 1)",
            True,
        ),
        (
            "registry/crawl",
            "from jsonschema_specifications import REGISTRY\n"
            "result = (REGISTRY.crawl() == REGISTRY)",
            True,
        ),
        (
            "registry/draft7",
            "from jsonschema_specifications import REGISTRY\nresult = REGISTRY.contents('http://json-schema.org/draft-07/schema')['title']",
            "Core schema meta-schema",
        ),
        (
            "registry/2020-schema",
            "from jsonschema_specifications import REGISTRY\nresult = REGISTRY.contents('https://json-schema.org/draft/2020-12/schema')['$schema']",
            "https://json-schema.org/draft/2020-12/schema",
        ),
        (
            "registry/legacy-alias",
            "from jsonschema_specifications import REGISTRY\nresult = REGISTRY.contents('http://json-schema.org/draft-07/schema#')['$id']",
            "http://json-schema.org/draft-07/schema#",
        ),
        (
            "registry/unique-keys",
            "from jsonschema_specifications import REGISTRY\n"
            "keys = list(REGISTRY)\n"
            "result = len(keys) == len(set(keys)) and "
            "all(isinstance(key, str) for key in keys)",
            True,
        ),
        (
            "registry/mapping-isolation",
            "from jsonschema_specifications import REGISTRY\n"
            "uri = 'https://json-schema.org/draft/2020-12/schema'\n"
            "first = dict(REGISTRY.contents(uri))\n"
            "second = dict(REGISTRY.contents(uri))\n"
            "result = first == second",
            True,
        ),
        (
            "loading/root-dotfile",
            "from pathlib import Path\n"
            "import jsonschema_specifications\n"
            "from jsonschema_specifications import _core\n"
            "path = (Path(jsonschema_specifications.__file__).parent / "
            "'schemas' / '.DS_Store')\n"
            "path.touch()\n"
            "try:\n    result = len(list(_core._schemas())) == 20\n"
            "finally:\n    path.unlink()",
            True,
        ),
        (
            "loading/vocabulary-dotfile",
            "from pathlib import Path\n"
            "import jsonschema_specifications\n"
            "from jsonschema_specifications import _core\n"
            "path = (Path(jsonschema_specifications.__file__).parent / "
            "'schemas' / 'draft7' / '.DS_Store')\n"
            "path.touch()\n"
            "try:\n    result = len(list(_core._schemas())) == 20\n"
            "finally:\n    path.unlink()",
            True,
        ),
        (
            "loading/resource-types",
            "from collections.abc import Mapping\n"
            "from jsonschema_specifications import REGISTRY\n"
            "result = all(isinstance(REGISTRY.contents(uri), Mapping) "
            "for uri in REGISTRY)",
            True,
        ),
        (
            "loading/schema-key",
            "from jsonschema_specifications import REGISTRY\n"
            "result = (REGISTRY.contents("
            "'https://json-schema.org/draft/2020-12/schema')['$schema'] == "
            "'https://json-schema.org/draft/2020-12/schema')",
            True,
        ),
    ]
)


def _run(source: str) -> tuple[Any, str | None]:
    observed = execute_script(source, timeout_sec=10.0)
    if not observed.ok:
        return None, observed.exception_type
    return observed.value, None


def main() -> int:
    leaves = []
    for leaf_id, source, expected in SCENARIOS:
        actual, exception_type = _run(source)
        passed = exception_type is None and actual == expected
        message = "" if passed else json.dumps(
            {"actual": actual, "exception_type": exception_type, "expected": expected},
            sort_keys=True,
        )[:1000]
        leaves.append(
            {
                "id": f"jsonschema-specifications/{leaf_id}",
                "status": "passed" if passed else "failed",
                "message": message,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
