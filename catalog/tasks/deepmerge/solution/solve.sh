#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/TehShrike/deepmerge"
UPSTREAM_REVISION="5b87756a5671635679001cbac72aa42f23472c81"
SOURCE_ARCHIVE_SHA256="6efceb65f541465fe6755f427fd8ca33f925b36a56b38f39ab1282bf9830b51d"
SOURCE_DIR="/tmp/deepmerge-source"
SOURCE_ARCHIVE="/tmp/deepmerge-source.tar"
rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" checkout -q --detach FETCH_HEAD
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse HEAD)"
[[ "$resolved_revision" == "$UPSTREAM_REVISION" ]]
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","main":"index.js","license":"MIT"}
JSON
cat > /workspace/index.js <<'JS'
var defaultIsMergeableObject = function(value) {
	if (!value || typeof value !== 'object') return false
	var tag = Object.prototype.toString.call(value)
	return tag !== '[object RegExp]' && tag !== '[object Date]' && !(value.$$typeof === (typeof Symbol === 'function' && Symbol.for ? Symbol.for('react.element') : 0xeac7))
}
function emptyTarget(value) { return Array.isArray(value) ? [] : {} }
function cloneUnlessOtherwiseSpecified(value, options) { return options.clone !== false && options.isMergeableObject(value) ? deepmerge(emptyTarget(value), value, options) : value }
function defaultArrayMerge(target, source, options) { return target.concat(source).map(function(element) { return cloneUnlessOtherwiseSpecified(element, options) }) }
function getMergeFunction(key, options) { if (!options.customMerge) return deepmerge; var custom = options.customMerge(key); return typeof custom === 'function' ? custom : deepmerge }
function getEnumerableOwnPropertySymbols(target) { return Object.getOwnPropertySymbols ? Object.getOwnPropertySymbols(target).filter(function(symbol) { return Object.propertyIsEnumerable.call(target, symbol) }) : [] }
function getKeys(target) { return Object.keys(target).concat(getEnumerableOwnPropertySymbols(target)) }
function propertyIsOnObject(object, property) { try { return property in object } catch (_) { return false } }
function propertyIsUnsafe(target, key) { return propertyIsOnObject(target, key) && !(Object.hasOwnProperty.call(target, key) && Object.propertyIsEnumerable.call(target, key)) }
function mergeObject(target, source, options) {
	var destination = {}
	if (options.isMergeableObject(target)) getKeys(target).forEach(function(key) { destination[key] = cloneUnlessOtherwiseSpecified(target[key], options) })
	getKeys(source).forEach(function(key) {
		if (propertyIsUnsafe(target, key)) return
		if (propertyIsOnObject(target, key) && options.isMergeableObject(source[key])) destination[key] = getMergeFunction(key, options)(target[key], source[key], options)
		else destination[key] = cloneUnlessOtherwiseSpecified(source[key], options)
	})
	return destination
}
function deepmerge(target, source, options) {
	options = options || {}
	options.arrayMerge = options.arrayMerge || defaultArrayMerge
	options.isMergeableObject = options.isMergeableObject || defaultIsMergeableObject
	options.cloneUnlessOtherwiseSpecified = cloneUnlessOtherwiseSpecified
	var sourceIsArray = Array.isArray(source), targetIsArray = Array.isArray(target)
	if (sourceIsArray !== targetIsArray) return cloneUnlessOtherwiseSpecified(source, options)
	if (sourceIsArray) return options.arrayMerge(target, source, options)
	return mergeObject(target, source, options)
}
deepmerge.all = function deepmergeAll(array, options) {
	if (!Array.isArray(array)) throw new Error('first argument should be an array')
	return array.reduce(function(prev, next) { return deepmerge(prev, next, options) }, {})
}
module.exports = deepmerge
JS
cat > /workspace/package-lock.json <<'JSON'
{"name":"deepmerge","version":"4.3.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"deepmerge","version":"4.3.1"}}}
JSON
cp "$SOURCE_DIR/license.txt" /workspace/license.txt
