# Rollup production terminalization blocked

The required production compile was attempted without `--allow-incomplete`
using `toolchain.node.lock.toml` and `--allow-private`.

It failed before Harbor execution because the locked private npm dependency
artifact was unavailable:

```text
sha256:8c92e7fbbdcc8184d403279fc29d65d355ff0aa4669edbb684eb1390d65c2219
```

No Oracle, empty, stub, or forgery runtime was started. The frozen WASM
contract, source digest, hidden assertions, and `expected_total = 11` remain
unchanged. Terminalization requires restoring that exact artifact to the
configured private artifact store and rerunning the full gate sequence.
