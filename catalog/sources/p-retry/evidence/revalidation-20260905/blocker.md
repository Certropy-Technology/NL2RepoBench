# p-retry revalidation blocker

Classification: `artifact-or-verifier-blocked`.

The source digest was validated before this evidence directory was created:
`sha256:74d4571907395aa0a316f47a888a4b200b2570802e527ef4bb84ed91b5022856`.
The frozen archive is 81,920 bytes with digest
`sha256:3eabac5b48586a9a65714ad4cc4685a03705e3adcf3ee57d7ce9dabf5beb8278`.
The trusted local recovery scan checked 47,217 files and seven size-matching
candidates, but found zero digest matches.

The declared npm, commands, tests, and Oracle artifacts were independently
verified by exact size and SHA-256 (4/4); they are not sufficient to run the
Oracle because `solve.sh` performs runtime Git acquisition from `github.com`.
All current Oracle and controls are therefore skipped under NoNetwork. This is
not a candidate/model result and does not change lifecycle or production
evidence.

Next unblock action: provide an exact digest-matching frozen source archive in
the parent-managed private CAS and a local, digest-bound Oracle payload, then
compile twice and rerun all required gates with Harbor 0.21.0.
