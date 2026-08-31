import { lstatSync, readFileSync } from "node:fs";

const args = process.argv.slice(2);
const path = args[args.indexOf("--path") + 1];
const expected = {
  identity: "node+npm",
  candidate_install: "npm-pack-offline-v1",
  report_format: "node-test-json-v1",
  runner: "node-test-subprocess-boundary-v1",
  schema_version: "1.0",
  test_root: "/tests/private",
};
if (!path) process.exit(64);
let payload;
try {
  const metadata = lstatSync(path);
  if (!metadata.isFile() || metadata.size > 4 * 1024 * 1024) process.exit(65);
  payload = JSON.parse(readFileSync(path, "utf8"));
} catch { process.exit(65); }
if (!payload || typeof payload !== "object" || Array.isArray(payload)) process.exit(66);
const actualKeys = Object.keys(payload).sort();
const expectedKeys = [...Object.keys(expected), "steps"].sort();
if (JSON.stringify(actualKeys) !== JSON.stringify(expectedKeys)) process.exit(66);
for (const key of Object.keys(expected)) {
  if (payload[key] !== expected[key]) process.exit(66);
}
if (!Array.isArray(payload.steps) || payload.steps.length !== 0) process.exit(66);
const ids = new Set();
for (const step of payload.steps) {
  if (!step || typeof step !== "object" || Array.isArray(step)) process.exit(66);
  const stepKeys = Object.keys(step).sort();
  if (JSON.stringify(stepKeys) !== JSON.stringify(["argv", "cwd", "environment", "step_id", "timeout_sec"].sort())) process.exit(66);
  if (typeof step.step_id !== "string" || step.step_id.length > 128 ||
      !/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(step.step_id) || ids.has(step.step_id)) process.exit(66);
  ids.add(step.step_id);
  if (!Array.isArray(step.argv) || step.argv.length < 1 ||
      step.argv.some((item) => typeof item !== "string" || item.length === 0 || item.includes("\u0000"))) process.exit(66);
  if (typeof step.cwd !== "string" || !step.cwd || step.cwd.startsWith("/") ||
      step.cwd.split("/").some((part) => part === "" || part === "..")) process.exit(66);
  if (!step.environment || typeof step.environment !== "object" || Array.isArray(step.environment)) process.exit(66);
  for (const [name, value] of Object.entries(step.environment)) {
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name) ||
        ["PATH", "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH", "NODE_PATH"].includes(name) ||
        typeof value !== "string") process.exit(66);
  }
  if (!Number.isInteger(step.timeout_sec) || step.timeout_sec < 1 || step.timeout_sec > 600) process.exit(66);
}
