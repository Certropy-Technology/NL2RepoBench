# Freeze Audit

- Upstream: `https://github.com/sindresorhus/get-stream`
- Revision: `cdbd77bebf332f28a2949613fc1534d8a7a04c95`
- Raw `git archive --format=tar` SHA-256: `85c68c24e1216863eb41e79754b10b50dcdbf94137b2f0b7821f802fd7ec2a06`
- License: MIT; frozen `license` file SHA-256 `5c932d88256b4ab958f64a856fa48e8bd1f55bc1d96b8149c65689e0c61789d3`
- Package: `get-stream@9.0.1`, ESM, Node `>=18`
- Source tree: 40 tracked files; public source modules are listed in `api-inventory.json`
- Baseline command: `npm test`, exit code 0, 189 passed on Node `22.23.1` / npm `10.9.8`
- Production runtime: Node `24.19.0`, npm `11.17.0`, Debian Bookworm amd64 glibc
- Runtime dependencies: `@sec-ant/readable-stream@0.6.1`, `is-stream@4.0.1`; no native addons
- Run policy: agent and verifier `no-network`; only Oracle may fetch the exact source host

The original repository carries `package-lock=false`; the task-local candidate
closure was regenerated with npm 11.17.0 as a lockfile v3 using only production
dependencies and `--ignore-scripts`. The closure manifest and cache are checked
by the Node compiler before they enter the generated bundle.
