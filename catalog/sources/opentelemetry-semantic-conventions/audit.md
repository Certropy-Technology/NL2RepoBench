# opentelemetry-semantic-conventions Authoring Audit

## Freeze

- Upstream: `https://github.com/open-telemetry/opentelemetry-python`
- Revision: `96df63add12f6e0453b265ac34c5c07ec7b9267e`
- Full checkout tree: `461346149cd647243de36681dcbe45276d687dd9`
- Package archive: `sha256:261528522499c80a3a264c33028a582476c8c460ef6411dea52b33946ad52d0b`
- Full repository archive at the same revision: `sha256:6d9e70371e0fe50b43c5274ab7d8e77349f5a50027b340946d53039e64c61208`
- License: Apache-2.0, package `LICENSE` SHA-256 `sha256:c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.

The package archive contains the generated `opentelemetry.semconv` namespace package,
including stable attributes, metrics, resource, trace, schemas, version, tests, and metadata.
The upstream package declares `opentelemetry-api==1.45.0.dev`, but a bounded `uv pip compile`
probe proved that this development sibling is not published. Stable scored modules import only
the standard library; the independent task therefore omits that unavailable runtime dependency
and records the relaxation in the public instruction and provenance.

## Contract inventory

The frozen upstream package has 23 non-incubating implementation modules and 4,537 lines in
the generated stable package. Its upstream test has one packaging smoke test. The private
contract expands this into 18 deterministic leaves covering version metadata, schema enum
membership and ordering, HTTP and database constants/enums, service/client/server/error/
exception constants, metric constants, namespace imports, `py.typed`, and distribution
metadata. All candidate imports happen in a child process under UID 10001.

## NoNetwork boundary

Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. The source
archive, dependency lock, verifier bundle, command plan, tests, and Oracle payload are frozen
before runtime. The Oracle restores `/solution/source.tar`, checks its digest, and installs the
candidate with no dependency resolution. The verifier does not import candidate code in the
trusted process; it invokes `adapter.py` subprocesses and owns collection, JUnit, and reward.
