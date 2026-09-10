"""Private deterministic scenarios for the wcag-contrast-ratio public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/gsnedders/wcag-contrast-ratio,
v0.9, immutable). The candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    (
        "contrast_black_white",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))',
        {'ok': True, 'value': 21.0},
    ),
    (
        "contrast_white_black_symmetry",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 1.0, 1.0), (0.0, 0.0, 0.0))',
        {'ok': True, 'value': 21.0},
    ),
    (
        "contrast_black_identical",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))',
        {'ok': True, 'value': 1.0},
    ),
    (
        "contrast_white_identical",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 1.0, 1.0), (1.0, 1.0, 1.0))',
        {'ok': True, 'value': 1.0},
    ),
    (
        "contrast_gray_00_01",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.1, 0.1, 0.1))',
        {'ok': True, 'value': 1.2004565114973809},
    ),
    (
        "contrast_gray_00_02",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.2, 0.2, 0.2))',
        {'ok': True, 'value': 1.6620953314177012},
    ),
    (
        "contrast_gray_00_05",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.5, 0.5, 0.5))',
        {'ok': True, 'value': 5.280822809644651},
    ),
    (
        "contrast_gray_00_08",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.8, 0.8, 0.8))',
        {'ok': True, 'value': 13.076546777106755},
    ),
    (
        "contrast_gray_00_10",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))',
        {'ok': True, 'value': 21.0},
    ),
    (
        "contrast_gray_01_03",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.1, 0.1, 0.1), (0.3, 0.3, 0.3))',
        {'ok': True, 'value': 2.053201506228396},
    ),
    (
        "contrast_gray_02_04",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.2, 0.2, 0.2), (0.4, 0.4, 0.4))',
        {'ok': True, 'value': 2.200455269889225},
    ),
    (
        "contrast_gray_03_05",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.3, 0.3, 0.3), (0.5, 0.5, 0.5))',
        {'ok': True, 'value': 2.1425136118708323},
    ),
    (
        "contrast_gray_04_06",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.4, 0.4, 0.4), (0.6, 0.6, 0.6))',
        {'ok': True, 'value': 2.015366986439086},
    ),
    (
        "contrast_gray_05_07",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.5, 0.5, 0.5), (0.7, 0.7, 0.7))',
        {'ok': True, 'value': 1.8860258349603407},
    ),
    (
        "contrast_gray_05_10",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.5, 0.5, 0.5), (1.0, 1.0, 1.0))',
        {'ok': True, 'value': 3.976653024912438},
    ),
    (
        "contrast_gray_06_08",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.6, 0.6, 0.6), (0.8, 0.8, 0.8))',
        {'ok': True, 'value': 1.7740687957755426},
    ),
    (
        "contrast_gray_07_09",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.7, 0.7, 0.7), (0.9, 0.9, 0.9))',
        {'ok': True, 'value': 1.6815899094707267},
    ),
    (
        "contrast_gray_08_10",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.8, 0.8, 0.8), (1.0, 1.0, 1.0))',
        {'ok': True, 'value': 1.6059285649300714},
    ),
    (
        "contrast_gray_05_05",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))',
        {'ok': True, 'value': 1.0},
    ),
    (
        "contrast_color_red_blue",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 0.0, 0.0), (0.0, 0.0, 1.0))',
        {'ok': True, 'value': 2.148936170212766},
    ),
    (
        "contrast_color_red_green",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))',
        {'ok': True, 'value': 2.9139375476009137},
    ),
    (
        "contrast_color_red_yellow",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 0.0, 0.0), (1.0, 1.0, 0.0))',
        {'ok': True, 'value': 3.7235338918507237},
    ),
    (
        "contrast_color_red_black",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 0.0, 0.0), (0.0, 0.0, 0.0))',
        {'ok': True, 'value': 5.252},
    ),
    (
        "contrast_color_green_blue",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 1.0, 0.0), (0.0, 0.0, 1.0))',
        {'ok': True, 'value': 6.261865793780687},
    ),
    (
        "contrast_color_green_yellow",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 1.0, 0.0), (1.0, 1.0, 0.0))',
        {'ok': True, 'value': 1.277835859905907},
    ),
    (
        "contrast_color_green_cyan",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 1.0, 0.0), (0.0, 1.0, 1.0))',
        {'ok': True, 'value': 1.0943544171458444},
    ),
    (
        "contrast_color_green_black",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 1.0, 0.0), (0.0, 0.0, 0.0))',
        {'ok': True, 'value': 15.303999999999998},
    ),
    (
        "contrast_color_blue_yellow",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 1.0), (1.0, 1.0, 0.0))',
        {'ok': True, 'value': 8.00163666121113},
    ),
    (
        "contrast_color_blue_cyan",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 1.0), (0.0, 1.0, 1.0))',
        {'ok': True, 'value': 6.852700490998363},
    ),
    (
        "contrast_color_blue_magenta",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 1.0), (1.0, 0.0, 1.0))',
        {'ok': True, 'value': 2.7397708674304417},
    ),
    (
        "contrast_color_blue_black",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 1.0), (0.0, 0.0, 0.0))',
        {'ok': True, 'value': 2.444},
    ),
    (
        "contrast_color_yellow_cyan",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 1.0, 0.0), (0.0, 1.0, 1.0))',
        {'ok': True, 'value': 1.1676618103654168},
    ),
    (
        "contrast_color_yellow_magenta",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 1.0, 0.0), (1.0, 0.0, 1.0))',
        {'ok': True, 'value': 2.9205495818399045},
    ),
    (
        "contrast_color_yellow_black",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((1.0, 1.0, 0.0), (0.0, 0.0, 0.0))',
        {'ok': True, 'value': 19.555999999999997},
    ),
    (
        "contrast_upstream_green198_blue198",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.7764705882352941, 0.0), (0.0, 0.0, 0.7764705882352941))',
        {'ok': True, 'value': 5.000229313902297},
    ),
    (
        "contrast_edge_000_001",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.01, 0.01, 0.01))',
        {'ok': True, 'value': 1.0154798761609907},
    ),
    (
        "contrast_edge_000_005",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.0, 0.0, 0.0), (0.05, 0.05, 0.05))',
        {'ok': True, 'value': 1.0787187900817792},
    ),
    (
        "contrast_edge_095_100",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.95, 0.95, 0.95), (1.0, 1.0, 1.0))',
        {'ok': True, 'value': 1.1170148513914115},
    ),
    (
        "contrast_edge_020_060",
        'import wcag_contrast_ratio as contrast\nresult = contrast.rgb((0.2, 0.3, 0.4), (0.6, 0.7, 0.8))',
        {'ok': True, 'value': 4.0476761805122585},
    ),
    (
        "passes_AA_normal_00",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(0.0, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AA_large_00",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(0.0, large=True)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AA_normal_29",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(2.9, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AA_large_29",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(2.9, large=True)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AA_normal_30",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(3.0, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AA_large_30",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(3.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_normal_40",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(4.0, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AA_large_40",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(4.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_normal_45",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(4.5, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_large_45",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(4.5, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_normal_70",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(7.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_large_70",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(7.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_normal_100",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(10.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_large_100",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(10.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_normal_150",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(15.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_large_150",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(15.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_normal_210",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(21.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AA_large_210",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AA(21.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_00",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(0.0, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AAA_large_00",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(0.0, large=True)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AAA_normal_30",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(3.0, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AAA_large_30",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(3.0, large=True)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AAA_normal_45",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(4.5, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AAA_large_45",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(4.5, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_69",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(6.9, large=False)',
        {'ok': True, 'value': False},
    ),
    (
        "passes_AAA_large_69",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(6.9, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_70",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(7.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_large_70",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(7.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_100",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(10.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_large_100",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(10.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_150",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(15.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_large_150",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(15.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_200",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(20.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_large_200",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(20.0, large=True)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_normal_210",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(21.0, large=False)',
        {'ok': True, 'value': True},
    ),
    (
        "passes_AAA_large_210",
        'import wcag_contrast_ratio as contrast\nresult = contrast.passes_AAA(21.0, large=True)',
        {'ok': True, 'value': True},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
