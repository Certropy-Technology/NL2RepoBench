# Oracle And Remediation Evidence

The generic private-bundle Harbor verifier passed one Oracle run:

- `valid=true`
- `collected=2898`, `expected=2898`, `passed=2898`
- `reward=1.0`
- evidence: `.nl2repo/runs/oracle/fastjsonschema-custom-compiled-current-v12/2026-08-24__09-25-39/fastjsonschema__AEnQqFq/verifier/grading.json`

Remediation included adding Git to the agent image, correcting a pytest
reserved parameter name, adding frozen meta-schemas and localhost remote
fixtures to the offline verifier, and making empty candidates fail all
contract cases instead of matching invalid cases by accident. Controls and
publication remain separate gates. No model run was started by the authoring
loop.

The public catalog contains no verifier/test bytes. The custom adapter,
suite, remotes, meta-schemas and dependency wheelhouse are addressed by the
private refs in `task.toml`; generic compilation materializes them only in the
separate verifier image.
