#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
printf '%s\n' '{"name":"hast-util-to-estree","version":"3.1.3","type":"module","exports":"./index.js"}' > /workspace/package.json
printf '%s\n' '{"name":"hast-util-to-estree","version":"3.1.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"hast-util-to-estree","version":"3.1.3"}}}' > /workspace/package-lock.json
printf '%s\n' 'export const toEstree = () => ({type:"Program",body:[],sourceType:"module",comments:[]}); export const defaultHandlers = {};' > /workspace/index.js
