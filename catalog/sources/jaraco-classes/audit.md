# jaraco-classes authoring audit

## Frozen source

- Upstream: `https://github.com/jaraco/jaraco.classes`
- Revision: `eeccd0b835bccf18353c44f4b35a1a27c9284fce`
- Authoring source archive: `git archive --format=tar HEAD`, SHA-256
  `sha256:3a5b0c0b0ff76f73bd4285f15286b1b87f37b0b217f17b6c8bdcfe6f6ea463ad`.
  The production Oracle solve fetches the same immutable commit from
  `codeload.github.com`; its downloaded tarball SHA-256 is
  `sha256:4c3f9931ea112ae1f06448efe329ab40a700ed8f484cf32431e2cb66b7ddd28f`,
  which is the catalog `source_digest` because the slim Oracle image has no
  git or curl binary.
- License metadata: MIT. The source revision has no tracked license file;
  setuptools/coherent.licensed materializes the standard MIT text during the
  source build. The generated license bytes are retained in task-local
  provenance and are not used as candidate code.
- The frozen tree contains `jaraco/classes/{__init__,ancestry,meta,properties}.py`
  and `jaraco/classes/py.typed`, with no tracked `tests/` directory.

## Inventory and adaptation

The upstream doctest collection is executable and passed `7/7` in the pinned
authoring probe. The scored contract covers the actual local API: MRO helpers,
diamond-safe subclass traversal, non-data properties, class properties with
and without the metaclass hook, leaf-class tracking, tag registration, package
identity, and the typing marker. No network, subprocess, native extension,
Graphviz, or external service behavior is included.

## Packaging remediation

The upstream `pyproject.toml` uses dynamic setuptools SCM versioning and
release-only build requirements. The Oracle solve script rewrites only those
packaging fields after verifying the pinned source commit, using a static
version and the pinned setuptools build backend. The runtime dependency
`more_itertools` remains declared and is installed from a private hash lock at
image build time.

## Boundary

The private verifier uses `custom-json-v1`. Every scenario runs candidate code
through the UID-isolated candidate client; the trusted verifier never imports
candidate code into its own interpreter. Oracle source acquisition is confined
to the private Oracle `solve.sh` and receives a run-scoped exact `github.com`
host authorization. Agent and verifier metadata remain no-network.
