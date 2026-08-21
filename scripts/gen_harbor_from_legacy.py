#!/usr/bin/env python3
"""Generate Harbor verifier assets from frozen legacy verifier images.

The legacy images contain the exact test dependencies and hidden tests used by
the original four-file runner. Harbor supplies the candidate at /workspace.
The verifier copies only frozen test paths into a private candidate copy and
prepends candidate source paths through an executable .pth file. No candidate
build backend or network access is required.
"""

from __future__ import annotations

import stat
from pathlib import Path

REPO = Path(__file__).parent.parent
REGISTRY = "ghcr.io/multimodal-art-projection/nl2repobench"
IMAGE_DIGESTS = {
    "aiofiles": "c2c5990b82801b434d40d0be1fb21ae8b914a2336ff2486ebc7ea622924e4e7a",
    "arguably": "93563ba710a490978afdb11275583ac8357492bd41821a28d8b5fb9eccb84751",
    "boltons": "770deb94e716b3a1592900ab389ac628f7b2a41d360e55bdb633bbff4c948e52",
    "cerberus": "b097a72dfc814cc9cd26a418a4a413e2ea6bafafbef6e567413976ed70fba946",
    "decouple": "cb97d0b98c23641262708449c4de30d6294c90b139f7b01379c7e5b38ee553a6",
    "ftfy": "7b81cb54efc741a160aac403bdb672d6a724f0726cd9376d321d26efd4367afb",
    "humanize": "18407d80e95c1a277a5e6fb66c1174b7f2b3699ec10125adc7d6e180f2f6a626",
    "parse": "b62739aff75c836823bf0140ae6db4d329beb74cf79cdb170ed5adb85966ee18",
    "pytz": "c331cc311b7112b55f66e0eaa505f6a6e63fc97a40e963c5a4b21900341477fc",
    "six": "403962b64fa09689196c6d29a82bf7a9525a95dbb4459f12cca4a920a056dc91",
    "jsonlines": "53d4f953222214651e979d00d81b8b10af86adec9a24982be0ce95e5ece2c246",
    "freezegun": "c3525ea5c356aea4bd8e2ebef5f44db9fe9e1fbe40173ae270057d8c7641e3d5",
    "tinydb": "3db19fe6b19b93ed836def4c78e351fc95454018a3978057ffdf99e3bb2ff1cc",
    "tenacity": "d8de6dbe1756b785974c57baf2a033767a6fd0324ff2fd70c861940e6372cd2e",
    "autopep8": "dbecf8fbccb83e9071ba33e16d127c2b0797c6f31372b9cbf40104b8ac9a66fe",
    "bleach": "87cabcf36717c72b75f2b2bedef2fee3f70db75864e09bb6c3a950a4fcc34941",
    "cookiecutter": "fb42f82d4a45d9ac9856dfd81b61daaa620ed081508968ad75315b7f29060cb8",
    "pyjwt": "b9a14097413982736072aef5831c10df3370b0127477bc13d4f55a46161760de",
    "deepdiff": "e643e3d13892f4bd3494eec93faa93799b259e38bdae44f4d3f39794d3c65173",
    "docopt-ng": "d759e56c0c96c73e975f92d24a6464c3a99eb0832f94e4e5a4d092af37671c49",
    "sortedcontainers": "6958cd0d6a2c6cf84e84f3638633a3fc70c9f9392fddfa9f6385a6d6de91517a",
    "python-dotenv": "f604ad8f1f95679d3d78463ca6c23be1a4ca92f6a55769c2f5d60f4031dae0a0",
    "asteval": "7c9fd70a06c18ab0d5d3f806bbef2edd8484e7f6c01375033caecdb03d29468d",
    "more-Itertools": "a63479c4938b00cc4bc2ec636eed5c392325ac98dc11ce2f4212f9213b57dfde",
    "pypinyin": "e6d86e2b150ea5ebe79ed78dff2a13f60f1a73cfe99e827ba100ce4da37d8f3e",
    "typing_extensions": "43d768b2998bf39f873319f2ac1ba13f42490e3c16013f497175fea5a736814c",
    "pathlib2": "82a6649dd844244a64005c198148649222cac6f8792358a506c1f86f7a0948ba",
    "pytest-cov": "23e86c9c10233b812adfd98ec44c5847499c5e12e04e38f50dc90a3115513c18",
    "schema": "39cc925630f3643f539c608e89942a01a8d9c208f2d358fa9d36aee9b49017a3",
    "boto": "6a70abf3ae8807746d708ce0ab1de72e46f7b14e3f91d68c542a112523468c24",
    "dictdatabase": "823bcedc503f2cef1b47abe39c3a582d977376bd4b0343f011637de40dd80c7e",
    "flask-restful": "79d845aef38ea77517f3d4e6f7b38440d06c717d1cce2c1869bedaabe3856237",
    "paillier": "914780b2b3429aa9bb1c441d3c223c380e389c529bcca436121674e37e0beb7a",
    "cachier": "310c22efd29951e65bc94945448158fc8c79db716ae8954cbf0e5f1c3359d9cd",
    "voluptuous": "9d1deaa58ac3e73dc8de4b8d3fdc5c574830637753d71e93ce5b5cdbad0c05fd",
    "tablib": "03b7d18dbf1c726305b417964ad657cfd6d6a0817593cb0cb98c968f66e89f48",
    "deslib": "a770394bb31e568ee05a607a6daf8b5d0b96d89e5ab45eac9fb4f6d48c0716f8",
    "fastapi-users": "7d138cafb8b38642b53ab505c86e143ea257d808474314b41d7725bb9d259420",
    "sqlparse": "fdc248879569aa72db0c14a15cafb5a57436879a530726d313de83b3c6061138",
    "math-verify": "09eeca141f24aa13c6b33dae1c255f086b4916f41cbd8cb99ca0541d7c63ce02",
    "databases": "dd74f0c7837985a4d6a122a9ddc7101f58cfdbc0114dd626a8a38ca841a12891",
    "python-fsutil": "3094bacae5c910e6bdc2d72d76346bbef8d5fbbbc3e1b45594a0a708227e85b6",
    "funcy": "76ebd62df511fa695050585d0d4a8222d742ba1a451349e683857815d0aa5189",
    "python-pathspec": "8e05b4044ed04d3c6a39dd4a468be773baaed5fb06ce8fe6dd861d30198dcb43",
    "markdownify": "65c016ba9b1503f1c33cb01a732dc877fb43ed1a65e700f5cbab721bb06c499b",
    "python-slugify": "a5124fec018d540e2201a687ee16d5748be5ac9c38981cb7a9e746b0dc76a83c",
    "tqdm": "75c3dba71f588b7022445fcefc59ba03163a8161ca5e4ba9dcc556a8f5403fa9",
    "stamina": "21cbd1883da2af9c19dbf9ba0d4fe2a3780cc64279fa4e9bc8ae67d19e4122bf",
    "rich-click": "8f091fb134fce469a442c928a3a8494510e3ff68c7e88b2c1378aff8c813d241",
    "box": "216814b130e1822af7721203bc14c3aa0bcc100a643659db6d29ec07f9b3bd3f",
    "mechanicalsoup": "54a9ee32015e3b67b09459f08ae752b7bd9f7920a78a2ffc5b2ba772ca8d60d6",
    "emoji": "4b7b1ef33001317d8ebc54a7467e2ad1688d7a6d3ac0672911de770098037d0b",
    "pdfplumber-stable": "5f1afa11a502918e9624cdc26b849d7c9351ec5ec0cd171c6118a8465e382f30",
    "structlog": "ad5c6ff2b6ddd2a7f463b9e31dcd8c201e6f17092eb9c28cd77a4c62421d9d1b",
    "stable-baselines3": "f099a531a115b93c5207db35ab49ff792f1c4e4d222a0991a41e19d0dc6b3295",
    "gitingest": "bbd145dbf70464c96b4f085af13911b53e599ab79ca46e5c9c9a25a159a093a2",
    "xlrd": "caa59581e78ccd3f66d20d1edd160ccd6b41e60f85647c112e912fb49cda5b41",
    "fuzzywuzzy": "108be49ca52d07b24d49566a517556f906c6de4e3674f30fb992452efdd7c563",
    "dbutils": "8794762c4581cb6862818baacd9f684a687ad275822b99d0257657b3b199e5f9",
    "unidecode": "941e1824c14fd13d4d67c457badbd2eaf2ed39459ee75582e9f9bf31f340a795",
    "unittest-parametrize": "fcc862e8f8ae0e6c279dc8075d4136f3713bdc72e5686626e284024e5259dacb",
    "markupsafe": "9a385b240fa9430e853999c19e0bfe3a648287dd19f5c41e3d16ff18d3407d76",
    "pyquery": "55b0be41dfafa65c0251ebbb524f2ed6ec2064524113c41e83037782b0705343",
}

