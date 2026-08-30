# `yoctocolors` Provenance

- Upstream: `https://github.com/sindresorhus/yoctocolors`
- Revision: `a02a16ec36fbd58a0848e95598fb4913c54c7591`
- Git tree: `8e1ff2575754f9473b7107e9bde46fc4ccc7be1a`
- Version: `2.2.0`
- License: MIT, `license` SHA-256
  `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- `git archive` size: 51,200 bytes
- `git archive` SHA-256:
  `eae1cee24fce2d4242f126fcb614bd4d446c4390b2ee299674425cf35f69e640`
- Submodules: none
- Frozen source worktree: clean before baseline dependency installation

## Ground-truth probes

| Stage | Command | Exit | Result |
| --- | --- | ---: | --- |
| source fetch | `git fetch --depth 1 origin a02a16e...` and exact `rev-parse` assertion | 0 | exact revision and archive digest verified |
| upstream baseline | Node 24.19.0/npm 11.17.0 image; `npm install --ignore-scripts --no-audit --no-fund && npm test` | 0 | AVA 78/78; XO and TSD passed |
| dependency closure | `validate_npm_dependency_bundle(..., expected_npm_version="11.17.0")` | 0 | dependency-free npm v3 bundle valid |
| private verifier preflight | packed frozen source installed offline, then trusted Node runner | 0 | 80 collected, 80 passed, no collection error |

Task-local logs and reports are under
`.nl2repo/authoring-work/node-author-wave2-20260828/yoctocolors/`. Private
Oracle, verifier, command-plan, and dependency bytes are stored only in the
visibility-separated `.nl2repo/artifacts` CAS and are referenced by digest in
`task.toml`.
