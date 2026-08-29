from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ADAPTER = Path(__file__).with_name("adapter.py")
SCHEMA = "keyring-deterministic-contract-v1"

CASES = [
    ("packaging-surface", "packaging_surface", {"all": ["set_keyring", "get_keyring", "set_password", "get_password", "delete_password", "get_credential"], "callables": True, "console": 1, "version": "25.7.1.dev8+g7603e7cad"}),
    ("simple-credential", "simple_credential", {"password": "s3cret", "username": "alice", "vars": {"password": "s3cret", "username": "alice"}}),
    ("anonymous-credential", "anonymous_credential", {"password": "token", "username_error": ["ValueError", "Anonymous credential has no username"], "vars": {"password": "token"}}),
    ("environment-credential", "environ_credential", {"equal": True, "missing": ["ValueError", "Missing environment variable:KR_USER"], "unequal": False, "values": {"password": "secret", "username": "ada"}}),
    ("credential-abstract", "credential_abstract", {"message_has_abstract": True, "type": "TypeError"}),
    ("exception-hierarchy", "exception_hierarchy", {"delete": True, "locked": True, "no_keyring_runtime": True, "set": True}),
    ("exception-context", "exception_context", {"clear": False, "message": "bad", "suppressed": True, "type": "ValueError", "warning": "DeprecationWarning"}),
    ("null-backend", "null_backend", {"delete": None, "get": None, "priority": -1, "set": None}),
    ("fail-backend", "fail_backend", {"failures": [["NoKeyringError", True], ["NoKeyringError", True], ["NoKeyringError", True]], "priority": 0}),
    ("null-crypter", "null_crypter", {"decrypt_identity": True, "encrypt_identity": True}),
    ("scheme-default", "scheme_default", {"full": {"extra": "x", "service": "svc", "username": "alice"}, "service": {"service": "svc"}}),
    ("scheme-keepass", "scheme_keepass", {"full": {"Title": "svc", "UserName": "alice"}, "service": {"Title": "svc"}}),
    ("backend-identity", "backend_identity", {"name_suffix": True, "priority": 4.5, "string_priority": True, "string_suffix": True}),
    ("backend-viability", "backend_viability", {"bad": False, "good": True, "listed": True}),
    ("backend-registration", "backend_registration", {"registered": True}),
    ("backend-default-credential", "backend_default_credential", {"found": {"password": "pw", "username": "alice"}, "missing": None, "none_username": None}),
    ("backend-default-delete", "backend_default_delete", {"message": "reason", "type": "PasswordDeleteError"}),
    ("backend-empty-username", "backend_empty_username", {"stored": "pw", "warning": "DeprecationWarning"}),
    ("backend-env-properties", "backend_env_properties", {"foo_bar": "fizz buzz", "other": False}),
    ("backend-with-properties", "backend_with_properties", {"alt": "bar", "independent": True, "original_has": False}),
    ("core-facade", "core_facade", {"after": None, "before": "pw", "credential": {"password": "pw", "username": "alice"}, "same": True}),
    ("core-set-keyring-validation", "core_set_keyring_validation", {"message": "The keyring must be an instance of KeyringBackend", "type": "TypeError"}),
    ("core-load-env", "core_load_env", {"loaded": "keyring.backends.null.Keyring", "missing": None}),
    ("core-load-config-missing", "core_load_config_missing", {"value": None}),
    ("core-load-config-backend", "core_load_config_backend", {"class": "keyring.backends.null.Keyring", "priority": -1}),
    ("core-disable", "core_disable", {"content": "[backend]\ndefault-keyring=keyring.backends.null.Keyring", "second": ["RuntimeError", True]}),
    ("core-detect-priority", "core_detect_priority", {"recommended": 8, "selected": 8}),
    ("chainer-priority", "chainer_priority", {"multiple": 10, "order": [3, 2], "single": -1}),
    ("chainer-read", "chainer_read", {"value": "high"}),
    ("chainer-write-delete", "chainer_write_delete", {"deleted": None, "stored": "pw"}),
    ("chainer-credential", "chainer_credential", {"password": "high", "username": "alice"}),
    ("non-data-property", "non_data_property", {"before": 3, "class_descriptor": "NonDataProperty", "override": 4}),
    ("classproperty-mutation", "classproperty_mutation", {"class": 5, "instance": 5, "instance_vars": {}}),
    ("classproperty-readonly", "classproperty_readonly", {"message": "can't set attribute", "type": "AttributeError", "value": "fixed"}),
    ("cli-strip", "cli_strip", {"empty": "", "many": "a\n", "none": "abc", "one": "abc"}),
    ("cli-set-pipe", "cli_set_pipe", {"stored": "pipe-secret"}),
    ("cli-get-plain", "cli_get_plain", {"lines": ["alice", "pw"]}),
    ("cli-get-json", "cli_get_json", {"password": "pw", "username": "alice"}),
    ("cli-missing-args", "cli_missing_args", {"code": 2, "requires": True}),
    ("cli-parser-contract", "cli_parser_contract", {"formats": ["plain", "json"], "modes": ["password", "creds"], "operations": ["get", "set", "del", "diagnose"]}),
    ("completion-missing", "completion_missing", {"code": 1, "notice": True}),
    ("http-existing", "http_password_mgr_existing", {"value": ["ada", "stored"]}),
    ("http-prompt", "http_password_mgr_prompt", {"prompt_has_context": True, "stored": "prompted", "value": ["ada", "prompted"]}),
    ("http-clear", "http_password_mgr_clear", {"remaining": None}),
    ("plugin-loading", "plugin_loading", {"called": ["loaded"]}),
]


def invoke(operation: str) -> dict[str, object]:
    request = json.dumps({"operation": operation, "schema_version": SCHEMA}, sort_keys=True, separators=(",", ":"))
    command = [
        "runuser", "-u", "candidate", "--", "env", "HOME=/home/candidate",
        "PYTHONDONTWRITEBYTECODE=1", "PYTHONHASHSEED=0", "PYTHONNOUSERSITE=1",
        sys.executable, "-I", "-B", "-", "--candidate-site",
        os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--dependency-site", os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"),
        "--request", request,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") == "1":
        command = [
            sys.executable, "-I", "-B", "-", "--candidate-site",
            os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
            "--dependency-site", os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", ""),
            "--request", request,
        ]
    try:
        completed = subprocess.run(command, input=ADAPTER.read_bytes(), capture_output=True, timeout=20, check=False)
    except (OSError, subprocess.SubprocessError) as error:
        return {"ok": False, "exception_type": type(error).__name__, "exception_message": str(error)}
    lines = [line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        detail = (completed.stderr or completed.stdout).decode("utf-8", "replace")[-2000:]
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": detail}
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(error)}
    return value if isinstance(value, dict) else {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": "adapter response is not an object"}


def main() -> None:
    leaves = []
    for case_id, operation, expected in CASES:
        actual = invoke(operation)
        passed = actual.get("ok") is True and actual.get("value") == expected
        leaf = {"id": "keyring/" + case_id, "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1600]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
