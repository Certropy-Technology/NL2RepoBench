#!/usr/bin/env bash
set -euo pipefail

revision=09e2f1d01be98dff129f52555a733cf25a319067
expected_archive_sha256=f2c17dd0596c7e2b89f506f78b22ea49265ecda48d6822051413a401b29d177c
reference_root=$(mktemp -d /tmp/crypto-random-string-reference.XXXXXX)
trap 'rm -rf "$reference_root"' EXIT

git init -q "$reference_root"
git -C "$reference_root" remote add origin https://github.com/sindresorhus/crypto-random-string
git -C "$reference_root" fetch -q --depth=1 origin "$revision"
resolved_revision=$(git -C "$reference_root" rev-parse FETCH_HEAD)
if [[ "$resolved_revision" != "$revision" ]]; then
  echo "reference revision mismatch: $resolved_revision" >&2
  exit 65
fi
archive_sha256=$(git -C "$reference_root" archive --format=tar FETCH_HEAD | sha256sum | cut -d' ' -f1)
if [[ "$archive_sha256" != "$expected_archive_sha256" ]]; then
  echo "reference archive digest mismatch: $archive_sha256" >&2
  exit 66
fi
rm -rf "$reference_root"
trap - EXIT

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/package.json <<'JSON'
{
  "name": "crypto-random-string",
  "version": "6.0.0",
  "description": "Generate a cryptographically strong random string",
  "license": "MIT",
  "type": "module",
  "exports": {".": {"types": "./index.d.ts", "import": "./index.js", "default": "./index.js"}, "./package.json": "./package.json"},
  "sideEffects": false,
  "engines": {"node": ">=22"},
  "files": ["index.js", "index.d.ts"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "crypto-random-string",
  "version": "6.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "crypto-random-string", "version": "6.0.0", "license": "MIT", "engines": {"node": ">=22"}}}
}
JSON
cat > /workspace/index.js <<'JS'
import {randomBytes as nodeRandomBytes} from 'node:crypto';

const maxBytesPerRequest = 65_536;
const maxCharacterSetSize = 0x1_00_00;

function random(byteLength) {
  if (!Number.isSafeInteger(byteLength) || byteLength < 0) {
    throw new RangeError('Expected `byteLength` to be a non-negative integer');
  }

  const bytes = new Uint8Array(byteLength);
  for (let offset = 0; offset < byteLength; offset += maxBytesPerRequest) {
    const chunkLength = Math.min(maxBytesPerRequest, byteLength - offset);
    bytes.set(nodeRandomBytes(chunkLength), offset);
  }

  return bytes;
}

function fillWithRandomValues(typedArray) {
  for (let offset = 0; offset < typedArray.length; offset += maxBytesPerRequest / typedArray.BYTES_PER_ELEMENT) {
    const end = Math.min(typedArray.length, offset + maxBytesPerRequest / typedArray.BYTES_PER_ELEMENT);
    const bytes = nodeRandomBytes((end - offset) * typedArray.BYTES_PER_ELEMENT);
    if (typedArray.BYTES_PER_ELEMENT === 1) {
      typedArray.set(bytes, offset);
    } else {
      for (let index = 0; index < end - offset; index++) {
        typedArray[offset + index] = bytes[index * 2] | (bytes[index * 2 + 1] << 8);
      }
    }
  }

  return typedArray;
}

function generateForCustomCharacters(length, characters) {
  if (length === 0) return '';
  const characterCount = characters.length;
  const validSelectorCount = Math.floor(maxCharacterSetSize / characterCount) * characterCount;
  const entropyLength = Math.max(1, Math.ceil(1.1 * length * (maxCharacterSetSize / validSelectorCount)));
  let result = '';
  let stringLength = 0;

  while (stringLength < length) {
    const entropy = fillWithRandomValues(new Uint16Array(entropyLength));
    for (const value of entropy) {
      if (value < validSelectorCount) {
        result += characters[value % characterCount];
        stringLength++;
        if (stringLength === length) return result;
      }
    }
  }

  return result;
}

const characterSets = new Map([
  ['url-safe', [...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~']],
  ['numeric', [...'0123456789']],
  ['distinguishable', [...'CDEHKMPRTUWXY012458']],
  ['ascii-printable', [...'!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~']],
  ['alphanumeric', [...'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789']],
]);
const allowedTypes = new Set(['hex', 'base64', ...characterSets.keys()]);

export default function cryptoRandomString({length, type, characters}) {
  if (!Number.isSafeInteger(length) || length < 0) {
    throw new TypeError('Expected `length` to be a non-negative integer');
  }

  if (type !== undefined && characters !== undefined) {
    throw new TypeError('Expected either `type` or `characters`');
  }

  if (characters !== undefined) {
    if (typeof characters !== 'string') throw new TypeError('Expected `characters` to be a string');
    const customCharacterSet = [...characters];
    if (customCharacterSet.length === 0) throw new TypeError('Expected `characters` to contain at least 1 character');
    if (customCharacterSet.length > maxCharacterSetSize) throw new TypeError(`Expected \`characters\` to contain at most ${maxCharacterSetSize} characters, got ${customCharacterSet.length}`);
    return generateForCustomCharacters(length, customCharacterSet);
  }

  if (type !== undefined && !allowedTypes.has(type)) throw new TypeError(`Unknown type: ${type}`);
  const characterSet = characterSets.get(type);
  if (characterSet !== undefined) return generateForCustomCharacters(length, characterSet);
  if (type === 'base64') return Buffer.from(random(Math.ceil(length * 0.75))).toString('base64').slice(0, length);
  return Buffer.from(random(Math.ceil(length * 0.5))).toString('hex').slice(0, length);
}

JS
cat > /workspace/index.d.ts <<'TS'
type BaseOptions = {length: number};
type TypeOption = {type?: 'hex' | 'base64' | 'url-safe' | 'numeric' | 'distinguishable' | 'ascii-printable' | 'alphanumeric'; characters?: never};
type CharactersOption = {characters: string; type?: never};
export type Options = BaseOptions & (TypeOption | CharactersOption);
export default function cryptoRandomString(options: Options): string;
TS
chmod 0555 /workspace/index.js /workspace/index.d.ts /workspace/package.json /workspace/package-lock.json