TASKS: dict[str, dict[str, object]] = {
    "aiofiles": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 211,
    },
    "arguably": {
        "paths": ["test"],
        "pytest": "--continue-on-collection-errors test",
        "expected": 70,
    },
    "boltons": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 423,
    },
    "cerberus": {
        "paths": [
            "cerberus/tests",
            "cerberus/benchmarks/test_overall_performance_1.py",
            "cerberus/benchmarks/test_overall_performance_2.py",
        ],
        "pytest": (
            "--continue-on-collection-errors cerberus/tests "
            "cerberus/benchmarks/test_overall_performance_1.py "
            "cerberus/benchmarks/test_overall_performance_2.py"
        ),
        # One upstream test is intentionally skipped on this frozen image;
        # the metric denominator excludes skipped cases.
        "expected": 248,
    },
    "decouple": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 67,
    },
    "ftfy": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 336,
        "prepare": [
            "printf '#!/bin/sh\\nexec python -m ftfy.cli \\\"$@\\\"\\n' > /usr/local/bin/ftfy",
            "chmod 755 /usr/local/bin/ftfy",
        ],
    },
    "humanize": {
        "paths": [
            "tests/test_filesize.py",
            "tests/test_i18n.py",
            "tests/test_lists.py",
            "tests/test_number.py",
            "tests/test_time.py",
        ],
        "pytest": (
            "--continue-on-collection-errors tests/test_filesize.py "
            "tests/test_i18n.py tests/test_lists.py tests/test_number.py "
            "tests/test_time.py"
        ),
        "expected": 607,
        "prepare": [
            "mkdir -p /tmp/candidate/src/humanize",
            "test -f /tmp/candidate/src/humanize/_version.py || "
            "echo '__version__ = \"0.0.0\"' > "
            "/tmp/candidate/src/humanize/_version.py",
        ],
    },
    "parse": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 96,
    },
    "pytz": {
        "paths": ["test_docs.py", "test_lazy.py", "test_tzinfo.py"],
        "pytest": ("--continue-on-collection-errors test_docs.py test_lazy.py test_tzinfo.py"),
        "expected": 235,
        "blocked": (
            "The frozen image stores pytz as an egg and the source build requires "
            "generated zoneinfo data; needs a dedicated offline source-freeze stage."
        ),
    },
    "six": {
        "paths": ["test_six.py"],
        "pytest": "--continue-on-collection-errors test_six.py",
        "expected": 200,
    },
    "jsonlines": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 27,
    },
    "freezegun": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 133,
    },
    "tinydb": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 204,
    },
    "tenacity": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 124,
    },
    "autopep8": {
        "paths": ["test"],
        "pytest": "--continue-on-collection-errors test",
        "expected": 564,
    },
    "bleach": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 448,
    },
    "cookiecutter": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 377,  # 381 collected - 4 skipped (Windows-only tests)
    },
    "pyjwt": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 299,
    },
    "deepdiff": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 970,
    },
    "docopt-ng": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 614,
    },
    "sortedcontainers": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 299,
    },
    "python-dotenv": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 209,
    },
    "asteval": {
        "paths": ["tests"],
        "pytest": "-o addopts='' --continue-on-collection-errors tests",
        "expected": 227,
        "prepare": [
            "mkdir -p /tmp/candidate/asteval",
            "test -f /tmp/candidate/asteval/version.py || "
            "echo \"version = '0.0.1'\" > /tmp/candidate/asteval/version.py",
        ],
    },
    "more-Itertools": {
        "image": "more-itertools",
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 682,
    },
    "pypinyin": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 964,
    },
    "typing_extensions": {
        "paths": ["src/test_typing_extensions.py"],
        "pytest": "--continue-on-collection-errors src",
        "expected": 535,
    },
    "pathlib2": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 344,
        "docker_prepare": ["python -m pip install --no-cache-dir six"],
    },
    "pytest-cov": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 184,
    },
    "schema": {
        "paths": ["test_schema.py"],
        "pytest": "--continue-on-collection-errors test_schema.py",
        "expected": 118,
    },
    "boto": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 1009,
        "docker_prepare": [
            "python -m pip install --no-cache-dir "
            "pytest 'botocore>=1.40.52,<1.41.0' 'jmespath>=0.7.1,<2.0.0' "
            "'s3transfer>=0.14.0,<0.15.0'",
        ],
    },
    "dictdatabase": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 594,
    },
    "flask-restful": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 362,
        "docker_prepare": [
            "python -m pip install --no-cache-dir pytest "
            "'Flask==1.1.4' 'Werkzeug==1.0.1' 'Jinja2==2.11.3' "
            "'MarkupSafe==2.0.1' 'itsdangerous==1.1.0' 'click==7.1.2' "
            "aniso8601 six pytz mock blinker",
        ],
    },
    "paillier": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 234,
    },
    "cachier": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 180,
    },
    "voluptuous": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 152,
    },
    "tablib": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 172,
    },
    "deslib": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 532,
    },
    "fastapi-users": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 556,
    },
    "sqlparse": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 462,
    },
    "math-verify": {
        "paths": ["tests"],
        "pytest": "-n 0 --continue-on-collection-errors tests/test_all.py -v -s",
        "expected": 192,
    },
    "databases": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 154,
    },
    "python-fsutil": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 153,
    },
    "funcy": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 203,
    },
    "python-pathspec": {
        "paths": [
            "tests/test_01_util.py",
            "tests/test_02_gitwildmatch.py",
            "tests/test_03_pathspec.py",
            "tests/test_04_gitignore.py",
        ],
        "pytest": (
            "--continue-on-collection-errors tests/test_01_util.py "
            "tests/test_02_gitwildmatch.py tests/test_03_pathspec.py "
            "tests/test_04_gitignore.py"
        ),
        "expected": 119,
    },
    "markdownify": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 83,
        "docker_prepare": [
            "python -m pip install --no-cache-dir beautifulsoup4 six",
        ],
    },
    "python-slugify": {
        "paths": ["test.py"],
        "pytest": "--continue-on-collection-errors test.py",
        "expected": 82,
    },
    "tqdm": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 141,
        "prepare": [
            "mkdir -p /tmp/candidate/tqdm",
            "echo \"__version__ = '0.0.1'\" > /tmp/candidate/tqdm/version.py",
        ],
    },
    "stamina": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 129,
    },
    "rich-click": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 139,
        "docker_prepare": [
            "python -m pip install --no-cache-dir 'setuptools>=45' click rich",
        ],
    },
    "box": {
        "paths": ["test"],
        "pytest": "--continue-on-collection-errors test",
        "expected": 147,
    },
    "mechanicalsoup": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 127,
    },
    "emoji": {
        "paths": ["tests", "utils/testutils.py"],
        "pytest": "--continue-on-collection-errors tests utils/testutils.py",
        "expected": 102,
    },
    "pdfplumber-stable": {
        "image": "pdfplumber-stable",
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 171,
    },
    "structlog": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 828,
        "docker_prepare": ["python -m pip install --no-cache-dir colorama"],
    },
    "stable-baselines3": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 798,
    },
    "gitingest": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 133,
        "docker_prepare": [
            "python -m pip install --no-cache-dir gitpython loguru strenum eval-type-backport",
        ],
    },
    "xlrd": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 84,
    },
    "fuzzywuzzy": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 71,
    },
    "dbutils": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 140,
    },
    "unidecode": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 65,
    },
    "unittest-parametrize": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 26,
    },
    "markupsafe": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 39,
    },
    "pyquery": {
        "paths": ["tests"],
        "pytest": "--continue-on-collection-errors tests",
        "expected": 74,
        "docker_prepare": ["python -m pip install --no-cache-dir cssselect"],
    },
}

