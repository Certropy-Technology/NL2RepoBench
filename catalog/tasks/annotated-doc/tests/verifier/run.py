from __future__ import annotations

import json
import pickle
import subprocess
import sys


WORKER = r'''
import pickle
import sys
from typing import Annotated, get_type_hints
sys.path.insert(0, "/tmp/candidate-site")
from annotated_doc import Doc

case = sys.argv[1]
if case == "exports":
    import annotated_doc
    assert annotated_doc.Doc is Doc
    assert "Doc" in dir(annotated_doc)
elif case == "version":
    import annotated_doc
    assert annotated_doc.__version__ == "0.0.5"
elif case == "documentation":
    assert Doc("hello").documentation == "hello"
    assert Doc("").documentation == ""
    assert Doc("line 1\nline 2").documentation == "line 1\nline 2"
elif case == "repr":
    assert repr(Doc("hello")) == "Doc('hello')"
    value = "quote ' and \""
    assert repr(Doc(value)) == "Doc(" + repr(value) + ")"
elif case == "repr_unicode":
    value = "说明\t🙂"
    assert repr(Doc(value)) == "Doc(" + repr(value) + ")"
elif case == "equality":
    assert Doc("same") == Doc("same")
    assert Doc("same") != Doc("different")
    assert Doc("same") != "same"
elif case == "self_equality":
    value = Doc("same")
    assert value == value
elif case == "hash":
    assert hash(Doc("same")) == hash(Doc("same"))
    assert isinstance(hash(Doc("same")), int)
elif case == "hash_difference":
    assert hash(Doc("Who to say hi to")) != hash(Doc("Who not to say hi to"))
elif case == "positional_only":
    try:
        Doc("a", "b")
    except TypeError:
        pass
    else:
        raise AssertionError("constructor accepted a second positional argument")
elif case == "annotated_parameter":
    def greet(name: Annotated[str, Doc("Who to greet")]) -> None:
        return None
    info = get_type_hints(greet, include_extras=True)["name"]
    assert info.__metadata__[0].documentation == "Who to greet"
    assert isinstance(info.__metadata__[0], Doc)
elif case == "annotated_return":
    def make() -> Annotated[str, Doc("A result")]:
        return "ok"
    info = get_type_hints(make, include_extras=True)["return"]
    assert info.__metadata__[0] == Doc("A result")
elif case == "annotated_attribute":
    class Model:
        value: Annotated[int, Doc("A model value")]
    info = get_type_hints(Model, include_extras=True)["value"]
    assert info.__metadata__[0].documentation == "A model value"
elif case == "pickle_protocols":
    original = Doc("pickle me")
    for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
        assert pickle.loads(pickle.dumps(original, protocol=protocol)) == original
elif case == "pickle_state":
    original = Doc("state")
    restored = pickle.loads(pickle.dumps(original))
    assert restored.documentation == "state"
    assert type(restored) is Doc
elif case == "special_text":
    value = "  leading and trailing  \n\x00"
    assert Doc(value).documentation == value
elif case == "class_name":
    assert Doc.__name__ == "Doc"
    assert callable(Doc)
else:
    raise AssertionError("unknown case: " + case)
'''


CASES = (
    "exports",
    "version",
    "documentation",
    "repr",
    "repr_unicode",
    "equality",
    "self_equality",
    "hash",
    "hash_difference",
    "positional_only",
    "annotated_parameter",
    "annotated_return",
    "annotated_attribute",
    "pickle_protocols",
    "pickle_state",
    "special_text",
    "class_name",
    "all_cases_are_isolated",
)


def main() -> None:
    leaves = []
    for case in CASES:
        if case == "all_cases_are_isolated":
            code = "import sys; sys.path.insert(0, '/tmp/candidate-site'); from annotated_doc import Doc; assert Doc('x').documentation == 'x'"
        else:
            code = WORKER
        completed = subprocess.run(
            [sys.executable, "-I", "-c", code, case],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if completed.returncode == 0:
            leaves.append({"id": "annotated-doc/" + case, "status": "passed"})
        else:
            detail = (completed.stderr or completed.stdout).strip().splitlines()
            leaves.append(
                {
                    "id": "annotated-doc/" + case,
                    "status": "failed",
                    "message": detail[-1][-500:] if detail else "case failed",
                }
            )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
