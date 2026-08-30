from __future__ import annotations

import json
from typing import Any

from nl2repobench.verification.candidate_client import CandidateCallResult, execute_script


CASES: dict[str, str] = {
    "api_surface": r'''
import smmap
import smmap.buf
import smmap.mman
import smmap.util
result = (
    smmap.__version__ == "5.0.3"
    and smmap.SlidingWindowMapBuffer is smmap.buf.SlidingWindowMapBuffer
    and smmap.WindowCursor is smmap.mman.WindowCursor
    and smmap.StaticWindowMapManager is smmap.mman.StaticWindowMapManager
    and smmap.SlidingWindowMapManager is smmap.mman.SlidingWindowMapManager
    and isinstance(smmap.util.ALLOCATIONGRANULARITY, int)
    and smmap.util.ALLOCATIONGRANULARITY > 0
)
''',
    "alignment": r'''
from smmap.util import ALLOCATIONGRANULARITY, align_to_mmap, is_64_bit
g = ALLOCATIONGRANULARITY
result = (
    isinstance(is_64_bit(), bool)
    and align_to_mmap(0, False) == 0
    and align_to_mmap(g + 1, False) == g
    and align_to_mmap(g + 1, True) == 2 * g
    and align_to_mmap(g, True) == g
)
''',
    "window_arithmetic": r'''
from smmap.util import ALLOCATIONGRANULARITY, MapWindow
g = ALLOCATIONGRANULARITY
w = MapWindow(3, 5)
before = (w.ofs, w.size, w.ofs_end())
w.align()
aligned = w.ofs % g == 0 and w.ofs <= 3 and w.ofs_end() >= 8
left = MapWindow(w.ofs, w.size)
left.extend_left_to(MapWindow(max(0, w.ofs - 7), 7), 12)
left_state = (left.ofs, left.size)
left.extend_left_to(MapWindow(0, 100), 12)
left_idempotent = (left.ofs, left.size) == left_state and left.size <= 12
right = MapWindow(0, 2)
right.extend_right_to(MapWindow(2, 9), 8)
right_state = (right.ofs, right.size)
right.extend_right_to(MapWindow(2, 9), 8)
result = before == (3, 5, 8) and aligned and left_idempotent and right.size <= 8 and (right.ofs, right.size) == right_state
''',
    "region_path": r'''
import os
import tempfile
from smmap.util import MapRegion, MapRegionList
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"0123456789abcdef")
    path = handle.name
try:
    region = MapRegion(path, 0, 7)
    view = memoryview(region.buffer())
    result = (
        region.ofs_begin() == 0 and region.size() == 7 and region.ofs_end() == 7
        and region.includes_ofs(0) and region.includes_ofs(6) and not region.includes_ofs(7)
        and bytes(view) == b"0123456" and bytes(region.map()[2:7]) == b"23456"
        and view.readonly and region.client_count() == 1
    )
    del view
    region.release()
    result = result and region.client_count() == 1
    listing = MapRegionList(path)
    result = result and listing.path_or_fd() == path and listing.file_size() == 16
finally:
    os.unlink(path)
result = result
''',
    "region_fd": r'''
import os
import tempfile
from smmap.util import MapRegion, MapRegionList
fd, path = tempfile.mkstemp()
try:
    os.write(fd, b"abcdefghij")
    os.lseek(fd, 0, os.SEEK_SET)
    region = MapRegion(fd, 0, 4)
    listing = MapRegionList(fd)
    result = bytes(region.buffer()) == b"abcd" and listing.path_or_fd() == fd and listing.file_size() == 10
    del region
    os.fstat(fd)
finally:
    os.close(fd)
    os.unlink(path)
result = result
''',
    "cursor_association": r'''
import os
import tempfile
from smmap.mman import StaticWindowMapManager
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"abcdefghij")
    path = handle.name
try:
    manager = StaticWindowMapManager()
    cursor = manager.make_cursor(path)
    initial = cursor.is_associated() and not cursor.is_valid() and cursor.path_or_fd() == path
    used = cursor.use_region(2, 4) is cursor
    result = initial and used and cursor.is_valid() and cursor.ofs_begin() == 2 and cursor.ofs_end() == 6 and bytes(cursor.buffer()) == b"cdef"
    try:
        cursor.fd()
    except ValueError:
        wrong_fd = True
    else:
        wrong_fd = False
    cursor.unuse_region()
    result = result and wrong_fd and not cursor.is_valid()
finally:
    manager.collect()
    os.unlink(path)
result = result
''',
    "static_manager": r'''
import os
import tempfile
from smmap.mman import StaticWindowMapManager
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(bytes(range(32)))
    path = handle.name
try:
    manager = StaticWindowMapManager(window_size=0, max_memory_size=0, max_open_handles=4)
    cursor = manager.make_cursor(path)
    cursor.use_region(0, 0)
    mapped = manager.mapped_memory_size()
    open_files = manager.num_open_files()
    result = (
        cursor.size() == 32 and bytes(cursor.buffer()) == bytes(range(32))
        and manager.window_size() >= 0 and manager.max_file_handles() == 4
        and manager.max_mapped_memory_size() > 0 and mapped >= 32
        and manager.num_file_handles() >= 1 and open_files >= 1
    )
    cursor.unuse_region()
    freed = manager.collect()
    result = result and freed >= 1 and manager.num_file_handles() == 0
finally:
    os.unlink(path)
''',
    "sliding_manager": r'''
import os
import tempfile
from smmap.mman import SlidingWindowMapManager
from smmap.buf import SlidingWindowMapBuffer
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"0123456789abcdef")
    path = handle.name
try:
    manager = SlidingWindowMapManager(window_size=4, max_memory_size=0, max_open_handles=8)
    cursor = manager.make_cursor(path)
    buffer = SlidingWindowMapBuffer(cursor, 0, 16)
    result = len(buffer) == 16 and buffer[0] == ord("0") and buffer[-1] == ord("f")
    result = result and buffer[2:13] == b"23456789abc"
    buffer.end_access()
    result = result and manager.collect() >= 1
finally:
    os.unlink(path)
''',
    "buffer_access": r'''
import os
import tempfile
from smmap.buf import SlidingWindowMapBuffer
from smmap.mman import SlidingWindowMapManager
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"abcdefghijklmnop")
    path = handle.name
try:
    cursor = SlidingWindowMapManager(window_size=4).make_cursor(path)
    buffer = SlidingWindowMapBuffer(cursor, offset=0, size=16)
    result = len(buffer) == 16 and buffer[0] == ord("a") and buffer[-1] == ord("p") and buffer[1:8] == b"bcdefgh" and buffer[-5:-1] == b"lmno"
finally:
    os.unlink(path)
''',
    "buffer_lifecycle": r'''
import os
import tempfile
from smmap.buf import SlidingWindowMapBuffer
from smmap.mman import StaticWindowMapManager
buffer = SlidingWindowMapBuffer()
result = buffer.cursor() is None
buffer.end_access()
result = result and len(buffer) == 0
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"hello")
    path = handle.name
try:
    cursor = StaticWindowMapManager().make_cursor(path)
    result = result and buffer.begin_access(cursor, 1, 3) and len(buffer) == 3
    buffer.end_access()
    buffer.end_access()
    result = result and len(buffer) == 0
    with SlidingWindowMapBuffer(cursor, 0, 5) as scoped:
        result = result and bytes(scoped[0:5]) == b"hello"
    result = result and len(scoped) == 0
finally:
    os.unlink(path)
''',
    "cursor_copy_assign": r'''
import os
import tempfile
from smmap.mman import StaticWindowMapManager, WindowCursor
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"copy-me")
    path = handle.name
try:
    manager = StaticWindowMapManager()
    first = manager.make_cursor(path)
    first.use_region(1, 3)
    second = WindowCursor(manager)
    second.assign(first)
    result = second.is_associated() and second.is_valid() and bytes(second.buffer()) == b"opy"
    second.unuse_region()
    first.unuse_region()
    result = result and manager.collect() >= 1
finally:
    os.unlink(path)
''',
    "region_refcounts": r'''
import os
import tempfile
from smmap.util import MapRegion
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"refcount")
    path = handle.name
try:
    region = MapRegion(path, 0, 8)
    result = region.client_count() == 1 and not region.increment_client_count(1) and region.client_count() == 2
    result = result and not region.increment_client_count(-1) and region.client_count() == 1
    result = result and region.increment_client_count(-1) and region.client_count() == 0
    result = result
finally:
    os.unlink(path)
''',
    "manager_options": r'''
import os
import tempfile
from smmap.mman import SlidingWindowMapManager
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(b"options")
    path = handle.name
try:
    manager = SlidingWindowMapManager(window_size=4, max_memory_size=64, max_open_handles=3)
    result = manager.window_size() == 4 and manager.max_mapped_memory_size() == 64 and manager.max_file_handles() == 3
    result = result and manager.force_map_handle_removal_win(path) is None
    result = result
finally:
    os.unlink(path)
''',
    "error_contract": r'''
from smmap.buf import SlidingWindowMapBuffer
from smmap.mman import WindowCursor
result = True
try:
    WindowCursor().buffer()
except (AttributeError, ValueError, RuntimeError):
    pass
else:
    result = False
buffer = SlidingWindowMapBuffer()
try:
    buffer[0]
except (AttributeError, IndexError, ValueError, RuntimeError):
    pass
else:
    result = False
try:
    WindowCursor().use_region()
except (AttributeError, ValueError, RuntimeError):
    pass
else:
    result = False
try:
    from smmap.util import MapRegion
    MapRegion("/definitely/missing/smmap-file", 0, 1)
except (OSError, ValueError):
    pass
else:
    result = False
    result = result
''',
    "deterministic_reads": r'''
import os
import tempfile
from smmap.buf import SlidingWindowMapBuffer
from smmap.mman import SlidingWindowMapManager, StaticWindowMapManager
payload = bytes((index * 37 + 11) % 256 for index in range(97))
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(payload)
    path = handle.name
try:
    a = SlidingWindowMapBuffer(StaticWindowMapManager().make_cursor(path), 0, 97)
    b = SlidingWindowMapBuffer(SlidingWindowMapManager(window_size=9).make_cursor(path), 0, 97)
    result = bytes(a[0:97]) == payload and bytes(b[0:97]) == payload and bytes(a[0:97]) == bytes(b[0:97])
finally:
    os.unlink(path)
''',
    "tutorial_flow": r'''
import os
import tempfile
from smmap.buf import SlidingWindowMapBuffer
from smmap.mman import SlidingWindowMapManager
payload = b"header|payload|trailer"
with tempfile.NamedTemporaryFile(delete=False) as handle:
    handle.write(payload)
    path = handle.name
try:
    manager = SlidingWindowMapManager(window_size=5)
    cursor = manager.make_cursor(path)
    buffer = SlidingWindowMapBuffer(cursor, offset=0, size=len(payload))
    result = bytes(buffer[7:14]) == b"payload" and cursor.is_valid()
    buffer.end_access()
    cursor.unuse_region()
    result = result and manager.collect() >= 1
finally:
    os.unlink(path)
''',
}


def observe(source: str) -> dict[str, Any]:
    result: CandidateCallResult = execute_script(source, timeout_sec=12.0)
    if result.ok:
        return {"passed": result.value is True, "actual": result.value}
    return {
        "passed": False,
        "actual": f"{result.exception_type}: {(result.exception_message or '')[-500:]}",
    }


def main() -> int:
    leaves = []
    for case_id, source in CASES.items():
        observed = observe(source)
        leaves.append(
            {
                "id": f"smmap/{case_id}",
                "status": "passed" if observed["passed"] else "failed",
                "message": "" if observed["passed"] else json.dumps(observed, sort_keys=True)[:1000],
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
