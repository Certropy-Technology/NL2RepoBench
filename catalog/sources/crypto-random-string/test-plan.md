# Frozen Test Plan

The private verifier contains one `node:test` file with 32 unique leaves. Each
leaf runs through `test_client.mjs`, which starts a bounded child as UID 10001;
the trusted test process never imports candidate code. Requests and responses
stay within the Node boundary limits.

| Behavior group | Leaves |
| --- | ---: |
| Package metadata and ESM default export | 2 |
| Default, base64, and predefined character sets | 8 |
| Custom Unicode sets, weighting, and zero-length behavior | 5 |
| Invalid options and generated alphabet boundaries | 9 |
| Large entropy, independent calls, and rejection distribution | 8 |
| **Frozen total** | **32** |

The runner derives collection from TAP leaf lines and fails closed if the
collected count differs from 32. The grader uses the verifier-owned structured
report and reward, not files written by the candidate workspace.
