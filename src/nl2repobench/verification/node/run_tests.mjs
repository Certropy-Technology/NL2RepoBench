import { spawnSync } from "node:child_process";
import { readdirSync, writeFileSync } from "node:fs";
import { join, relative } from "node:path";

const MAX_REPORT_BYTES = 8 * 1024 * 1024;
const MAX_OUTPUT_BYTES = 8 * 1024 * 1024;
const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const testsRoot = value("--tests");
const candidate = value("--candidate");
const expected = Number(value("--expected"));
const output = value("--output");
if (!testsRoot || !candidate || !Number.isSafeInteger(expected) || expected < 1 || !output) {
  process.stderr.write("invalid fixed test runner arguments\n");
  process.exit(64);
}

function filesUnder(root) {
  const files = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) files.push(...filesUnder(path));
    else if (
      entry.isFile()
      && entry.name !== "test_client.mjs"
      && /\.(?:mjs|js|cjs)$/.test(entry.name)
    ) files.push(path);
  }
  return files.sort();
}

function parseTap(text, file) {
  const cases = [];
  const seen = new Map();
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^(ok|not ok)\s+(\d+)\s+-\s+(.*)$/);
    if (!match) continue;
    let name = match[3];
    let status = match[1] === "ok" ? "passed" : "failed";
    const marker = name.match(/\s+#\s+(SKIP|TODO)\b/i);
    if (marker) {
      status = marker[1].toLowerCase() === "skip" ? "skipped" : "todo";
      name = name.slice(0, marker.index).trim();
    }
    const base = name || `leaf-${match[2]}`;
    const occurrence = (seen.get(base) ?? 0) + 1;
    seen.set(base, occurrence);
    const suffix = occurrence === 1 ? "" : `#${occurrence}`;
    cases.push({ schema_version: "1.0", test_id: `${file}::${base}${suffix}`, status, duration_ms: 0 });
  }
  return cases;
}

const cases = [];
const collectionErrors = [];
let runnerExitCode = 0;
for (const file of filesUnder(testsRoot)) {
  const relativeFile = relative(testsRoot, file);
  const result = spawnSync(
    process.execPath,
    ["--no-addons", "--test", "--test-reporter=tap", file],
    {
      cwd: candidate,
      env: {
        ...process.env,
        NODE_CANDIDATE_SITE: candidate,
        NODE_TEST_CLIENT: process.env.NODE_TEST_CLIENT ?? join(testsRoot, "test_client.mjs"),
        NODE_PATH: undefined,
        NODE_OPTIONS: undefined,
      },
      encoding: "utf8",
      timeout: 120_000,
      maxBuffer: MAX_OUTPUT_BYTES,
    },
  );
  const fileCases = parseTap(result.stdout ?? "", relativeFile);
  cases.push(...fileCases);
  if (result.error || (!fileCases.length && (result.stderr ?? "").trim())) {
    collectionErrors.push({
      schema_version: "1.0",
      test_id: relativeFile,
      message: String(result.error?.message ?? result.stderr ?? "test file failed to load").slice(0, 4096),
    });
  }
  if (result.error) runnerExitCode = 70;
  else if (result.status !== 0 && runnerExitCode === 0) runnerExitCode = 1;
}
const report = {
  schema_version: "1.0",
  framework: "node:test",
  report_format: "node-test-json-v1",
  collected: cases.length,
  tests: cases,
  collection_errors: collectionErrors,
  runner_exit_code: runnerExitCode,
};
const encoded = JSON.stringify(report);
if (Buffer.byteLength(encoded) > MAX_REPORT_BYTES) {
  process.stderr.write("node report exceeds bound\n");
  process.exit(70);
}
writeFileSync(output, `${encoded}\n`, { encoding: "utf8", flag: "wx", mode: 0o400 });
process.exitCode = runnerExitCode === 70
  ? 70
  : runnerExitCode === 0 && cases.length === expected
    ? 0
    : 1;
