from __future__ import annotations

import json
import subprocess


CHILD = r'''
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, os.environ["CANDIDATE_ROOT"])
sys.path.insert(1, os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"])

from pysondb.db import PysonDB
from pysondb.errors import IdDoesNotExistError, SchemaTypeError, UnknownKeyError
from pysondb.utils import merge_n_db, migrate, purge_db


DATA2 = {
    "version": 2,
    "keys": ["age", "name"],
    "data": {
        "2352346": {"age": 4, "name": "mathew_first"},
        "1234567": {"age": 9, "name": "new_user"},
    },
}
DATA3 = {
    "version": 2,
    "keys": ["age", "name", "place"],
    "data": {
        "219520953066905460": {"name": "ad0", "age": 0, "place": "US"},
        "110180374400879352": {"name": "ad1", "age": 1, "place": "US"},
        "224980674034561069": {"name": "ad2", "age": 7, "place": "UK"},
        "228563587602913112": {"name": "ad3", "age": 3, "place": "UK"},
        "167833310760833974": {"name": "ad4", "age": 4, "place": "IN"},
    },
}
MANY = [
    {"name": "ad", "age": 19},
    {"name": "fredy", "age": 69},
    {"name": "mathew", "age": 69},
]


def expect_error(error_type, function):
    try:
        function()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def path_with(data=None):
    root = Path(tempfile.mkdtemp(prefix="pysondb-contract-"))
    path = root / "database.json"
    if data is not None:
        path.write_text(json.dumps(data), encoding="utf-8")
    return path


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def ids(start=0):
    value = start
    while True:
        yield str(value)
        value += 1


def run_cli(*args):
    from pysondb.cli import main
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(args)
    return code, stdout.getvalue(), stderr.getvalue()


def run_case(name):
    if name == "test_cli.py::test_cli_info_ujson_exist":
        import pysondb.db as module
        module.UJSON = True
        assert run_cli("--info") == (0, "PysonDB - 2.0.0\nusing 'ujson' JSON parser\n", "")
        return
    if name == "test_cli.py::test_cli_info_ujson_does_not_exist":
        import pysondb.db as module
        module.UJSON = False
        assert run_cli("--info") == (0, "PysonDB - 2.0.0\nusing builtin JSON parser\n", "")
        return
    if name.startswith("test_cli_merge.py::"):
        left = {
            "version": 2,
            "keys": ["test"],
            "data": {"211194894507061604": {"test": "3"}, "107314111299174914": {"test": "4"}},
        }
        right = {
            "version": 2,
            "keys": ["test"],
            "data": {"211194894507061605": {"test": "3"}, "107314111299174916": {"test": "4"}},
        }
        first, second, output = path_with(left), path_with(right), path_with().with_name("merged.json")
        if name.endswith("test_cli_merge"):
            code, stdout, stderr = run_cli("merge", str(first), str(second), "-o", str(output))
            assert (code, stdout, stderr) == (0, "DB's merged successfully\n", "")
            assert read(output) == {"version": 2, "keys": ["test"], "data": {**left["data"], **right["data"]}}
        else:
            right["keys"] = ["age"]
            right["data"] = {key: {"age": value["test"]} for key, value in right["data"].items()}
            second.write_text(json.dumps(right), encoding="utf-8")
            assert run_cli("merge", str(first), str(second), "-o", str(output)) == (
                1, "", "All the DB's must have the same keys\n"
            )
        return
    if name == "test_cli_purge.py::test_cli_purge":
        path = path_with(DATA3)
        assert run_cli("purge", str(path)) == (0, "", "")
        assert read(path) == {"version": 2, "data": {}, "keys": []}
        return
    if name.startswith("test_cli_show.py::"):
        path = path_with(DATA3)
        if name.endswith("test_cli_show"):
            expected = (
                "+--------------------+-----+------+-------+\n"
                "|         id         | age | name | place |\n"
                "+--------------------+-----+------+-------+\n"
                "| 219520953066905460 |  0  | ad0  |   US  |\n"
                "| 110180374400879352 |  1  | ad1  |   US  |\n"
                "| 224980674034561069 |  7  | ad2  |   UK  |\n"
                "| 228563587602913112 |  3  | ad3  |   UK  |\n"
                "| 167833310760833974 |  4  | ad4  |   IN  |\n"
                "+--------------------+-----+------+-------+\n"
            )
            assert run_cli("show", str(path)) == (0, expected, "")
        elif name.endswith("test_cli_show_no_prettytable_installed"):
            import pysondb.utils as module
            module.PRETTYTABLE = False
            assert run_cli("show", str(path)) == (
                1, "install prettytable (pip3 install prettytable) to run the following command\n", ""
            )
        else:
            path.write_text(json.dumps({"data": [{"name": "ad", "age": 1, "id": 353634357}]}), encoding="utf-8")
            assert run_cli("show", str(path)) == (
                1, "the DB must be a v2 DB, you can use the migrate command to the convert your DB\n", ""
            )
        return
    if name == "test_cli_tocsv.py::test_tocsv":
        path = path_with({
            "version": 2,
            "keys": ["age", "name", "place"],
            "data": {
                "219520953066905460": {"name": "ad0", "age": 0, "place": "US"},
                "110180374400879352": {"name": "ad1", "age": 1, "place": "US"},
                "224980674034561069": {"name": "ad2", "age": 7, "place": "UK"},
            },
        })
        output = path.with_suffix(".csv")
        assert run_cli("tocsv", str(path), "-o", str(output)) == (0, "", "")
        assert output.read_text(encoding="utf-8").replace("\n", "").replace("\r", "") == (
            "id,age,name,place219520953066905460,0,ad0,US"
            "110180374400879352,1,ad1,US224980674034561069,7,ad2,UK"
        )
        return

    if name.startswith("test_db_add.py::"):
        path = path_with()
        db = PysonDB(str(path))
        if name.endswith("test_add_empty_file"):
            db.set_id_generator(lambda: "2352346")
            assert db.add({"age": 4, "name": "mathew"}) == "2352346"
            assert read(path) == {"version": 2, "keys": ["age", "name"], "data": {"2352346": {"age": 4, "name": "mathew"}}}
        elif name.endswith("test_add_non_empty_file"):
            path.write_text(json.dumps({"version": 2, "keys": ["age", "name"], "data": {"2352346": {"age": 4, "name": "mathew"}}}), encoding="utf-8")
            db.set_id_generator(lambda: "1234567")
            assert db.add({"name": "ad", "age": 18}) == "1234567"
            assert read(path)["data"]["1234567"] == {"name": "ad", "age": 18}
        elif name.endswith("test_add_unknown_key_error"):
            path.write_text(json.dumps(DATA2), encoding="utf-8")
            expect_error(UnknownKeyError, lambda: db.add({"age": 4, "name": "fredy", "place": "GB"}))
        elif name.endswith("test_schema_type_error"):
            broken = deepcopy(DATA2); broken["keys"] = "test"
            path.write_text(json.dumps(broken), encoding="utf-8")
            expect_error(SchemaTypeError, lambda: db.add({"name": "test", "age": 69}))
        elif name.endswith("test_add_keys_mismatched_length"):
            path.write_text(json.dumps(DATA2), encoding="utf-8")
            expect_error(UnknownKeyError, lambda: db.add({"name": "test"}))
        else:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"data0": [0, 2], "1": 1, "hello": "hello", "data3": (1, 2), "Foo": type("Foo", (), {})}
            expect_error(TypeError, lambda: db.add(values[suffix]))
        return

    if name.startswith("test_db_add_many.py::"):
        path = path_with()
        db = PysonDB(str(path))
        generator = ids()
        db.set_id_generator(lambda: next(generator))
        if name.endswith("test_add_many_empty_file"):
            assert db.add_many(MANY) is None
            assert read(path) == {"version": 2, "keys": ["age", "name"], "data": {str(i): item for i, item in enumerate(MANY)}}
        elif name.endswith("test_add_many_non_empty_file"):
            path.write_text(json.dumps({"version": 2, "keys": ["age", "name"], "data": {"2352346": {"age": 4, "name": "mathew_first"}}}), encoding="utf-8")
            db.add_many(MANY)
            assert read(path)["data"] == {"2352346": {"age": 4, "name": "mathew_first"}, **{str(i): item for i, item in enumerate(MANY)}}
        elif "type_error_for_list" in name:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"data0": (1,), "data1": {"a": "3"}, "data2": {1, 2}}
            expect_error(TypeError, lambda: db.add_many(values[suffix]))
        elif "type_error_for_dict_in_list" in name:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"data0": [1, 2], "data1": ["a", "b"], "data2": [[1, 2], [3, 4]], "data3": [(1, 2), 3], "data4": [{1, 2}]}
            expect_error(TypeError, lambda: db.add_many(values[suffix]))
        elif name.endswith("test_add_many_unknown_key_error"):
            expect_error(UnknownKeyError, lambda: db.add_many([{"name": "ad", "age": 4}, {"name": "test", "age": 2}, {"name": "new_ad", "age": 5, "place": "GB"}]))
        elif "unknown_key_error_non_empty_file" in name:
            path.write_text(json.dumps({"version": 2, "keys": ["age", "name"], "data": {"2352346": {"age": 4, "name": "mathew_first"}}}), encoding="utf-8")
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"data0": {"name": "ad", "age": 4, "place": "GB"}, "data1": {"name": "ad"}, "data2": {"place": "GB", "is_alive": True}}
            expect_error(UnknownKeyError, lambda: db.add_many([values[suffix]]))
        elif "test_add_many_empty_data" in name:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"": "", "data1": [], "data2": {}}
            assert db.add_many(values[suffix]) is None
        else:
            assert db.add_many(MANY, json_response=True) == {str(i): item for i, item in enumerate(MANY)}
        return

    if name.startswith("test_db_add_new_key.py::"):
        path = path_with(DATA2)
        db = PysonDB(str(path))
        if name.endswith("test_add_new_key"):
            db.add_new_key("place", "GB")
            assert read(path) == {"version": 2, "keys": ["age", "name", "place"], "data": {key: {**value, "place": "GB"} for key, value in DATA2["data"].items()}}
        elif name.endswith("test_add_new_key_no_default"):
            db.add_new_key("place")
            assert read(path) == {"version": 2, "keys": ["age", "name", "place"], "data": {key: {**value, "place": None} for key, value in DATA2["data"].items()}}
        else:
            suffix = name.rsplit("[", 1)[1][:-1]
            value = (1,) if suffix == "default0" else type("test", (), {})
            expect_error(TypeError, lambda: db.add_new_key(value))
        return

    if name.startswith("test_db_autoupdate.py::"):
        final = {"version": 2, "keys": ["age", "name"], "data": {"0": {"age": 3, "name": "test"}}}
        path = path_with()
        if name.endswith("test_autoupdate"):
            db = PysonDB(str(path), auto_update=False); generator = ids(); db.set_id_generator(lambda: next(generator)); db.add({"name": "test", "age": 3})
            assert db.auto_update is False and db._au_memory == final and not path.is_file()
        elif name.endswith("test_autoupdate_force_load"):
            path.write_text(json.dumps(final), encoding="utf-8"); db = PysonDB(str(path), auto_update=False); db.force_load()
            assert db.auto_update is False and db._au_memory == final
        elif name.endswith("test_autoupdate_commit"):
            db = PysonDB(str(path), auto_update=False); generator = ids(); db.set_id_generator(lambda: next(generator)); db.add({"name": "test", "age": 3}); db.commit()
            assert db.auto_update is False and read(path) == final
        elif name.endswith("test_autoupdate_accidental_commit"):
            db = PysonDB(str(path)); db.commit(); assert db.auto_update is True
        else:
            path.write_text(json.dumps(final), encoding="utf-8"); db = PysonDB(str(path)); db.force_load(); assert db.auto_update is True
        return

    if name.startswith("test_db_delete_by_query.py::"):
        path = path_with(DATA3); db = PysonDB(str(path))
        if name.endswith("test_delete_by_query"):
            assert db.delete_by_query(lambda item: item["age"] < 6) == ["219520953066905460", "110180374400879352", "228563587602913112", "167833310760833974"]
            assert list(read(path)["data"]) == ["224980674034561069"]
        else:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"query0": {"a": "4"}, "query1": [1, 2], "1": 1, "2": "2", "query4": {1, 2}}
            expect_error(TypeError, lambda: db.delete_by_query(values[suffix]))
        return

    if name.startswith("test_db_get_all.py::"):
        data = DATA2 if name.endswith("test_get_all") else {"version": 2, "keys": [], "data": {}}
        path = path_with(data)
        assert PysonDB(str(path)).get_all() == data["data"]
        return
    if name.startswith("test_db_get_all_select_keys.py::"):
        data = {"version": 2, "keys": ["age", "name", "toy"], "data": {"2352346": {"age": 4, "name": "mathew_first", "toy": "car"}, "1234567": {"age": 9, "name": "new_user", "toy": "ball"}}}
        path = path_with(data); db = PysonDB(str(path))
        if name.endswith("test_get_all_select_keys"):
            assert db.get_all_select_keys(["age"]) == {key: {"age": value["age"]} for key, value in data["data"].items()}
            assert db.get_all_select_keys(["name", "toy"]) == {key: {"name": value["name"], "toy": value["toy"]} for key, value in data["data"].items()}
        elif name.endswith("test_get_all_select_keys_empty_file"):
            path.write_text(json.dumps({"version": 2, "keys": [], "data": {}}), encoding="utf-8"); assert db.get_all_select_keys([]) == {}
        else:
            expect_error(UnknownKeyError, lambda: db.get_all_select_keys(["wrong_key"]))
        return
    if name.startswith("test_db_get_by_id.py::"):
        path = path_with(DATA2); db = PysonDB(str(path))
        if name.endswith("test_get_by_id"):
            assert db.get_by_id("2352346") == {"age": 4, "name": "mathew_first"}
        elif name.endswith("test_get_by_id_id_does_no_exist_error"):
            expect_error(IdDoesNotExistError, lambda: db.get_by_id("1212121"))
        else:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"2235235": 2235235, "data1": [1, 2], "data2": (1, 2, 3), "data3": {1, 2, 3}, "data4": {"2": "4"}}
            expect_error(TypeError, lambda: db.get_by_id(values[suffix]))
        return
    if name.startswith("test_db_get_by_query.py::"):
        path = path_with(DATA2); db = PysonDB(str(path))
        if "[<lambda>-output0]" in name:
            assert db.get_by_query(lambda item: item["age"] >= 4) == DATA2["data"]
        elif "[<lambda>-output1]" in name:
            assert db.get_by_query(lambda item: item["name"] == "new_user") == {"1234567": DATA2["data"]["1234567"]}
        elif "[<lambda>-output2]" in name:
            assert db.get_by_query(lambda item: item["age"] >= 4 and item["name"] == "mathew_first") == {"2352346": DATA2["data"]["2352346"]}
        elif name.endswith("test_get_by_query_no_matches"):
            pass
        else:
            value = [1, 2] if name.endswith("condition0]") else {"age": 4, "name": 3}
            expect_error(TypeError, lambda: db.get_by_query(value))
        return
    if name == "test_db_purge.py::test_purge":
        path = path_with(DATA3); db = PysonDB(str(path)); db.purge()
        assert read(path) == {"version": 2, "keys": [], "data": {}}
        return
    if name.startswith("test_db_update_by_id.py::"):
        path = path_with(DATA2); db = PysonDB(str(path))
        if name.endswith("test_update_by_id"):
            assert db.update_by_id("1234567", {"age": 69}) == {"age": 69, "name": "new_user"}
            assert read(path)["data"]["1234567"] == {"age": 69, "name": "new_user"}
        elif name.endswith("test_update_by_id_id_does_not_exists"):
            expect_error(IdDoesNotExistError, lambda: db.update_by_id("23526556", {"age": 69}))
        else:
            expect_error(UnknownKeyError, lambda: db.update_by_id("534535", {"place": "GB"}))
        return
    if name.startswith("test_db_update_by_query.py::"):
        data = deepcopy(DATA3); data["data"]["224980674034561069"]["age"] = 74574654
        path = path_with(data); db = PysonDB(str(path))
        if name.endswith("test_update_by_query"):
            assert db.update_by_query(lambda item: item["place"] == "US", {"place": "AU"}) == ["219520953066905460", "110180374400879352"]
            assert read(path)["data"]["219520953066905460"]["place"] == "AU"
        elif name.endswith("test_update_by_query_unknown_key_error"):
            expect_error(UnknownKeyError, lambda: db.update_by_query(lambda item: item["place"] == "IN", {"summer": True}))
        elif "test_update_by_query_type_error" in name:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"a": "a", "query1": [1, 2], "query2": (1, 3), "query3": {"1, 3"}, "query4": {"a": 4, "b": 5}}
            expect_error(TypeError, lambda: db.update_by_query(values[suffix], {"name": "ad"}))
        else:
            suffix = name.rsplit("[", 1)[1][:-1]
            values = {"data0": [1, 2], "1": 1, "string": "string", "data3": (1, 3), "data4": {1, 3}}
            expect_error(TypeError, lambda: db.update_by_query(lambda _: True, values[suffix]))
        return
    if name.startswith("test_db_utils_methods.py::"):
        sample = {"version": 2, "keys": ["a", "b", "c"], "data": {"384753047545745": {"a": 1, "b": "something", "c": True}}}
        path = path_with(sample)
        if name.endswith("test_load"):
            assert PysonDB(str(path))._load_file() == sample
        elif name.endswith("test_dump"):
            PysonDB(str(path))._dump_file(sample); assert path.read_text(encoding="utf-8") == json.dumps(sample, indent=4)
        elif name.endswith("test_gen_file_file_exists"):
            before = path.read_text(encoding="utf-8"); PysonDB(str(path)); assert path.read_text(encoding="utf-8") == before
        else:
            path.unlink(); PysonDB(path); assert path.is_file() and path.read_text(encoding="utf-8") == json.dumps({"version": 2, "keys": [], "data": {}}, indent=4)
        return
    if name.startswith("test_delete_by_id.py::"):
        path = path_with(DATA3); db = PysonDB(str(path))
        if name.endswith("test_delete_by_id"):
            db.delete_by_id("110180374400879352"); assert "110180374400879352" not in read(path)["data"]
        else:
            expect_error(IdDoesNotExistError, lambda: db.delete_by_id("2345"))
        return
    if name == "test_id_generator.py::test_id_generator_incremental_id":
        path = path_with(); db = PysonDB(str(path)); generator = ids(1); db.set_id_generator(lambda: next(generator))
        items = [{"age": 4, "name": "mathew_first"}, {"age": 9, "name": "new_user"}]
        assert db.add_many(items, json_response=True) == {"1": items[0], "2": items[1]}
        assert read(path) == {"version": 2, "keys": ["age", "name"], "data": {"1": items[0], "2": items[1]}}
        return
    if name == "test_something.py::test_foo":
        return
    if name.startswith("test_utils_migrate.py::"):
        if name.endswith("test_migrate"):
            old = {"data": [{"id": 1, "name": "one", "age": 2}, {"id": 2, "name": "two", "age": 3}]}
            assert migrate(old) == {"version": 2, "keys": ["name", "age"], "data": {"1": {"name": "one", "age": 2}, "2": {"name": "two", "age": 3}}}
        else:
            assert migrate({"data": []}) == {"version": 2, "keys": [], "data": {}}
        return
    raise AssertionError(f"unknown case: {name}")


try:
    request = json.load(sys.stdin)
    run_case(request["case"])
    print(json.dumps({"ok": True}, sort_keys=True))
except Exception as exc:
    print(json.dumps({"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}, sort_keys=True))
'''


