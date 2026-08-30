import { copyFileSync, lstatSync, mkdirSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";

const MAX_ENTRIES = 20_000;
const MAX_FILE_BYTES = 64 * 1024 * 1024;
const MAX_TOTAL_BYTES = 256 * 1024 * 1024;
const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const source = value("--source");
const destination = value("--destination");
if (!source || !destination) process.exit(64);

let entries = 0;
let totalBytes = 0;
function copyTree(current, target) {
  const metadata = lstatSync(current);
  if (metadata.isSymbolicLink() || (!metadata.isDirectory() && !metadata.isFile())) {
    throw new Error(`unsupported workspace entry: ${current}`);
  }
  if (metadata.isFile()) {
    entries += 1;
    totalBytes += metadata.size;
    if (entries > MAX_ENTRIES || metadata.size > MAX_FILE_BYTES || totalBytes > MAX_TOTAL_BYTES) {
      throw new Error("workspace exceeds bounded copy limits");
    }
    mkdirSync(join(target, ".."), { recursive: true });
    copyFileSync(current, target);
    return;
  }
  mkdirSync(target, { recursive: true });
  for (const name of readdirSync(current)) {
    copyTree(join(current, name), join(target, name));
  }
}

try {
  copyTree(source, destination);
} catch (error) {
  process.stderr.write(`${String(error?.message ?? error)}\n`);
  process.exit(20);
}
