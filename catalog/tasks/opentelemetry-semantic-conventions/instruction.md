# Project Description

Create a complete, installable Python package named `opentelemetry-semantic-conventions`
from an empty workspace. It provides generated, deterministic names used by OpenTelemetry
instrumentation: semantic attribute keys, metric names, and schema-version enum members.
The package is a namespace package under `opentelemetry.semconv`; the implementation must
not contact a network or require an external service at import time.

# Supports

- Support CPython 3.10 and newer, with a standard PEP 517 build and editable installation.
- Set the distribution and runtime semantic-conventions version to `0.66b0.dev`.
- Use the `src` layout with `opentelemetry/semconv/` as a namespace-compatible package.
- Provide `opentelemetry/semconv/py.typed` and preserve normal importability of the
  `attributes`, `metrics`, `resource`, `schemas`, `trace`, and `version` modules.
- The scored stable modules use only Python's standard library. Do not add a runtime network,
  filesystem, subprocess, telemetry, or service dependency.
- Keep constants as strings and enum members as real `enum.Enum` members. Do not replace
  enums with dictionaries or expose mutable substitutes for constants.

# API Usage Guide

## Schema versions

Import `Schemas` from `opentelemetry.semconv.schemas`. It is an `enum.Enum` whose members,
in declaration order, are `V1_21_0`, `V1_23_1`, `V1_25_0`, `V1_26_0`, `V1_27_0`, `V1_28_0`,
`V1_29_0`, `V1_30_0`, `V1_31_0`, `V1_32_0`, `V1_33_0`, `V1_34_0`, `V1_36_0`, `V1_37_0`,
`V1_38_0`, `V1_39_0`, `V1_40_0`, `V1_41_0`, `V1_41_1`, `V1_42_0`, `V1_43_0`, and
`V1_44_0`. Each member's value is the corresponding string
`https://opentelemetry.io/schemas/<version>`, and construction by that value must work.

## HTTP attributes

Import constants and `HttpRequestMethodValues` from
`opentelemetry.semconv.attributes.http_attributes`. The constants are:

```text
HTTP_REQUEST_HEADER_TEMPLATE = "http.request.header"
HTTP_REQUEST_METHOD = "http.request.method"
HTTP_REQUEST_METHOD_ORIGINAL = "http.request.method_original"
HTTP_REQUEST_RESEND_COUNT = "http.request.resend_count"
HTTP_RESPONSE_HEADER_TEMPLATE = "http.response.header"
HTTP_RESPONSE_STATUS_CODE = "http.response.status_code"
HTTP_ROUTE = "http.route"
```

`HttpRequestMethodValues` is an `enum.Enum` with ordered members `CONNECT`, `DELETE`, `GET`,
`HEAD`, `OPTIONS`, `PATCH`, `POST`, `PUT`, `TRACE`, and `OTHER`; their values are the same
uppercase names except `OTHER`, whose value is `"_OTHER"`.

## Database attributes

Import constants and `DbSystemNameValues` from
`opentelemetry.semconv.attributes.db_attributes`. Constants are
`DB_COLLECTION_NAME="db.collection.name"`, `DB_NAMESPACE="db.namespace"`,
`DB_OPERATION_BATCH_SIZE="db.operation.batch.size"`, `DB_OPERATION_NAME="db.operation.name"`,
`DB_QUERY_SUMMARY="db.query.summary"`, `DB_QUERY_TEXT="db.query.text"`,
`DB_RESPONSE_STATUS_CODE="db.response.status_code"`,
`DB_STORED_PROCEDURE_NAME="db.stored_procedure.name"`, and
`DB_SYSTEM_NAME="db.system.name"`.
`DbSystemNameValues` has ordered members `MARIADB="mariadb"`,
`MICROSOFT_SQL_SERVER="microsoft.sql_server"`, `MYSQL="mysql"`, and
`POSTGRESQL="postgresql"`.

## Other stable attribute and metric constants

The following modules expose the named string constants exactly as shown:

- `opentelemetry.semconv.attributes.service_attributes`: `SERVICE_INSTANCE_ID="service.instance.id"`,
  `SERVICE_NAME="service.name"`, `SERVICE_NAMESPACE="service.namespace"`, and
  `SERVICE_VERSION="service.version"`.
- `opentelemetry.semconv.attributes.client_attributes`: `CLIENT_ADDRESS="client.address"` and
  `CLIENT_PORT="client.port"`.
- `opentelemetry.semconv.attributes.server_attributes`: `SERVER_ADDRESS="server.address"` and
  `SERVER_PORT="server.port"`.
- `opentelemetry.semconv.attributes.exception_attributes`: `EXCEPTION_ESCAPED="exception.escaped"`,
  `EXCEPTION_MESSAGE="exception.message"`, `EXCEPTION_STACKTRACE="exception.stacktrace"`, and
  `EXCEPTION_TYPE="exception.type"`.
- `opentelemetry.semconv.attributes.error_attributes`: `ERROR_TYPE="error.type"`.
- `opentelemetry.semconv.metrics.http_metrics`: `HTTP_CLIENT_REQUEST_DURATION="http.client.request.duration"`
  and `HTTP_SERVER_REQUEST_DURATION="http.server.request.duration"`.
- `opentelemetry.semconv.metrics.db_metrics`: `DB_CLIENT_OPERATION_DURATION="db.client.operation.duration"`.

All constants are deterministic strings. Importing any listed module repeatedly must return
the same values, and enum iteration must preserve the stated order.

## Package metadata

`opentelemetry.semconv.version.__version__` is exactly `"0.66b0.dev"`.
Installed distribution metadata must report the PEP 440 normalized equivalent
`"0.66b0.dev0"` for `opentelemetry-semantic-conventions`, and
`opentelemetry.semconv.py.typed` must exist.

# Implementation Notes

Use regular Python modules and `enum.Enum`; preserve the generated import paths and namespace
package behavior. The verifier checks the stable modules and representative generated values
described above, not every incubating convention file in the upstream monorepo. Keep module
imports side-effect free and avoid fetching the source repository or package dependencies at
runtime. The independent task intentionally excludes the monorepo's unreleased
`opentelemetry-api==1.45.0.dev` sibling requirement because it is unavailable from the package
index and is not imported by the scored stable semantic-convention modules.
