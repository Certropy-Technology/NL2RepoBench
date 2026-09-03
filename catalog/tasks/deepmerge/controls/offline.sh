#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","main":"index.js"}
JSON
cat > index.js <<'JS'
function isMergeableObject(value) {
  return value !== null
    && typeof value === 'object'
    && !(value instanceof Date)
    && !(value instanceof RegExp)
    && !(value instanceof Error);
}

function emptyTarget(value) {
  return Array.isArray(value) ? [] : {};
}

function keys(value) {
  return Object.keys(value).concat(
    Object.getOwnPropertySymbols(value).filter((symbol) =>
      Object.prototype.propertyIsEnumerable.call(value, symbol)),
  );
}

function has(target, key) {
  try { return key in Object(target); } catch { return false; }
}

function unsafe(target, key) {
  return has(target, key)
    && !(Object.prototype.hasOwnProperty.call(target, key)
      && Object.prototype.propertyIsEnumerable.call(target, key));
}

function clone(value, options) {
  return options.clone !== false && options.isMergeableObject(value)
    ? deepmerge(emptyTarget(value), value, options)
    : value;
}

function mergeObject(target, source, options) {
  const destination = {};
  if (options.isMergeableObject(target)) {
    for (const key of keys(target)) destination[key] = clone(target[key], options);
  }
  for (const key of keys(source)) {
    if (unsafe(target, key)) continue;
    if (has(target, key) && options.isMergeableObject(source[key])) {
      destination[key] = mergeFunction(key, options)(target[key], source[key], options);
    } else {
      destination[key] = clone(source[key], options);
    }
  }
  return destination;
}

function defaultArrayMerge(target, source, options) {
  return target.concat(source).map((value) => clone(value, options));
}

function mergeFunction(key, options) {
  if (!options.customMerge) return deepmerge;
  const custom = options.customMerge(key);
  return typeof custom === 'function' ? custom : deepmerge;
}

function deepmerge(target, source, options = {}) {
  options.arrayMerge = options.arrayMerge || defaultArrayMerge;
  options.isMergeableObject = options.isMergeableObject || isMergeableObject;
  options.cloneUnlessOtherwiseSpecified = clone;
  const targetArray = Array.isArray(target);
  const sourceArray = Array.isArray(source);
  if (targetArray !== sourceArray) return clone(source, options);
  if (sourceArray) return options.arrayMerge(target, source, options);
  return mergeObject(target, source, options);
}

deepmerge.all = function deepmergeAll(values, options) {
  if (!Array.isArray(values)) throw new Error('first argument should be an array');
  return values.reduce((result, value) => deepmerge(result, value, options), {});
};

module.exports = deepmerge;
JS
cat > package-lock.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"deepmerge","version":"4.3.1"}}}
JSON
