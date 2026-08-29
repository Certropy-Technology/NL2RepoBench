#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"espree","version":"11.2.0","type":"module","exports":{".":"./index.js","./package.json":"./package.json"}}
JSON
cat > package-lock.json <<'JSON'
{"name":"espree","version":"11.2.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"espree","version":"11.2.0","type":"module"}}}
JSON
cat > index.js <<'JS'
export const name='espree'; export const version='11.2.0'; export const parse=()=>({type:'Program',body:[],sourceType:'script'}); export const tokenize=()=>[]; export const Syntax={}; export const VisitorKeys={}; export const latestEcmaVersion=17; export const supportedEcmaVersions=[3,5,6,7,8,9,10,11,12,13,14,15,16,17];
JS
