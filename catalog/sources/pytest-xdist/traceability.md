# Test-to-spec traceability

| Private leaf | Public contract | Ground-truth families |
| --- | --- | --- |
| packaging-surface | Supports, root exports and entry point | `testing/test_plugin.py`, `testing/test_newhooks.py` |
| parse-numprocesses | `parse_numprocesses` | `testing/test_plugin.py` |
| parse-ramp-valid | `parse_ramp_duration` valid units | `testing/test_plugin.py` |
| parse-ramp-invalid | `parse_ramp_duration` error contract | `testing/test_plugin.py` |
| worker-identity | Worker identity helpers | `testing/test_plugin.py`, `testing/test_remote.py` |
| local-fixtures | `worker_id` and `testrun_uid` | `testing/acceptance_test.py`, `testing/test_plugin.py` |
| distributed-pass | `-n1` popen execution | `testing/acceptance_test.py` |
| distributed-failure-skip | pytest-compatible failed/skipped status | `testing/acceptance_test.py` |
| distribution-modes | `each`, `load`, `loadscope`, `loadfile`, `loadgroup`, `worksteal` | `testing/acceptance_test.py`, scheduler tests |
| hook-data-exchange | configure/testnodedown worker data | `testing/acceptance_test.py` |
| collect-only | no distributed session during collection | `testing/test_plugin.py`, `testing/acceptance_test.py` |
| options-and-usage | options, max workers, pdb incompatibility | `testing/test_plugin.py` |
| no-network-runtime | offline deterministic behavior | all local families |

Every scored leaf is observable through a child process and has a unique
identifier. The verifier owns collection, JUnit, grading, and reward output.
