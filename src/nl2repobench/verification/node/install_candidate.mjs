import { mkdtempSync, readdirSync, statSync } from "node:fs";
import { randomBytes } from "node:crypto";
import { dirname, relative, resolve } from "node:path";
import { spawnSync } from "node:child_process";

// All candidate commands use the reviewed generic supervisor transport. This
// compatibility entry point is retained for old task bundles only.
const ROOT = "/opt/nl2repobench-node";
const NODE = `${ROOT}/bin/node`;
const NPM = `${ROOT}/lib/npm/bin/npm-cli.js`;
const PYTHON = "/usr/local/bin/python3";
const RUNTIME = "/opt/nl2repobench-runtime";
const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const source = value("--source");
const target = value("--target");
const cache = value("--cache");
if (!source || !target || !cache) process.exit(64);

function commonRoot(paths) {
  let root = resolve(paths[0]);
  for (const item of paths.slice(1)) {
    const candidate = resolve(item);
    while (candidate !== root && !candidate.startsWith(`${root}/`)) root = dirname(root);
  }
  return root;
}

function run(command, cwd, writeRoot) {
  const root = commonRoot([cwd, writeRoot]);
  const id = randomBytes(16).toString("hex");
  const environment = {
    HOME: `${resolve(writeRoot)}/home`,
    TMPDIR: `${resolve(writeRoot)}/tmp`,
    npm_config_cache: resolve(cache),
    npm_config_ignore_scripts: "true",
    npm_config_offline: "true",
    npm_config_audit: "false",
    npm_config_fund: "false",
  };
  const body = {
    schema_version: "1.0", request_id: id, context: "install",
    command: {
      argv: command, cwd: relative(root, resolve(cwd)) || ".",
      environment: Object.entries(environment).sort(([a], [b]) => a.localeCompare(b)),
    },
    limits: { timeout_sec: 90, cpu_sec: 90, max_stdin_bytes: 1048576,
      max_output_bytes: 8388608, max_file_bytes: 536870912, max_open_files: 256,
      uid: 10001, gid: 10001, max_processes: 64 },
    policy: { task_id: "node-npm-install", staging_root: root,
      read_only_roots: [ROOT], write_root: resolve(writeRoot),
      allowed_executable_roots: [`${ROOT}/bin`],
      allowed_environment_names: Object.keys(environment).sort(),
      require_no_new_privs: true, require_empty_capabilities: true },
    stdin_base64: "",
  };
  const bootstrap = `import sys;sys.path.insert(0,${JSON.stringify(RUNTIME)});from nl2repobench.verification.candidate_process_cli import main;raise SystemExit(main())`;
  const transport = spawnSync(PYTHON, ["-I", "-c", bootstrap], {
    cwd: resolve(cwd), input: JSON.stringify(body), encoding: "utf8",
    env: { PATH: "/usr/local/bin:/usr/bin:/bin", HOME: "/nonexistent" },
    timeout: 100000, maxBuffer: 8 * 1024 * 1024,
  });
  if (transport.error || transport.status !== 0) process.exit(70);
  let result;
  try { result = JSON.parse(transport.stdout); } catch { process.exit(70); }
  if (result.request_id !== id || result.cleanup_complete !== true ||
      result.spawn_error !== null || result.cleanup_error !== null) process.exit(70);
  if (result.timed_out || result.output_limit_exceeded || result.returncode !== 0) process.exit(71);
}

const pack = mkdtempSync("/tmp/node-pack-");
run([NODE, NPM, "ci", "--offline", "--ignore-scripts", "--no-audit", "--no-fund", `--cache=${cache}`], source, source);
run([NODE, NPM, "pack", "--ignore-scripts", "--pack-destination", pack], source, pack);
const tarballs = readdirSync(pack).filter((name) => name.endsWith(".tgz"));
if (tarballs.length !== 1 || !statSync(`${pack}/${tarballs[0]}`).isFile()) process.exit(71);
run([NODE, "/tests/runtime/node/validate-package.mjs", `${pack}/${tarballs[0]}`], pack, pack);
run([NODE, NPM, "install", `${pack}/${tarballs[0]}`, "--offline", "--ignore-scripts", "--no-audit", "--no-fund", `--cache=${cache}`, "--prefix", resolve(target)], source, target);
process.exit(0);
