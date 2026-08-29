# Remediation Record

- The first task-local production projection was a legacy Harbor schema `1.4`
  output and was not reused as source evidence. The source was recompiled with
  the current Node lane into
  `.nl2repo/authoring-work/node-author-wave2-20260828/basic-ftp/compiled-production-final`.
- `source.tar` matches the declared source digest
  `sha256:e7998232ed9c801ef5b2277b8164c74d7595317bbbb08f57ef8dc1c8aca27364`.
  The codeload archive used by the trusted Oracle matches
  `sha256:515fbf4bfc6fed25ed9b58d5ef72d9d67cbe13cb4a2b6ca5abdcff4435ae092e`.
- The npm runtime closure is intentionally empty and is represented by the
  private npm bundle artifact in `task.toml`; the verifier dependency lock and
  both base images are digest-bound.
- The install-script control initially emitted malformed JSON because of an
  over-escaped shell literal. The control was corrected, recompiled, and
  rechecked. It now reaches the candidate installation failure path under the
  verifier's `--ignore-scripts` policy.
- A first official Harbor invocation used the obsolete `--output` option and
  exited `2`; the documented `-o/--jobs-dir` form then completed the trusted
  Oracle run with exit `0` and reward `1.0`.
- No model Agent Run was started. The direct control replays use Docker
  `--network none`; every network receipt reports
  `public_network_available=false`.
