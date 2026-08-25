from __future__ import annotations

import io
import json
import os
import sys

candidate_site = os.environ.get("NL2REPO_TQDM_CANDIDATE_SITE", "/tmp/candidate-site")
if candidate_site not in sys.path:
    sys.path.insert(0, candidate_site)

from tqdm import tqdm, trange
from tqdm.contrib import tmap, tenumerate, tzip
from tqdm.utils import disp_len, disp_trim


def format_helpers() -> dict[str, object]:
    return {
        "sizeof": tqdm.format_sizeof(1024),
        "interval": tqdm.format_interval(3661),
        "number": tqdm.format_num(12.3456),
        "meter": tqdm.format_meter(
            3,
            10,
            2.0,
            rate=1.5,
            prefix="run",
            ascii=True,
            unit="item",
            bar_format="{desc}|{bar}|{n_fmt}/{total_fmt}|{elapsed}|{rate_fmt}",
        ),
    }


def disabled_iteration() -> dict[str, object]:
    output = io.StringIO()
    bar = tqdm(range(3), file=output, disable=True)
    values = list(bar)
    return {"values": values, "n": bar.n, "total": bar.total, "output": output.getvalue()}


def update_reset() -> dict[str, object]:
    bar = tqdm(total=5, file=io.StringIO(), mininterval=10**9, miniters=1)
    bar.update(2)
    before = [bar.n, bar.total]
    bar.reset(total=3)
    after_reset = [bar.n, bar.total]
    bar.update(1)
    after_update = [bar.n, bar.total]
    bar.close()
    bar.close()
    return {"before": before, "after_reset": after_reset, "after_update": after_update}


def lazy_iteration() -> dict[str, object]:
    consumed: list[int] = []

    def values():
        for value in range(2):
            consumed.append(value)
            yield value

    bar = tqdm(values(), disable=True)
    constructed = list(consumed)
    iterator = iter(bar)
    first = next(iterator)
    after_first = list(consumed)
    rest = list(iterator)
    return {"constructed": constructed, "first": first, "after_first": after_first, "rest": rest}


def utilities() -> dict[str, object]:
    coloured = "a\x1b[31mred\x1b[0m"
    return {
        "disp_len": disp_len(coloured),
        "disp_trim": disp_trim("abcdef", 4),
        "enumerate": [list(item) for item in tenumerate("ab", start=2)],
        "zip": [list(item) for item in tzip([1, 2], [3, 4])],
        "map": list(tmap(lambda value: value * 2, [1, 2, 3])),
    }


def public_api() -> dict[str, object]:
    return {
        "range": list(trange(3, disable=True)),
        "same_class": tqdm is __import__("tqdm.std", fromlist=["tqdm"]).tqdm,
        "module": tqdm.__module__,
    }


def format_width() -> dict[str, object]:
    return {
        "meter": tqdm.format_meter(
            2,
            4,
            0.0,
            ncols=20,
            rate=4.0,
            prefix="x",
            ascii=True,
            unit="it",
        ),
    }


def context_manager() -> dict[str, object]:
    with tqdm(range(2), disable=True) as bar:
        values = list(bar)
    return {"values": values, "disabled": bar.disable, "n": bar.n}


OPERATIONS = {
    "format_helpers": format_helpers,
    "disabled_iteration": disabled_iteration,
    "update_reset": update_reset,
    "lazy_iteration": lazy_iteration,
    "utilities": utilities,
    "public_api": public_api,
    "format_width": format_width,
    "context_manager": context_manager,
}


def main() -> None:
    for line in sys.stdin:
        request = json.loads(line)
        try:
            result = OPERATIONS[request["operation"]]()
            response = {"id": request["id"], "ok": True, "result": result}
        except Exception as exc:
            response = {"id": request.get("id"), "ok": False, "error": type(exc).__name__}
        print(json.dumps(response, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
