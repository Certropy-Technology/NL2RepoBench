import {
  cpSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { join } from "node:path";
import { stripTypeScriptTypes } from "node:module";

const sourceRoot = process.argv[2];
const workspace = process.argv[3];
if (!sourceRoot || !workspace) throw new Error("source and workspace paths are required");

function filesUnder(root) {
  const files = [];
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const path = join(root, entry.name);
    if (entry.isDirectory()) files.push(...filesUnder(path));
    else if (entry.isFile()) files.push(path);
  }
  return files.sort();
}

mkdirSync(workspace, { recursive: true });
for (const entry of readdirSync(workspace)) {
  rmSync(join(workspace, entry), { recursive: true, force: true });
}
cpSync(join(sourceRoot, "src"), join(workspace, "src"), { recursive: true });
cpSync(join(sourceRoot, "LICENSE.md"), join(workspace, "LICENSE.md"));

for (const path of filesUnder(join(workspace, "src"))) {
  if (!path.endsWith(".ts")) continue;
  if (path.endsWith(".d.ts") || /\/test(?:\.tp)?\.ts$/.test(path)) {
    unlinkSync(path);
    continue;
  }
  const source = readFileSync(path, "utf8");
  const javascript = stripTypeScriptTypes(source, {
    mode: "transform",
    sourceMap: false,
    sourceUrl: path,
  }).replace(/(["'])(\.\.?\/[^"']+)\.ts\1/g, "$1$2.js$1");
  writeFileSync(path.slice(0, -3) + ".js", javascript);
  unlinkSync(path);
}

const sourceManifest = JSON.parse(readFileSync(join(sourceRoot, "package.json"), "utf8"));
const manifest = {
  name: sourceManifest.name,
  version: sourceManifest.version,
  description: sourceManifest.description,
  license: sourceManifest.license,
  type: "module",
  sideEffects: false,
  exports: {
    ".": "./src/index.js",
    "./package.json": "./package.json",
  },
  files: ["src", "LICENSE.md"],
};
const lock = {
  name: sourceManifest.name,
  version: sourceManifest.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    "": {
      name: sourceManifest.name,
      version: sourceManifest.version,
      license: sourceManifest.license,
    },
  },
};
writeFileSync(join(workspace, "package.json"), `${JSON.stringify(manifest, null, 2)}\n`);
writeFileSync(join(workspace, "package-lock.json"), `${JSON.stringify(lock, null, 2)}\n`);
