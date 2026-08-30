import { lstatSync, readFileSync } from "node:fs";

const args = process.argv.slice(2);
const path = args[args.indexOf("--path") + 1];
const expected = {
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
  if (!metadata.isFile() || metadata.size > 4096) process.exit(65);
  payload = JSON.parse(readFileSync(path, "utf8"));
} catch { process.exit(65); }
if (JSON.stringify(payload) !== JSON.stringify(expected)) process.exit(66);
