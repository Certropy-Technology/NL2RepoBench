# Oracle And Remediation Evidence

The generic private-bundle Harbor verifier passed one Oracle run after
candidate-dependency isolation and child import-path fixes:

- `valid=true`
- `collected=24`, `expected=24`, `passed=24`
- `reward=1.0`
- evidence: `.nl2repo/runs/oracle/dataclasses-json-custom-compiled-current-v4/2026-08-24__09-06-20/dataclasses-json__QQknj2V/verifier/grading.json`

The fixes were to install a source directory without `--require-hashes`,
bypass Poetry dynamic versioning when the verifier has no Git checkout,
isolate candidate dependencies from the trusted verifier runtime, and insert
candidate/dependency paths before importing the candidate package. Controls
and publication remain separate gates. No model run was started by the
authoring loop.

The public catalog contains no verifier/test bytes. The custom adapter and
dependency/Oracle bundles are addressed by private refs in `task.toml`; the
generic compiler materializes them only in the separate verifier image.
