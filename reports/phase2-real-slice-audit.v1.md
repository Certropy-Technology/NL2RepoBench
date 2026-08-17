# Phase 2 Real-Task Slice Audit v1

Phase 2 requires one Easy, one Medium, and one Hard real task before claiming a
production vertical slice. The selected candidates are `autorccar`, `aiofiles`,
and `boltons`.

| Task | Difficulty | Tests | Immutable legacy image |
| --- | --- | ---: | --- |
| `autorccar` | Easy | 13 | `sha256:fe7beae3a278...` |
| `aiofiles` | Medium | 211 | `sha256:c2c5990b8280...` |
| `boltons` | Hard | 423 | `sha256:770deb94e716...` |

All three GHCR images exist for `linux/amd64` and can potentially become a
separate verifier base. They are not publishable tasks yet. Every candidate is
blocked on the same evidence:

1. immutable upstream revision and source digest;
2. license evidence;
3. Oracle/reference implementation bundle;
4. explicit hidden test bundle provenance rather than only an opaque legacy image;
5. frozen collection evidence replacing `test_case_count.txt`;
6. offline dependency lock.

The machine-readable evidence is in
[`phase2-real-slice-audit.v1.json`](phase2-real-slice-audit.v1.json). The image
digests were resolved with `docker manifest inspect -v`; instruction digests
were computed from the exact checked-in `start.md` bytes.

These tasks remain `blocked`, not failed and not published. Pulling an image or
making Harbor execute it would not recover source/license/Oracle provenance and
would not justify a parity claim.
