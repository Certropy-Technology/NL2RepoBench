# `go-docker-volume-backup` authoring audit - blocked

**Status: blocked / audit-only.** This source records the frozen upstream
candidate and the evidence preventing a faithful Harbor task. It is not a
generated task, hidden-test package, Oracle, verifier, dependency bundle, or
approval to emulate Docker or cloud services.

## Candidate Lock

- Package: `docker-volume-backup`.
- Upstream: `https://github.com/offen/docker-volume-backup`.
- Revision: `bd50ba96c439e6003b982cf6b371278eff946669`.
- Commit subject: `Bump google.golang.org/api from 0.293.0 to 0.295.0 (#845)`.
- Commit date: `2026-09-01T07:49:55+02:00`.
- License: MPL-2.0.
- Git archive: 1,003,520 bytes, SHA-256
  `4eac23163d7de803af9f610fb7adb80fdcf9aca885cf57659a2b8ea461a852e0`.
- LICENSE: 1,757 bytes, Git blob
  `a612ad9813b006ce81d1ee438dd784da99a54007`, SHA-256
  `1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5`.
- The archive contains 184 tracked paths and 31 Go source files.

## Project Boundary

This is a Docker companion CLI, not a self-contained Go library. It backs up
mounted Docker volumes to local storage, S3, WebDAV, Azure Blob Storage,
Dropbox, Google Drive, or SSH; it can compress and encrypt archives, prune
old backups, stop/restart labeled containers, execute hooks, schedule cron
runs, and send notifications.

The primary command is `cmd/backup`, with a `print-config` subcommand and a
foreground scheduler. Configuration is primarily environment-driven. The
internal storage backends are not exported API packages and their behavior is
coupled to files, credentials, network services, and long-running processes.

## Runtime And Dependency Blockers

The exact `go.mod` declares `go 1.27` and `toolchain go1.27.0`. The locked Go
Harbor lane currently provides Go `1.26.5`; with `GOTOOLCHAIN=local` the
source does not collect or compile:

```text
go: go.mod requires go >= 1.27 (running go 1.26.5; GOTOOLCHAIN=local)
```

The module closure has 27 direct and many indirect dependencies, including
Docker client APIs, AWS-compatible S3, Azure, Dropbox, Google Drive, WebDAV,
SSH/SFTP, encryption, compression, cron, and notification libraries. No
private module bundle was frozen for this revision, and the current lane does
not provide a production Go 1.27 image.

## Official Test Boundary

The upstream tree has only two Go unit-test files and 31 executable integration
scenario scripts under `test/`. The test harness builds a Docker image and
runs each scenario in an isolated Docker environment containing another
Docker daemon. Scenarios use Docker Compose, Docker socket access, Docker
Swarm (including multinode mode), named volumes, image loading, MinIO, SSH,
GPG, age, SMTP/notification endpoints, and cloud-compatible storage services.
Several scenarios require networked service containers, credentials, host
filesystem mounts, or external binaries. The test harness therefore cannot
be collected as a positive fixed denominator in the current separate verifier.

## Adapter Assessment

The current typed Go bridge supports bounded JSON calls into a candidate
process. It does not provide a faithful contract for Docker daemon APIs,
Docker socket and Swarm lifecycle, nested Compose environments, mounted
volumes and mount metadata, cloud OAuth/credentials, SSH servers, GPG/age
executables, SMTP endpoints, cron scheduling, signal handling, or arbitrary
external hooks. A generic fake implementation would test the adapter rather
than this project's public behavior. Directly importing the candidate into a
trusted verifier would violate candidate isolation.

The candidate remains blocked until all of the following are approved and
frozen: a Go 1.27 production toolchain, complete hash-locked module closure,
an isolated child-side CLI/service fixture covering Docker and storage
backends, and a reviewed deterministic test collection with no real secrets or
unfrozen external services.

## Remediation

1. Freeze a Go 1.27 linux/amd64 image and the complete module closure for this
   revision.
2. Decide whether a task-specific child-side adapter can faithfully model the
   Docker daemon, volume/mount, scheduler, encryption, notification, and
   storage contracts without exposing host or network capabilities.
3. If approved, replace the integration shell corpus with a deterministic
   verifier-owned collection whose denominator is collected in the target
   image; otherwise retain this candidate as blocked.

No `catalog/tasks/go-docker-volume-backup/` projection is present.