CASES = '''
test_cli.py::test_cli_info_ujson_exist
test_cli.py::test_cli_info_ujson_does_not_exist
test_cli_merge.py::test_cli_merge
test_cli_merge.py::test_cli_merge_key_mismatch
test_cli_purge.py::test_cli_purge
test_cli_show.py::test_cli_show
test_cli_show.py::test_cli_show_no_prettytable_installed
test_cli_show.py::test_cli_show_v1_db
test_cli_tocsv.py::test_tocsv
test_db_add.py::test_add_empty_file
test_db_add.py::test_add_non_empty_file
test_db_add.py::test_add_unknown_key_error
test_db_add.py::test_schema_type_error
test_db_add.py::test_add_keys_mismatched_length
test_db_add.py::test_add_type_error[data0]
test_db_add.py::test_add_type_error[1]
test_db_add.py::test_add_type_error[hello]
test_db_add.py::test_add_type_error[data3]
test_db_add.py::test_add_type_error[Foo]
test_db_add_many.py::test_add_many_empty_file
test_db_add_many.py::test_add_many_non_empty_file
test_db_add_many.py::test_add_many_type_error_for_list[data0]
test_db_add_many.py::test_add_many_type_error_for_list[data1]
test_db_add_many.py::test_add_many_type_error_for_list[data2]
test_db_add_many.py::test_add_many_type_error_for_dict_in_list[data0]
test_db_add_many.py::test_add_many_type_error_for_dict_in_list[data1]
test_db_add_many.py::test_add_many_type_error_for_dict_in_list[data2]
test_db_add_many.py::test_add_many_type_error_for_dict_in_list[data3]
test_db_add_many.py::test_add_many_type_error_for_dict_in_list[data4]
test_db_add_many.py::test_add_many_unknown_key_error
test_db_add_many.py::test_add_many_unknown_key_error_non_empty_file[data0]
test_db_add_many.py::test_add_many_unknown_key_error_non_empty_file[data1]
test_db_add_many.py::test_add_many_unknown_key_error_non_empty_file[data2]
test_db_add_many.py::test_add_many_empty_data[]
test_db_add_many.py::test_add_many_empty_data[data1]
test_db_add_many.py::test_add_many_empty_data[data2]
test_db_add_many.py::test_add_many_json_response
test_db_add_new_key.py::test_add_new_key
test_db_add_new_key.py::test_add_new_key_no_default
test_db_add_new_key.py::test_add_new_key_invalid_data_type[default0]
test_db_add_new_key.py::test_add_new_key_invalid_data_type[test]
test_db_autoupdate.py::test_autoupdate
test_db_autoupdate.py::test_autoupdate_force_load
test_db_autoupdate.py::test_autoupdate_commit
test_db_autoupdate.py::test_autoupdate_accidental_commit
test_db_autoupdate.py::test_autoupdate_accidental_force_load
test_db_delete_by_query.py::test_delete_by_query
test_db_delete_by_query.py::test_delete_by_query_type_error[query0]
test_db_delete_by_query.py::test_delete_by_query_type_error[query1]
test_db_delete_by_query.py::test_delete_by_query_type_error[1]
test_db_delete_by_query.py::test_delete_by_query_type_error[2]
test_db_delete_by_query.py::test_delete_by_query_type_error[query4]
test_db_get_all.py::test_get_all
test_db_get_all.py::test_get_all_empty_file
test_db_get_all_select_keys.py::test_get_all_select_keys
test_db_get_all_select_keys.py::test_get_all_select_keys_empty_file
test_db_get_all_select_keys.py::test_get_all_select_keys_wrong_key
test_db_get_by_id.py::test_get_by_id
test_db_get_by_id.py::test_get_by_id_id_does_no_exist_error
test_db_get_by_id.py::test_get_id_type_error[2235235]
test_db_get_by_id.py::test_get_id_type_error[data1]
test_db_get_by_id.py::test_get_id_type_error[data2]
test_db_get_by_id.py::test_get_id_type_error[data3]
test_db_get_by_id.py::test_get_id_type_error[data4]
test_db_get_by_query.py::test_get_by_query[<lambda>-output0]
test_db_get_by_query.py::test_get_by_query[<lambda>-output1]
test_db_get_by_query.py::test_get_by_query[<lambda>-output2]
test_db_get_by_query.py::test_get_by_query_no_matches
test_db_get_by_query.py::test_get_by_query_type_error[condition0]
test_db_get_by_query.py::test_get_by_query_type_error[condition1]
test_db_purge.py::test_purge
test_db_update_by_id.py::test_update_by_id
test_db_update_by_id.py::test_update_by_id_id_does_not_exists
test_db_update_by_id.py::test_update_by_id_unknown_key_error
test_db_update_by_query.py::test_update_by_query
test_db_update_by_query.py::test_update_by_query_unknown_key_error
test_db_update_by_query.py::test_update_by_query_type_error[a]
test_db_update_by_query.py::test_update_by_query_type_error[query1]
test_db_update_by_query.py::test_update_by_query_type_error[query2]
test_db_update_by_query.py::test_update_by_query_type_error[query3]
test_db_update_by_query.py::test_update_by_query_type_error[query4]
test_db_update_by_query.py::test_new_data_type_error[data0]
test_db_update_by_query.py::test_new_data_type_error[1]
test_db_update_by_query.py::test_new_data_type_error[string]
test_db_update_by_query.py::test_new_data_type_error[data3]
test_db_update_by_query.py::test_new_data_type_error[data4]
test_db_utils_methods.py::test_load
test_db_utils_methods.py::test_dump
test_db_utils_methods.py::test_gen_file_file_exists
test_db_utils_methods.py::test_gen_file_file_does_not_exist
test_delete_by_id.py::test_delete_by_id
test_delete_by_id.py::test_delete_by_id_id_not_found_error
test_id_generator.py::test_id_generator_incremental_id
test_something.py::test_foo
test_utils_migrate.py::test_migrate
test_utils_migrate.py::test_migrate_empty_data
'''.strip().splitlines()


def main() -> None:
    leaves = []
    for case in CASES:
        passed = False
        try:
            completed = subprocess.run(
                [
                    "runuser", "-u", "candidate", "--", "env",
                    "CANDIDATE_ROOT=/tmp/candidate-site",
                    "NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site",
                    "/usr/local/bin/python", "-I", "-c", CHILD,
                ],
                input=json.dumps({"case": case}),
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )
            response = json.loads(completed.stdout)
            passed = completed.returncode == 0 and response.get("ok") is True
        except Exception:
            passed = False
        leaves.append({"id": case, "status": "passed" if passed else "failed"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
