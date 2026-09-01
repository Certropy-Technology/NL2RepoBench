import { spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, statSync } from "node:fs";
import { randomBytes } from "node:crypto";
import { dirname, relative, resolve } from "node:path";

const NODE_ROOT = "/opt/nl2repobench-node";
const NODE = `${NODE_ROOT}/bin/node`;
const PNPM = `${NODE_ROOT}/lib/pnpm/bin/pnpm.cjs`;
const PYTHON = "/usr/local/bin/python3";
const PYTHON_RUNTIME = "/opt/nl2repobench-runtime";
const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const source = value("--source");
const target = value("--target");
const store = value("--store");
if (!source || !target || !store) process.exit(64);

function commonRoot(paths) {
  let root = resolve(paths[0]);
  for (const item of paths.slice(1)) {
    const candidate = resolve(item);
    while (candidate !== root && !candidate.startsWith(`${root}/`)) root = dirname(root);
  }
  return root;
}

function supervisorRequest(command, cwd, writeRoot, environment) {
  const stagingRoot = commonRoot([cwd, writeRoot]);
  const requestId = randomBytes(16).toString("hex");
  const relativeCwd = relative(stagingRoot, resolve(cwd)) || ".";
  return {
    requestId,
    body: Buffer.from(JSON.stringify({
      schema_version: "1.0",
      request_id: requestId,
      context: "install",
      command: {
        argv: command,
        cwd: relativeCwd,
        environment: Object.entries(environment).sort(([left], [right]) => left.localeCompare(right)),
      },
      limits: {
        timeout_sec: 90,
        cpu_sec: 90,
        max_stdin_bytes: 1048576,
        max_output_bytes: 8388608,
        max_file_bytes: 536870912,
        max_open_files: 256,
        uid: 10001,
        gid: 10001,
        max_processes: 64,
      },
      policy: {
        task_id: "node-pnpm-install",
        staging_root: stagingRoot,
        read_only_roots: [NODE_ROOT],
        write_root: resolve(writeRoot),
        allowed_executable_roots: [`${NODE_ROOT}/bin`],
        allowed_environment_names: Object.keys(environment).sort(),
        require_no_new_privs: true,
        require_empty_capabilities: true,
      },
      stdin_base64: "",
    }), "utf8"),
  };
}

function run(command, cwd, writeRoot) {
  const environment = {
    HOME: `${resolve(writeRoot)}/home`,
    TMPDIR: `${resolve(writeRoot)}/tmp`,
    npm_config_cache: resolve(store),
    npm_config_ignore_scripts: "true",
    npm_config_offline: "true",
    npm_config_auto_install_peers: "false",
    npm_config_exclude_links_from_lockfile: "false",
  };
  const request = supervisorRequest(command, cwd, writeRoot, environment);
  const bootstrap = `import sys;sys.path.insert(0,${JSON.stringify(PYTHON_RUNTIME)});from nl2repobench.verification.candidate_process_cli import main;raise SystemExit(main())`;
  const completed = spawnSync(
    PYTHON,
    ["-I", "-c", bootstrap],
    { cwd: resolve(cwd), input: request.body, env: { PATH: "/usr/local/bin:/usr/bin:/bin", HOME: "/nonexistent" }, encoding: "utf8", timeout: 100000 },
  );
  if (completed.error || completed.status !== 0) {
    process.stderr.write(`${command[1]} supervisor transport failed\n${completed.stderr ?? completed.error}\n`);
    process.exit(70);
  }
  let result;
  try {
    result = JSON.parse(completed.stdout);
  } catch {
    process.stderr.write("malformed generic supervisor response\n");
    process.exit(70);
  }
  if (result.schema_version !== "1.0" || result.request_id !== request.requestId
      || result.cleanup_complete !== true || result.cleanup_error !== null
      || result.spawn_error !== null) process.exit(70);
  if (result.timed_out) process.exit(71);
  if (result.output_limit_exceeded) process.exit(71);
  if (result.returncode !== 0) {
    process.stderr.write(`${command[1]} failed\n`);
    process.exit(71);
  }
}

mkdirSync(target, { recursive: true, mode: 0o755 });
mkdirSync(store, { recursive: true, mode: 0o755 });
mkdirSync(`${resolve(target)}/home`, { recursive: true, mode: 0o700 });
mkdirSync(`${resolve(target)}/tmp`, { recursive: true, mode: 0o700 });
run([NODE, PNPM, "install", "--offline", "--frozen-lockfile", "--ignore-scripts", `--store-dir=${resolve(store)}`], source, target);
run([NODE, PNPM, "pack", "--pack-destination", resolve(target)], source, target);
const tarballs = readdirSync(target).filter((name) => name.endsWith(".tgz"));
if (tarballs.length !== 1 || !statSync(`${resolve(target)}/${tarballs[0]}`).isFile()) process.exit(71);
run([NODE, PNPM, "install", `${resolve(target)}/${tarballs[0]}`, "--offline", "--ignore-scripts", `--store-dir=${resolve(store)}`, `--dir=${resolve(target)}`], target, target);
