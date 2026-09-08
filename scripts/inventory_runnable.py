#!/usr/bin/env python3
"""Trusted-runnable inventory + cross-check against a benchmark queue.

A task is TRUSTED (safe to run in a benchmark) when:
  (a) source lifecycle status is 'controls-passed' AND a compiled projection
      exists under catalog/tasks/<task>/, OR
  (b) lifecycle is 'piloted' AND its production-evidence.json shows
      oracle.valid=true AND oracle.reward>=0.80 AND every control reward<=0.20.

Usage:
  python3 scripts/inventory_runnable.py <queue.log>   # report trusted vs not
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path('/data/NL2RepoBench-integration-20260827')
SOURCES = ROOT / 'catalog/sources'
TASKS = ROOT / 'catalog/tasks'


def lifecycle_status(task):
    p = SOURCES / task / 'task.toml'
    if not p.exists():
        return None
    try:
        import tomllib
        return tomllib.load(open(p, 'rb')).get('lifecycle', {}).get('status')
    except Exception:
        return None


def projection_ok(task):
    return (TASKS / task / 'task.toml').exists()


def prod_evidence_trusted(task):
    pe = SOURCES / task / 'production-evidence.json'
    if not pe.exists():
        return False
    try:
        d = json.load(open(pe))
    except Exception:
        return False
    o = d.get('oracle', {})
    if not (o.get('valid') and (o.get('reward') or 0) >= 0.80):
        return False
    controls = d.get('controls', {})
    if controls and any((v or {}).get('reward', 0) > 0.20 for v in controls.values()):
        return False
    return True


def is_trusted(task):
    st = lifecycle_status(task)
    if st == 'controls-passed' and projection_ok(task):
        return True
    if st == 'piloted' and prod_evidence_trusted(task):
        return True
    return False


def main():
    trusted = {d.name for d in SOURCES.iterdir() if d.is_dir() and is_trusted(d.name)}
    print(f'trusted runnable in catalog: {len(trusted)}')

    if len(sys.argv) < 2:
        return
    q = (ROOT / sys.argv[1]).read_text().splitlines()
    hdr = [l for l in q if l.startswith('queue_start=')]
    if not hdr:
        print('no queue_start line in', sys.argv[1])
        return
    raw = hdr[0].split('tasks=')[1].split(',')
    tasks = [t.strip() for t in raw if t.strip() and not t.startswith('concurrency=')]
    done = set(re.findall(r'^done\[([^\]]+)\]', '\n'.join(q), re.M))
    remaining = [t for t in tasks if t not in done]
    not_trusted = [t for t in tasks if t not in trusted]
    not_trusted_remaining = [t for t in remaining if t not in trusted]
    print(f'queue tasks: {len(tasks)}, done: {len(done)}, remaining: {len(remaining)}')
    print(f'NOT trusted (any): {len(not_trusted)} | NOT trusted & still remaining: {len(not_trusted_remaining)}')
    for t in not_trusted_remaining:
        print(f'  WILL-RUN-UNTRUSTED: {t} (status={lifecycle_status(t)})')


if __name__ == '__main__':
    main()
