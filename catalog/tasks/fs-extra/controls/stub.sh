#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/lib
cat > /workspace/package.json <<'JSON'
{
  "name": "fs-extra",
  "version": "11.4.0",
  "main": "./lib/index.js",
  "exports": {".": "./lib/index.js", "./esm": "./lib/esm.mjs"},
  "files": ["lib/"],
  "engines": {"node": ">=14.14"}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "fs-extra",
  "version": "11.4.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {"": {"name": "fs-extra", "version": "11.4.0"}}
}
JSON
cat > /workspace/lib/index.js <<'JS'
'use strict'
const fs = require('node:fs')
const asyncVoid = async () => undefined
const syncVoid = () => undefined
const asyncFalse = async () => false
const syncFalse = () => false
const asyncNull = async () => null
const syncNull = () => null
module.exports = {
  ...fs,
  copy: asyncVoid, copySync: syncVoid,
  emptyDir: asyncVoid, emptyDirSync: syncVoid, emptydir: asyncVoid, emptydirSync: syncVoid,
  ensureDir: asyncVoid, ensureDirSync: syncVoid, mkdirs: asyncVoid, mkdirsSync: syncVoid,
  mkdirp: asyncVoid, mkdirpSync: syncVoid,
  ensureFile: asyncVoid, ensureFileSync: syncVoid, createFile: asyncVoid, createFileSync: syncVoid,
  ensureLink: asyncVoid, ensureLinkSync: syncVoid, createLink: asyncVoid, createLinkSync: syncVoid,
  ensureSymlink: asyncVoid, ensureSymlinkSync: syncVoid,
  createSymlink: asyncVoid, createSymlinkSync: syncVoid,
  move: asyncVoid, moveSync: syncVoid, outputFile: asyncVoid, outputFileSync: syncVoid,
  pathExists: asyncFalse, pathExistsSync: syncFalse,
  readJson: asyncNull, readJsonSync: syncNull, readJSON: asyncNull, readJSONSync: syncNull,
  writeJson: asyncVoid, writeJsonSync: syncVoid, writeJSON: asyncVoid, writeJSONSync: syncVoid,
  outputJson: asyncVoid, outputJsonSync: syncVoid, outputJSON: asyncVoid, outputJSONSync: syncVoid,
  remove: asyncVoid, removeSync: syncVoid,
}
JS
cat > /workspace/lib/esm.mjs <<'JS'
import api from './index.js'
export const copy = api.copy
export const copySync = api.copySync
export const emptyDir = api.emptyDir
export const emptyDirSync = api.emptyDirSync
export const emptydir = api.emptydir
export const emptydirSync = api.emptydirSync
export const ensureDir = api.ensureDir
export const ensureDirSync = api.ensureDirSync
export const mkdirs = api.mkdirs
export const mkdirsSync = api.mkdirsSync
export const mkdirp = api.mkdirp
export const mkdirpSync = api.mkdirpSync
export const ensureFile = api.ensureFile
export const ensureFileSync = api.ensureFileSync
export const createFile = api.createFile
export const createFileSync = api.createFileSync
export const ensureLink = api.ensureLink
export const ensureLinkSync = api.ensureLinkSync
export const createLink = api.createLink
export const createLinkSync = api.createLinkSync
export const ensureSymlink = api.ensureSymlink
export const ensureSymlinkSync = api.ensureSymlinkSync
export const createSymlink = api.createSymlink
export const createSymlinkSync = api.createSymlinkSync
export const move = api.move
export const moveSync = api.moveSync
export const outputFile = api.outputFile
export const outputFileSync = api.outputFileSync
export const pathExists = api.pathExists
export const pathExistsSync = api.pathExistsSync
export const readJson = api.readJson
export const readJsonSync = api.readJsonSync
export const readJSON = api.readJSON
export const readJSONSync = api.readJSONSync
export const writeJson = api.writeJson
export const writeJsonSync = api.writeJsonSync
export const writeJSON = api.writeJSON
export const writeJSONSync = api.writeJSONSync
export const outputJson = api.outputJson
export const outputJsonSync = api.outputJsonSync
export const outputJSON = api.outputJSON
export const outputJSONSync = api.outputJSONSync
export const remove = api.remove
export const removeSync = api.removeSync
export default api
JS
