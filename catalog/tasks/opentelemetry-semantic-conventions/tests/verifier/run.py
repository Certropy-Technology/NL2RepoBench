from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCENARIOS = {
    "distribution-version": "0.66b0.dev0",
    "runtime-version": "0.66b0.dev",
    "pytyped": True,
    "namespace-imports": [
        "opentelemetry.semconv.attributes", "opentelemetry.semconv.metrics",
        "opentelemetry.semconv.resource", "opentelemetry.semconv.schemas",
        "opentelemetry.semconv.trace", "opentelemetry.semconv.version",
    ],
    "schema-type": [True, "Schemas"],
    "schema-order": ["V1_21_0", "V1_23_1", "V1_25_0", "V1_26_0", "V1_27_0", "V1_28_0", "V1_29_0", "V1_30_0", "V1_31_0", "V1_32_0", "V1_33_0", "V1_34_0", "V1_36_0", "V1_37_0", "V1_38_0", "V1_39_0", "V1_40_0", "V1_41_0", "V1_41_1", "V1_42_0", "V1_43_0", "V1_44_0"],
    "schema-values": [f"https://opentelemetry.io/schemas/{v}" for v in ["1.21.0", "1.23.1", "1.25.0", "1.26.0", "1.27.0", "1.28.0", "1.29.0", "1.30.0", "1.31.0", "1.32.0", "1.33.0", "1.34.0", "1.36.0", "1.37.0", "1.38.0", "1.39.0", "1.40.0", "1.41.0", "1.41.1", "1.42.0", "1.43.0", "1.44.0"]],
    "schema-lookup": "V1_44_0",
    "http-constants": {"HTTP_REQUEST_HEADER_TEMPLATE":"http.request.header", "HTTP_REQUEST_METHOD":"http.request.method", "HTTP_REQUEST_METHOD_ORIGINAL":"http.request.method_original", "HTTP_REQUEST_RESEND_COUNT":"http.request.resend_count", "HTTP_RESPONSE_HEADER_TEMPLATE":"http.response.header", "HTTP_RESPONSE_STATUS_CODE":"http.response.status_code", "HTTP_ROUTE":"http.route"},
    "http-enum": [["CONNECT","CONNECT"],["DELETE","DELETE"],["GET","GET"],["HEAD","HEAD"],["OPTIONS","OPTIONS"],["PATCH","PATCH"],["POST","POST"],["PUT","PUT"],["TRACE","TRACE"],["OTHER","_OTHER"]],
    "http-lookup": "GET",
    "db-constants": {"DB_COLLECTION_NAME":"db.collection.name", "DB_NAMESPACE":"db.namespace", "DB_OPERATION_BATCH_SIZE":"db.operation.batch.size", "DB_OPERATION_NAME":"db.operation.name", "DB_QUERY_SUMMARY":"db.query.summary", "DB_QUERY_TEXT":"db.query.text", "DB_RESPONSE_STATUS_CODE":"db.response.status_code", "DB_STORED_PROCEDURE_NAME":"db.stored_procedure.name", "DB_SYSTEM_NAME":"db.system.name"},
    "db-enum": [["MARIADB","mariadb"],["MICROSOFT_SQL_SERVER","microsoft.sql_server"],["MYSQL","mysql"],["POSTGRESQL","postgresql"]],
    "db-lookup": "POSTGRESQL",
    "service-client-server": {"service":{"SERVICE_INSTANCE_ID":"service.instance.id","SERVICE_NAME":"service.name","SERVICE_NAMESPACE":"service.namespace","SERVICE_VERSION":"service.version"},"client":{"CLIENT_ADDRESS":"client.address","CLIENT_PORT":"client.port"},"server":{"SERVER_ADDRESS":"server.address","SERVER_PORT":"server.port"}},
    "exception-error": {"exception":{"EXCEPTION_ESCAPED":"exception.escaped","EXCEPTION_MESSAGE":"exception.message","EXCEPTION_STACKTRACE":"exception.stacktrace","EXCEPTION_TYPE":"exception.type"},"error":{"ERROR_TYPE":"error.type"}},
    "metrics": {"http":{"HTTP_CLIENT_REQUEST_DURATION":"http.client.request.duration","HTTP_SERVER_REQUEST_DURATION":"http.server.request.duration"},"db":{"DB_CLIENT_OPERATION_DURATION":"db.client.operation.duration"}},
    "types": [True, True],
}


def invoke(scenario: str) -> dict[str, object]:
    command = [sys.executable, "-I", "-B", str(Path(__file__).with_name("adapter.py")), "--candidate-site", "/tmp/candidate-site", "--scenario", scenario]
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/tmp", "TMPDIR": "/tmp", "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        completed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=30, check=False, preexec_fn=_drop_candidate_privileges)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "exception_message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "exception_message": completed.stderr[-1000:]}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "exception_message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def _drop_candidate_privileges() -> None:
    os.setgroups([])
    os.setgid(10001)
    os.setuid(10001)


def main() -> int:
    leaves = []
    for scenario, expected in SCENARIOS.items():
        result = invoke(scenario)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = actual == expected
        leaves.append({"id": f"opentelemetry-semantic-conventions/{scenario}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True)[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
