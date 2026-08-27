# Project Description

Implement a clean-room Python repository that provides the public behavior of
`boto3` version 1.43.78. Boto3 is the high-level AWS SDK for Python: it wraps
Botocore service models and exposes sessions, low-level service clients,
resource abstractions, waiters, service model documenters, transfer helpers,
and small compatibility utilities.

The repository is evaluated in a deterministic offline environment. The task
must work with fake credentials and local service-model fixtures; it must not
contact AWS, the instance metadata service, a credentials endpoint, or any
other network service during normal API use.

# Supports

- Python 3.12 on a Linux amd64 image.
- Installation from an empty workspace with `pip install --no-deps
  --no-build-isolation .`.
- A conventional setuptools package named `boto3`, importable as both
  `import boto3` and `from boto3.session import Session`.
- The runtime dependencies already present in the environment:
  `botocore==1.43.78`, `jmespath==1.0.1`, and `s3transfer==0.19.0`.
- Standard package metadata, version `1.43.78`, Apache-2.0 licensing, and the
  package data required by Botocore-backed service/resource models.

Do not require network access, AWS credentials, a local AWS CLI, or optional
native CRT libraries. Optional CRT entry points must fail with their documented
exception or warning when the optional dependency is unavailable.

# API Usage Guide

## Top-level `boto3`

Provide `boto3.__version__ == "1.43.78"`, `boto3.Session` as the session class,
and a lazily-created default session. Implement:

- `setup_default_session(**kwargs) -> None`: replace the module default with a
  `Session` constructed from the supplied keyword arguments.
- `client(service_name, *args, **kwargs)`: delegate to the default session's
  `client` method, creating that session on first use.
- `resource(service_name, *args, **kwargs)`: equivalent delegation to
  `Session.resource`.
- `set_stream_logger(name="boto3", level=logging.DEBUG,
  format_string=None) -> None`: add a stream handler with the requested level
  and formatter; use the documented default format when no format is given.

Importing the library must install a no-op logging handler and must not perform
network I/O or eagerly create credentials.

## `boto3.session.Session`

Support the constructor parameters `aws_access_key_id`,
`aws_secret_access_key`, `aws_session_token`, `region_name`,
`botocore_session`, `profile_name`, and `aws_account_id`. Preserve a supplied
Botocore session; otherwise create one. Set the Boto3 user-agent only when the
underlying user-agent is still Botocore's default. Reject an account ID without
credentials with Botocore's `NoCredentialsError`, and preserve all credential
fields when complete credentials are provided.

Expose read-only `profile_name`, `region_name`, `events`, and
`available_profiles` properties. Implement these discovery methods with the
same return shapes and delegation semantics as Botocore:

- `get_available_services() -> list[str]`
- `get_available_resources() -> list[str]`
- `get_available_partitions() -> list[str]`
- `get_available_regions(service_name, partition_name="aws",
  allow_non_regional=False) -> list[str]`
- `get_credentials()`
- `get_partition_for_region(region_name) -> str`

Implement `client(service_name, region_name=None, api_version=None,
use_ssl=True, verify=None, endpoint_url=None, aws_access_key_id=None,
aws_secret_access_key=None, aws_session_token=None, config=None,
aws_account_id=None)`. It must pass the effective arguments to Botocore,
honor explicit region/config precedence, and return the low-level client
without making a request merely by constructing it.

Implement `resource(service_name, region_name=None, api_version=None,
use_ssl=True, verify=None, endpoint_url=None, aws_access_key_id=None,
aws_secret_access_key=None, aws_session_token=None, config=None,
aws_account_id=None)`. Load the latest resource model, construct the matching
client with the `Resource` user-agent marker, and return a generated resource
object. Raise `ResourceNotExistsError` for unknown or unavailable resources and
`UnknownAPIVersionError` when a requested resource API version cannot be
loaded. The resource path must support identifiers, actions, collections,
waiters, subresources, batch actions, and lazy collection iteration without
network access until the returned Botocore client is explicitly called.

`Session.__repr__` must identify the concrete class and current region, for
example `Session(region_name='us-east-1')`.

## Resources, collections, actions, and models

Provide the public resource machinery under `boto3.resources`, including the
factory, model, collection, action, response, parameter, subresource, waiter,
and collection-manager modules. Generated resource classes must expose the
identifiers, attributes, actions, collection managers, waiters, and service
metadata described by Botocore JSON resource definitions. Preserve lazy loading,
copy/clone behavior, parent-resource links, parameter validation, and the
documented `ResourceNotExistsError`/`ValueError` contracts for malformed
definitions.

Support condition expressions and DynamoDB helpers under `boto3.dynamodb`,
including condition objects' composition, placeholder name/value generation,
type serialization, table helpers, and transformation utilities. Preserve
deterministic ordering of generated expression maps.

## Service-model documentation

Implement the public documenter classes and functions under `boto3.docs` for
actions, attributes, clients, collections, docstrings, methods, resources,
services, subresources, utilities, and waiters. They should render the
documented reStructuredText-style sections from Botocore service models,
including required parameters, return/response shapes, links, examples, and
stable ordering. `boto3.docs.generate_docs` must accept the documented model
and output arguments and produce deterministic text.

## Utilities and transfers

Implement the public helpers in `boto3.utils` and `boto3.compat`, including
lazy waiter-model loading, module importing, attribute injection with shadowing
checks, append-mode detection, file renaming, deprecation-warning filtering,
and the platform-specific compatibility behavior. Preserve exception types and
messages where the API documents them.

Expose `boto3.s3.transfer.S3Transfer`, `TransferConfig`, and related transfer
helpers with the constructor validation, context-manager lifecycle, upload and
download delegation, callback wrapping, path-type checks, retry/error
propagation, and mutually-exclusive argument rules expected of the public API.

The optional `boto3.crt` module must retain its public names and singleton/
identity/configuration behavior. If `awscrt` is absent, use the documented
skip/warning/error behavior rather than importing a substitute implementation.

# Implementation Notes

- Keep public re-exports and module paths compatible with the signatures above;
  hidden checks import both top-level names and submodules directly.
- Use the supplied Botocore loader/model data instead of hard-coding AWS
  network responses. All behavior tested by this task is local and deterministic
  when clients are stubbed.
- Do not copy the upstream implementation or tests into the generated answer.
  Recreate the contracts from this specification and use normal package/data
  files so installation from an empty workspace succeeds.
- Avoid module-global state leaks between sessions and tests. Default-session
  state, logging handlers, lazy caches, and resource factories must be resettable
  and deterministic.
- Preserve Python exceptions rather than converting them to strings. In
  particular, invalid service/resource names, invalid credentials combinations,
  invalid transfer arguments, missing data models, and expression/type errors
  must remain distinguishable.
- The grader uses fake credentials, Botocore stubs, local JSON service models,
  and filesystem fixtures. A successful implementation never needs to contact
  AWS.
