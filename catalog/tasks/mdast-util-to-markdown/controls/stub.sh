#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'EOF'
{"name":"mdast-util-to-markdown","version":"2.1.2","type":"module","exports":"./index.js","types":"./index.d.ts"}
EOF
cat > /workspace/index.js <<'EOF'
export function toMarkdown() { return ''; }
export const defaultHandlers = {};
EOF
cat > /workspace/index.d.ts <<'EOF'
export function toMarkdown(tree: unknown, options?: unknown): string;
export const defaultHandlers: Record<string, Function>;
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"mdast-util-to-markdown","version":"2.1.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-to-markdown","version":"2.1.2"}}}
EOF
