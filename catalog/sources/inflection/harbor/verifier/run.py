"""Private deterministic scenarios for the inflection public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/jpvanhal/inflection,
v0.5.1, immutable revision b00d4d348b32ef5823221b20ee4cbd1d2d924462). The
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
    # pluralize - regular patterns (15 scenarios)
    ("pluralize-post", "import inflection\nresult = inflection.pluralize('post')", {"ok": True, "value": "posts"}),
    ("pluralize-box", "import inflection\nresult = inflection.pluralize('box')", {"ok": True, "value": "boxes"}),
    ("pluralize-category", "import inflection\nresult = inflection.pluralize('category')", {"ok": True, "value": "categories"}),
    ("pluralize-wife", "import inflection\nresult = inflection.pluralize('wife')", {"ok": True, "value": "wives"}),
    ("pluralize-datum", "import inflection\nresult = inflection.pluralize('datum')", {"ok": True, "value": "data"}),
    ("pluralize-analysis", "import inflection\nresult = inflection.pluralize('analysis')", {"ok": True, "value": "analyses"}),
    ("pluralize-quiz", "import inflection\nresult = inflection.pluralize('quiz')", {"ok": True, "value": "quizzes"}),
    ("pluralize-buffalo", "import inflection\nresult = inflection.pluralize('buffalo')", {"ok": True, "value": "buffaloes"}),
    ("pluralize-matrix", "import inflection\nresult = inflection.pluralize('matrix')", {"ok": True, "value": "matrices"}),
    ("pluralize-axis", "import inflection\nresult = inflection.pluralize('axis')", {"ok": True, "value": "axes"}),
    
    # pluralize - irregular forms (5 scenarios)
    ("pluralize-person", "import inflection\nresult = inflection.pluralize('person')", {"ok": True, "value": "people"}),
    ("pluralize-child", "import inflection\nresult = inflection.pluralize('child')", {"ok": True, "value": "children"}),
    ("pluralize-ox", "import inflection\nresult = inflection.pluralize('ox')", {"ok": True, "value": "oxen"}),
    ("pluralize-mouse", "import inflection\nresult = inflection.pluralize('mouse')", {"ok": True, "value": "mice"}),
    ("pluralize-man", "import inflection\nresult = inflection.pluralize('man')", {"ok": True, "value": "men"}),
    
    # pluralize - uncountables (3 scenarios)
    ("pluralize-fish", "import inflection\nresult = inflection.pluralize('fish')", {"ok": True, "value": "fish"}),
    ("pluralize-sheep", "import inflection\nresult = inflection.pluralize('sheep')", {"ok": True, "value": "sheep"}),
    ("pluralize-information", "import inflection\nresult = inflection.pluralize('information')", {"ok": True, "value": "information"}),
    
    # pluralize - case preservation (2 scenarios)
    ("pluralize-cameloctopus", "import inflection\nresult = inflection.pluralize('CamelOctopus')", {"ok": True, "value": "CamelOctopi"}),
    ("pluralize-empty", "import inflection\nresult = inflection.pluralize('')", {"ok": True, "value": ""}),
    
    # singularize - regular patterns (8 scenarios)
    ("singularize-posts", "import inflection\nresult = inflection.singularize('posts')", {"ok": True, "value": "post"}),
    ("singularize-boxes", "import inflection\nresult = inflection.singularize('boxes')", {"ok": True, "value": "box"}),
    ("singularize-categories", "import inflection\nresult = inflection.singularize('categories')", {"ok": True, "value": "category"}),
    ("singularize-wives", "import inflection\nresult = inflection.singularize('wives')", {"ok": True, "value": "wife"}),
    ("singularize-data", "import inflection\nresult = inflection.singularize('data')", {"ok": True, "value": "datum"}),
    ("singularize-analyses", "import inflection\nresult = inflection.singularize('analyses')", {"ok": True, "value": "analysis"}),
    ("singularize-quizzes", "import inflection\nresult = inflection.singularize('quizzes')", {"ok": True, "value": "quiz"}),
    ("singularize-matrices", "import inflection\nresult = inflection.singularize('matrices')", {"ok": True, "value": "matrix"}),
    
    # singularize - irregular forms (3 scenarios)
    ("singularize-people", "import inflection\nresult = inflection.singularize('people')", {"ok": True, "value": "person"}),
    ("singularize-children", "import inflection\nresult = inflection.singularize('children')", {"ok": True, "value": "child"}),
    ("singularize-mice", "import inflection\nresult = inflection.singularize('mice')", {"ok": True, "value": "mouse"}),
    
    # camelize (7 scenarios)
    ("camelize-device_type", "import inflection\nresult = inflection.camelize('device_type')", {"ok": True, "value": "DeviceType"}),
    ("camelize-lower-device_type", "import inflection\nresult = inflection.camelize('device_type', False)", {"ok": True, "value": "deviceType"}),
    ("camelize-http_server", "import inflection\nresult = inflection.camelize('http_server')", {"ok": True, "value": "HttpServer"}),
    ("camelize-api_response", "import inflection\nresult = inflection.camelize('api_response')", {"ok": True, "value": "ApiResponse"}),
    ("camelize-empty", "import inflection\nresult = inflection.camelize('')", {"ok": True, "value": ""}),
    ("camelize-single", "import inflection\nresult = inflection.camelize('word')", {"ok": True, "value": "Word"}),
    ("camelize-lower-single", "import inflection\nresult = inflection.camelize('word', False)", {"ok": True, "value": "word"}),
    
    # underscore (6 scenarios)
    ("underscore-DeviceType", "import inflection\nresult = inflection.underscore('DeviceType')", {"ok": True, "value": "device_type"}),
    ("underscore-IOError", "import inflection\nresult = inflection.underscore('IOError')", {"ok": True, "value": "io_error"}),
    ("underscore-HTTPServer", "import inflection\nresult = inflection.underscore('HTTPServer')", {"ok": True, "value": "http_server"}),
    ("underscore-APIResponse", "import inflection\nresult = inflection.underscore('APIResponse')", {"ok": True, "value": "api_response"}),
    ("underscore-empty", "import inflection\nresult = inflection.underscore('')", {"ok": True, "value": ""}),
    ("underscore-hyphen", "import inflection\nresult = inflection.underscore('my-var')", {"ok": True, "value": "my_var"}),
    
    # dasherize (3 scenarios)
    ("dasherize-puni_puni", "import inflection\nresult = inflection.dasherize('puni_puni')", {"ok": True, "value": "puni-puni"}),
    ("dasherize-my_variable", "import inflection\nresult = inflection.dasherize('my_variable_name')", {"ok": True, "value": "my-variable-name"}),
    ("dasherize-no-underscore", "import inflection\nresult = inflection.dasherize('street')", {"ok": True, "value": "street"}),
    
    # humanize (5 scenarios)
    ("humanize-employee_salary", "import inflection\nresult = inflection.humanize('employee_salary')", {"ok": True, "value": "Employee salary"}),
    ("humanize-author_id", "import inflection\nresult = inflection.humanize('author_id')", {"ok": True, "value": "Author"}),
    ("humanize-first_name", "import inflection\nresult = inflection.humanize('first_name')", {"ok": True, "value": "First name"}),
    ("humanize-user_id", "import inflection\nresult = inflection.humanize('user_id')", {"ok": True, "value": "User"}),
    ("humanize-simple", "import inflection\nresult = inflection.humanize('word')", {"ok": True, "value": "Word"}),
    
    # titleize (4 scenarios)
    ("titleize-man-from", "import inflection\nresult = inflection.titleize('man from the boondocks')", {"ok": True, "value": "Man From The Boondocks"}),
    ("titleize-xmen", "import inflection\nresult = inflection.titleize('x-men: the last stand')", {"ok": True, "value": "X Men: The Last Stand"}),
    ("titleize-camel", "import inflection\nresult = inflection.titleize('TheManWithoutAPast')", {"ok": True, "value": "The Man Without A Past"}),
    ("titleize-underscore", "import inflection\nresult = inflection.titleize('raiders_of_the_lost_ark')", {"ok": True, "value": "Raiders Of The Lost Ark"}),
    
    # ordinal (8 scenarios)
    ("ordinal-1", "import inflection\nresult = inflection.ordinal(1)", {"ok": True, "value": "st"}),
    ("ordinal-2", "import inflection\nresult = inflection.ordinal(2)", {"ok": True, "value": "nd"}),
    ("ordinal-3", "import inflection\nresult = inflection.ordinal(3)", {"ok": True, "value": "rd"}),
    ("ordinal-4", "import inflection\nresult = inflection.ordinal(4)", {"ok": True, "value": "th"}),
    ("ordinal-11", "import inflection\nresult = inflection.ordinal(11)", {"ok": True, "value": "th"}),
    ("ordinal-21", "import inflection\nresult = inflection.ordinal(21)", {"ok": True, "value": "st"}),
    ("ordinal-22", "import inflection\nresult = inflection.ordinal(22)", {"ok": True, "value": "nd"}),
    ("ordinal-negative", "import inflection\nresult = inflection.ordinal(-21)", {"ok": True, "value": "st"}),
    
    # ordinalize (5 scenarios)
    ("ordinalize-1", "import inflection\nresult = inflection.ordinalize(1)", {"ok": True, "value": "1st"}),
    ("ordinalize-2", "import inflection\nresult = inflection.ordinalize(2)", {"ok": True, "value": "2nd"}),
    ("ordinalize-1003", "import inflection\nresult = inflection.ordinalize(1003)", {"ok": True, "value": "1003rd"}),
    ("ordinalize-11", "import inflection\nresult = inflection.ordinalize(11)", {"ok": True, "value": "11th"}),
    ("ordinalize-negative", "import inflection\nresult = inflection.ordinalize(-11)", {"ok": True, "value": "-11th"}),
    
    # parameterize (5 scenarios)
    ("parameterize-donald", "import inflection\nresult = inflection.parameterize('Donald E. Knuth')", {"ok": True, "value": "donald-e-knuth"}),
    ("parameterize-unicode", "import inflection\nresult = inflection.parameterize('älämölö')", {"ok": True, "value": "alamolo"}),
    ("parameterize-separator", "import inflection\nresult = inflection.parameterize('Hello World!', '_')", {"ok": True, "value": "hello_world"}),
    ("parameterize-spaces", "import inflection\nresult = inflection.parameterize('the quick brown fox')", {"ok": True, "value": "the-quick-brown-fox"}),
    ("parameterize-special", "import inflection\nresult = inflection.parameterize('a@b#c$d')", {"ok": True, "value": "a-b-c-d"}),
    
    # transliterate (2 scenarios)
    ("transliterate-alamolo", "import inflection\nresult = inflection.transliterate('älämölö')", {"ok": True, "value": "alamolo"}),
    ("transliterate-aeroskob", "import inflection\nresult = inflection.transliterate('Ærøskøbing')", {"ok": True, "value": "rskbing"}),
    
    # tableize (4 scenarios)
    ("tableize-RawScaledScorer", "import inflection\nresult = inflection.tableize('RawScaledScorer')", {"ok": True, "value": "raw_scaled_scorers"}),
    ("tableize-fancyCategory", "import inflection\nresult = inflection.tableize('fancyCategory')", {"ok": True, "value": "fancy_categories"}),
    ("tableize-Person", "import inflection\nresult = inflection.tableize('Person')", {"ok": True, "value": "people"}),
    ("tableize-Country", "import inflection\nresult = inflection.tableize('Country')", {"ok": True, "value": "countries"}),
]

assert len(CASES) == 80, f"Expected 80 cases but got {len(CASES)}"


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
