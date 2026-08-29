# Test Inventory

The frozen upstream checkout has 17 `*Spec.js` files and 101 local node:test
leaves when the non-network unit files are built and run. Three leaves are
upstream TODOs. Connectivity, upload, download, implicit TLS, and ProFTPD
integration files require a live FTP server or container and are excluded from
the no-network production denominator.

The production denominator is 47 unique leaves in the private
`contract.test.mjs` bundle. Every leaf calls the candidate through a separate
UID-isolated Node child and is mapped to the public instruction as follows:

| Leaf group | Count | Instruction section |
| --- | ---: | --- |
| root exports, `FileInfo`, `FileType` | 7 | Root exports and `FileInfo` |
| control response parsing and code predicates | 7 | Control responses |
| MLSD, Unix, DOS listing parsing | 13 | `parseList(rawList)` |
| PASV/EPSV parsing | 6 | Passive-mode response parsing |
| MLSx UTC date conversion | 2 | `parseList(rawList)` |
| `StringWriter` | 4 | `StringWriter` |
| `Client` initial state | 3 | `Client` initial state |
| additional order/metadata/regression cases | 5 | `parseList` and control responses |
| **Frozen total** | **47** | `node-test-leaf-pass-rate-v1` |

Collection is performed by the generic Node subprocess runner. A collection
mismatch is invalid; skipped and TODO statuses are represented explicitly by
the report normalizer and are not silently treated as passed.
