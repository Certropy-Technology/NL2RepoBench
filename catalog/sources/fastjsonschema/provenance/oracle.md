# Oracle And Remediation Evidence

The release `0.3.1` production bundle at
`.nl2repo/authoring-work/compiled-r3-20260826/fastjsonschema` passed the
trusted Oracle run with `valid=true`, `collected=2899`, `passed=2899`, and
`reward=1.0`. The exact grading artifact is
`.nl2repo/authoring-work/r3-jobs/oracle/fastjsonschema-r3-oracle/fastjsonschema__Cp6gLHJ/verifier/grading.json`.

The Oracle command authorized only `github.com`, the hostname in the declared
upstream URL. Its output records `/tmp/fastjsonschema-source.tar: OK`, proving
the fetched revision archive matched the source digest. The separate verifier
network probe recorded both `1.1.1.1:443` and `pypi.org:443` unavailable.

Remediation added Git to the agent image, froze meta-schemas and localhost
remote fixtures, isolated candidate imports in a UID 10001 JSONL child, and
made a timed-out or exited child produce a bounded complete failed collection.
The public catalog contains no verifier or hidden-test bytes, and no wheelhouse
is vendored. Private bundle and hash-locked dependency refs are declared in
`task.toml` and materialized only during compilation. The preceding release
0.3.0 Oracle receipt collected only 2,898 leaves and is superseded: it omitted
the declared `public-api-surface` leaf. No model Agent Run was started by this
lane.
