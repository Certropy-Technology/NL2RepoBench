"""Private deterministic scenarios for the pyfiglet public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction. The candidate runner executes
the script and reads the ``result`` binding.
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
        's001',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hello', font='standard')",
        {'ok': True, 'value': ' _   _      _ _       \n| | | | ___| | | ___  \n| |_| |/ _ \\ | |/ _ \\ \n|  _  |  __/ | | (_) |\n|_| |_|\\___|_|_|\\___/ \n                      \n'},
    ),
    (
        's002',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi', font='standard')",
        {'ok': True, 'value': ' _   _ _ \n| | | (_)\n| |_| | |\n|  _  | |\n|_| |_|_|\n         \n'},
    ),
    (
        's003',
        "import pyfiglet\nresult = pyfiglet.figlet_format('World', font='standard')",
        {'ok': True, 'value': "__        __         _     _ \n\\ \\      / /__  _ __| | __| |\n \\ \\ /\\ / / _ \\| '__| |/ _` |\n  \\ V  V / (_) | |  | | (_| |\n   \\_/\\_/ \\___/|_|  |_|\\__,_|\n                             \n"},
    ),
    (
        's004',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Test', font='standard')",
        {'ok': True, 'value': ' _____         _   \n|_   _|__  ___| |_ \n  | |/ _ \\/ __| __|\n  | |  __/\\__ \\ |_ \n  |_|\\___||___/\\__|\n                   \n'},
    ),
    (
        's005',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Python', font='standard')",
        {'ok': True, 'value': " ____        _   _                 \n|  _ \\ _   _| |_| |__   ___  _ __  \n| |_) | | | | __| '_ \\ / _ \\| '_ \\ \n|  __/| |_| | |_| | | | (_) | | | |\n|_|    \\__, |\\__|_| |_|\\___/|_| |_|\n       |___/                       \n"},
    ),
    (
        's006',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hello', font='doom')",
        {'ok': True, 'value': ' _   _      _ _       \n| | | |    | | |      \n| |_| | ___| | | ___  \n|  _  |/ _ \\ | |/ _ \\ \n| | | |  __/ | | (_) |\n\\_| |_/\\___|_|_|\\___/ \n                      \n                      \n'},
    ),
    (
        's007',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi', font='doom')",
        {'ok': True, 'value': ' _   _ _ \n| | | (_)\n| |_| |_ \n|  _  | |\n| | | | |\n\\_| |_/_|\n         \n         \n'},
    ),
    (
        's008',
        "import pyfiglet\nresult = pyfiglet.figlet_format('World', font='doom')",
        {'ok': True, 'value': " _    _            _     _ \n| |  | |          | |   | |\n| |  | | ___  _ __| | __| |\n| |/\\| |/ _ \\| '__| |/ _` |\n\\  /\\  / (_) | |  | | (_| |\n \\/  \\/ \\___/|_|  |_|\\__,_|\n                           \n                           \n"},
    ),
    (
        's009',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hello', font='small')",
        {'ok': True, 'value': ' _  _     _ _     \n| || |___| | |___ \n| __ / -_) | / _ \\\n|_||_\\___|_|_\\___/\n                  \n'},
    ),
    (
        's010',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi', font='small')",
        {'ok': True, 'value': ' _  _ _ \n| || (_)\n| __ | |\n|_||_|_|\n        \n'},
    ),
    (
        's011',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Test', font='small')",
        {'ok': True, 'value': ' _____       _   \n|_   _|__ __| |_ \n  | |/ -_|_-<  _|\n  |_|\\___/__/\\__|\n                 \n'},
    ),
    (
        's012',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hello', font='slant')",
        {'ok': True, 'value': '    __  __     ____    \n   / / / /__  / / /___ \n  / /_/ / _ \\/ / / __ \\\n / __  /  __/ / / /_/ /\n/_/ /_/\\___/_/_/\\____/ \n                       \n'},
    ),
    (
        's013',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi', font='slant')",
        {'ok': True, 'value': '    __  ___ \n   / / / (_)\n  / /_/ / / \n / __  / /  \n/_/ /_/_/   \n            \n'},
    ),
    (
        's014',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Code', font='slant')",
        {'ok': True, 'value': '   ______          __   \n  / ____/___  ____/ /__ \n / /   / __ \\/ __  / _ \\\n/ /___/ /_/ / /_/ /  __/\n\\____/\\____/\\__,_/\\___/ \n                        \n'},
    ),
    (
        's015',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hello', font='banner3')",
        {'ok': True, 'value': '##     ## ######## ##       ##        #######  \n##     ## ##       ##       ##       ##     ## \n##     ## ##       ##       ##       ##     ## \n######### ######   ##       ##       ##     ## \n##     ## ##       ##       ##       ##     ## \n##     ## ##       ##       ##       ##     ## \n##     ## ######## ######## ########  #######  \n'},
    ),
    (
        's016',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi', font='banner3')",
        {'ok': True, 'value': '##     ## #### \n##     ##  ##  \n##     ##  ##  \n#########  ##  \n##     ##  ##  \n##     ##  ##  \n##     ## #### \n'},
    ),
    (
        's017',
        "import pyfiglet\nresult = pyfiglet.figlet_format('OK', font='banner3')",
        {'ok': True, 'value': ' #######  ##    ## \n##     ## ##   ##  \n##     ## ##  ##   \n##     ## #####    \n##     ## ##  ##   \n##     ## ##   ##  \n #######  ##    ## \n'},
    ),
    (
        's018',
        "import pyfiglet\nresult = pyfiglet.figlet_format('123', font='standard')",
        {'ok': True, 'value': ' _ ____  _____ \n/ |___ \\|___ / \n| | __) | |_ \\ \n| |/ __/ ___) |\n|_|_____|____/ \n               \n'},
    ),
    (
        's019',
        "import pyfiglet\nresult = pyfiglet.figlet_format('2024', font='standard')",
        {'ok': True, 'value': ' ____   ___ ____  _  _   \n|___ \\ / _ \\___ \\| || |  \n  __) | | | |__) | || |_ \n / __/| |_| / __/|__   _|\n|_____|\\___/_____|  |_|  \n                         \n'},
    ),
    (
        's020',
        "import pyfiglet\nresult = pyfiglet.figlet_format('42', font='doom')",
        {'ok': True, 'value': "   ___  _____ \n  /   |/ __  \\\n / /| |`' / /'\n/ /_| |  / /  \n\\___  |./ /___\n    |_/\\_____/\n              \n              \n"},
    ),
    (
        's021',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi!', font='standard')",
        {'ok': True, 'value': ' _   _ _ _ \n| | | (_) |\n| |_| | | |\n|  _  | |_|\n|_| |_|_(_)\n           \n'},
    ),
    (
        's022',
        "import pyfiglet\nresult = pyfiglet.figlet_format('OK?', font='standard')",
        {'ok': True, 'value': "  ___  _  _____ \n / _ \\| |/ /__ \\\n| | | | ' /  / /\n| |_| | . \\ |_| \n \\___/|_|\\_\\(_) \n                \n"},
    ),
    (
        's023',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Go!', font='doom')",
        {'ok': True, 'value': ' _____       _ \n|  __ \\     | |\n| |  \\/ ___ | |\n| | __ / _ \\| |\n| |_\\ \\ (_) |_|\n \\____/\\___/(_)\n               \n               \n'},
    ),
    (
        's024',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi There', font='standard')",
        {'ok': True, 'value': " _   _ _   _____ _                   \n| | | (_) |_   _| |__   ___ _ __ ___ \n| |_| | |   | | | '_ \\ / _ \\ '__/ _ \\\n|  _  | |   | | | | | |  __/ | |  __/\n|_| |_|_|   |_| |_| |_|\\___|_|  \\___|\n                                     \n"},
    ),
    (
        's025',
        "import pyfiglet\nresult = pyfiglet.figlet_format('A B', font='small')",
        {'ok': True, 'value': '   _     ___ \n  /_\\   | _ )\n / _ \\  | _ \\\n/_/ \\_\\ |___/\n             \n'},
    ),
    (
        's026',
        "import pyfiglet\nresult = pyfiglet.figlet_format('', font='standard')",
        {'ok': True, 'value': ''},
    ),
    (
        's027',
        "import pyfiglet\nresult = pyfiglet.figlet_format('', font='doom')",
        {'ok': True, 'value': ''},
    ),
    (
        's028',
        "import pyfiglet\nf = pyfiglet.Figlet(font='standard')\nresult = f.renderText('Hello')",
        {'ok': True, 'value': ' _   _      _ _       \n| | | | ___| | | ___  \n| |_| |/ _ \\ | |/ _ \\ \n|  _  |  __/ | | (_) |\n|_| |_|\\___|_|_|\\___/ \n                      \n'},
    ),
    (
        's029',
        "import pyfiglet\nf = pyfiglet.Figlet(font='doom')\nresult = f.renderText('Hi')",
        {'ok': True, 'value': ' _   _ _ \n| | | (_)\n| |_| |_ \n|  _  | |\n| | | | |\n\\_| |_/_|\n         \n         \n'},
    ),
    (
        's030',
        "import pyfiglet\nf = pyfiglet.Figlet(font='slant')\nresult = f.renderText('Test')",
        {'ok': True, 'value': '  ______          __ \n /_  __/__  _____/ /_\n  / / / _ \\/ ___/ __/\n / / /  __(__  ) /_  \n/_/  \\___/____/\\__/  \n                     \n'},
    ),
    (
        's031',
        'import pyfiglet\nresult = isinstance(pyfiglet.FigletFont.getFonts(), list)',
        {'ok': True, 'value': True},
    ),
    (
        's032',
        "import pyfiglet\nresult = 'standard' in pyfiglet.FigletFont.getFonts()",
        {'ok': True, 'value': True},
    ),
    (
        's033',
        "import pyfiglet\nresult = 'doom' in pyfiglet.FigletFont.getFonts()",
        {'ok': True, 'value': True},
    ),
    (
        's034',
        "import pyfiglet\nresult = 'small' in pyfiglet.FigletFont.getFonts()",
        {'ok': True, 'value': True},
    ),
    (
        's035',
        "import pyfiglet\nresult = 'slant' in pyfiglet.FigletFont.getFonts()",
        {'ok': True, 'value': True},
    ),
    (
        's036',
        "import pyfiglet\nresult = 'banner3' in pyfiglet.FigletFont.getFonts()",
        {'ok': True, 'value': True},
    ),
    (
        's037',
        'import pyfiglet\nresult = len(pyfiglet.FigletFont.getFonts()) > 100',
        {'ok': True, 'value': True},
    ),
    (
        's038',
        "import pyfiglet\ntry:\n    pyfiglet.figlet_format('Test', font='nonexistent_font_xyz')\n    result = False\nexcept Exception:\n    result = True",
        {'ok': True, 'value': True},
    ),
    (
        's039',
        "import pyfiglet\nresult = pyfiglet.figlet_format('ABC', font='standard')",
        {'ok': True, 'value': '    _    ____   ____ \n   / \\  | __ ) / ___|\n  / _ \\ |  _ \\| |    \n / ___ \\| |_) | |___ \n/_/   \\_\\____/ \\____|\n                     \n'},
    ),
    (
        's040',
        "import pyfiglet\nresult = pyfiglet.figlet_format('XYZ', font='doom')",
        {'ok': True, 'value': '__   ____   ________\n\\ \\ / /\\ \\ / /___  /\n \\ V /  \\ V /   / / \n /   \\   \\ /   / /  \n/ /^\\ \\  | | ./ /___\n\\/   \\/  \\_/ \\_____/\n                    \n                    \n'},
    ),
    (
        's041',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Code', font='banner3')",
        {'ok': True, 'value': ' ######   #######  ########  ######## \n##    ## ##     ## ##     ## ##       \n##       ##     ## ##     ## ##       \n##       ##     ## ##     ## ######   \n##       ##     ## ##     ## ##       \n##    ## ##     ## ##     ## ##       \n ######   #######  ########  ######## \n'},
    ),
    (
        's042',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Run', font='small')",
        {'ok': True, 'value': " ___           \n| _ \\_  _ _ _  \n|   / || | ' \\ \n|_|_\\\\_,_|_||_|\n               \n"},
    ),
    (
        's043',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Dev', font='slant')",
        {'ok': True, 'value': '    ____           \n   / __ \\___ _   __\n  / / / / _ \\ | / /\n / /_/ /  __/ |/ / \n/_____/\\___/|___/  \n                   \n'},
    ),
    (
        's044',
        "import pyfiglet\nresult = pyfiglet.figlet_format('PyFiglet', font='standard')",
        {'ok': True, 'value': ' ____        _____ _       _      _   \n|  _ \\ _   _|  ___(_) __ _| | ___| |_ \n| |_) | | | | |_  | |/ _` | |/ _ \\ __|\n|  __/| |_| |  _| | | (_| | |  __/ |_ \n|_|    \\__, |_|   |_|\\__, |_|\\___|\\__|\n       |___/         |___/            \n'},
    ),
    (
        's045',
        "import pyfiglet\nresult = pyfiglet.figlet_format('GitHub', font='doom')",
        {'ok': True, 'value': " _____ _ _   _   _       _     \n|  __ (_) | | | | |     | |    \n| |  \\/_| |_| |_| |_   _| |__  \n| | __| | __|  _  | | | | '_ \\ \n| |_\\ \\ | |_| | | | |_| | |_) |\n \\____/_|\\__\\_| |_/\\__,_|_.__/ \n                               \n                               \n"},
    ),
    (
        's046',
        "import pyfiglet\nresult = pyfiglet.figlet_format('A', font='standard')",
        {'ok': True, 'value': '    _    \n   / \\   \n  / _ \\  \n / ___ \\ \n/_/   \\_\\\n         \n'},
    ),
    (
        's047',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Z', font='doom')",
        {'ok': True, 'value': ' ______\n|___  /\n   / / \n  / /  \n./ /___\n\\_____/\n       \n       \n'},
    ),
    (
        's048',
        "import pyfiglet\nresult = pyfiglet.figlet_format('1', font='small')",
        {'ok': True, 'value': ' _ \n/ |\n| |\n|_|\n   \n'},
    ),
    (
        's049',
        "import pyfiglet\nresult = pyfiglet.figlet_format('OK', font='standard')",
        {'ok': True, 'value': "  ___  _  __\n / _ \\| |/ /\n| | | | ' / \n| |_| | . \\ \n \\___/|_|\\_\\\n            \n"},
    ),
    (
        's050',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Yes', font='doom')",
        {'ok': True, 'value': '__   __        \n\\ \\ / /        \n \\ V /___  ___ \n  \\ // _ \\/ __|\n  | |  __/\\__ \\\n  \\_/\\___||___/\n               \n               \n'},
    ),
    (
        's051',
        "import pyfiglet\nresult = pyfiglet.figlet_format('No', font='small')",
        {'ok': True, 'value': ' _  _     \n| \\| |___ \n| .` / _ \\\n|_|\\_\\___/\n          \n'},
    ),
    (
        's052',
        "import pyfiglet\nf = pyfiglet.Figlet(font='small')\nresult = f.renderText('OK')",
        {'ok': True, 'value': "  ___  _  __\n / _ \\| |/ /\n| (_) | ' < \n \\___/|_|\\_\\\n            \n"},
    ),
    (
        's053',
        "import pyfiglet\nf = pyfiglet.Figlet(font='banner3')\nresult = f.renderText('ABC')",
        {'ok': True, 'value': '   ###    ########   ######  \n  ## ##   ##     ## ##    ## \n ##   ##  ##     ## ##       \n##     ## ########  ##       \n######### ##     ## ##       \n##     ## ##     ## ##    ## \n##     ## ########   ######  \n'},
    ),
    (
        's054',
        "import pyfiglet\nresult = pyfiglet.figlet_format('100', font='standard')",
        {'ok': True, 'value': ' _  ___   ___  \n/ |/ _ \\ / _ \\ \n| | | | | | | |\n| | |_| | |_| |\n|_|\\___/ \\___/ \n               \n'},
    ),
    (
        's055',
        "import pyfiglet\nresult = pyfiglet.figlet_format('999', font='doom')",
        {'ok': True, 'value': ' _____  _____  _____ \n|  _  ||  _  ||  _  |\n| |_| || |_| || |_| |\n\\____ |\\____ |\\____ |\n.___/ /.___/ /.___/ /\n\\____/ \\____/ \\____/ \n                     \n                     \n'},
    ),
    (
        's056',
        "import pyfiglet\nresult = pyfiglet.figlet_format('A1', font='standard')",
        {'ok': True, 'value': '    _    _ \n   / \\  / |\n  / _ \\ | |\n / ___ \\| |\n/_/   \\_\\_|\n           \n'},
    ),
    (
        's057',
        "import pyfiglet\nresult = pyfiglet.figlet_format('3D', font='doom')",
        {'ok': True, 'value': ' ___________ \n|____ |  _  \\\n    / / | | |\n    \\ \\ | | |\n.___/ / |/ / \n\\____/|___/  \n             \n             \n'},
    ),
    (
        's058',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Hi.', font='standard')",
        {'ok': True, 'value': ' _   _ _   \n| | | (_)  \n| |_| | |  \n|  _  | |_ \n|_| |_|_(_)\n           \n'},
    ),
    (
        's059',
        "import pyfiglet\nresult = pyfiglet.figlet_format('OK!', font='small')",
        {'ok': True, 'value': "  ___  _  ___ \n / _ \\| |/ / |\n| (_) | ' <|_|\n \\___/|_|\\_(_)\n              \n"},
    ),
    (
        's060',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Fix', font='standard')",
        {'ok': True, 'value': ' _____ _      \n|  ___(_)_  __\n| |_  | \\ \\/ /\n|  _| | |>  < \n|_|   |_/_/\\_\\\n              \n'},
    ),
    (
        's061',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Bug', font='standard')",
        {'ok': True, 'value': ' ____              \n| __ ) _   _  __ _ \n|  _ \\| | | |/ _` |\n| |_) | |_| | (_| |\n|____/ \\__,_|\\__, |\n             |___/ \n'},
    ),
    (
        's062',
        "import pyfiglet\nresult = pyfiglet.figlet_format('API', font='standard')",
        {'ok': True, 'value': '    _    ____ ___ \n   / \\  |  _ \\_ _|\n  / _ \\ | |_) | | \n / ___ \\|  __/| | \n/_/   \\_\\_|  |___|\n                  \n'},
    ),
    (
        's063',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Fun', font='doom')",
        {'ok': True, 'value': "______           \n|  ___|          \n| |_ _   _ _ __  \n|  _| | | | '_ \\ \n| | | |_| | | | |\n\\_|  \\__,_|_| |_|\n                 \n                 \n"},
    ),
    (
        's064',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Job', font='doom')",
        {'ok': True, 'value': "   ___       _     \n  |_  |     | |    \n    | | ___ | |__  \n    | |/ _ \\| '_ \\ \n/\\__/ / (_) | |_) |\n\\____/ \\___/|_.__/ \n                   \n                   \n"},
    ),
    (
        's065',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Key', font='small')",
        {'ok': True, 'value': " _  __         \n| |/ /___ _  _ \n| ' </ -_) || |\n|_|\\_\\___|\\_, |\n          |__/ \n"},
    ),
    (
        's066',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Val', font='small')",
        {'ok': True, 'value': '__   __    _ \n\\ \\ / /_ _| |\n \\ V / _` | |\n  \\_/\\__,_|_|\n             \n'},
    ),
    (
        's067',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Art', font='slant')",
        {'ok': True, 'value': '    ___         __ \n   /   |  _____/ /_\n  / /| | / ___/ __/\n / ___ |/ /  / /_  \n/_/  |_/_/   \\__/  \n                   \n'},
    ),
    (
        's068',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Box', font='slant')",
        {'ok': True, 'value': '    ____            \n   / __ )____  _  __\n  / __  / __ \\| |/_/\n / /_/ / /_/ />  <  \n/_____/\\____/_/|_|  \n                    \n'},
    ),
    (
        's069',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Up', font='banner3')",
        {'ok': True, 'value': '##     ## ########  \n##     ## ##     ## \n##     ## ##     ## \n##     ## ########  \n##     ## ##        \n##     ## ##        \n #######  ##        \n'},
    ),
    (
        's070',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Go', font='banner3')",
        {'ok': True, 'value': ' ######    #######  \n##    ##  ##     ## \n##        ##     ## \n##   #### ##     ## \n##    ##  ##     ## \n##    ##  ##     ## \n ######    #######  \n'},
    ),
    (
        's071',
        "import pyfiglet\nresult = pyfiglet.figlet_format('hello', font='standard')",
        {'ok': True, 'value': " _          _ _       \n| |__   ___| | | ___  \n| '_ \\ / _ \\ | |/ _ \\ \n| | | |  __/ | | (_) |\n|_| |_|\\___|_|_|\\___/ \n                      \n"},
    ),
    (
        's072',
        "import pyfiglet\nresult = pyfiglet.figlet_format('world', font='doom')",
        {'ok': True, 'value': "                    _     _ \n                   | |   | |\n__      _____  _ __| | __| |\n\\ \\ /\\ / / _ \\| '__| |/ _` |\n \\ V  V / (_) | |  | | (_| |\n  \\_/\\_/ \\___/|_|  |_|\\__,_|\n                            \n                            \n"},
    ),
    (
        's073',
        "import pyfiglet\nresult = pyfiglet.figlet_format('A-B', font='standard')",
        {'ok': True, 'value': '    _         ____  \n   / \\       | __ ) \n  / _ \\ _____|  _ \\ \n / ___ \\_____| |_) |\n/_/   \\_\\    |____/ \n                    \n'},
    ),
    (
        's074',
        "import pyfiglet\nresult = pyfiglet.figlet_format('C_D', font='small')",
        {'ok': True, 'value': '  ___   ___  \n / __| |   \\ \n| (__  | |) |\n \\___|_|___/ \n    |___|    \n'},
    ),
    (
        's075',
        "import pyfiglet\nf = pyfiglet.Figlet(font='standard')\nresult = f.renderText('End')",
        {'ok': True, 'value': " _____           _ \n| ____|_ __   __| |\n|  _| | '_ \\ / _` |\n| |___| | | | (_| |\n|_____|_| |_|\\__,_|\n                   \n"},
    ),
    (
        's076',
        "import pyfiglet\nf = pyfiglet.Figlet(font='doom')\nresult = f.renderText('Top')",
        {'ok': True, 'value': " _____           \n|_   _|          \n  | | ___  _ __  \n  | |/ _ \\| '_ \\ \n  | | (_) | |_) |\n  \\_/\\___/| .__/ \n          | |    \n          |_|    \n"},
    ),
    (
        's077',
        "import pyfiglet\nf = pyfiglet.Figlet(font='slant')\nresult = f.renderText('Git')",
        {'ok': True, 'value': '   _______ __ \n  / ____(_) /_\n / / __/ / __/\n/ /_/ / / /_  \n\\____/_/\\__/  \n              \n'},
    ),
    (
        's078',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Set', font='standard')",
        {'ok': True, 'value': ' ____       _   \n/ ___|  ___| |_ \n\\___ \\ / _ \\ __|\n ___) |  __/ |_ \n|____/ \\___|\\__|\n                \n'},
    ),
    (
        's079',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Get', font='doom')",
        {'ok': True, 'value': ' _____      _   \n|  __ \\    | |  \n| |  \\/ ___| |_ \n| | __ / _ \\ __|\n| |_\\ \\  __/ |_ \n \\____/\\___|\\__|\n                \n                \n'},
    ),
    (
        's080',
        "import pyfiglet\nresult = pyfiglet.figlet_format('Put', font='small')",
        {'ok': True, 'value': ' ___      _   \n| _ \\_  _| |_ \n|  _/ || |  _|\n|_|  \\_,_|\\__|\n              \n'},
    ),
]

assert len(CASES) == 80, f"Expected 80 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True, default=repr)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
