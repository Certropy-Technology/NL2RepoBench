# Build `botocore`

Create a complete, installable Python package named `botocore` from an empty
workspace. The package is the local, data-driven core used by AWS SDK clients.
The implementation must be usable without network access, AWS credentials, an
AWS account, or a running service. The frozen source revision is the behavior
reference, but do not copy the upstream source or tests into the generated
workspace.

## Project Description

Implement a compatible subset of botocore centered on deterministic local
operations: session and credential configuration, service-model loading,
request construction, Signature Version 4 signing, retry configuration,
exception classes, and the `Stubber` test double. Keep the package modular and
installable from a source-only workspace.

The task intentionally excludes live AWS calls, metadata-service calls,
credential-process commands, CRT acceleration, TLS/network integration, and
all behavior requiring an account or remote data. Local model files for the
S3 and DynamoDB services must be available after installation so that model and
client operations can be created offline.

## Supports

- CPython 3.12 on Linux amd64.
- A normal setuptools source build with `pip install .` or the Harbor
  candidate installer.
- Runtime dependencies: `jmespath==1.0.1`, `python-dateutil==2.9.0.post0`,
  and `urllib3==2.5.0`.
- No runtime network access and no subprocesses for the tested APIs.
- Stable behavior for fixed inputs and fixed local model data.

## API Usage Guide

### Session and credentials

`botocore.session.get_session()` returns a fresh `Session`. Support
`set_config_variable(name, value)`, `get_config_variable(name)`,
`set_credentials(access_key, secret_key, token=None, account_id=None)`,
`get_credentials()`, `get_available_services()`,
`get_available_regions(service_name)`, `get_service_model(service_name)`,
`get_paginator_model(service_name)`, `get_waiter_model(service_name)`, and
`create_client(service_name, region_name=..., aws_access_key_id=...,
aws_secret_access_key=..., aws_session_token=..., endpoint_url=...,
config=...)`.

Explicit session configuration takes precedence over environment variables.
Credential objects expose `access_key`, `secret_key`, `token`, and
`method`. Missing credentials for a client must raise the documented
botocore credential exception instead of contacting the instance metadata
service. Service and region lists come from bundled model data.

### Configuration

`botocore.config.Config` accepts common client options including
`region_name`, `signature_version`, `connect_timeout`, `read_timeout`,
`retries`, `s3`, and `user_agent_extra`. Config objects are immutable-like:
`merge()` returns a new config and does not mutate either input. The unsigned
constant `botocore.UNSIGNED` is supported as a signature choice.

### Service models and clients

`Session.get_service_model("s3")` returns a service model loaded from the
installed JSON data. It must expose service metadata, operation lookup, input
shape lookup, and operation names. A created S3 client exposes modeled
operations such as `list_objects_v2` and `put_object`; client metadata includes
the service model and region. Invalid service names raise a normal botocore
exception.

### Requests and signing

`botocore.awsrequest.AWSRequest(method, url, data=None, headers=None)` stores a
request and `prepare()` returns a prepared request with normalized headers and
body. `botocore.auth.SigV4Auth(credentials, service_name, region_name)` signs
an `AWSRequest` using the standard `Authorization`, `X-Amz-Date`, and payload
hash behavior. Fixed credentials, request, and timestamp must produce stable
header values. `botocore.UNSIGNED` leaves the request unsigned.

### Stubber

`botocore.stub.Stubber(client)` is a local context manager and activation
helper. `add_response(operation, response, expected_params=None)` queues a
successful modeled response and `add_client_error(operation, error_code,
error_message=None, expected_params=None, modeled_fields=None)` queues a
modeled error. Activated stubs are consumed in order; unexpected calls,
parameter mismatches, and exhausted queues raise the corresponding botocore
stub exceptions. No network call may happen while a stub is active.

### Exceptions and retry helpers

Preserve the public exception classes and their inheritance relationships,
including `ClientError`, `NoCredentialsError`, `ParamValidationError`,
`ProfileNotFound`, `StubAssertionError`, `StubResponseError`, and
`UnStubbedResponseError`. `botocore.retryhandler.create_retry_handler` and
`botocore.translate.build_retry_config` must accept the documented local
configuration shapes and return deterministic retry behavior for success,
throttling, and capped-attempt cases.

## Determinism and Error Boundaries

- Model loading, serialization, request construction, signing, config merging,
  and stub responses are local and deterministic.
- Preserve insertion order where the API exposes order; do not rely on hash
  iteration for generated request or model output.
- Invalid parameters, missing credentials, unknown models, unexpected stub
  calls, and malformed configuration raise normal typed exceptions.
- Do not invoke `curl`, `wget`, `git`, a credential process, the metadata
  service, or any other subprocess to satisfy this task.
- Do not require `awscrt`, Graphviz, an AWS account, or a live HTTP endpoint.

## Implementation Notes

Keep public re-exports and exception identity consistent across modules. The
installed package must include the local service-model JSON data required by
the S3 and DynamoDB scenarios. The build must succeed without a `.git`
directory and must expose a stable `botocore.__version__` matching the chosen
package metadata. Hidden verification compares observable API results and
typed failures, not object identities or memory addresses.
