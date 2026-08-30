# `strnum` Harbor source

This canonical source defines an offline Node/npm reconstruction task for
`strnum@2.4.2` at revision
`117d6a5f59fbb8f29d2f88c0c292d7dc44d67a7f`.

- Public behavior: [instruction.md](instruction.md)
- API/source inventory: [api-inventory.json](api-inventory.json)
- Frozen test denominator: [test-inventory.json](test-inventory.json)
- Candidate isolation: [candidate-boundary.json](candidate-boundary.json)
- Public/private mapping: [traceability.md](traceability.md)
- Freeze and environment record: [provenance.md](provenance.md)

Private npm, test, and Oracle bytes are content-addressed under `.nl2repo` and
are referenced by `task.toml`. `catalog/tasks/strnum` is compiler output and is
not edited by this source lane.
