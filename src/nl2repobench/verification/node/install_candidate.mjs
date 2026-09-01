import { readdirSync, statSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";

const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const source = value("--source");
const target = value("--target");
const cache = value("--cache");
if (!source || !target || !cache) process.exit(64);

function run(command, commandArgs, cwd) {
  const result = spawnSync(command, commandArgs, {
    cwd,
    env: {
      PATH: "/usr/bin:/bin",
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

const NODE_ROOT = "/opt/nl2repobench-node";
const NODE = `${NODE_ROOT}/bin/node`;
const NPM = `${NODE_ROOT}/lib/npm/bin/npm-cli.js`;
run(NODE, [NPM, "ci", "--offline", "--ignore-scripts", "--no-audit", "--no-fund", `--cache=${cache}`], source);
run(NODE, [NPM, "pack", "--ignore-scripts", "--pack-destination", target], source);
const tarballs = readdirSync(target).filter((name) => name.endsWith(".tgz"));
if (tarballs.length !== 1) process.exit(71);
run(NODE, ["/tests/runtime/node/validate-package.mjs", join(target, tarballs[0])], target);
run(NODE, [NPM, "install", join(target, tarballs[0]), "--offline", "--ignore-scripts", "--no-audit", "--no-fund", `--cache=${cache}`, "--prefix", target], source);
// npm installs the packed dependency tree but may not create a package root
// descriptor for an empty prefix. Keep the resolver's cwd contract explicit
// without giving the candidate site the candidate's self-referencing name.
const targetPackage = join(target, "package.json");
try {
  statSync(targetPackage);
} catch {
  writeFileSync(
    targetPackage,
    JSON.stringify({ private: true, type: "module" }) + "\n",
    { mode: 0o444 },
  );
}
try {
  for (const name of readdirSync(target)) statSync(join(target, name));
} catch {
  process.exit(71);
}
