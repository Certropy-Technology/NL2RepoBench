import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { scanSource } from "./inventory.js";
const a = process.argv.slice(2),
  source = a.find((x) => !x.startsWith("-"));
if (!source || a.includes("--help")) {
  console.error(
    "Usage: node dist/cli.js <source-root> [--output <inventory.json>]",
  );
  process.exitCode = source ? 0 : 2;
} else
  try {
    const json = `${JSON.stringify(scanSource(source), null, 2)}\n`,
      i = a.indexOf("--output"),
      out = i >= 0 ? a[i + 1] : undefined;
    if (out) {
      mkdirSync(dirname(resolve(out)), { recursive: true });
      writeFileSync(out, json);
    } else process.stdout.write(json);
  } catch (e) {
    console.error(e instanceof Error ? e.message : String(e));
    process.exitCode = 1;
  }
