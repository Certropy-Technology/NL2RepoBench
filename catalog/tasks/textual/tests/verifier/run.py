from __future__ import annotations

import json

from nl2repobench.verification import candidate_client as c


def leaf(leaf_id: str, passed: bool, message: str = "") -> dict[str, str]:
    return {"id": leaf_id, "status": "passed" if passed else "failed", "message": message}


def eq(
    leaf_id: str,
    module: str,
    attribute: str,
    args: list[object],
    expected: object,
) -> dict[str, str]:
    result = c.call(module, attribute, *args)
    message = f"expected {expected!r}, got {result!r}"
    return leaf(leaf_id, result.ok and result.value == expected, message)


def exc(
    leaf_id: str,
    module: str,
    attribute: str,
    args: list[object],
    expected_type: str,
) -> dict[str, str]:
    result = c.call(module, attribute, *args)
    message = f"expected {expected_type}, got {result!r}"
    return leaf(leaf_id, not result.ok and result.exception_type == expected_type, message)


def main() -> None:
    leaves = [
        eq("slug-basic", "textual._slug", "slug", ["  Hello, World!  "], "hello-world"),
        eq("slug-unicode", "textual._slug", "slug", ["Café 🚀"], "caf%C3%A9-"),
        eq("slug-empty", "textual._slug", "slug", ["!!!"], ""),
        eq("tcss-id", "textual._slug", "slug_for_tcss_id", ["Hello World!"], "hello-world21"),
        eq("tcss-id-special", "textual._slug", "slug_for_tcss_id", ["A/B"], "a2fb"),
        eq("camel-simple", "textual.case", "camel_to_snake", ["HelloWorld"], "hello_world"),
        eq(
            "camel-acronym",
            "textual.case",
            "camel_to_snake",
            ["HTTPServerResponse"],
            "httpserver_response",
        ),
        eq("cell-ascii", "textual._cells", "cell_len", ["hello"], 5),
        eq("cell-combining", "textual._cells", "cell_len", ["Cafe\u0301"], 4),
        eq("cell-cjk", "textual._cells", "cell_len", ["界"], 2),
        eq("column-tab", "textual._cells", "cell_width_to_column_index", ["ab\tcd", 4, 4], 3),
        eq("wrap-words", "textual._wrap", "compute_wrap_offsets", ["one two three", 7, 4], [4, 8]),
        eq("wrap-fold", "textual._wrap", "compute_wrap_offsets", ["abcdefgh", 3, 4], [3, 6]),
        eq("clamp-low", "textual.geometry", "clamp", [-1, 0, 10], 0),
        eq("clamp-high", "textual.geometry", "clamp", [12, 0, 10], 10),
        eq("offset-value", "textual.geometry", "Offset", [3, 4], [3, 4]),
        eq("size-value", "textual.geometry", "Size", [80, 24], [80, 24]),
        eq(
            "region-corners",
            "textual.geometry",
            "Region.from_corners",
            [2, 3, 12, 19],
            [2, 3, 10, 16],
        ),
        eq("region-value", "textual.geometry", "Region", [1, 2, 10, 20], [1, 2, 10, 20]),
        eq(
            "color-hex",
            "textual.color",
            "Color.parse",
            ["#123456"],
            [18, 52, 86, 1.0, None, False],
        ),
        eq("color-red", "textual.color", "Color.parse", ["red"], [255, 0, 0, 1.0, None, False]),
        eq(
            "color-hsl",
            "textual.color",
            "Color.from_hsl",
            [1 / 3, 1, 0.5],
            [0, 255, 0, 1.0, None, False],
        ),
        eq(
            "markup-escape",
            "textual.markup",
            "escape",
            ["[bold]hello[/bold]"],
            "\\[bold]hello\\[/bold]",
        ),
        exc(
            "color-invalid",
            "textual.color",
            "Color.parse",
            ["not-a-color"],
            "textual.color.ColorParseError",
        ),
    ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":")))


if __name__ == "__main__":
    main()
