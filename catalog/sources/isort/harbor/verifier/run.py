"""Private deterministic scenarios for the isort public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/PyCQA/isort,
v5.13.2, immutable revision 131f4adcd5582bfc53928ab0d740eceb8b506b6c). The
candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    # === Basic Import Sorting ===
    (
        "sort-basic-stdlib",
        "import isort\ncode = \"import sys\\nimport os\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "import os\nimport sys\n"},
    ),
    (
        "sort-basic-from-import",
        "import isort\ncode = \"from os import path\\nfrom os import getcwd\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from os import getcwd, path\n"},
    ),
    (
        "sort-mixed-import-types",
        "import isort\ncode = \"from os import path\\nimport sys\\nimport os\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "import os\nimport sys\nfrom os import path\n"},
    ),
    (
        "sort-with-future-import",
        "import isort\ncode = \"import sys\\nfrom __future__ import annotations\\nimport os\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from __future__ import annotations\n\nimport os\nimport sys\n"},
    ),
    (
        "sort-preserves-code",
        "import isort\ncode = \"import sys\\n\\nprint('hello')\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "import sys\n\nprint('hello')\n"},
    ),
    
    # === Check Functions ===
    (
        "check-code-sorted",
        "import isort\ncode = \"import os\\nimport sys\\n\"\nresult = isort.check_code(code)",
        {"ok": True, "value": True},
    ),
    (
        "check-code-unsorted",
        "import isort\ncode = \"import sys\\nimport os\\n\"\nresult = isort.check_code(code)",
        {"ok": True, "value": False},
    ),
    (
        "check-code-no-imports",
        "import isort\ncode = \"print('hello')\\n\"\nresult = isort.check_code(code)",
        {"ok": True, "value": True},
    ),
    (
        "check-code-future-correct",
        "import isort\ncode = \"from __future__ import annotations\\n\\nimport os\\n\"\nresult = isort.check_code(code)",
        {"ok": True, "value": True},
    ),
    (
        "check-code-future-wrong",
        "import isort\ncode = \"import os\\nfrom __future__ import annotations\\n\"\nresult = isort.check_code(code)",
        {"ok": True, "value": False},
    ),
    
    # === Config Class ===
    (
        "config-init-default",
        "from isort import Config\nconfig = Config()\nresult = config.line_length",
        {"ok": True, "value": 79},
    ),
    (
        "config-line-length",
        "from isort import Config\nconfig = Config(line_length=100)\nresult = config.line_length",
        {"ok": True, "value": 100},
    ),
    (
        "config-force-single-line",
        "from isort import Config\nconfig = Config(force_single_line=True)\nresult = config.force_single_line",
        {"ok": True, "value": True},
    ),
    (
        "config-profile-black",
        "from isort import Config\nconfig = Config(profile=\"black\")\nresult = config.profile",
        {"ok": True, "value": "black"},
    ),
    (
        "config-skip-list",
        "from isort import Config\nconfig = Config(skip=[\"migrations\", \"test.py\"])\nresult = len(config.skip) >= 2",
        {"ok": True, "value": True},
    ),
    
    # === Sort with Config ===
    (
        "sort-with-line-length",
        "import isort\nfrom isort import Config\nconfig = Config(line_length=40)\ncode = \"from os import path, getcwd, makedirs, remove\\n\"\nresult = isort.code(code, config=config)",
        {"ok": True, "value": "from os import (\n    getcwd,\n    makedirs,\n    path,\n    remove,\n)\n"},
    ),
    (
        "sort-with-force-single-line",
        "import isort\nfrom isort import Config\nconfig = Config(force_single_line=True)\ncode = \"from os import path, getcwd\\n\"\nresult = isort.code(code, config=config)",
        {"ok": True, "value": "from os import getcwd\nfrom os import path\n"},
    ),
    (
        "sort-with-config-kwargs",
        "import isort\ncode = \"from os import path, getcwd\\n\"\nresult = isort.code(code, force_single_line=True)",
        {"ok": True, "value": "from os import getcwd\nfrom os import path\n"},
    ),
    
    # === ImportKey Enum ===
    (
        "importkey-package",
        "from isort import ImportKey\nresult = ImportKey.PACKAGE.value",
        {"ok": True, "value": 1},
    ),
    (
        "importkey-module",
        "from isort import ImportKey\nresult = ImportKey.MODULE.value",
        {"ok": True, "value": 2},
    ),
    (
        "importkey-attribute",
        "from isort import ImportKey\nresult = ImportKey.ATTRIBUTE.value",
        {"ok": True, "value": 3},
    ),
    (
        "importkey-alias",
        "from isort import ImportKey\nresult = ImportKey.ALIAS.value",
        {"ok": True, "value": 4},
    ),
    (
        "importkey-enum-members",
        "from isort import ImportKey\nmembers = [e.name for e in ImportKey]\nresult = sorted(members)",
        {"ok": True, "value": ["ALIAS", "ATTRIBUTE", "MODULE", "PACKAGE"]},
    ),
    
    # === Place Module ===
    (
        "place-module-stdlib-os",
        "import isort\nresult = isort.place_module(\"os\")",
        {"ok": True, "value": "STDLIB"},
    ),
    (
        "place-module-stdlib-sys",
        "import isort\nresult = isort.place_module(\"sys\")",
        {"ok": True, "value": "STDLIB"},
    ),
    (
        "place-module-stdlib-json",
        "import isort\nresult = isort.place_module(\"json\")",
        {"ok": True, "value": "STDLIB"},
    ),
    (
        "place-module-stdlib-pathlib",
        "import isort\nresult = isort.place_module(\"pathlib\")",
        {"ok": True, "value": "STDLIB"},
    ),
    (
        "place-module-third-party-unknown",
        "import isort\nresult = isort.place_module(\"unknown_package_xyz\")",
        {"ok": True, "value": "THIRDPARTY"},
    ),
    (
        "place-module-with-reason-stdlib",
        "import isort\nsection, reason = isort.place_module_with_reason(\"os\")\nresult = section",
        {"ok": True, "value": "STDLIB"},
    ),
    (
        "place-module-with-reason-returns-tuple",
        "import isort\nres = isort.place_module_with_reason(\"sys\")\nresult = len(res) == 2 and isinstance(res, tuple)",
        {"ok": True, "value": True},
    ),
    (
        "place-module-with-config-known-first-party",
        "import isort\nfrom isort import Config\nconfig = Config(known_first_party=[\"myproject\"])\nresult = isort.place_module(\"myproject\", config=config)",
        {"ok": True, "value": "FIRSTPARTY"},
    ),
    
    # === Find Imports ===
    (
        "find-imports-in-code-basic",
        "import isort\ncode = \"import os\\nimport sys\\n\"\nimports = list(isort.find_imports_in_code(code))\nresult = len(imports) >= 1",
        {"ok": True, "value": True},
    ),
    (
        "find-imports-in-code-empty",
        "import isort\ncode = \"print('hello')\\n\"\nimports = list(isort.find_imports_in_code(code))\nresult = len(imports)",
        {"ok": True, "value": 0},
    ),
    (
        "find-imports-in-code-from-import",
        "import isort\ncode = \"from os import path\\n\"\nimports = list(isort.find_imports_in_code(code))\nresult = len(imports) >= 1",
        {"ok": True, "value": True},
    ),
    (
        "find-imports-returns-iterator",
        "import isort\nfrom collections.abc import Iterator\ncode = \"import os\\n\"\nimports = isort.find_imports_in_code(code)\nresult = isinstance(imports, Iterator)",
        {"ok": True, "value": True},
    ),
    
    # === Package Exports ===
    (
        "export-code-function",
        "import isort\nresult = callable(isort.code)",
        {"ok": True, "value": True},
    ),
    (
        "export-check-code-function",
        "import isort\nresult = callable(isort.check_code)",
        {"ok": True, "value": True},
    ),
    (
        "export-file-function",
        "import isort\nresult = callable(isort.file)",
        {"ok": True, "value": True},
    ),
    (
        "export-check-file-function",
        "import isort\nresult = callable(isort.check_file)",
        {"ok": True, "value": True},
    ),
    (
        "export-stream-function",
        "import isort\nresult = callable(isort.stream)",
        {"ok": True, "value": True},
    ),
    (
        "export-check-stream-function",
        "import isort\nresult = callable(isort.check_stream)",
        {"ok": True, "value": True},
    ),
    (
        "export-config-class",
        "import isort\nfrom isort import Config\nresult = isinstance(Config(), Config)",
        {"ok": True, "value": True},
    ),
    (
        "export-importkey-enum",
        "import isort\nfrom isort import ImportKey\nfrom enum import Enum\nresult = issubclass(ImportKey, Enum)",
        {"ok": True, "value": True},
    ),
    (
        "export-find-imports-in-code",
        "import isort\nresult = callable(isort.find_imports_in_code)",
        {"ok": True, "value": True},
    ),
    (
        "export-find-imports-in-file",
        "import isort\nresult = callable(isort.find_imports_in_file)",
        {"ok": True, "value": True},
    ),
    (
        "export-find-imports-in-paths",
        "import isort\nresult = callable(isort.find_imports_in_paths)",
        {"ok": True, "value": True},
    ),
    (
        "export-find-imports-in-stream",
        "import isort\nresult = callable(isort.find_imports_in_stream)",
        {"ok": True, "value": True},
    ),
    (
        "export-place-module",
        "import isort\nresult = callable(isort.place_module)",
        {"ok": True, "value": True},
    ),
    (
        "export-place-module-with-reason",
        "import isort\nresult = callable(isort.place_module_with_reason)",
        {"ok": True, "value": True},
    ),
    (
        "export-settings-module",
        "import isort\nresult = hasattr(isort, 'settings')",
        {"ok": True, "value": True},
    ),
    (
        "export-version",
        "import isort\nresult = hasattr(isort, '__version__') and isinstance(isort.__version__, str)",
        {"ok": True, "value": True},
    ),
    
    # === Stream Operations ===
    (
        "stream-basic-sort",
        "import isort\nfrom io import StringIO\ninput_s = StringIO(\"import sys\\nimport os\\n\")\noutput_s = StringIO()\nisort.stream(input_s, output_s)\noutput_s.seek(0)\nresult = output_s.read()",
        {"ok": True, "value": "import os\nimport sys\n"},
    ),
    (
        "stream-returns-bool",
        "import isort\nfrom io import StringIO\ninput_s = StringIO(\"import sys\\nimport os\\n\")\noutput_s = StringIO()\nchanged = isort.stream(input_s, output_s)\nresult = isinstance(changed, bool)",
        {"ok": True, "value": True},
    ),
    (
        "stream-returns-true-when-changed",
        "import isort\nfrom io import StringIO\ninput_s = StringIO(\"import sys\\nimport os\\n\")\noutput_s = StringIO()\nresult = isort.stream(input_s, output_s)",
        {"ok": True, "value": True},
    ),
    (
        "stream-returns-false-when-sorted",
        "import isort\nfrom io import StringIO\ninput_s = StringIO(\"import os\\nimport sys\\n\")\noutput_s = StringIO()\nresult = isort.stream(input_s, output_s)",
        {"ok": True, "value": False},
    ),
    (
        "check-stream-sorted",
        "import isort\nfrom io import StringIO\nstream = StringIO(\"import os\\nimport sys\\n\")\nresult = isort.check_stream(stream)",
        {"ok": True, "value": True},
    ),
    (
        "check-stream-unsorted",
        "import isort\nfrom io import StringIO\nstream = StringIO(\"import sys\\nimport os\\n\")\nresult = isort.check_stream(stream)",
        {"ok": True, "value": False},
    ),
    
    # === Multi-line Imports ===
    (
        "sort-multiline-imports",
        "import isort\ncode = \"from os import (\\n    path,\\n    getcwd\\n)\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from os import getcwd, path\n"},
    ),
    (
        "sort-long-import-wraps",
        "import isort\nfrom isort import Config\nconfig = Config(line_length=30)\ncode = \"from os import path, getcwd, makedirs\\n\"\nsorted_code = isort.code(code, config=config)\nresult = \"(\" in sorted_code and \")\" in sorted_code",
        {"ok": True, "value": True},
    ),
    
    # === Section Separation ===
    (
        "sort-sections-stdlib-thirdparty",
        "import isort\ncode = \"import unknown_pkg\\nimport os\\n\"\nsorted_code = isort.code(code)\nresult = sorted_code.index(\"os\") < sorted_code.index(\"unknown_pkg\")",
        {"ok": True, "value": True},
    ),
    (
        "sort-sections-blank-line",
        "import isort\ncode = \"import unknown_pkg\\nimport os\\n\"\nsorted_code = isort.code(code)\nresult = \"\\n\\n\" in sorted_code",
        {"ok": True, "value": True},
    ),
    (
        "sort-future-first",
        "import isort\ncode = \"import os\\nfrom __future__ import annotations\\n\"\nsorted_code = isort.code(code)\nresult = sorted_code.startswith(\"from __future__\")",
        {"ok": True, "value": True},
    ),
    
    # === Edge Cases ===
    (
        "sort-empty-string",
        "import isort\nresult = isort.code(\"\")",
        {"ok": True, "value": ""},
    ),
    (
        "sort-only-code-no-imports",
        "import isort\ncode = \"x = 1\\ny = 2\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "x = 1\ny = 2\n"},
    ),
    (
        "sort-comment-preservation",
        "import isort\ncode = \"# Comment\\nimport os\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "# Comment\nimport os\n"},
    ),
    (
        "sort-whitespace-preservation",
        "import isort\ncode = \"import os\\n\\n\\nprint('hello')\\n\"\nsorted_code = isort.code(code)\nresult = \"print\" in sorted_code",
        {"ok": True, "value": True},
    ),
    (
        "check-code-empty",
        "import isort\nresult = isort.check_code(\"\")",
        {"ok": True, "value": True},
    ),
    
    # === Type Annotations ===
    (
        "sort-typing-imports",
        "import isort\ncode = \"from typing import Dict\\nfrom typing import List\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from typing import Dict, List\n"},
    ),
    (
        "sort-typing-extensions",
        "import isort\ncode = \"from typing_extensions import Literal\\nimport os\\n\"\nsorted_code = isort.code(code)\nresult = sorted_code.index(\"os\") < sorted_code.index(\"typing_extensions\")",
        {"ok": True, "value": True},
    ),
    
    # === Multiple Imports from Same Module ===
    (
        "sort-combine-from-imports",
        "import isort\ncode = \"from os import path\\nfrom os import getcwd\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from os import getcwd, path\n"},
    ),
    (
        "sort-multiple-from-same-module",
        "import isort\ncode = \"from os import getcwd\\nfrom os import path\\nfrom os import makedirs\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from os import getcwd, makedirs, path\n"},
    ),
    
    # === Alphabetical Sorting ===
    (
        "sort-alphabetical-modules",
        "import isort\ncode = \"import zlib\\nimport abc\\nimport os\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "import abc\nimport os\nimport zlib\n"},
    ),
    (
        "sort-alphabetical-imports",
        "import isort\ncode = \"from os import walk, path, getcwd\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from os import getcwd, path, walk\n"},
    ),
    
    # === Config with Known Packages ===
    (
        "config-known-third-party",
        "import isort\nfrom isort import Config\nconfig = Config(known_third_party=[\"mylib\"])\nresult = isort.place_module(\"mylib\", config=config)",
        {"ok": True, "value": "THIRDPARTY"},
    ),
    (
        "config-known-first-party-placement",
        "import isort\nfrom isort import Config\nconfig = Config(known_first_party=[\"myapp\"])\ncode = \"import sys\\nimport myapp\\n\"\nsorted_code = isort.code(code, config=config)\nresult = sorted_code.index(\"sys\") < sorted_code.index(\"myapp\")",
        {"ok": True, "value": True},
    ),
    
    # === Extension Parameter ===
    (
        "sort-with-extension-py",
        "import isort\ncode = \"import sys\\nimport os\\n\"\nresult = isort.code(code, extension=\"py\")",
        {"ok": True, "value": "import os\nimport sys\n"},
    ),
    (
        "sort-with-extension-pyi",
        "import isort\ncode = \"import sys\\nimport os\\n\"\nresult = isort.code(code, extension=\"pyi\")",
        {"ok": True, "value": "import os\nimport sys\n"},
    ),
    
    # === Import with Aliases ===
    (
        "sort-imports-with-aliases",
        "import isort\ncode = \"import sys as system\\nimport os\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "import os\nimport sys as system\n"},
    ),
    (
        "sort-from-imports-with-aliases",
        "import isort\ncode = \"from os import path as p\\nfrom os import getcwd as cwd\\n\"\nresult = isort.code(code)",
        {"ok": True, "value": "from os import getcwd as cwd, path as p\n"},
    ),
    
    # === Relative Imports ===
    (
        "sort-relative-imports",
        "import isort\ncode = \"from . import module\\nimport os\\n\"\nsorted_code = isort.code(code)\nresult = sorted_code.index(\"os\") < sorted_code.index(\".\")",
        {"ok": True, "value": True},
    ),
    (
        "sort-multiple-relative-imports",
        "import isort\ncode = \"from .. import parent\\nfrom . import local\\n\"\nsorted_code = isort.code(code)\nresult = sorted_code.index(\"..\") < sorted_code.index(\". import\")",
        {"ok": True, "value": True},
    ),
    
    # === Integration Tests ===
    (
        "integration-full-file-sort",
        "import isort\ncode = \"\"\"\nimport sys\nfrom typing import List\nimport os\nfrom collections import OrderedDict\n\ndef main():\n    pass\n\"\"\"\nsorted_code = isort.code(code)\nresult = \"import os\" in sorted_code and \"import sys\" in sorted_code",
        {"ok": True, "value": True},
    ),
    (
        "integration-check-then-sort",
        "import isort\ncode = \"import sys\\nimport os\\n\"\nis_sorted = isort.check_code(code)\nif not is_sorted:\n    code = isort.code(code)\nresult = isort.check_code(code)",
        {"ok": True, "value": True},
    ),
    
    # === Config Validation ===
    (
        "config-sections-default",
        "from isort import Config\nconfig = Config()\nresult = \"STDLIB\" in config.sections",
        {"ok": True, "value": True},
    ),
    (
        "config-multi-line-output-default",
        "from isort import Config\nconfig = Config()\nresult = isinstance(config.multi_line_output, int)",
        {"ok": True, "value": True},
    ),
    
    # === Additional Scenario to reach 86 ===
    (
        "config-wrap-length-default",
        "from isort import Config\nconfig = Config()\nresult = config.wrap_length",
        {"ok": True, "value": 0},
    ),
]


assert len(CASES) == 86, f"Expected 86 test cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
