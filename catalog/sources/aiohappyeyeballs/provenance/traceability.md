# Public Contract Traceability

The private verifier has a fixed 17-leaf JSON protocol. Candidate code is only
imported in bounded UID 10001 child processes. A trusted root-owned verifier
compares child observations and writes collection, JUnit, grading, and reward
artifacts.

| Public contract area | Instruction section | Deterministic coverage |
| --- | --- | --- |
| Distribution and exports | Supports; Root exports | distribution name/version, root export order, typed package marker |
| Address conversion | `addr_to_addr_infos` | `None`, IPv4, IPv6, IPv6 flow/scope defaults and preservation |
| Interleave mutation | Address-list mutation helpers | default and explicit per-family removal with stable retained order |
| Address removal | Address-list mutation helpers | exact match, normalized IPv6 spelling, mutation, absent-address error |
| Empty connections | `start_connection` | documented `ValueError` for no addresses |
| Sequential connection | `start_connection` | verifier-owned loopback TCP success and sequential fallback after a refused local port |
| Happy Eyeballs behavior | `start_connection` | delayed race reaches a later viable local address without external networking |
| Local bind and factory | `start_connection` | same-family ephemeral local bind and supplied socket-factory invocation |

The 66-leaf upstream suite is retained only as frozen source/environment
evidence. It is not copied into the task or used as the production denominator.
