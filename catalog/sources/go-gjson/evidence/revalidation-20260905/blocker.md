# go-gjson instruction revalidation blocker

The expected migrated catalog digest is `sha256:4fa887067e300b0d87108f905ff1fe6a6f62f689ad61ab828335a295a6d3b752`.
Source validation and instruction quality passed. The frozen upstream is revision
`7d8b3821e9d2acf35e8a226b63fcf801078e9b96` with archive digest
`sha256:91ec8257d29e04f0b67cac8641197ddb86d975138a8588d128bf4f27b447692a`.

The three declared private CAS objects were present and size/hash valid. Two locked
production compiles were byte-identical: 90 files, raw manifest
`sha256:598a4e4a7b4708275bde299f9262b69905b8c223bc89a8f32709458d215fdb9f`, and
canonical manifest `sha256:ecea2b4601fee0153f7c9ca6ff50b395970adc005528845251ddb138ad2b425c`.

The current Oracle bundle contains `solve.sh` and the private module closure but no
source archive. `solve.sh` performs runtime `git fetch` and `git archive` from the
upstream host. Local recovery checked the current Oracle bundle, historical generated
`go-gjson` solution directories, task-specific authoring sessions, run roots, and
preserved authoring archives. Fifty-three generated solution directories were checked;
none contained `source.tar`, and no matching revision payload was found. No replacement
bundle can therefore be proposed without introducing unverified bytes.

Oracle and controls were not run. Authorizing the source host or reusing historical
receipts would violate the task's NoNetwork policy. The parent should obtain or restore
a hash-verifiable private source payload, update the Oracle artifact reference, compile
twice, and run fresh Oracle, empty, stub, forgery, and offline-compatible controls.
