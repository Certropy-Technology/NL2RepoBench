# ghapi provenance

- Authoring mode: `author-one`.
- Candidate checkout: `.nl2repo/authoring-work/python-author-wave2-20260828/ghapi`.
- Revision and source archive digest are recorded in `task.toml` and `audit.md`.
- The upstream package declares `fastcore>=2.2.7`, `fastspec>=0.2.1`, and
  `tomli` on Python below 3.11. The task runtime pins the resolved Python 3.12
  closure and includes the verifier runner dependencies in one hash lock.
- Oracle source acquisition, if run, must fetch only the exact revision,
  assert its commit, verify the archive digest, and never expose source to the
  model Agent Run.
- Large clones and bundles remain under `.nl2repo/authoring-work`; no private
  tests or source bytes are placed in public instruction or catalog metadata.
