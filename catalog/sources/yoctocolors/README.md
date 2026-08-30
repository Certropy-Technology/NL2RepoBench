# yoctocolors Harbor source

This declarative source asks an agent to build the dependency-free
`yoctocolors` 2.2.0 ESM package from an empty workspace. The public contract is
in `instruction.md`; private tests and the trusted Oracle are content-addressed
artifacts and are not present in the agent image.

The production compiler uses the digest-pinned Node 24.19.0 Debian image, npm
11.17.0, an empty npm v3 cache closure, a separate no-network verifier, and an
80-leaf fixed-denominator metric. Candidate calls run in bounded UID 10001
children under explicit forced-color modes.

Source-local controls cover empty workspace, identity stubs, verifier-output
forgery, lifecycle scripts, loader environment stripping, call hangs, and
offline network attempts. Generated Harbor output must be produced with
`nl2repo harbor compile`; do not edit `catalog/tasks/yoctocolors` manually.