GRADE_PY = r"""from __future__ import annotations
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--junit", type=Path)
    parser.add_argument("--pytest-exit-code", type=int)
    parser.add_argument("--reason")
    args = parser.parse_args()

    counts = {"collected": 0, "failed": 0, "errors": 0, "skipped": 0, "passed": 0}
    reason = args.reason
    valid = reason is None
    if args.junit is not None and args.junit.is_file():
        cases = list(ET.parse(args.junit).getroot().iter("testcase"))
        counts["collected"] = len(cases)
        counts["failed"] = sum(c.find("failure") is not None for c in cases)
        counts["errors"] = sum(c.find("error") is not None for c in cases)
        counts["skipped"] = sum(c.find("skipped") is not None for c in cases)
        counts["passed"] = (
            counts["collected"] - counts["failed"] - counts["errors"] - counts["skipped"]
        )
    elif reason is None:
        reason = "junit-missing"
        valid = False

    effective_total = counts["collected"] - counts["skipped"]
    if reason is None and effective_total != args.expected:
        reason = "collection-mismatch"
        valid = False
    if reason is None and args.pytest_exit_code not in {0, 1}:
        reason = "pytest-abnormal-exit"
        valid = False
    score = counts["passed"] / args.expected if valid and args.expected > 0 else 0.0
    score = max(0.0, min(score, 1.0))

    verifier_dir = Path("/logs/verifier")
    verifier_dir.mkdir(parents=True, exist_ok=True)
    (verifier_dir / "reward.json").write_text(
        json.dumps({"reward": score, "test_pass_rate": score}, indent=2) + "\n"
    )
    (verifier_dir / "grading.json").write_text(
        json.dumps(
            {
                **counts,
                "effective_total": effective_total,
                "expected": args.expected,
                "pytest_exit_code": args.pytest_exit_code,
                "reason": reason,
                "reward": score,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
    )


if __name__ == "__main__":
    main()
"""


