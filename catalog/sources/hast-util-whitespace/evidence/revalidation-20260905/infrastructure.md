# Revalidation Infrastructure Blocker

- Task: `hast-util-whitespace`
- Source revision: `22b88c3f4d51f3777929758e980c257a2838a4b2`
- Current queue/source digest: `sha256:66fc7e9df78fc3916e35892a0f9651976b398fb9c7e8417a49dd8ba7f01317e3`
- Instruction digest: `sha256:557bcbb55b00fbc8027164ae530d64e8da20bc7739ff31d772716bf582803ec1`
- Frozen denominator: `24`
- Required policy: NoNetwork for Agent, candidate, verifier, Oracle, and controls.

## Local Recovery

The declared npm dependency bundle, command bundle, test bundle, and Oracle bundle
were found in the authorized local CAS with exact size and SHA-256 verification:

| artifact | size | digest |
| --- | ---: | --- |
| npm dependencies | 475 | `sha256:2709f7f061b612e134913f158f1fae41e6f5872bfdd887454e599ad4fed17232` |
| commands | 206 | `sha256:87f9b085c4130b18155b4a202e67376324866cce37c516ebd668ef44c8e25898` |
| tests | 1493 | `sha256:baa80dde0c7030b7b0258ef7649e614f9ed5043c967142eb9a49fb994f917596` |
| Oracle | 5930 | `sha256:abcadf37573c3a374fed8ae05497ed84c1d294a6893ba34effa140eca43a74c0` |

The Oracle tar inventory was checked offline: `solve.sh` is 898 bytes and
`source.tar` is 30,720 bytes with digest
`sha256:d012e1fee404e631ad5a5b5aa3f338b413417e73f80b53d5d0c0e7a469f8e1be`.
No replacement payload was needed or proposed.

## Commands and Results

1. `uv run nl2repo task validate-source catalog/sources/hast-util-whitespace`
   exited `0`; queue digest matched the validated source digest.
2. Two locked compiles with `--allow-private` and no `--allow-incomplete` each
   exited `0`; both produced 78 files and identical bytes. Canonical manifest:
   `sha256:f007ec8efdd1d848a5c89b89edb8634d36b8d94a82f99e8f7adb75acbe9c610e`.
3. `uv run --frozen --project harbor-runner harbor run -p <compiled-bundle>
   -a oracle --job-name hast-util-whitespace-revalidation-oracle-20260905
   --n-concurrent 1 --yes` exited `1` before execution with:
   `Docker daemon is not running. Please start Docker and try again.`
4. One bounded retry of the same NoNetwork Oracle command exited `1` with the
   same error. `docker info` was recorded and no daemon restart or Docker prune
   was performed.

## Remediation

Failure class: `infrastructure`. Oracle, verifier, and all controls are pending;
no grading, network, collection, reward, or leaf failure is claimed. Next step:
repair the Harbor/Docker daemon-state integration, then rerun Oracle and the full
control matrix against a newly compiled bundle without reusing prior receipts.
