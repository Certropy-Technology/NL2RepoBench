"""Private deterministic scenarios for the stevedore public contract.

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
        'exc_01_nomatch_is_nouniquematch',
        '\nfrom stevedore.exception import NoMatches, NoUniqueMatch\ntry:\n    raise NoMatches("test message")\nexcept NoUniqueMatch:\n    result = "caught"\n',
        {"ok": True, "value": "caught"},
    ),
    (
        'exc_02_multiplematch_is_nouniquematch',
        '\nfrom stevedore.exception import MultipleMatches, NoUniqueMatch\ntry:\n    raise MultipleMatches("test message")\nexcept NoUniqueMatch:\n    result = "caught"\n',
        {"ok": True, "value": "caught"},
    ),
    (
        'exc_03_nouniquematch_is_runtimeerror',
        '\nfrom stevedore.exception import NoUniqueMatch\ntry:\n    raise NoUniqueMatch("test message")\nexcept RuntimeError:\n    result = "caught"\n',
        {"ok": True, "value": "caught"},
    ),
    (
        'exc_04_nomatch_message',
        '\nfrom stevedore.exception import NoMatches\ne = NoMatches("custom error message")\nresult = str(e)',
        {"ok": True, "value": "custom error message"},
    ),
    (
        'exc_05_multiplematch_message',
        '\nfrom stevedore.exception import MultipleMatches\ne = MultipleMatches("duplicate found")\nresult = str(e)',
        {"ok": True, "value": "duplicate found"},
    ),
    (
        'ext_01_formatter_names',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nresult = sorted(mgr.names())",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'ext_02_formatter_count',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nresult = len(mgr.extensions)",
        {"ok": True, "value": 3},
    ),
    (
        'ext_03_empty_namespace',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='nonexistent.namespace', invoke_on_load=False)\nresult = len(mgr.extensions)",
        {"ok": True, "value": 0},
    ),
    (
        'ext_04_extension_list',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nresult = [e.name for e in mgr.extensions]",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'ext_05_map_names',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nnames = mgr.map(lambda ext: ext.name)\nresult = sorted(names)",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'ext_06_iteration',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nnames = [ext.name for ext in mgr]\nresult = sorted(names)",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'ext_07_simple_module_name',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'simple'][0]\nresult = ext.module_name",
        {"ok": True, "value": "stevedore.example.simple"},
    ),
    (
        'ext_08_simple_attr',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'simple'][0]\nresult = ext.attr",
        {"ok": True, "value": "Simple"},
    ),
    (
        'ext_09_simple_entry_point_target',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'simple'][0]\nresult = ext.entry_point_target",
        {"ok": True, "value": "stevedore.example.simple:Simple"},
    ),
    (
        'ext_10_simple_obj_none',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'simple'][0]\nresult = ext.obj is None",
        {"ok": True, "value": True},
    ),
    (
        'ext_11_simple_plugin_name',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'simple'][0]\nresult = ext.plugin.__name__",
        {"ok": True, "value": "Simple"},
    ),
    (
        'ext_12_field_module_name',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'field'][0]\nresult = ext.module_name",
        {"ok": True, "value": "stevedore.example2.fields"},
    ),
    (
        'ext_13_field_attr',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'field'][0]\nresult = ext.attr",
        {"ok": True, "value": "FieldList"},
    ),
    (
        'ext_14_field_entry_point_target',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'field'][0]\nresult = ext.entry_point_target",
        {"ok": True, "value": "stevedore.example2.fields:FieldList"},
    ),
    (
        'ext_15_field_plugin_name',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'field'][0]\nresult = ext.plugin.__name__",
        {"ok": True, "value": "FieldList"},
    ),
    (
        'ext_16_plain_module_name',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'plain'][0]\nresult = ext.module_name",
        {"ok": True, "value": "stevedore.example.simple"},
    ),
    (
        'ext_17_plain_entry_point_target',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'plain'][0]\nresult = ext.entry_point_target",
        {"ok": True, "value": "stevedore.example.simple:Simple"},
    ),
    (
        'drv_01_simple_driver',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)\nresult = dm.driver.__name__",
        {"ok": True, "value": "Simple"},
    ),
    (
        'drv_02_field_driver',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='field', invoke_on_load=False)\nresult = dm.driver.__name__",
        {"ok": True, "value": "FieldList"},
    ),
    (
        'drv_03_plain_driver',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='plain', invoke_on_load=False)\nresult = dm.driver.__name__",
        {"ok": True, "value": "Simple"},
    ),
    (
        'drv_04_extension_count',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)\nresult = len(dm.extensions)",
        {"ok": True, "value": 1},
    ),
    (
        'drv_05_extension_names',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)\nresult = dm.names()",
        {"ok": True, "value": ["simple"]},
    ),
    (
        'drv_06_nonexistent_nomatch',
        '\nfrom stevedore import DriverManager\nfrom stevedore.exception import NoMatches\ntry:\n    dm = DriverManager(namespace=\'stevedore.example.formatter\', name=\'nonexistent\', invoke_on_load=False)\n    result = None\nexcept NoMatches as e:\n    result = "NoMatches"',
        {"ok": True, "value": "NoMatches"},
    ),
    (
        'drv_07_empty_namespace_nomatch',
        '\nfrom stevedore import DriverManager\nfrom stevedore.exception import NoMatches\ntry:\n    dm = DriverManager(namespace=\'empty.namespace\', name=\'anything\', invoke_on_load=False)\n    result = None\nexcept NoMatches as e:\n    result = "NoMatches"',
        {"ok": True, "value": "NoMatches"},
    ),
    (
        'drv_08_extension_module_name',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='field', invoke_on_load=False)\next = dm.extensions[0]\nresult = ext.module_name",
        {"ok": True, "value": "stevedore.example2.fields"},
    ),
    (
        'drv_09_extension_name',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)\next = dm.extensions[0]\nresult = ext.name",
        {"ok": True, "value": "simple"},
    ),
    (
        'named_01_single_simple',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple'], invoke_on_load=False)\nresult = [e.name for e in nm.extensions]",
        {"ok": True, "value": ["simple"]},
    ),
    (
        'named_02_single_field',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['field'], invoke_on_load=False)\nresult = [e.name for e in nm.extensions]",
        {"ok": True, "value": ["field"]},
    ),
    (
        'named_03_two_names',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple', 'field'], invoke_on_load=False)\nresult = sorted([e.name for e in nm.extensions])",
        {"ok": True, "value": ["field", "simple"]},
    ),
    (
        'named_04_three_names',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple', 'field', 'plain'], invoke_on_load=False)\nresult = len(nm.extensions)",
        {"ok": True, "value": 3},
    ),
    (
        'named_05_all_three_sorted',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['plain', 'simple', 'field'], invoke_on_load=False)\nresult = sorted([e.name for e in nm.extensions])",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'named_06_with_missing_warn_off',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(\n    namespace='stevedore.example.formatter',\n    names=['simple', 'nonexistent'],\n    invoke_on_load=False,\n    warn_on_missing_entrypoint=False\n)\nresult = sorted([e.name for e in nm.extensions])",
        {"ok": True, "value": ["simple"]},
    ),
    (
        'named_07_all_missing',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(\n    namespace='stevedore.example.formatter',\n    names=['nonexistent1', 'nonexistent2'],\n    invoke_on_load=False,\n    warn_on_missing_entrypoint=False\n)\nresult = len(nm.extensions)",
        {"ok": True, "value": 0},
    ),
    (
        'named_08_empty_names',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=[], invoke_on_load=False)\nresult = len(nm.extensions)",
        {"ok": True, "value": 0},
    ),
    (
        'named_09_count_two',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple', 'field'], invoke_on_load=False)\nresult = len(nm.extensions)",
        {"ok": True, "value": 2},
    ),
    (
        'test_01_test_extension_names',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.test.extension', invoke_on_load=False)\nresult = sorted(mgr.names())",
        {"ok": True, "value": ["e1", "t1", "t2"]},
    ),
    (
        'test_02_test_extension_count',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.test.extension', invoke_on_load=False)\nresult = len(mgr.extensions)",
        {"ok": True, "value": 3},
    ),
    (
        'test_03_test_t1_module',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.test.extension', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 't1'][0]\nresult = ext.module_name",
        {"ok": True, "value": "stevedore.tests.test_extension"},
    ),
    (
        'test_04_test_t1_plugin',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.test.extension', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 't1'][0]\nresult = ext.plugin.__name__",
        {"ok": True, "value": "FauxExtension"},
    ),
    (
        'test_05_test_e1_plugin',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.test.extension', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'e1'][0]\nresult = ext.plugin.__name__",
        {"ok": True, "value": "BrokenExtension"},
    ),
    (
        'test_06_driver_t1',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.test.extension', name='t1', invoke_on_load=False)\nresult = dm.driver.__name__",
        {"ok": True, "value": "FauxExtension"},
    ),
    (
        'test_07_driver_e1',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.test.extension', name='e1', invoke_on_load=False)\nresult = dm.driver.__name__",
        {"ok": True, "value": "BrokenExtension"},
    ),
    (
        'test_08_named_t1_t2',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.test.extension', names=['t1', 't2'], invoke_on_load=False)\nresult = sorted([e.name for e in nm.extensions])",
        {"ok": True, "value": ["t1", "t2"]},
    ),
    (
        'map_01_map_module_names',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nmodules = mgr.map(lambda ext: ext.module_name)\nresult = sorted(modules)",
        {"ok": True, "value": ["stevedore.example.simple", "stevedore.example.simple", "stevedore.example2.fields"]},
    ),
    (
        'map_02_map_plugin_names',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nplugins = mgr.map(lambda ext: ext.plugin.__name__)\nresult = sorted(plugins)",
        {"ok": True, "value": ["FieldList", "Simple", "Simple"]},
    ),
    (
        'map_03_map_entry_point_targets',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\ntargets = mgr.map(lambda ext: ext.entry_point_target)\nresult = sorted(targets)",
        {"ok": True, "value": ["stevedore.example.simple:Simple", "stevedore.example.simple:Simple", "stevedore.example2.fields:FieldList"]},
    ),
    (
        'map_04_named_manager_map',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple', 'field'], invoke_on_load=False)\nnames = nm.map(lambda ext: ext.name)\nresult = sorted(names)",
        {"ok": True, "value": ["field", "simple"]},
    ),
    (
        'map_05_driver_manager_map',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)\nnames = dm.map(lambda ext: ext.name)\nresult = names",
        {"ok": True, "value": ["simple"]},
    ),
    (
        'names_01_extension_manager',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nnames = mgr.names()\nresult = sorted(names)",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'names_02_named_manager',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['field', 'simple'], invoke_on_load=False)\nnames = nm.names()\nresult = sorted(names)",
        {"ok": True, "value": ["field", "simple"]},
    ),
    (
        'names_03_driver_manager',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='field', invoke_on_load=False)\nnames = dm.names()\nresult = names",
        {"ok": True, "value": ["field"]},
    ),
    (
        'names_04_empty_namespace',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='empty.namespace', invoke_on_load=False)\nnames = mgr.names()\nresult = names",
        {"ok": True, "value": []},
    ),
    (
        'edge_01_same_plugin_different_names',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nsimple_ext = [e for e in mgr.extensions if e.name == 'simple'][0]\nplain_ext = [e for e in mgr.extensions if e.name == 'plain'][0]\nresult = simple_ext.plugin is plain_ext.plugin",
        {"ok": True, "value": True},
    ),
    (
        'edge_02_named_duplicate_names',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(\n    namespace='stevedore.example.formatter',\n    names=['simple', 'simple'],\n    invoke_on_load=False\n)\nresult = len(nm.extensions)",
        {"ok": True, "value": 1},
    ),
    (
        'edge_03_named_order_preserved',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(\n    namespace='stevedore.example.formatter',\n    names=['plain', 'field', 'simple'],\n    invoke_on_load=False\n)\nresult = [e.name for e in nm.extensions]",
        {"ok": True, "value": ["field", "plain", "simple"]},
    ),
    (
        'edge_04_extension_obj_none_without_invoke',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nobjs = [ext.obj for ext in mgr.extensions]\nresult = all(obj is None for obj in objs)",
        {"ok": True, "value": True},
    ),
    (
        'edge_05_driver_access_via_extensions',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='field', invoke_on_load=False)\nresult = dm.extensions[0].plugin is dm.driver",
        {"ok": True, "value": True},
    ),
    (
        'cov_01_multiple_namespaces_independent',
        "\nfrom stevedore import ExtensionManager\nmgr1 = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nmgr2 = ExtensionManager(namespace='stevedore.test.extension', invoke_on_load=False)\nresult = [len(mgr1.extensions), len(mgr2.extensions)]",
        {"ok": True, "value": [3, 3]},
    ),
    (
        'cov_02_named_with_all_formatter_names',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(\n    namespace='stevedore.example.formatter',\n    names=['simple', 'plain', 'field'],\n    invoke_on_load=False\n)\nresult = len(nm.extensions)",
        {"ok": True, "value": 3},
    ),
    (
        'cov_03_driver_then_extension_manager_same_namespace',
        "\nfrom stevedore import DriverManager, ExtensionManager\ndm = DriverManager(namespace='stevedore.example.formatter', name='simple', invoke_on_load=False)\nem = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\nresult = [dm.driver.__name__, len(em.extensions)]",
        {"ok": True, "value": ["Simple", 3]},
    ),
    (
        'cov_04_extension_iteration_count',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\ncount = sum(1 for _ in mgr)\nresult = count",
        {"ok": True, "value": 3},
    ),
    (
        'cov_05_named_iteration',
        "\nfrom stevedore import NamedExtensionManager\nnm = NamedExtensionManager(namespace='stevedore.example.formatter', names=['field', 'simple'], invoke_on_load=False)\nnames = [ext.name for ext in nm]\nresult = sorted(names)",
        {"ok": True, "value": ["field", "simple"]},
    ),
    (
        'cov_06_test_namespace_driver',
        "\nfrom stevedore import DriverManager\ndm = DriverManager(namespace='stevedore.test.extension', name='t2', invoke_on_load=False)\nresult = dm.driver.__name__",
        {"ok": True, "value": "FauxExtension"},
    ),
    (
        'cov_07_exception_type_check',
        '\nfrom stevedore.exception import NoMatches, NoUniqueMatch\nresult = issubclass(NoMatches, NoUniqueMatch)',
        {"ok": True, "value": True},
    ),
    (
        'cov_08_exception_type_check_multi',
        '\nfrom stevedore.exception import MultipleMatches, NoUniqueMatch\nresult = issubclass(MultipleMatches, NoUniqueMatch)',
        {"ok": True, "value": True},
    ),
    (
        'cov_09_extension_attr_access',
        "\nfrom stevedore import ExtensionManager\nmgr = ExtensionManager(namespace='stevedore.example.formatter', invoke_on_load=False)\next = [e for e in mgr.extensions if e.name == 'field'][0]\nresult = [ext.name, ext.attr, ext.module_name.startswith('stevedore')]",
        {"ok": True, "value": ["field", "FieldList", True]},
    ),
    (
        'cov_10_named_single_then_multiple',
        "\nfrom stevedore import NamedExtensionManager\nnm1 = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple'], invoke_on_load=False)\nnm2 = NamedExtensionManager(namespace='stevedore.example.formatter', names=['simple', 'field'], invoke_on_load=False)\nresult = [len(nm1.extensions), len(nm2.extensions)]",
        {"ok": True, "value": [1, 2]},
    ),
]

assert len(CASES) == 72, f"Expected 72 cases, got {len(CASES)}"


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
