import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

const archive = process.argv[2];
if (!archive || archive.includes("\0")) process.exit(64);

const listing = spawnSync("/usr/bin/tar", ["-tvzf", archive], {
  encoding: "utf8",
  maxBuffer: 8 * 1024 * 1024,
});
if (listing.error || listing.status !== 0) process.exit(65);
const seen = new Set();
for (const line of listing.stdout.split(/\r?\n/)) {
  if (!line) continue;
  const name = line.slice(0, 10);
  const fields = line.trim().split(/\s+/);
  const path = fields.at(-1) ?? "";
  if (seen.has(path)) process.exit(66);
  seen.add(path);
  if (!path.startsWith("package/") || path.includes("../") || path.startsWith("/") || name[0] === "l" || name[0] === "h") {
    process.exit(66);
  }
  if (path.endsWith(".node") || path.endsWith("binding.gyp") || path.endsWith("binding.gypi") || path.includes("/prebuilds/")) {
    process.exit(67);
  }
}
const manifest = spawnSync("/usr/bin/tar", ["-xOzf", archive, "package/package.json"], {
  encoding: "utf8",
  maxBuffer: 4 * 1024 * 1024,
});
if (manifest.error || manifest.status !== 0) process.exit(68);
let packageJson;
try {
  packageJson = JSON.parse(manifest.stdout);
} catch {
  process.exit(69);
}
if (!packageJson || typeof packageJson !== "object" || Array.isArray(packageJson)) process.exit(70);
const lifecycleHooks = new Set([
  "preinstall",
  "install",
  "postinstall",
  "prepare",
  "prepublish",
  "prepublishonly",
  "publish",
  "postpublish",
]);
if (Object.hasOwn(packageJson, "workspaces") || Object.hasOwn(packageJson, "gypfile") || Object.hasOwn(packageJson, "binary")) process.exit(71);
if (packageJson.scripts !== undefined) {
  if (!packageJson.scripts || typeof packageJson.scripts !== "object" || Array.isArray(packageJson.scripts)) process.exit(71);
  if (Object.keys(packageJson.scripts).some((name) => lifecycleHooks.has(name.toLowerCase()))) process.exit(71);
}
process.exit(0);
