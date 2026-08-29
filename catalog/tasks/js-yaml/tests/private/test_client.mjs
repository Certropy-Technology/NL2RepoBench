import { readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const site = process.env.NODE_CANDIDATE_SITE;
const runner = process.env.NODE_TEST_RUNNER ?? "/tests/runtime/node/candidate_runner.mjs";

export function call(exportName, ...args) {
  const result = spawnSync(process.execPath, ["--no-addons", runner], {
    cwd: site,
    env: {
      PATH: "/usr/local/bin:/usr/bin:/bin",
      HOME: `${site}/.home`,
      TMPDIR: `${site}/.tmp`,
      NODE_CANDIDATE_SITE: site,
      NODE_ALLOWED_PACKAGE: "js-yaml",
      NODE_TEST_CLIENT: fileURLToPath(import.meta.url),
    },
    input: `${JSON.stringify({ package: "js-yaml", export: exportName, args })}\n`,
    encoding: "utf8",
    timeout: 60_000,
    maxBuffer: 256 * 1024,
  });
  const line = (result.stdout ?? "").trim().split(/\r?\n/).at(-1) ?? "";
  try {
    return JSON.parse(line);
  } catch {
    return {
      ok: false,
      error: "malformed-test-client-response",
      message: `${result.stderr ?? ""}`.slice(0, 2048),
    };
  }
}

export function value(exportName, ...args) {
  const response = call(exportName, ...args);
  if (!response.ok) {
    throw new Error(`${response.exception_type ?? response.error}: ${response.message ?? ""}`);
  }
  return response.value;
}

export function packageJson() {
  return JSON.parse(readFileSync(`${site}/node_modules/js-yaml/package.json`, "utf8"));
}

export function packageLock() {
  return JSON.parse(readFileSync(`${site}/package-lock.json`, "utf8"));
}
