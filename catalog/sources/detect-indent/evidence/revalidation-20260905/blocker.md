# Detect-indent revalidation blocker

- The validated catalog source digest is `sha256:6d745e20c2aef62dae5f3ce74dfb27a65f50de6d7b50850245af88a2c34578a2`.
- `uv run nl2repo task validate-source catalog/sources/detect-indent` exited 0 and reported that digest.
- Two production compiles with `toolchain.node.lock.toml`, the authorized parent private CAS, and `--allow-private` exited 0. Both produced the same 73-file manifest: `sha256:cf1fce309b624189bb12573a6295526a4eeec0014fac6aff689b10fbb811300e`; canonical digest `sha256:741c46409679eb81119007b4d9b39ed0f89ead1fd189b843f8f8aea564c76f87`.
- The private Oracle artifact is present and hash-valid at `sha256:1697bce7063600a86f08b5b6b587311797ff748346d13d521925adb29d9ae6a8`, but its `solve.sh` executes `git fetch` from `github.com` at runtime before checking the pinned revision and source archive digest.
- Oracle and all controls were not run for this revalidation. The existing lifecycle and historical `production-evidence.json` remain unchanged.

## Remediation

Replace or rebuild the private Oracle payload so it materializes the same immutable source archive locally without a runtime source-host fetch, then run Harbor 0.21.0 Oracle once and the complete declared control matrix against the fresh manifest. Persist every receipt under this directory before updating production evidence.
