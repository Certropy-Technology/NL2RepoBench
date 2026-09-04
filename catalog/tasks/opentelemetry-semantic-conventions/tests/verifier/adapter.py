from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import importlib.resources
import json
import os
import sys
from enum import Enum


def constants(module: str) -> dict[str, str]:
    return {k: v for k, v in vars(importlib.import_module(module)).items() if k.isupper() and isinstance(v, str)}


def pairs(value: type[Enum]) -> list[list[str]]:
    return [[member.name, member.value] for member in value]


def exercise(scenario: str) -> object:
    if scenario == "distribution-version":
        return importlib.metadata.version("opentelemetry-semantic-conventions")
    if scenario == "runtime-version":
        return importlib.import_module("opentelemetry.semconv.version").__version__
    if scenario == "pytyped":
        return importlib.resources.files("opentelemetry.semconv").joinpath("py.typed").is_file()
    if scenario == "namespace-imports":
        names = [
            "opentelemetry.semconv.attributes",
            "opentelemetry.semconv.metrics",
            "opentelemetry.semconv.resource",
            "opentelemetry.semconv.schemas",
            "opentelemetry.semconv.trace",
            "opentelemetry.semconv.version",
        ]
        return [importlib.import_module(name).__name__ for name in names]
    schemas = importlib.import_module("opentelemetry.semconv.schemas").Schemas
    if scenario == "schema-type":
        return [issubclass(schemas, Enum), schemas.__name__]
    if scenario == "schema-order":
        return [member.name for member in schemas]
    if scenario == "schema-values":
        return [member.value for member in schemas]
    if scenario == "schema-lookup":
        return schemas("https://opentelemetry.io/schemas/1.44.0").name
    http = importlib.import_module("opentelemetry.semconv.attributes.http_attributes")
    if scenario == "http-constants":
        return constants(http.__name__)
    if scenario == "http-enum":
        return pairs(http.HttpRequestMethodValues)
    if scenario == "http-lookup":
        return http.HttpRequestMethodValues("GET").name
    db = importlib.import_module("opentelemetry.semconv.attributes.db_attributes")
    if scenario == "db-constants":
        return constants(db.__name__)
    if scenario == "db-enum":
        return pairs(db.DbSystemNameValues)
    if scenario == "db-lookup":
        return db.DbSystemNameValues("postgresql").name
    if scenario == "service-client-server":
        return {
            "service": constants("opentelemetry.semconv.attributes.service_attributes"),
            "client": constants("opentelemetry.semconv.attributes.client_attributes"),
            "server": constants("opentelemetry.semconv.attributes.server_attributes"),
        }
    if scenario == "exception-error":
        return {
            "exception": constants("opentelemetry.semconv.attributes.exception_attributes"),
            "error": constants("opentelemetry.semconv.attributes.error_attributes"),
        }
    if scenario == "metrics":
        return {
            "http": constants("opentelemetry.semconv.metrics.http_metrics"),
            "db": constants("opentelemetry.semconv.metrics.db_metrics"),
        }
    if scenario == "types":
        enum_types = [type(member).__name__ for member in schemas]
        values = constants("opentelemetry.semconv.attributes.http_attributes")
        return [all(name == "Schemas" for name in enum_types), all(isinstance(value, str) for value in values.values())]
    raise ValueError(f"unknown scenario: {scenario}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    print(json.dumps({"ok": True, "value": exercise(args.scenario)}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}", "exception_message": str(exc)}, sort_keys=True))