def dockerfile(task: str, config: dict[str, object]) -> str:
    image = str(config.get("image", task))
    save_paths = "\n".join(
        f"RUN mkdir -p /tests/fixture/$(dirname {path}) "
        f"&& cp -a /workspace/{path} /tests/fixture/{path}"
        for path in config["paths"]
    )
    prepare = "\n".join(f"RUN {command}" for command in config.get("docker_prepare", []))
    return f"""FROM {REGISTRY}/{image}@sha256:{IMAGE_DIGESTS[task]}

RUN python -c "import site; open('/opt/sitepkg', 'w').write(site.getsitepackages()[0])"
RUN mkdir -p /tests/fixture
{save_paths}
{prepare}

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py
RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true
RUN chmod +x /tests/test.sh
WORKDIR /tests
"""


def test_script(config: dict[str, object]) -> str:
    expected = config["expected"]
    overlays = "\n".join(
        f"rm -rf /tmp/candidate/{path}\n"
        f"mkdir -p /tmp/candidate/$(dirname {path})\n"
        f"cp -a /tests/fixture/{path} /tmp/candidate/{path}"
        for path in config["paths"]
    )
    prepare = "\n".join(config.get("prepare", []))
    return f"""#!/usr/bin/env bash
set -uo pipefail
mkdir -p /logs/verifier

rm -rf /tmp/candidate
if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt 2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected {expected} --reason artifact-copy-failed
    exit 0
fi

# Replace candidate-created tests with the frozen test paths.
{overlays}

# Executable .pth lines run at interpreter start and put candidate code first.
SITEPKG=$(cat /opt/sitepkg)
printf "import sys; sys.path[:0] = ['/tmp/candidate/src', '/tmp/candidate']\n" \
    > "$SITEPKG/_candidate_override.pth"
{prepare}

chown -R candidate:candidate /tmp/candidate /logs/verifier
runuser -u candidate -- env HOME=/home/candidate \
    sh -c "cd /tmp/candidate && python -m pytest {config["pytest"]} \
           --junitxml=/logs/verifier/junit.xml --tb=short" \
    > /logs/verifier/pytest-stdout.txt 2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

python /tests/grade.py --expected {expected} \
    --junit /logs/verifier/junit.xml --pytest-exit-code "$pytest_exit_code"
"""


def write_task(task: str, config: dict[str, object]) -> None:
    if config.get("blocked"):
        print(f"  ! {task} blocked: {config['blocked']}")
        return
    tests = REPO / "catalog" / "tasks" / task / "harbor" / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / "Dockerfile").write_text(dockerfile(task, config), encoding="utf-8")
    (tests / "grade.py").write_text(GRADE_PY, encoding="utf-8")
    script = tests / "test.sh"
    script.write_text(test_script(config), encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> None:
    for task, config in TASKS.items():
        write_task(task, config)
        print(f"generated {task}")


if __name__ == "__main__":
    main()
