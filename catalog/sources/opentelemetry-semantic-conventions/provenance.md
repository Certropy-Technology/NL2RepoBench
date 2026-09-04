# Provenance

The assigned source was cloned during authoring and detached at the exact full commit
`96df63add12f6e0453b265ac34c5c07ec7b9267e`. The package-only archive was created with
`git archive --format=tar --prefix=opentelemetry-semantic-conventions/ HEAD:opentelemetry-semantic-conventions`.
Its SHA-256 is `261528522499c80a3a264c33028a582476c8c460ef6411dea52b33946ad52d0b` and its
size is 870400 bytes. The package license is Apache-2.0 with SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.

The package's original `pyproject.toml` uses Hatchling and declares the unreleased monorepo
dependency `opentelemetry-api==1.45.0.dev`. `uv pip compile` returned an unsatisfiable
resolution because no such published version exists. Since stable semantic-conventions
modules use only `enum`, `typing`, `typing_extensions` only in unscored legacy modules, and
standard-library imports, this task uses a standalone build closure containing Hatchling,
Setuptools, Wheel, `typing-extensions`, and Hatchling's pinned transitive build requirements. No unavailable sibling
is silently claimed as installed; the packaging relaxation is recorded here and in the public
instruction.

The candidate dependency lock is `requirements.lock.txt`, generated with hashes for Python
3.12. The verifier uses the repository's pinned Harbor runtime and a separate child-side JSON
adapter. Private artifacts are kept outside the public source under the assigned handoff path.
