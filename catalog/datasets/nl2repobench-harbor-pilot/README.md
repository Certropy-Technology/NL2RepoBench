# NL2RepoBench Harbor Pilot

This dataset source names the development pilot tasks that have a catalog
source and a hand-reviewed Harbor task under `catalog/tasks/<task-id>/harbor/`.

It is a development dataset, not a published benchmark release. A task can
remain blocked until its upstream revision, license evidence, dependency
closure, frozen collection count, Oracle controls, and verifier review are
complete.

Current pilot inventory: 37 active catalog tasks and 13 blocked candidates.
The active list is authoritative in `dataset.toml`; blocked candidates remain
in the catalog for repair and audit, but are excluded from model scoring.

Run outputs are stored outside task directories under `.nl2repo/runs/` and are
not part of this dataset source.
