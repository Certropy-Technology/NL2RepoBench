"""Private deterministic scenarios for the termcolor public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/termcolor/termcolor,
v3.3.0, immutable revision 0980eb52aa867fc32f70859a61c0609501b73a99). The
candidate runner executes the script and reads the ``result`` binding.
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
    # Constants exports
    (
        "exports-all",
        "import termcolor\nresult = sorted(termcolor.__all__)",
        {"ok": True, "value": ["ATTRIBUTES", "COLORS", "HIGHLIGHTS", "RESET", "can_colorize", "colored", "cprint"]},
    ),
    (
        "colors-red",
        "from termcolor import COLORS\nresult = COLORS['red']",
        {"ok": True, "value": 31},
    ),
    (
        "colors-green",
        "from termcolor import COLORS\nresult = COLORS['green']",
        {"ok": True, "value": 32},
    ),
    (
        "colors-blue",
        "from termcolor import COLORS\nresult = COLORS['blue']",
        {"ok": True, "value": 34},
    ),
    (
        "colors-yellow",
        "from termcolor import COLORS\nresult = COLORS['yellow']",
        {"ok": True, "value": 33},
    ),
    (
        "colors-black",
        "from termcolor import COLORS\nresult = COLORS['black']",
        {"ok": True, "value": 30},
    ),
    (
        "colors-grey-alias",
        "from termcolor import COLORS\nresult = COLORS['grey']",
        {"ok": True, "value": 30},
    ),
    (
        "colors-magenta",
        "from termcolor import COLORS\nresult = COLORS['magenta']",
        {"ok": True, "value": 35},
    ),
    (
        "colors-cyan",
        "from termcolor import COLORS\nresult = COLORS['cyan']",
        {"ok": True, "value": 36},
    ),
    (
        "colors-white",
        "from termcolor import COLORS\nresult = COLORS['white']",
        {"ok": True, "value": 97},
    ),
    (
        "colors-light-grey",
        "from termcolor import COLORS\nresult = COLORS['light_grey']",
        {"ok": True, "value": 37},
    ),
    (
        "colors-dark-grey",
        "from termcolor import COLORS\nresult = COLORS['dark_grey']",
        {"ok": True, "value": 90},
    ),
    (
        "colors-light-red",
        "from termcolor import COLORS\nresult = COLORS['light_red']",
        {"ok": True, "value": 91},
    ),
    (
        "colors-light-green",
        "from termcolor import COLORS\nresult = COLORS['light_green']",
        {"ok": True, "value": 92},
    ),
    (
        "colors-light-yellow",
        "from termcolor import COLORS\nresult = COLORS['light_yellow']",
        {"ok": True, "value": 93},
    ),
    (
        "colors-light-blue",
        "from termcolor import COLORS\nresult = COLORS['light_blue']",
        {"ok": True, "value": 94},
    ),
    (
        "colors-light-magenta",
        "from termcolor import COLORS\nresult = COLORS['light_magenta']",
        {"ok": True, "value": 95},
    ),
    (
        "colors-light-cyan",
        "from termcolor import COLORS\nresult = COLORS['light_cyan']",
        {"ok": True, "value": 96},
    ),
    (
        "highlights-on-red",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_red']",
        {"ok": True, "value": 41},
    ),
    (
        "highlights-on-green",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_green']",
        {"ok": True, "value": 42},
    ),
    (
        "highlights-on-blue",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_blue']",
        {"ok": True, "value": 44},
    ),
    (
        "highlights-on-yellow",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_yellow']",
        {"ok": True, "value": 43},
    ),
    (
        "highlights-on-black",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_black']",
        {"ok": True, "value": 40},
    ),
    (
        "highlights-on-grey",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_grey']",
        {"ok": True, "value": 40},
    ),
    (
        "highlights-on-magenta",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_magenta']",
        {"ok": True, "value": 45},
    ),
    (
        "highlights-on-cyan",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_cyan']",
        {"ok": True, "value": 46},
    ),
    (
        "highlights-on-white",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_white']",
        {"ok": True, "value": 107},
    ),
    (
        "highlights-on-light-grey",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_grey']",
        {"ok": True, "value": 47},
    ),
    (
        "highlights-on-dark-grey",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_dark_grey']",
        {"ok": True, "value": 100},
    ),
    (
        "highlights-on-light-red",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_red']",
        {"ok": True, "value": 101},
    ),
    (
        "highlights-on-light-green",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_green']",
        {"ok": True, "value": 102},
    ),
    (
        "highlights-on-light-yellow",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_yellow']",
        {"ok": True, "value": 103},
    ),
    (
        "highlights-on-light-blue",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_blue']",
        {"ok": True, "value": 104},
    ),
    (
        "highlights-on-light-magenta",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_magenta']",
        {"ok": True, "value": 105},
    ),
    (
        "highlights-on-light-cyan",
        "from termcolor import HIGHLIGHTS\nresult = HIGHLIGHTS['on_light_cyan']",
        {"ok": True, "value": 106},
    ),
    (
        "attributes-bold",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['bold']",
        {"ok": True, "value": 1},
    ),
    (
        "attributes-dark",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['dark']",
        {"ok": True, "value": 2},
    ),
    (
        "attributes-italic",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['italic']",
        {"ok": True, "value": 3},
    ),
    (
        "attributes-underline",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['underline']",
        {"ok": True, "value": 4},
    ),
    (
        "attributes-blink",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['blink']",
        {"ok": True, "value": 5},
    ),
    (
        "attributes-reverse",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['reverse']",
        {"ok": True, "value": 7},
    ),
    (
        "attributes-concealed",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['concealed']",
        {"ok": True, "value": 8},
    ),
    (
        "attributes-strike",
        "from termcolor import ATTRIBUTES\nresult = ATTRIBUTES['strike']",
        {"ok": True, "value": 9},
    ),
    (
        "reset-constant",
        'from termcolor import RESET\nresult = RESET',
        {"ok": True, "value": "\\033[0m"},
    ),
    # can_colorize function
    (
        "can-colorize-force-true",
        "from termcolor import can_colorize\nresult = can_colorize(force_color=True)",
        {"ok": True, "value": True},
    ),
    (
        "can-colorize-no-true",
        "from termcolor import can_colorize\nresult = can_colorize(no_color=True)",
        {"ok": True, "value": False},
    ),
    (
        "can-colorize-no-overrides-force",
        "from termcolor import can_colorize\nresult = can_colorize(no_color=True, force_color=True)",
        {"ok": True, "value": False},
    ),
    # colored function - basic colors
    (
        "colored-red",
        'from termcolor import colored\nresult = colored("text", "red", force_color=True)',
        {"ok": True, "value": "\\033[31mtext\\033[0m"},
    ),
    (
        "colored-green",
        'from termcolor import colored\nresult = colored("text", "green", force_color=True)',
        {"ok": True, "value": "\\033[32mtext\\033[0m"},
    ),
    (
        "colored-blue",
        'from termcolor import colored\nresult = colored("text", "blue", force_color=True)',
        {"ok": True, "value": "\\033[34mtext\\033[0m"},
    ),
    (
        "colored-yellow",
        'from termcolor import colored\nresult = colored("text", "yellow", force_color=True)',
        {"ok": True, "value": "\\033[33mtext\\033[0m"},
    ),
    (
        "colored-black",
        'from termcolor import colored\nresult = colored("text", "black", force_color=True)',
        {"ok": True, "value": "\\033[30mtext\\033[0m"},
    ),
    (
        "colored-magenta",
        'from termcolor import colored\nresult = colored("text", "magenta", force_color=True)',
        {"ok": True, "value": "\\033[35mtext\\033[0m"},
    ),
    (
        "colored-cyan",
        'from termcolor import colored\nresult = colored("text", "cyan", force_color=True)',
        {"ok": True, "value": "\\033[36mtext\\033[0m"},
    ),
    (
        "colored-white",
        'from termcolor import colored\nresult = colored("text", "white", force_color=True)',
        {"ok": True, "value": "\\033[97mtext\\033[0m"},
    ),
    (
        "colored-light-colors",
        'from termcolor import colored\nresult = colored("text", "light_blue", force_color=True)',
        {"ok": True, "value": "\\033[94mtext\\033[0m"},
    ),
    # colored function - backgrounds
    (
        "colored-on-red",
        'from termcolor import colored\nresult = colored("text", on_color="on_red", force_color=True)',
        {"ok": True, "value": "\\033[41mtext\\033[0m"},
    ),
    (
        "colored-on-green",
        'from termcolor import colored\nresult = colored("text", on_color="on_green", force_color=True)',
        {"ok": True, "value": "\\033[42mtext\\033[0m"},
    ),
    (
        "colored-on-blue",
        'from termcolor import colored\nresult = colored("text", on_color="on_blue", force_color=True)',
        {"ok": True, "value": "\\033[44mtext\\033[0m"},
    ),
    # colored function - attributes
    (
        "colored-bold",
        'from termcolor import colored\nresult = colored("text", attrs=["bold"], force_color=True)',
        {"ok": True, "value": "\\033[1mtext\\033[0m"},
    ),
    (
        "colored-underline",
        'from termcolor import colored\nresult = colored("text", attrs=["underline"], force_color=True)',
        {"ok": True, "value": "\\033[4mtext\\033[0m"},
    ),
    (
        "colored-italic",
        'from termcolor import colored\nresult = colored("text", attrs=["italic"], force_color=True)',
        {"ok": True, "value": "\\033[3mtext\\033[0m"},
    ),
    # colored function - RGB tuples
    (
        "colored-rgb-foreground",
        'from termcolor import colored\nresult = colored("text", color=(255, 100, 50), force_color=True)',
        {"ok": True, "value": "\\033[38;2;255;100;50mtext\\033[0m"},
    ),
    (
        "colored-rgb-background",
        'from termcolor import colored\nresult = colored("text", on_color=(50, 60, 70), force_color=True)',
        {"ok": True, "value": "\\033[48;2;50;60;70mtext\\033[0m"},
    ),
    # colored function - combinations
    (
        "colored-color-and-background",
        'from termcolor import colored\nr = colored("text", "red", "on_blue", force_color=True)\nresult = ("\\\\033[31m" in r, "\\\\033[44m" in r, r.endswith("\\\\033[0m"))',
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "colored-multiple-attrs",
        'from termcolor import colored\nr = colored("text", attrs=["bold", "underline"], force_color=True)\nresult = ("\\\\033[1m" in r, "\\\\033[4m" in r)',
        {"ok": True, "value": [True, True]},
    ),
    # colored function - no_color override
    (
        "colored-no-color-override",
        'from termcolor import colored\nresult = colored("text", "red", no_color=True)',
        {"ok": True, "value": "text"},
    ),
    # colored function - empty/None
    (
        "colored-empty-string",
        'from termcolor import colored\nresult = colored("", "red", force_color=True)',
        {"ok": True, "value": "\\033[31m\\033[0m"},
    ),
    (
        "colored-none-color",
        'from termcolor import colored\nresult = colored("text", force_color=True)',
        {"ok": True, "value": "text\\033[0m"},
    ),
    (
        "colored-empty-attrs",
        'from termcolor import colored\nresult = colored("text", "red", attrs=[], force_color=True)',
        {"ok": True, "value": "\\033[31mtext\\033[0m"},
    ),
    # colored function - type conversion
    (
        "colored-integer-input",
        'from termcolor import colored\nr = colored(42, "blue", force_color=True)\nresult = ("42" in r, r.startswith("\\\\033[34m"))',
        {"ok": True, "value": [True, True]},
    ),
    (
        "colored-float-input",
        'from termcolor import colored\nr = colored(3.14, "green", force_color=True)\nresult = "3.14" in r',
        {"ok": True, "value": True},
    ),
    # colored function - more attributes
    (
        "colored-strike",
        'from termcolor import colored\nresult = colored("text", attrs=["strike"], force_color=True)',
        {"ok": True, "value": "\\033[9mtext\\033[0m"},
    ),
    (
        "colored-blink",
        'from termcolor import colored\nresult = colored("text", attrs=["blink"], force_color=True)',
        {"ok": True, "value": "\\033[5mtext\\033[0m"},
    ),
    (
        "colored-concealed",
        'from termcolor import colored\nresult = colored("text", attrs=["concealed"], force_color=True)',
        {"ok": True, "value": "\\033[8mtext\\033[0m"},
    ),
    (
        "colored-dark",
        'from termcolor import colored\nresult = colored("text", attrs=["dark"], force_color=True)',
        {"ok": True, "value": "\\033[2mtext\\033[0m"},
    ),
    (
        "colored-reverse",
        'from termcolor import colored\nresult = colored("text", attrs=["reverse"], force_color=True)',
        {"ok": True, "value": "\\033[7mtext\\033[0m"},
    ),
    # colored function - more light colors
    (
        "colored-light-red",
        'from termcolor import colored\nresult = colored("text", "light_red", force_color=True)',
        {"ok": True, "value": "\\033[91mtext\\033[0m"},
    ),
    (
        "colored-light-green",
        'from termcolor import colored\nresult = colored("text", "light_green", force_color=True)',
        {"ok": True, "value": "\\033[92mtext\\033[0m"},
    ),
    (
        "colored-grey-alias",
        'from termcolor import colored\nresult = colored("text", "grey", force_color=True)',
        {"ok": True, "value": "\\033[30mtext\\033[0m"},
    ),
    # cprint function
    (
        "cprint-returns-none",
        'from termcolor import cprint\nresult = cprint("text", "red", force_color=True)',
        {"ok": True, "value": None},
    ),
    # Additional RGB variations
    (
        "colored-rgb-zeros",
        'from termcolor import colored\nresult = colored("text", color=(0, 0, 0), force_color=True)',
        {"ok": True, "value": "\\033[38;2;0;0;0mtext\\033[0m"},
    ),
    (
        "colored-rgb-max",
        'from termcolor import colored\nresult = colored("text", color=(255, 255, 255), force_color=True)',
        {"ok": True, "value": "\\033[38;2;255;255;255mtext\\033[0m"},
    ),
    # Additional RGB and combination tests
    (
        "colored-rgb-mid-range",
        'from termcolor import colored\nresult = colored("text", color=(128, 128, 128), force_color=True)',
        {"ok": True, "value": "\\033[38;2;128;128;128mtext\\033[0m"},
    ),
    (
        "colored-all-features-combined",
        'from termcolor import colored\nr = colored("test", "red", "on_blue", ["bold", "underline"], force_color=True)\nresult = ("\\\\033[31m" in r, "\\\\033[44m" in r, "\\\\033[1m" in r, "\\\\033[4m" in r, r.endswith("\\\\033[0m"))',
        {"ok": True, "value": [True, True, True, True, True]},
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
