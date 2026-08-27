# Control Evidence

All commands used the production-compiled `dataclasses-json` verifier image
with `--network none`. The trusted verifier wrote each `grading.json` under
`.nl2repo/evidence/controls-direct/`.

| Control | Result | Evidence |
| --- | --- | --- |
| Empty workspace | `valid=true`, reward `0.0`, candidate install failed | `empty-logs/grading.json` |
| Packaging-only stub | `valid=true`, `0/24` passed, reward `0.0` | `stub-logs/grading.json` |
| Forged reward file | `valid=true`, `0/24` passed, reward `0.0` | `forgery-logs/grading.json` |
| Install timeout | `valid=true`, reward `0.0`; trusted status `outcome=timeout`, return code `-9` | `install-hang-logs/grading.json`, `candidate-install.json` |

The forgery control writes candidate-controlled `/workspace/reward.json` and
`/logs/verifier/reward.json` before grading. The final reward remains the
trusted verifier's `0.0`, proving that candidate-provided reward bytes do not
alter grading. The call-timeout control was compiled and syntax-checked but was
not run because its valid task budget is 300 seconds; the installation-timeout
control already exercised the trusted timeout supervisor with a bounded 90
second budget.
