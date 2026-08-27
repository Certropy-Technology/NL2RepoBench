import { readdirSync, statSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const source = value("--source");
const target = value("--target");
const store = value("--store");
if (!source || !target || !store) process.exit(64);

function run(command, commandArgs, cwd) {
  const result = spawnSync("/usr/bin/timeout", [
    "--kill-after=5s", "90s", "/usr/bin/prlimit", "--cpu=90", "--nproc=32",
    "--nofile=128", "--", command, ...commandArgs,
  ], {
    cwd,
    env: {
      PATH: "/usr/local/bin:/usr/bin:/bin",
      HOME: join(target, "home"),
      TMPDIR: join(target, "tmp"),
      COREPACK_ENABLE_PROJECT_SPEC: "0",
      npm_config_ignore_scripts: "true",
      npm_config_registry: "https://registry.invalid",
      npm_config_auto_install_peers: "false",
      npm_config_exclude_links_from_lockfile: "false",
    },
    encoding: "utf8",
    timeout: 90_000,
    maxBuffer: 256 * 1024,
  });
  if (result.error || result.status !== 0) {
    process.stderr.write(`${command} failed\n${result.stderr ?? result.error}\n`);
    process.exit(71);
  }
}

run("/usr/local/bin/pnpm", [
  "install", "--offline", "--frozen-lockfile", "--ignore-scripts", `--store-dir=${store}`,
], source);
run("/usr/local/bin/pnpm", ["pack", "--pack-destination", target], source);
const tarballs = readdirSync(target).filter((name) => name.endsWith(".tgz"));
if (tarballs.length !== 1) process.exit(71);
run("/usr/local/bin/node", ["/tests/runtime/node/validate-package.mjs", join(target, tarballs[0])], target);
run("/usr/local/bin/pnpm", [
  "install", join(target, tarballs[0]), "--offline", "--ignore-scripts",
  `--store-dir=${store}`, `--dir=${target}`,
], target);
try {
  statSync(join(target, "package.json"));
} catch {
  writeFileSync(join(target, "package.json"), JSON.stringify({ private: true, type: "module" }) + "\n", { mode: 0o444 });
}
