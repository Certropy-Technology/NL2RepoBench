# `process-warning` Authoring Provenance

## Source freeze

- Upstream: `https://github.com/fastify/process-warning`.
- Frozen revision: `d55637b341e21fef9dc7222590b36b14d030a839` (`5.1.0`, commit subject
  `docs(readme): grammar fixes (#146)`).
- Git tree: `d14791ab6d74c6976fa5272f822212752e50e313`.
- Raw `git archive --format=tar` SHA-256:
  `6ea9bf54d357fb67d7024510e082e37b59fea0516c32f3e0fdabc897fa9344a4`.
- License: MIT; root `LICENSE` SHA-256:
  `8d3c1dd501e056405ab56f4ad87b987070d55d1fe814616584ec2360045f9017`.
- Submodules: none.

The raw source archive and exact checkout are stored only under task-local authoring work.
The trusted Oracle solve script repeats the fetch, commit assertion, archive digest check, and
package adaptation. The model agent receives no source-host authorization.

## API and test inventory

The selected package has one implementation module and one declaration module, no runtime
dependencies, and the root CommonJS export object described in `api-inventory.json`. The
authoring host ran the selected nine `node:test` files under Node `22.23.1`: 24 leaves passed
and no tests failed. The Jest-only smoke file is excluded because the production task has a
zero-entry npm closure and does not expose Jest as runtime or verifier dependency.

The production denominator is a private 24-leaf `node:test` collection. It covers package
aliases, metadata, formatting, process warning argument delivery, once-only/unlimited state,
deprecation naming, validation errors, isolated configurations, formatting's truthy-prefix
rule, and the spy lifecycle's distinct argument trimming and return behavior. The exact mapping
is in `traceability.json`.

## Environment and dependency closure

- Production runtime: Node `24.19.0`, npm `11.17.0`, Debian bookworm, linux/amd64, glibc.
- Candidate dependency closure: no packages; a private npm v3 lock/cache bundle is still
  materialized so `npm ci --offline --ignore-scripts --no-audit --no-fund` is exercised.
- Candidate and separate verifier phases use `no-network`; source, registry, and provider hosts
  are absent from task metadata.

## Verifier boundary

The separate verifier runs private `node:test` files as root, while every candidate API request
is executed by `test_client.mjs` as UID 10001 under bounded `timeout`/`prlimit`. The child
adapter loads the installed candidate, replaces `process.emitWarning` only inside that child to
capture its arguments, and returns bounded JSON projections. Trusted tests never import
candidate code and candidate output cannot write trusted reports. The private directory remains
root-readable only; the shared compiler remediation grants UID 10001 traversal and execution of
only `test_client.mjs`, leaving test assertions and adapter source unreadable.

## Status

The final production bundle compiled deterministically with 81 files (80 declared members plus
the manifest). Harbor 0.21.0 Oracle passed 24/24 with reward 1.0 and verifier network probes
false. Official empty, stub, forgery, offline, install-script, call-hang, and loader-hook controls
all completed without trial exceptions; fixed-denominator controls scored 0/24, while empty and
install-script used the allowed candidate-installation-failed exception. An earlier Oracle probe
against a superseded bundle exposed a missing `checkout --detach FETCH_HEAD`; that script was
fixed, the Oracle artifact was rebound, and the successful evidence uses only the final bundle.

Review, model Agent Run, generated `catalog/tasks/` integration, and publication remain
integrator-stage gates. The local OpenHands base tag resolves to image ID
`sha256:bb48824b85940a3b6083ce0a1d713af6963ebf92bcba318dfc5838461a4081c3`, not the toolchain's
locked `sha256:c50b3e3c39e1802399d659604f0a4d478ee48997ec463bcf815fe3fdc9abc85f`;
the integrator must restore or explicitly relock that immutable image before a model Agent Run.
