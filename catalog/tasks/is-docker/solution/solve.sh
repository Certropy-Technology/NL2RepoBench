#!/usr/bin/env bash
set -euo pipefail

# Oracle-only source acquisition. This bundle is never part of the Agent image.
readonly UPSTREAM_URL="https://github.com/sindresorhus/is-docker"
readonly UPSTREAM_REVISION="59379f14b6dda26a0167fce55d80bf546857f92d"
readonly SOURCE_ARCHIVE_SHA256="4b0b0b2f7949858e2c44da8b3dd2224ccc95eb8545674c867147ae93e6381cb5"
readonly SOURCE_DIR="/tmp/is-docker-source"
readonly SOURCE_ARCHIVE="/tmp/is-docker-source.tar"
readonly ROOT="/workspace"

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
test "$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar --prefix=is-docker/ "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" --strip-components=1 -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/.git" "$ROOT/.npmrc" "$ROOT/test.js" "$ROOT/cli.js" "$ROOT/readme.md"

cat >> "$ROOT/index.js" <<'JS'

function validateSignals(value) {
	if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('signals must be an object');
	const expected = ['cgroup', 'dockerenv', 'mountinfo'];
	const keys = Object.keys(value).sort();
	if (keys.length !== expected.length || keys.some((key, index) => key !== expected[index])) throw new Error('signals must have exactly the documented keys');
	for (const key of expected) {
		if (typeof value[key] !== 'boolean') throw new Error('signal values must be boolean');
	}
	return value;
}

function detectSignals(value) {
	const signals = validateSignals(value);
	return signals.dockerenv || signals.cgroup || signals.mountinfo;
}

export function run(request) {
	if (!request || typeof request !== 'object' || Array.isArray(request)) throw new Error('request must be an object');
	if (request.op === 'version' && Object.keys(request).length === 1) return {version: '4.0.0'};
	if (request.op === 'detect' && Object.keys(request).length === 2) return detectSignals(request.signals);
	if (request.op === 'cache' && Object.keys(request).length === 3) {
		const first = detectSignals(request.first);
		validateSignals(request.second);
		return {first, second: first};
	}
	throw new Error('unsupported adapter request');
}
JS

cat > "$ROOT/package.json" <<'JSON'
{"name":"is-docker","version":"4.0.0","type":"module","exports":"./index.js","files":["index.js","index.d.ts"],"engines":{"node":">=20"}}
JSON
cat > "$ROOT/package-lock.json" <<'JSON'
{"name":"is-docker","version":"4.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"is-docker","version":"4.0.0","engines":{"node":">=20"}}}}
JSON

echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
