# mdast-util-phrasing instruction revalidation blocker

- Task: `mdast-util-phrasing` version `4.1.0`
- Queue source digest: `sha256:e185e030aa30018baae06d76bb82ebc16a608d602a00ecc84b26965ae893bd74`
- Frozen upstream revision: `67d563d643f75cf4fd26bc3121ddebb89e3a0a9c`
- Frozen source archive digest: `sha256:fe71915a39869c97b9a9132886ff511654b42d4109183853592b580db458650b`
- Failure class: `artifact`
- Status: revalidation blocked before Oracle and controls; existing lifecycle and production evidence preserved.

## Verified artifacts

All four declared private artifacts were found in the parent CAS and matched their declared size and SHA-256. The exact records are in `artifact-check.json`.

## Local recovery

The bounded offline search checked the current generated runtime and solution, task-local source/evidence, the exact current Oracle CAS bundle, retained authoring archives/runs/worktrees/handoffs/session artifacts, repository Git objects, and local package/module caches. No source archive or installable payload matched both the frozen revision and archive digest. Details are in `local-recovery-search.json`.

The current Oracle payload was inspected before any execution. Its archive contains only `package-lock.json` and `solve.sh`; the script performs `git fetch` from GitHub at runtime. That source acquisition path is forbidden by the task's NoNetwork policy, so no Oracle or control command was run and no host authorization was added.

## Safe compile

Two offline production compiles completed with `--allow-private`, `toolchain.node.lock.toml`, and the parent CAS. Both produced byte-identical 100-file bundles with canonical manifest digest `sha256:3ce33468f38a8460655307b34f1e65eb87545d8bd2a9afab9f34690e586429b3` and raw manifest SHA-256 `sha256:9e5519fad705d737061859b4a7c07baeac16c1e8c38dedb9b66d2359307adad5`. Outputs were kept under ignored `.nl2repo/revalidation-mdast-util-phrasing-a/` and `-b/`; the checked-in `catalog/tasks/mdast-util-phrasing` projection was not changed.

## Commands and results

```text
uv run nl2repo task validate-source catalog/sources/mdast-util-phrasing
exit 0; queue and validated source digest matched sha256:e185e030aa30018baae06d76bb82ebc16a608d602a00ecc84b26965ae893bd74

uv run nl2repo harbor compile catalog/sources/mdast-util-phrasing --output ignored local compile output A --toolchain toolchain.node.lock.toml --artifact-root parent-private-CAS --allow-private
exit 0; 100 files; canonical manifest sha256:3ce33468f38a8460655307b34f1e65eb87545d8bd2a9afab9f34690e586429b3

uv run nl2repo harbor compile catalog/sources/mdast-util-phrasing --output ignored local compile output B --toolchain toolchain.node.lock.toml --artifact-root parent-private-CAS --allow-private
exit 0; byte-identical to compile A
```

No Harbor Oracle or control command was run because the only Oracle source acquisition path requires forbidden network access and no exact local replacement exists. No generated projection, task metadata, lifecycle status, or historical production evidence was changed.

## Next step

The parent integrator must recover an exact source payload matching the frozen archive digest and revision, register a NoNetwork Oracle bundle in the shared CAS, then rerun double compile and the complete current-manifest Oracle/control matrix. Prior GitHub-authorized receipts must not be reused.
