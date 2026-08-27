var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __commonJS = (cb, mod) => function __require() {
  try {
    return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
  } catch (e) {
    throw mod = 0, e;
  }
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// .nl2repo/authoring-work/node-author-wide-20260826-remediation/vite/source/repo/node_modules/.pnpm/dotenv-expand@13.0.0_patch_hash=49330a663821151418e003e822a82a6a61d2f0f8a6e3cab00c1c94815a112889/node_modules/dotenv-expand/lib/main.js
var require_main = __commonJS({
  ".nl2repo/authoring-work/node-author-wide-20260826-remediation/vite/source/repo/node_modules/.pnpm/dotenv-expand@13.0.0_patch_hash=49330a663821151418e003e822a82a6a61d2f0f8a6e3cab00c1c94815a112889/node_modules/dotenv-expand/lib/main.js"(exports, module) {
    "use strict";
    function _resolveEscapeSequences(value) {
      return value.replace(/\\\$/g, "$");
    }
    function expandValue(value, processEnv, runningParsed) {
      const env = { ...runningParsed, ...processEnv };
      const regex = /(?<!\\)\${([^{}]+)}|(?<!\\)\$([A-Za-z_][A-Za-z0-9_]*)/g;
      let result = value;
      let match;
      const seen = /* @__PURE__ */ new Set();
      while ((match = regex.exec(result)) !== null) {
        seen.add(result);
        const [template, bracedExpression, unbracedExpression] = match;
        const expression = bracedExpression || unbracedExpression;
        const opRegex = /(:\+|\+|:-|-)/;
        const opMatch = expression.match(opRegex);
        const splitter = opMatch ? opMatch[0] : null;
        const r = expression.split(splitter);
        let defaultValue;
        let value2;
        const key = r.shift();
        if ([":+", "+"].includes(splitter)) {
          defaultValue = env[key] ? r.join(splitter) : "";
          value2 = null;
        } else {
          defaultValue = r.join(splitter);
          value2 = env[key];
        }
        if (value2) {
          if (seen.has(value2)) {
            result = result.replace(template, defaultValue);
          } else {
            result = result.replace(template, value2);
          }
        } else {
          result = result.replace(template, defaultValue);
        }
        if (result === runningParsed[key]) {
          break;
        }
        regex.lastIndex = 0;
      }
      return result;
    }
    function expand2(options) {
      let processEnv = process.env;
      if (options && options.processEnv != null) {
        processEnv = options.processEnv;
      }
      for (const key in options.parsed) {
        let value = options.parsed[key];
        if (processEnv[key] && processEnv[key] !== value) {
          value = processEnv[key];
        } else {
          value = expandValue(value, processEnv, options.parsed);
        }
        options.parsed[key] = _resolveEscapeSequences(value);
      }
      for (const processKey in options.parsed) {
        processEnv[processKey] = options.parsed[processKey];
      }
      return options;
    }
    module.exports.expand = expand2;
  }
});

// .nl2repo/authoring-work/node-author-wide-20260826-remediation/vite/oracle-reference/entry.mjs
var import_main = __toESM(require_main(), 1);
import fs from "node:fs";
import path from "node:path";
import { parseEnv } from "node:util";
var CSS_LANGS_RE = /\.(css|less|sass|scss|styl|stylus|pcss|postcss|sss)(?:$|\?)/;
var ENVIRONMENT_PATH_RE = /^environments\.[^.]+$/;
function arraify(value) {
  return Array.isArray(value) ? value : [value];
}
function isObject(value) {
  return Object.prototype.toString.call(value) === "[object Object]";
}
function normalizeSingleAlias({ find, replacement, customResolver }) {
  if (typeof find === "string" && find.endsWith("/") && replacement.endsWith("/")) {
    find = find.slice(0, -1);
    replacement = replacement.slice(0, -1);
  }
  const alias = { find, replacement };
  if (customResolver) alias.customResolver = customResolver;
  return alias;
}
function normalizeAlias(value = []) {
  return Array.isArray(value) ? value.map(normalizeSingleAlias) : Object.keys(value).map(
    (find) => normalizeSingleAlias({ find, replacement: value[find] })
  );
}
function normalizeToInputObject(input) {
  if (typeof input === "string") {
    return { [path.basename(input, path.extname(input))]: input };
  }
  if (Array.isArray(input)) {
    return Object.fromEntries(
      input.map((item) => [path.basename(item, path.extname(item)), item])
    );
  }
  return input;
}
function mergeInput(left, right) {
  if (!left) return right;
  if (!right) return left;
  if (typeof left === "string" && typeof right === "string") {
    return [left, right];
  }
  if (Array.isArray(left) && (typeof right === "string" || Array.isArray(right))) {
    return [...left, ...Array.isArray(right) ? right : [right]];
  }
  if (Array.isArray(right) && (typeof left === "string" || Array.isArray(left))) {
    return [...Array.isArray(left) ? left : [left], ...right];
  }
  if (typeof left !== "string" && !Array.isArray(left)) {
    return { ...left, ...normalizeToInputObject(right) };
  }
  return { ...normalizeToInputObject(left), ...right };
}
function mergeConfigRecursively(defaults, overrides, rootPath) {
  const merged = { ...defaults };
  for (const key in overrides) {
    const value = overrides[key];
    if (value == null) continue;
    const existing = merged[key];
    if (existing == null) {
      merged[key] = value;
      continue;
    }
    if (key === "input" && rootPath === "") {
      merged[key] = mergeInput(existing, value);
      continue;
    }
    if (key === "alias" && (rootPath === "resolve" || rootPath === "")) {
      merged[key] = mergeAlias(existing, value);
      continue;
    }
    if (key === "assetsInclude" && rootPath === "") {
      merged[key] = [].concat(existing, value);
      continue;
    }
    if (((key === "noExternal" || key === "external") && (rootPath === "ssr" || rootPath === "resolve") || key === "allowedHosts" && rootPath === "server") && (existing === true || value === true)) {
      merged[key] = true;
      continue;
    }
    if (Array.isArray(existing) || Array.isArray(value)) {
      merged[key] = [...arraify(existing), ...arraify(value)];
      continue;
    }
    if (isObject(existing) && isObject(value)) {
      merged[key] = mergeConfigRecursively(
        existing,
        value,
        rootPath && !ENVIRONMENT_PATH_RE.test(rootPath) ? `${rootPath}.${key}` : key
      );
      continue;
    }
    merged[key] = value;
  }
  return merged;
}
function defineConfig(config) {
  return config;
}
function isCSSRequest(request) {
  return CSS_LANGS_RE.test(request);
}
function mergeAlias(left, right) {
  if (!left) return right;
  if (!right) return left;
  if (isObject(left) && isObject(right)) return { ...left, ...right };
  return [...normalizeAlias(right), ...normalizeAlias(left)];
}
function mergeConfig(defaults, overrides, isRoot = true) {
  if (typeof defaults === "function" || typeof overrides === "function") {
    throw new Error("Cannot merge config in form of callback");
  }
  return mergeConfigRecursively(defaults, overrides, isRoot ? "" : ".");
}
function normalizePath(id) {
  return path.posix.normalize(id);
}
function envFilesForMode(mode, envDir) {
  if (envDir === false) return [];
  return [".env", ".env.local", `.env.${mode}`, `.env.${mode}.local`].map(
    (file) => normalizePath(path.join(envDir, file))
  );
}
function loadEnv(mode, envDir, prefixes = "VITE_") {
  if (mode === "local") {
    throw new Error(
      '"local" cannot be used as a mode name because it conflicts with the .local postfix for .env files.'
    );
  }
  prefixes = arraify(prefixes);
  const env = {};
  const parsed = Object.fromEntries(
    envFilesForMode(mode, envDir).flatMap((file) => {
      try {
        const stat = fs.statSync(file);
        if (!stat.isFile() && !stat.isFIFO()) return [];
        return Object.entries(parseEnv(fs.readFileSync(file, "utf8")));
      } catch {
        return [];
      }
    })
  );
  const processEnv = { ...process.env };
  (0, import_main.expand)({ parsed, processEnv });
  for (const [key, value] of Object.entries(parsed)) {
    if (prefixes.some((prefix) => key.startsWith(prefix))) env[key] = value;
  }
  for (const key in process.env) {
    if (prefixes.some((prefix) => key.startsWith(prefix))) {
      env[key] = process.env[key];
    }
  }
  return env;
}
function resolveEnvPrefix({ envPrefix = "VITE_" }) {
  const prefixes = arraify(envPrefix);
  if (prefixes.includes("")) {
    throw new Error(
      "envPrefix option contains value '', which could lead unexpected exposure of sensitive information."
    );
  }
  return prefixes;
}
function isReadable(file) {
  try {
    fs.accessSync(file, fs.constants.R_OK);
    return true;
  } catch {
    return false;
  }
}
function hasWorkspacePackageJson(root) {
  const file = path.join(root, "package.json");
  if (!isReadable(file)) return false;
  try {
    return Boolean(JSON.parse(fs.readFileSync(file, "utf8"))?.workspaces);
  } catch {
    return false;
  }
}
function hasWorkspaceDenoJson(root) {
  for (const name of ["deno.json", "deno.jsonc"]) {
    const file = path.join(root, name);
    if (!isReadable(file)) continue;
    try {
      if (JSON.parse(fs.readFileSync(file, "utf8"))?.workspace) return true;
    } catch {
    }
  }
  return false;
}
function searchForPackageRoot(current, root = current) {
  if (fs.existsSync(path.join(current, "package.json"))) return current;
  const parent = path.dirname(current);
  if (!parent || parent === current) return root;
  return searchForPackageRoot(parent, root);
}
function searchForWorkspaceRoot(current, root = searchForPackageRoot(current)) {
  if (fs.existsSync(path.join(current, "pnpm-workspace.yaml")) || fs.existsSync(path.join(current, "lerna.json")) || hasWorkspacePackageJson(current) || hasWorkspaceDenoJson(current)) {
    return current;
  }
  const parent = path.dirname(current);
  if (!parent || parent === current) return root;
  return searchForWorkspaceRoot(parent, root);
}
function sortUserPlugins(plugins) {
  const prePlugins = [];
  const postPlugins = [];
  const normalPlugins = [];
  if (plugins) {
    plugins.flat().forEach((plugin) => {
      if (plugin.enforce === "pre") prePlugins.push(plugin);
      else if (plugin.enforce === "post") postPlugins.push(plugin);
      else normalPlugins.push(plugin);
    });
  }
  return [prePlugins, normalPlugins, postPlugins];
}
export {
  defineConfig,
  isCSSRequest,
  loadEnv,
  mergeAlias,
  mergeConfig,
  normalizePath,
  resolveEnvPrefix,
  searchForWorkspaceRoot,
  sortUserPlugins
};
