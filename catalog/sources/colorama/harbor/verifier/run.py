"""Private deterministic scenarios for the colorama 0.4.6 public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/tartley/colorama,
version 0.4.6, revision 4ea8b1c7cbf96cc21613bb51b38fc49831fdddb4). The
candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=30.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


# Test cases organized by module/API surface
# Each tuple: (id, source_code, expected_result)
CASES: list[tuple[str, str, object]] = []

# ============================================================================
# colorama root imports and version (5 cases)
# ============================================================================

CASES.extend([
    (
        "import-colorama",
        "import colorama\nresult = hasattr(colorama, 'init')",
        {"ok": True, "value": True},
    ),
    (
        "import-version",
        "import colorama\nresult = colorama.__version__",
        {"ok": True, "value": "0.4.6"},
    ),
    (
        "import-fore",
        "from colorama import Fore\nresult = hasattr(Fore, 'RED')",
        {"ok": True, "value": True},
    ),
    (
        "import-back",
        "from colorama import Back\nresult = hasattr(Back, 'GREEN')",
        {"ok": True, "value": True},
    ),
    (
        "import-style",
        "from colorama import Style\nresult = hasattr(Style, 'BRIGHT')",
        {"ok": True, "value": True},
    ),
])

# ============================================================================
# Fore color constants (10 cases)
# ============================================================================

CASES.extend([
    (
        "fore-red",
        "from colorama import Fore\nresult = Fore.RED",
        {"ok": True, "value": "\x1b[31m"},
    ),
    (
        "fore-green",
        "from colorama import Fore\nresult = Fore.GREEN",
        {"ok": True, "value": "\x1b[32m"},
    ),
    (
        "fore-blue",
        "from colorama import Fore\nresult = Fore.BLUE",
        {"ok": True, "value": "\x1b[34m"},
    ),
    (
        "fore-yellow",
        "from colorama import Fore\nresult = Fore.YELLOW",
        {"ok": True, "value": "\x1b[33m"},
    ),
    (
        "fore-black",
        "from colorama import Fore\nresult = Fore.BLACK",
        {"ok": True, "value": "\x1b[30m"},
    ),
    (
        "fore-white",
        "from colorama import Fore\nresult = Fore.WHITE",
        {"ok": True, "value": "\x1b[37m"},
    ),
    (
        "fore-cyan",
        "from colorama import Fore\nresult = Fore.CYAN",
        {"ok": True, "value": "\x1b[36m"},
    ),
    (
        "fore-magenta",
        "from colorama import Fore\nresult = Fore.MAGENTA",
        {"ok": True, "value": "\x1b[35m"},
    ),
    (
        "fore-reset",
        "from colorama import Fore\nresult = Fore.RESET",
        {"ok": True, "value": "\x1b[39m"},
    ),
    (
        "fore-lightred",
        "from colorama import Fore\nresult = Fore.LIGHTRED_EX",
        {"ok": True, "value": "\x1b[91m"},
    ),
])

# ============================================================================
# Back color constants (10 cases)
# ============================================================================

CASES.extend([
    (
        "back-red",
        "from colorama import Back\nresult = Back.RED",
        {"ok": True, "value": "\x1b[41m"},
    ),
    (
        "back-green",
        "from colorama import Back\nresult = Back.GREEN",
        {"ok": True, "value": "\x1b[42m"},
    ),
    (
        "back-blue",
        "from colorama import Back\nresult = Back.BLUE",
        {"ok": True, "value": "\x1b[44m"},
    ),
    (
        "back-yellow",
        "from colorama import Back\nresult = Back.YELLOW",
        {"ok": True, "value": "\x1b[43m"},
    ),
    (
        "back-black",
        "from colorama import Back\nresult = Back.BLACK",
        {"ok": True, "value": "\x1b[40m"},
    ),
    (
        "back-white",
        "from colorama import Back\nresult = Back.WHITE",
        {"ok": True, "value": "\x1b[47m"},
    ),
    (
        "back-cyan",
        "from colorama import Back\nresult = Back.CYAN",
        {"ok": True, "value": "\x1b[46m"},
    ),
    (
        "back-magenta",
        "from colorama import Back\nresult = Back.MAGENTA",
        {"ok": True, "value": "\x1b[45m"},
    ),
    (
        "back-reset",
        "from colorama import Back\nresult = Back.RESET",
        {"ok": True, "value": "\x1b[49m"},
    ),
    (
        "back-lightgreen",
        "from colorama import Back\nresult = Back.LIGHTGREEN_EX",
        {"ok": True, "value": "\x1b[102m"},
    ),
])

# ============================================================================
# Style constants (4 cases)
# ============================================================================

CASES.extend([
    (
        "style-bright",
        "from colorama import Style\nresult = Style.BRIGHT",
        {"ok": True, "value": "\x1b[1m"},
    ),
    (
        "style-dim",
        "from colorama import Style\nresult = Style.DIM",
        {"ok": True, "value": "\x1b[2m"},
    ),
    (
        "style-normal",
        "from colorama import Style\nresult = Style.NORMAL",
        {"ok": True, "value": "\x1b[22m"},
    ),
    (
        "style-reset-all",
        "from colorama import Style\nresult = Style.RESET_ALL",
        {"ok": True, "value": "\x1b[0m"},
    ),
])

# ============================================================================
# ansi module functions (15 cases)
# ============================================================================

CASES.extend([
    (
        "ansi-code-to-chars",
        "from colorama.ansi import code_to_chars\nresult = code_to_chars(31)",
        {"ok": True, "value": "\x1b[31m"},
    ),
    (
        "ansi-code-to-chars-zero",
        "from colorama.ansi import code_to_chars\nresult = code_to_chars(0)",
        {"ok": True, "value": "\x1b[0m"},
    ),
    (
        "ansi-clear-screen-default",
        "from colorama.ansi import clear_screen\nresult = clear_screen()",
        {"ok": True, "value": "\x1b[2J"},
    ),
    (
        "ansi-clear-screen-mode0",
        "from colorama.ansi import clear_screen\nresult = clear_screen(0)",
        {"ok": True, "value": "\x1b[0J"},
    ),
    (
        "ansi-clear-screen-mode1",
        "from colorama.ansi import clear_screen\nresult = clear_screen(1)",
        {"ok": True, "value": "\x1b[1J"},
    ),
    (
        "ansi-clear-line-default",
        "from colorama.ansi import clear_line\nresult = clear_line()",
        {"ok": True, "value": "\x1b[2K"},
    ),
    (
        "ansi-clear-line-mode0",
        "from colorama.ansi import clear_line\nresult = clear_line(0)",
        {"ok": True, "value": "\x1b[0K"},
    ),
    (
        "ansi-clear-line-mode1",
        "from colorama.ansi import clear_line\nresult = clear_line(1)",
        {"ok": True, "value": "\x1b[1K"},
    ),
    (
        "ansi-set-title",
        "from colorama.ansi import set_title\nresult = set_title('Test')",
        {"ok": True, "value": "\x1b]2;Test\x07"},
    ),
    (
        "ansi-csi-constant",
        "from colorama import ansi\nresult = ansi.CSI",
        {"ok": True, "value": "\x1b["},
    ),
    (
        "ansi-osc-constant",
        "from colorama import ansi\nresult = ansi.OSC",
        {"ok": True, "value": "\x1b]"},
    ),
    (
        "ansi-bel-constant",
        "from colorama import ansi\nresult = ansi.BEL",
        {"ok": True, "value": "\x07"},
    ),
    (
        "cursor-up-default",
        "from colorama import Cursor\nresult = Cursor.UP()",
        {"ok": True, "value": "\x1b[1A"},
    ),
    (
        "cursor-up-n",
        "from colorama import Cursor\nresult = Cursor.UP(5)",
        {"ok": True, "value": "\x1b[5A"},
    ),
    (
        "cursor-down-default",
        "from colorama import Cursor\nresult = Cursor.DOWN()",
        {"ok": True, "value": "\x1b[1B"},
    ),
])

# ============================================================================
# Cursor methods (8 cases)
# ============================================================================

CASES.extend([
    (
        "cursor-down-n",
        "from colorama import Cursor\nresult = Cursor.DOWN(3)",
        {"ok": True, "value": "\x1b[3B"},
    ),
    (
        "cursor-forward-default",
        "from colorama import Cursor\nresult = Cursor.FORWARD()",
        {"ok": True, "value": "\x1b[1C"},
    ),
    (
        "cursor-forward-n",
        "from colorama import Cursor\nresult = Cursor.FORWARD(10)",
        {"ok": True, "value": "\x1b[10C"},
    ),
    (
        "cursor-back-default",
        "from colorama import Cursor\nresult = Cursor.BACK()",
        {"ok": True, "value": "\x1b[1D"},
    ),
    (
        "cursor-back-n",
        "from colorama import Cursor\nresult = Cursor.BACK(7)",
        {"ok": True, "value": "\x1b[7D"},
    ),
    (
        "cursor-pos-default",
        "from colorama import Cursor\nresult = Cursor.POS()",
        {"ok": True, "value": "\x1b[1;1H"},
    ),
    (
        "cursor-pos-xy",
        "from colorama import Cursor\nresult = Cursor.POS(10, 20)",
        {"ok": True, "value": "\x1b[20;10H"},
    ),
    (
        "cursor-pos-origin",
        "from colorama import Cursor\nresult = Cursor.POS(1, 1)",
        {"ok": True, "value": "\x1b[1;1H"},
    ),
])

# ============================================================================
# init/deinit/reinit functions (10 cases)
# ============================================================================

CASES.extend([
    (
        "init-callable",
        "from colorama import init\nresult = callable(init)",
        {"ok": True, "value": True},
    ),
    (
        "deinit-callable",
        "from colorama import deinit\nresult = callable(deinit)",
        {"ok": True, "value": True},
    ),
    (
        "reinit-callable",
        "from colorama import reinit\nresult = callable(reinit)",
        {"ok": True, "value": True},
    ),
    (
        "just-fix-windows-console-callable",
        "from colorama import just_fix_windows_console\nresult = callable(just_fix_windows_console)",
        {"ok": True, "value": True},
    ),
    (
        "init-basic-call",
        "from colorama import init\ninit()\nresult = True",
        {"ok": True, "value": True},
    ),
    (
        "init-autoreset-true",
        "from colorama import init\ninit(autoreset=True)\nresult = True",
        {"ok": True, "value": True},
    ),
    (
        "init-wrap-false-conflict",
        "from colorama import init\ntry:\n    init(wrap=False, autoreset=True)\n    result = 'no-error'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "ValueError"},
    ),
    (
        "deinit-basic-call",
        "from colorama import deinit\ndeinit()\nresult = True",
        {"ok": True, "value": True},
    ),
    (
        "just-fix-windows-console-call",
        "from colorama import just_fix_windows_console\njust_fix_windows_console()\nresult = True",
        {"ok": True, "value": True},
    ),
    (
        "colorama-text-callable",
        "from colorama import colorama_text\nresult = callable(colorama_text)",
        {"ok": True, "value": True},
    ),
])

# ============================================================================
# AnsiToWin32 class (8 cases)
# ============================================================================

CASES.extend([
    (
        "ansitowin32-import",
        "from colorama import AnsiToWin32\nresult = AnsiToWin32.__name__",
        {"ok": True, "value": "AnsiToWin32"},
    ),
    (
        "ansitowin32-callable",
        "from colorama import AnsiToWin32\nresult = callable(AnsiToWin32)",
        {"ok": True, "value": True},
    ),
    (
        "ansitowin32-create-with-none",
        "from colorama import AnsiToWin32\nimport sys\nw = AnsiToWin32(None)\nresult = w.wrapped is None",
        {"ok": True, "value": True},
    ),
    (
        "ansitowin32-reset-all-method",
        "from colorama import AnsiToWin32\nimport sys\nw = AnsiToWin32(sys.stdout)\nresult = callable(w.reset_all)",
        {"ok": True, "value": True},
    ),
    (
        "ansitowin32-write-method",
        "from colorama import AnsiToWin32\nimport sys\nw = AnsiToWin32(sys.stdout)\nresult = callable(w.write)",
        {"ok": True, "value": True},
    ),
    (
        "ansitowin32-should-wrap-method",
        "from colorama import AnsiToWin32\nimport sys\nw = AnsiToWin32(sys.stdout)\nresult = callable(w.should_wrap)",
        {"ok": True, "value": True},
    ),
    (
        "ansitowin32-stream-attr",
        "from colorama import AnsiToWin32\nimport sys\nw = AnsiToWin32(sys.stdout)\nresult = hasattr(w, 'stream')",
        {"ok": True, "value": True},
    ),
    (
        "ansitowin32-convert-attr",
        "from colorama import AnsiToWin32\nimport sys\nw = AnsiToWin32(sys.stdout)\nresult = isinstance(w.convert, bool) or w.convert is None",
        {"ok": True, "value": True},
    ),
])

# ============================================================================
# Edge cases and combinations (10 cases)
# ============================================================================

CASES.extend([
    (
        "fore-and-back-concat",
        "from colorama import Fore, Back\nresult = Fore.RED + Back.GREEN",
        {"ok": True, "value": "\x1b[31m\x1b[42m"},
    ),
    (
        "fore-style-concat",
        "from colorama import Fore, Style\nresult = Fore.BLUE + Style.BRIGHT",
        {"ok": True, "value": "\x1b[34m\x1b[1m"},
    ),
    (
        "full-reset-sequence",
        "from colorama import Fore, Back, Style\nresult = Fore.RED + Back.GREEN + Style.BRIGHT + Style.RESET_ALL",
        {"ok": True, "value": "\x1b[31m\x1b[42m\x1b[1m\x1b[0m"},
    ),
    (
        "empty-string-concat",
        "from colorama import Fore\nresult = Fore.RED + ''",
        {"ok": True, "value": "\x1b[31m"},
    ),
    (
        "code-to-chars-string-arg",
        "from colorama.ansi import code_to_chars\nresult = code_to_chars('42')",
        {"ok": True, "value": "\x1b[42m"},
    ),
    (
        "clear-screen-string-arg",
        "from colorama.ansi import clear_screen\nresult = clear_screen('1')",
        {"ok": True, "value": "\x1b[1J"},
    ),
    (
        "cursor-up-zero",
        "from colorama import Cursor\nresult = Cursor.UP(0)",
        {"ok": True, "value": "\x1b[0A"},
    ),
    (
        "cursor-pos-same-xy",
        "from colorama import Cursor\nresult = Cursor.POS(5, 5)",
        {"ok": True, "value": "\x1b[5;5H"},
    ),
    (
        "ansi-multiple-code-calls",
        "from colorama.ansi import code_to_chars\nresult = [code_to_chars(i) for i in [30, 31, 32]]",
        {"ok": True, "value": ["\x1b[30m", "\x1b[31m", "\x1b[32m"]},
    ),
    (
        "set-title-empty",
        "from colorama.ansi import set_title\nresult = set_title('')",
        {"ok": True, "value": "\x1b]2;\x07"},
    ),
])

# Verify we have exactly the expected number of cases
assert len(CASES) == 80, f"Expected 90 cases, got {len(CASES)}"


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
