import { readdirSync, statSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const source = value("--source");
const target = value("--target");
const cache = value("--cache");
if (!source || !target || !cache) process.exit(64);

function run(command, commandArgs, cwd) {
  const result = spawnSync("/usr/bin/timeout", [
    "--kill-after=5s",
    "90s",
    "/usr/bin/prlimit",
    "--cpu=90",
    "--nproc=32",
    "--nofile=128",
    "--",
    command,
    ...commandArgs,
  ], {
    cwd,
    env: {
      PATH: "/usr/local/bin:/usr/bin:/bin",
      HOME: join(target, "home"),
      TMPDIR: join(target, "tmp"),
      npm_config_cache: cache,
      npm_config_offline: "true",
      npm_config_ignore_scripts: "true",
      npm_config_audit: "false",
      npm_config_fund: "false",
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

run("/usr/local/bin/npm", ["ci", "--offline", "--ignore-scripts", "--no-audit", "--no-fund", `--cache=${cache}`], source);
run("/usr/local/bin/npm", ["pack", "--ignore-scripts", "--pack-destination", target], source);
const tarballs = readdirSync(target).filter((name) => name.endsWith(".tgz"));
if (tarballs.length !== 1) process.exit(71);
run("/usr/local/bin/node", ["/tests/runtime/node/validate-package.mjs", join(target, tarballs[0])], target);
run("/usr/local/bin/npm", ["install", join(target, tarballs[0]), "--offline", "--ignore-scripts", "--no-audit", "--no-fund", `--cache=${cache}`, "--prefix", target], source);
// npm installs the packed dependency tree but may not create a package root
// descriptor for an empty prefix. Keep the resolver's cwd contract explicit.
const sourcePackage = join(source, "package.json");
const targetPackage = join(target, "package.json");
try {
  statSync(targetPackage);
} catch {
  const { copyFileSync } = await import("node:fs");
  copyFileSync(sourcePackage, targetPackage);
}
try {
  for (const name of readdirSync(target)) statSync(join(target, name));
} catch {
  process.exit(71);
}
