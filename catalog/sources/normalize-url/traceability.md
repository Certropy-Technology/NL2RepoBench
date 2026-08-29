# `normalize-url` Traceability

The frozen upstream suite has 33 AVA top-level tests plus a TypeScript declaration
probe. The private verifier freezes 45 `node:test` leaves. Each leaf invokes the
installed candidate through a UID-separated JSON child and the trusted test process
never imports candidate JavaScript.

| Contract area | Private coverage |
| --- | ---: |
| ESM package identity, export map, script-free install shape | 1 |
| Default protocol, trimming, casing, host and IDN normalization | 5 |
| Protocol-relative, custom protocol, forcing, stripping, host and IDN behavior | 15 |
| Authentication, WWW, ports and path normalization | 9 |
| Query removal, keeping, sorting and empty-value modes | 9 |
| Hash/text fragments, data URLs and path removal | 7 |
| Invalid input and deterministic repeated calls | 4 |
| **Total** | **45** |

The source's callback-valued `transformPath` option and RegExp-valued filters are
documented as excluded from the JSON boundary. `customProtocols` is covered as a
JSON-compatible string array. No leaf relies on a live network,
filesystem, clock, random value, native addon, loader, or mutable process state.
