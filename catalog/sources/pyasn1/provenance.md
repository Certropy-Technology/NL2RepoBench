# pyasn1 provenance

The source is the immutable Git revision `8003397013f6c0e0eabbd2605770477acbc2dc44`
from `https://github.com/pyasn1/pyasn1`. Its Git tree is
`209111189438390eb90c999488be48ab5e32cbb5`; the exported source archive and BSD-2-Clause
license bytes are recorded in `evidence/source-freeze.txt`.

The package is pure Python and declares no third-party runtime dependency. The candidate
build uses a hash-locked setuptools requirement. Hidden behavior is executed by a separate
trusted verifier, which launches a bounded UID-10001 child process and communicates only
through one JSON result line per scenario. The full verifier and Oracle bytes remain private
artifact bundles; only their digest, size, and handoff path are recorded in production evidence.
