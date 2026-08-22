import { resolve } from "node:path";
import { scanSource } from "./inventory.js";
const a = scanSource(resolve("test/fixture")),
  b = scanSource(resolve("test/fixture"));
if (JSON.stringify(a) !== JSON.stringify(b))
  throw Error("inventory is not deterministic");
if (
  a.package.name !== "inventory-fixture" ||
  a.package.main !== "dist/index.cjs" ||
  a.package.module !== "dist/index.js" ||
  a.package.types !== "dist/index.d.ts"
)
  throw Error("package metadata missing");
if (
  !a.package.exports ||
  a.package.package_manager !== "npm" ||
  a.package.package_manager_version !== "10.9.8"
)
  throw Error("package manager metadata missing");
if (
  !a.symbols.some((x) => x.export_name === "parse" && x.kind === "function") ||
  !a.symbols.some((x) => x.export_name === "legacy" && x.kind === "function") ||
  !a.symbols.some(
    (x) =>
      x.kind === "method" &&
      x.name === "read" &&
      x.signature?.includes("strict"),
  )
)
  throw Error("symbol inventory missing");
for (const x of [
  "dynamic-execution",
  "dynamic-import",
  "native-addon",
  "external-service",
  "postinstall",
  "workspace",
])
  if (!a.risk_flags.includes(x)) throw Error(`risk flag missing: ${x}`);
if (
  a.metrics.test_count !== 2 ||
  a.metrics.test_files !== 1 ||
  a.syntax_diagnostics.length !== 0
)
  throw Error("test inventory mismatch");
console.log(
  `node-inventory self-test passed: ${a.metrics.public_symbol_count} public symbols, ${a.metrics.test_count} tests`,
);
