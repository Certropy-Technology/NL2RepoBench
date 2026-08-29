import {spawnSync} from "node:child_process";

const NODE = "/usr/local/bin/node";
const MAX_REQUEST_BYTES = 16 * 1024;
const MAX_RESPONSE_BYTES = 64 * 1024;

const ADAPTER = String.raw`
import {createRequire} from "node:module";
import {join} from "node:path";
import {pathToFileURL} from "node:url";

function emit(payload, code = 0) {
  process.stdout.write(JSON.stringify(payload) + "\n");
  process.exit(code);
}

function makeScenario(name) {
  const symbols = new Map();
  const remember = (symbol, id) => { symbols.set(symbol, id); return symbol; };
  const data = (value, enumerable = true, configurable = true) => ({value, enumerable, configurable, writable: true});
  let target;
  let state = {};

  switch (name) {
    case "empty": target = {}; break;
    case "enumerable-order": target = {delta: 1, alpha: 2, charlie: 3, bravo: 4}; break;
    case "non-enumerable":
      target = {visible: 1};
      Object.defineProperty(target, "hidden", data(2, false));
      break;
    case "inherited":
      target = Object.create({inherited: true});
      target.own = true;
      break;
    case "symbols": {
      const first = remember(Symbol("first"), "first");
      const second = remember(Symbol("second"), "second");
      target = {text: 1};
      target[first] = 2;
      Object.defineProperty(target, second, data(3, false));
      break;
    }
    case "mixed-order": {
      const early = remember(Symbol("early"), "early");
      const late = remember(Symbol("late"), "late");
      target = {};
      target.zeta = 1;
      target[early] = 2;
      target.alpha = 3;
      target[late] = 4;
      break;
    }
    case "integer-order":
      target = {};
      target[10] = "ten";
      target[2] = "two";
      target.beta = 1;
      target.alpha = 2;
      break;
    case "dense-array": target = ["a", "b", "c"]; break;
    case "sparse-array":
      target = [];
      target[3] = "d";
      target.extra = true;
      break;
    case "null-prototype":
      target = Object.create(null);
      target.alpha = 1;
      Object.defineProperty(target, "hidden", data(2, false));
      break;
    case "frozen": target = Object.freeze({alpha: 1, beta: 2}); break;
    case "sealed": target = Object.seal({alpha: 1, beta: 2}); break;
    case "accessor":
      state.getterCalls = 0;
      target = {};
      Object.defineProperty(target, "computed", {enumerable: true, configurable: true, get() { state.getterCalls += 1; return 1; }});
      break;
    case "throwing-accessor":
      state.getterCalls = 0;
      target = {};
      Object.defineProperty(target, "danger", {enumerable: false, configurable: true, get() { state.getterCalls += 1; throw new Error("getter invoked"); }});
      break;
    case "delete-readd":
      target = {alpha: 1, beta: 2, gamma: 3};
      delete target.beta;
      target.beta = 4;
      break;
    case "redefine":
      target = {alpha: 1, beta: 2};
      Object.defineProperty(target, "alpha", data(3, false));
      break;
    case "duplicate-symbol-descriptions": {
      const first = remember(Symbol("same"), "one");
      const second = remember(Symbol("same"), "two");
      target = {};
      target[first] = 1;
      target[second] = 2;
      break;
    }
    case "global-symbol": {
      const global = remember(Symbol.for("shared-key"), "global");
      target = {[global]: true};
      break;
    }
    case "well-known-symbol":
      symbols.set(Symbol.iterator, "iterator");
      target = {[Symbol.iterator]: function iterator() { return [][Symbol.iterator](); }};
      break;
    case "proxy-order": {
      state.trapCalls = 0;
      const base = {alpha: 1, beta: 2};
      target = new Proxy(base, {ownKeys() { state.trapCalls += 1; return ["beta", "alpha"]; }});
      break;
    }
    case "proxy-duplicate": target = new Proxy({}, {ownKeys() { return ["alpha", "alpha"]; }}); break;
    case "proxy-missing-fixed": {
      const base = {};
      Object.defineProperty(base, "fixed", data(1, true, false));
      target = new Proxy(base, {ownKeys() { return []; }});
      break;
    }
    case "no-mutation":
      target = {alpha: 1};
      Object.defineProperty(target, "hidden", data(2, false));
      state.before = JSON.stringify(Object.getOwnPropertyDescriptors(target));
      break;
    case "null": target = null; break;
    case "undefined": target = undefined; break;
    case "string": target = "abc"; break;
    case "number": target = 42; break;
    case "boolean": target = true; break;
    case "symbol-primitive": target = Symbol("value"); break;
    case "bigint": target = 10n; break;
    default: throw new TypeError("unknown scenario");
  }
  return {target, symbols, state};
}

function describeKey(key, symbols) {
  if (typeof key === "string") return {type: "string", value: key};
  return {
    type: "symbol",
    id: symbols.get(key) ?? null,
    description: key.description ?? null,
    globalKey: Symbol.keyFor(key) ?? null,
  };
}

try {
  const request = JSON.parse(process.env.OWN_KEYS_REQUEST_JSON ?? "null");
  if (!request || typeof request !== "object" || Array.isArray(request)) throw new TypeError("request must be an object");
  const require = createRequire(pathToFileURL(join(process.cwd(), "package.json")));
  const ownKeys = require("own-keys");
  if (request.operation === "inventory") {
    emit({ok: true, type: typeof ownKeys, length: ownKeys.length});
  }
  const {target, symbols, state} = makeScenario(request.scenario);
  try {
    const keys = ownKeys(target);
    if (!Array.isArray(keys)) throw new TypeError("result must be an array");
    if (request.scenario === "no-mutation") state.after = JSON.stringify(Object.getOwnPropertyDescriptors(target));
    emit({ok: true, keys: keys.map((key) => describeKey(key, symbols)), state});
  } catch (error) {
    emit({ok: false, errorType: error?.constructor?.name ?? "Error", message: String(error?.message ?? error).slice(0, 256), state});
  }
} catch (error) {
  emit({ok: false, boundaryError: true, errorType: error?.constructor?.name ?? "Error", message: String(error?.message ?? error).slice(0, 256)}, 1);
}
`;

export function callCandidate(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const encoded = JSON.stringify(request);
  if (Buffer.byteLength(encoded) > MAX_REQUEST_BYTES) throw new Error("candidate request exceeds bound");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM", "--kill-after=5s", "30s",
      "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--",
      "env", "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
      `OWN_KEYS_REQUEST_JSON=${encoded}`,
      NODE, "--no-addons", "--input-type=module", "--eval", ADAPTER,
    ],
    {cwd: site, encoding: "utf8", maxBuffer: MAX_RESPONSE_BYTES, timeout: 35_000},
  );
  if (result.error) throw result.error;
  try {
    return JSON.parse(result.stdout);
  } catch {
    throw new Error("candidate response was not JSON");
  }
}
