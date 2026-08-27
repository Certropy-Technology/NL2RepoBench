import { createConnection } from "node:net";
import {
  readFileSync,
  readlinkSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname } from "node:path";
import { mkdirSync } from "node:fs";

const PROBE_TIMEOUT_MS = 1000;
const MAX_ROUTE_TABLE_BYTES = 64 * 1024;
const PROBES = [
  ["registry.npmjs.org", 443],
  ["1.1.1.1", 443],
];
const INTERNAL_ERROR_EXIT = 70;
const args = process.argv.slice(2);
const outputIndex = args.indexOf("--output");
const output = outputIndex >= 0 ? args[outputIndex + 1] : null;

function probe(host, port) {
  return new Promise((resolve) => {
    let socket;
    let settled = false;
    const timer = setTimeout(() => finish(false), PROBE_TIMEOUT_MS);

    function finish(available) {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      socket?.destroy();
      resolve(available);
    }

    try {
      socket = createConnection({ host, port });
      socket.setTimeout(PROBE_TIMEOUT_MS, () => finish(false));
      socket.once("connect", () => finish(true));
      socket.once("error", () => finish(false));
    } catch {
      finish(false);
    }
  });
}

function writeReceipt(path, receipt) {
  mkdirSync(dirname(path), { recursive: true, mode: 0o700 });
  const temporary = `${path}.${process.pid}.tmp`;
  try {
    writeFileSync(temporary, `${JSON.stringify(receipt, null, 2)}\n`, {
      encoding: "utf8",
      flag: "wx",
      mode: 0o400,
    });
    renameSync(temporary, path);
  } catch (error) {
    try {
      unlinkSync(temporary);
    } catch {
      // Preserve the original receipt-generation failure.
    }
    throw error;
  }
}

async function main() {
  if (!output || outputIndex !== 0 || args.length !== 2) {
    process.stderr.write("network-check requires exactly --output <path>\n");
    process.exitCode = 64;
    return;
  }

  const values = await Promise.all(PROBES.map(([host, port]) => probe(host, port)));
  const probes = Object.fromEntries(
    PROBES.map(([host, port], index) => [`${host}:${port}`, values[index]]),
  );
  const available = values.some(Boolean);
  const routeTable = readFileSync("/proc/net/route", "utf8");
  if (Buffer.byteLength(routeTable, "utf8") > MAX_ROUTE_TABLE_BYTES) {
    throw new Error("route table exceeds receipt bound");
  }
  const receipt = {
    schema_version: "1.0",
    probes,
    public_network_available: available,
    network_namespace: readlinkSync("/proc/self/ns/net"),
    route_table: routeTable,
  };
  writeReceipt(output, receipt);
  process.exitCode = available ? 1 : 0;
}

main().catch((error) => {
  process.stderr.write(`network receipt generation failed: ${String(error)}\n`);
  process.exitCode = INTERNAL_ERROR_EXIT;
});
