# Revalidation Blocker: Missing Frozen Oracle Payload

Task: `go-version`

Revalidation source digest from `reports/instruction-revalidation-queue-20260905.json`:
`sha256:8ae884ffaefb17fc56cb29c86f7e039cf81b23ddbd99861e26b64378374a4f18`.

Frozen upstream source authority:

- URL: `https://github.com/hashicorp/go-version`
- revision: `e2b1b0b0c4b32767e1570ddce50dff79fdddf092`
- required git-archive tar digest: `sha256:e79a0e175c9821ee538e9ca25a504bb15b4f445f8781a3208c4f7704c5448c12`

## Bounded Offline Checks

All checks below were run without granting network authorization.

1. The declared Oracle CAS object exists and matches `sha256:e220521ab7040823576b6c16743ed31b652c39cf8d8a17c84c19fd4ccd5de562`, size `706` bytes. Its complete tar listing contains only `solve.sh`; the script calls `git fetch` from `https://github.com/hashicorp/go-version` at runtime and does not contain `source.tar` or `oracle-package`.
2. The declared module bundle exists and matches `sha256:ac9751fca88240393a398179a0874c4aa669aa79b63a79e76ee8ea0d61b98315`, size `483` bytes. It contains only the empty Go module/vendor closure and no upstream source.
3. The declared verifier bundle exists and matches `sha256:604232821a49e36935897ed525251a7b0109d2a28e9627e7d54473c9a79b9829`, size `1876` bytes. It is not an Oracle source payload.
4. The retained generated task and every retained task-local `go-version` source/evidence tree contain `solution/solve.sh` but no `source.tar` or `oracle-package` matching the frozen source digest.
5. The local Go module cache contains `/root/go/pkg/mod/cache/download/github.com/hashicorp/go-version/@v/v1.6.0.zip`, digest `sha256:bf1d96bda50abf5e2d111bf99d220d978314907d815fd58f4bd4770dc7959b9e`, size `19227` bytes. It is a Go module zip for v1.6.0, not the required git-archive tar for revision `e2b1b0b0c4b32767e1570ddce50dff79fdddf092`, and is therefore not an equivalent replacement.
6. Historical authoring session records show the previous Oracle result validated `/tmp/go-version-source.tar` only during the original network-enabled authoring run; that temporary file and its run tree are not retained as a hash-verifiable local payload.

## Failure Classification

`artifact-or-verifier-blocked`: the trusted Oracle requires a frozen source archive that is not present in the current private CAS, Oracle bundle, retained runs, historical task-local handoffs, or local Go cache. Running the current Oracle would require forbidden runtime GitHub access, so no compile, Oracle, control, or receipt refresh was attempted. Existing `production-evidence.json` and lifecycle status are preserved unchanged.

## Next Step

Parent should locate or register a private bundle containing the exact git-archive tar for revision `e2b1b0b0c4b32767e1570ddce50dff79fdddf092` with digest `sha256:e79a0e175c9821ee538e9ca25a504bb15b4f445f8781a3208c4f7704c5448c12`, then update the Oracle binding and rerun two deterministic compiles, the full NoNetwork Oracle/control matrix, and all evidence/path validation. Do not substitute the v1.6.0 module zip or authorize GitHub during revalidation.
