#!/usr/bin/env python3
"""Build a trusted-runnable inventory and cross-check against the Fable R2 queue.

Trusted runnable = source lifecycle status 'controls-passed' (Oracle + controls
actually executed and passed) AND the compiled projection under catalog/tasks
exists.

Usage:
  python3 scripts/inventory_runnable.py <queue_file>   # cross-check vs a queue
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path('/data/NL2RepoBench-integration-20260827')
CATALOG = ROOT / 'catalog'
SOURCES = CATALOG / 'sources'
TASKS = CATALOG / 'tasks'  # compiled projections (may be a symlink or dir)


def source_status(task):
    p = SOURCES / task / 'task.toml'
    if not p.exists():
        return None
    t = p.read_text()
    m = re.search(r'\[lifecycle\]\nstatus\s*=\s*"([^"]+)"', t)
    return m.group(1) if m else None


def projection_ok(task):
    pt = TASKS / task / 'task.toml'
    return pt.exists()


def main():
    trusted = {}
    for d in sorted(SOURCES.iterdir()):
        if not d.is_dir():
            continue
        st = source_status(d.name)
        if st == 'controls-passed' and projection_ok(d.name):
            trusted[d.name] = 'controls-passed'
    print(f'trusted runnable (controls-passed + projection): {len(trusted)}')

    # cross-check the queue
    qfile = sys.argv[1] if len(sys.argv) > 1 else None
    if qfile:
        q = (ROOT / qfile).read_text().splitlines()
        hdr = [l for l in q if l.startswith('queue_start=')]
        if not hdr:
            print('no queue_start line in', qfile)
            return
        tasks = hdr[0].split('tasks=')[1].split(',')
        done = set(re.findall(r'^done\[([^\]]+)\]', '\n'.join(q), re.M))
        not_trusted = [t for t in tasks if t not in trusted]
        print(f'queue tasks: {len(tasks)}, trusted: {sum(1 for t in tasks if t in trusted)}, NOT trusted: {len(not_trusted)}')
        for t in not_trusted:
            print(f'  NOT-TRUSTED: {t} (status={source_status(t)})')
        # also report trusted-but-queued (good)
        print('trusted runnable actually in queue (valid benchmark):',
              sum(1 for t in tasks if t in trusted))


if __name__ == '__main__':
    main()
