# Source Freeze

- Upstream: `https://github.com/rr-/docstring_parser`
- Revision: `8347d8fb347bd66e4bf5711d3df586357166944a`
- Commit subject: `fix: parse PEP 604 union simple types (int | str) in Google-style returns (#112)`
- Commit tree: `f3132c0190969673397361cb9665ff21e801b514`
- Archive: `git archive --format=tar 8347d8fb347bd66e4bf5711d3df586357166944a`
- Archive SHA-256: `sha256:2cb59707c20099e0f8b61ab9eeb6faeb7fea370a03b3468c822f84c0ac21f3e9`
- Archive size: `225280` bytes
- License: MIT, `LICENSE.md` SHA-256
  `sha256:dfe514a337ae8417abd31a8af707bbd6172b03e5430bb083e145899ea97a3eea`

The detached checkout and archive were created under the task-local `.work`
directory. No branch, tag, or remote `HEAD` was used. The source package
declares version `0.18.0`, requires Python `>=3.8`, uses Hatchling, and has no
runtime dependencies.

The selected contract is a deterministic parse/compose slice of the frozen
revision. Stateful parser objects, source inspection, decorators, regular
expression match objects, and direct-import upstream pytest files are outside
this separate-verifier contract and are not hidden requirements.
