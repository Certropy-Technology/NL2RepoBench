import { spawnSync } from "node:child_process";

const RUNNER = "/tests/runtime/node/candidate_runner.mjs";
const NODE = "/usr/local/bin/node";

function runCandidate(exportName, args) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM",
      "--kill-after=5s",
      "30s",
      "runuser",
      "-u",
      "candidate",
      "--",
      "/usr/bin/prlimit",
      "--cpu=60",
      "--nproc=32",
      "--nofile=128",
      "--",
      "env",
      "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      "NODE_ALLOWED_PACKAGE=uuid",
      NODE,
      "--no-addons",
      RUNNER,
    ],
    {
      cwd: site,
      input: `${JSON.stringify({ package: "uuid", export: exportName, args })}\n`,
      encoding: "utf8",
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  if (!payload.ok) throw new Error(payload.error ?? "candidate-call-failed");
  return payload.value;
}

function hexToArray(hex) {
  if (typeof hex !== "string" || !/^[0-9a-fA-F]+$/.test(hex) || hex.length % 2 !== 0) {
    throw new TypeError("hex input must contain an even number of hexadecimal digits");
  }
  return Array.from(Buffer.from(hex, "hex"));
}

function arrayToHex(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("candidate parse result is not a byte array");
  }
  const bytes = Array.from({ length: 16 }, (_, index) => value[String(index)]);
  if (bytes.some((byte) => !Number.isInteger(byte) || byte < 0 || byte > 255)) {
    throw new Error("candidate parse result has invalid bytes");
  }
  return Buffer.from(bytes).toString("hex");
}

function optionsWithHex(options) {
  if (options === undefined || options === null) return options;
  const converted = { ...options };
  if (Object.hasOwn(converted, "random_hex")) {
    converted.random = hexToArray(converted.random_hex);
    delete converted.random_hex;
  }
  if (Object.hasOwn(converted, "node_hex")) {
    converted.node = hexToArray(converted.node_hex);
    delete converted.node_hex;
  }
  return converted;
}

export function callUuid(operation, input) {
  switch (operation) {
    case "parse":
      return arrayToHex(runCandidate("parse", [input]));
    case "stringify":
      return runCandidate("stringify", [hexToArray(input)]);
    case "validate":
      return runCandidate("validate", [input]);
    case "version":
      return runCandidate("version", [input]);
    case "v1ToV6":
    case "v6ToV1":
      return runCandidate(operation, [input]);
    case "v3":
    case "v5":
      return runCandidate(operation, [input.name, input.namespace]);
    case "v1":
    case "v4":
    case "v6":
    case "v7":
      return runCandidate(operation, [optionsWithHex(input)]);
    default:
      throw new Error(`unsupported UUID operation: ${operation}`);
  }
}
