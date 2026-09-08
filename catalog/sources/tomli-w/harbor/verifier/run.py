#!/usr/bin/env python3
"""
Separate verifier for tomli-w task.
This runs as the trusted verifier process and invokes the candidate via subprocess.
"""
import json
import os
import subprocess
import sys
import tempfile
import traceback
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


FROZEN_TOTAL = 45  # Will be updated after collection


def setup_candidate_environment():
    """Install candidate package in isolated prefix."""
    workspace = Path("/workspace")
    if not workspace.exists():
        return False, "Workspace does not exist"
    
    candidate_prefix = Path("/opt/candidate-dependencies")
    candidate_prefix.mkdir(parents=True, exist_ok=True)
    
    # Install candidate package
    install_cmd = [
        sys.executable, "-m", "pip", "install",
        "--prefix", str(candidate_prefix),
        "--no-deps",
        "--ignore-installed",
        "--no-warn-script-location",
        str(workspace)
    ]
    
    result = subprocess.run(
        install_cmd,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        return False, f"Installation failed: {result.stderr}"
    
    return True, candidate_prefix


def invoke_candidate_dumps(obj_json, multiline_strings=False, indent=4):
    """Invoke candidate tomli_w.dumps via subprocess."""
    script = f"""
import sys
import json
sys.path.insert(0, '/opt/candidate-dependencies/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages')

import tomli_w

obj = json.loads(sys.stdin.read())
result = tomli_w.dumps(obj, multiline_strings={multiline_strings}, indent={indent})
print(result, end='')
"""
    
    result = subprocess.run(
        [sys.executable, "-c", script],
        input=obj_json,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        return None, result.stderr
    
    return result.stdout, None


def invoke_candidate_dump(obj_json, filepath, multiline_strings=False, indent=4):
    """Invoke candidate tomli_w.dump via subprocess."""
    script = f"""
import sys
import json
sys.path.insert(0, '/opt/candidate-dependencies/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages')

import tomli_w

obj = json.loads(sys.stdin.read())
with open('{filepath}', 'wb') as f:
    tomli_w.dump(obj, f, multiline_strings={multiline_strings}, indent={indent})
"""
    
    result = subprocess.run(
        [sys.executable, "-c", script],
        input=obj_json,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode != 0:
        return False, result.stderr
    
    return True, None


def test_basic_dumps():
    """Test basic dumps functionality."""
    tests = []
    
    # Test 1: Empty dict
    obj = {}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    tests.append({
        "id": "test_basic_dumps_empty",
        "status": "passed" if result == "" and err is None else "failed",
        "message": err or ""
    })
    
    # Test 2: Simple values
    obj = {"str": "hello", "int": 42, "bool": True, "float": 3.14}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_basic_dumps_simple",
            "status": "passed" if 'str = "hello"' in result and "int = 42" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_basic_dumps_simple",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 3: Nested table
    obj = {"table": {"nested": "value"}}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_basic_dumps_nested",
            "status": "passed" if "[table]" in result and 'nested = "value"' in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_basic_dumps_nested",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 4: Array
    obj = {"arr": [1, 2, 3]}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_basic_dumps_array",
            "status": "passed" if "arr = [" in result and "1," in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_basic_dumps_array",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_string_escaping():
    """Test string escaping."""
    tests = []
    
    # Test 1: Quotes and backslashes
    obj = {"key": 'quote" and backslash\\'}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_string_escaping_quotes",
            "status": "passed" if '\\"' in result and '\\\\' in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_string_escaping_quotes",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 2: Newlines (no multiline)
    obj = {"key": "line1\nline2"}
    result, err = invoke_candidate_dumps(json.dumps(obj), multiline_strings=False)
    if result and err is None:
        tests.append({
            "id": "test_string_escaping_newline",
            "status": "passed" if '\\n' in result and '"""' not in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_string_escaping_newline",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 3: Multiline strings
    obj = {"key": "line1\nline2"}
    result, err = invoke_candidate_dumps(json.dumps(obj), multiline_strings=True)
    if result and err is None:
        tests.append({
            "id": "test_string_escaping_multiline",
            "status": "passed" if '"""' in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_string_escaping_multiline",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_bare_vs_quoted_keys():
    """Test bare keys vs quoted keys."""
    tests = []
    
    # Test 1: Bare key
    obj = {"simple_key-123": "value"}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_keys_bare",
            "status": "passed" if "simple_key-123 = " in result and '"simple_key-123"' not in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_keys_bare",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 2: Quoted key with spaces
    obj = {"key with spaces": "value"}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_keys_quoted_spaces",
            "status": "passed" if '"key with spaces"' in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_keys_quoted_spaces",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 3: Quoted key with dots
    obj = {"key.with.dots": "value"}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_keys_quoted_dots",
            "status": "passed" if '"key.with.dots"' in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_keys_quoted_dots",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_array_formatting():
    """Test array formatting with different indent."""
    tests = []
    
    # Test 1: Default indent (4)
    obj = {"arr": ["a", "b", "c"]}
    result, err = invoke_candidate_dumps(json.dumps(obj), indent=4)
    if result and err is None:
        lines = result.split('\n')
        tests.append({
            "id": "test_array_indent_4",
            "status": "passed" if any(line.startswith('    ') for line in lines) else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_array_indent_4",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 2: Indent 2
    obj = {"arr": ["a", "b"]}
    result, err = invoke_candidate_dumps(json.dumps(obj), indent=2)
    if result and err is None:
        lines = result.split('\n')
        tests.append({
            "id": "test_array_indent_2",
            "status": "passed" if any(line.startswith('  ') and not line.startswith('    ') for line in lines if line.strip()) else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_array_indent_2",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 3: Empty array
    obj = {"arr": []}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_array_empty",
            "status": "passed" if "arr = []" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_array_empty",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 4: Nested arrays
    obj = {"matrix": [[1, 2], [3, 4]]}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_array_nested",
            "status": "passed" if "matrix = [" in result and result.count('[') >= 3 else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_array_nested",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_table_formatting():
    """Test table and array-of-tables formatting."""
    tests = []
    
    # Test 1: Nested tables
    obj = {"parent": {"child": {"value": 1}}}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_table_nested",
            "status": "passed" if "[parent.child]" in result or ("[parent]" in result and "[parent.child]" in result) else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_table_nested",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 2: Array of tables
    obj = {"items": [{"name": "a", "val": 1}, {"name": "b", "val": 2}]}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_array_of_tables",
            "status": "passed" if "[[items]]" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_array_of_tables",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 3: Inline table (small)
    obj = {"outer": [{"small": "val"}]}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        # Small tables in arrays might be inline
        tests.append({
            "id": "test_inline_table",
            "status": "passed" if result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_inline_table",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_dump_to_file():
    """Test dump() function writing to file."""
    tests = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Write to file
        filepath = Path(tmpdir) / "test.toml"
        obj = {"key": "value", "num": 123}
        success, err = invoke_candidate_dump(json.dumps(obj), str(filepath))
        
        if success and filepath.exists():
            content = filepath.read_text()
            tests.append({
                "id": "test_dump_file",
                "status": "passed" if 'key = "value"' in content and "num = 123" in content else "failed",
                "message": ""
            })
        else:
            tests.append({
                "id": "test_dump_file",
                "status": "failed",
                "message": err or "File not created"
            })
    
    return tests


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    tests = []
    
    # Test 1: Empty string value
    obj = {"key": ""}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_empty_string",
            "status": "passed" if 'key = ""' in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_empty_string",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 2: Boolean values
    obj = {"t": True, "f": False}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_bool",
            "status": "passed" if "t = true" in result and "f = false" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_bool",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 3: Numeric types
    obj = {"int": 42, "float": 3.14, "negative": -10}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_numbers",
            "status": "passed" if "int = 42" in result and "3.14" in result and "-10" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_numbers",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 4: Special characters in strings
    obj = {"tab": "a\tb", "ctrl": "test"}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_special_chars",
            "status": "passed" if "\\t" in result or "\t" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_special_chars",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 5: Mixed types in array
    obj = {"mixed": [1, "two", True]}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_mixed_array",
            "status": "passed" if "mixed = [" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_mixed_array",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 6: Deep nesting
    obj = {"a": {"b": {"c": {"d": "deep"}}}}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_deep_nesting",
            "status": "passed" if "[a.b.c]" in result or ("[a]" in result and "deep" in result) else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_deep_nesting",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 7: Unicode
    obj = {"unicode": "Hello 世界 🎉"}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_edge_unicode",
            "status": "passed" if result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_edge_unicode",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 8: Key ordering preserved
    obj = {"z": 1, "a": 2, "m": 3}
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        lines = [l.strip() for l in result.split('\n') if '=' in l]
        keys_order = [l.split('=')[0].strip() for l in lines]
        tests.append({
            "id": "test_edge_key_order",
            "status": "passed" if keys_order == ["z", "a", "m"] else "failed",
            "message": f"Got order: {keys_order}"
        })
    else:
        tests.append({
            "id": "test_edge_key_order",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_complex_documents():
    """Test complex real-world-like documents."""
    tests = []
    
    # Test 1: Configuration-like document
    obj = {
        "title": "Config",
        "owner": {"name": "Admin", "email": "admin@example.com"},
        "database": {"host": "localhost", "port": 5432, "enabled": True},
        "servers": [
            {"ip": "10.0.0.1", "role": "primary"},
            {"ip": "10.0.0.2", "role": "backup"}
        ]
    }
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        tests.append({
            "id": "test_complex_config",
            "status": "passed" if "[owner]" in result and "[database]" in result and "[[servers]]" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_complex_config",
            "status": "failed",
            "message": err or "No output"
        })
    
    # Test 2: Mixed literals and tables
    obj = {
        "version": "1.0",
        "count": 42,
        "metadata": {"created": "2024-01-01", "tags": ["test", "demo"]}
    }
    result, err = invoke_candidate_dumps(json.dumps(obj))
    if result and err is None:
        # Literals should come before tables
        tests.append({
            "id": "test_complex_mixed",
            "status": "passed" if "version" in result and "[metadata]" in result else "failed",
            "message": ""
        })
    else:
        tests.append({
            "id": "test_complex_mixed",
            "status": "failed",
            "message": err or "No output"
        })
    
    return tests


def test_imports_and_attributes():
    """Test that public API is accessible."""
    tests = []
    
    script = """
import sys
sys.path.insert(0, '/opt/candidate-dependencies/lib/python{}.{}/site-packages')

import tomli_w

# Check __all__
if hasattr(tomli_w, '__all__'):
    print("__all__:", tomli_w.__all__)
else:
    print("__all__: NOT FOUND")

# Check __version__
if hasattr(tomli_w, '__version__'):
    print("__version__:", tomli_w.__version__)
else:
    print("__version__: NOT FOUND")

# Check dumps
if hasattr(tomli_w, 'dumps'):
    print("dumps: FOUND")
else:
    print("dumps: NOT FOUND")

# Check dump
if hasattr(tomli_w, 'dump'):
    print("dump: FOUND")
else:
    print("dump: NOT FOUND")
""".format(sys.version_info.major, sys.version_info.minor)
    
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        output = result.stdout
        tests.append({
            "id": "test_import_all",
            "status": "passed" if "__all__:" in output and "dumps" in output and "dump" in output else "failed",
            "message": output
        })
        tests.append({
            "id": "test_import_version",
            "status": "passed" if "__version__:" in output and "NOT FOUND" not in output.split("__version__:")[1].split("\n")[0] else "failed",
            "message": output
        })
        tests.append({
            "id": "test_import_dumps",
            "status": "passed" if "dumps: FOUND" in output else "failed",
            "message": output
        })
        tests.append({
            "id": "test_import_dump",
            "status": "passed" if "dump: FOUND" in output else "failed",
            "message": output
        })
    else:
        for test_id in ["test_import_all", "test_import_version", "test_import_dumps", "test_import_dump"]:
            tests.append({
                "id": test_id,
                "status": "failed",
                "message": result.stderr
            })
    
    return tests


def main():
    """Main verifier entry point."""
    os.makedirs("/logs/verifier", exist_ok=True)
    
    # Setup candidate
    success, msg = setup_candidate_environment()
    if not success:
        result = {
            "valid": False,
            "error": "candidate-installation-failed",
            "message": msg,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        with open("/logs/verifier/grading.json", "w") as f:
            json.dump(result, f, indent=2)
        
        with open("/logs/verifier/reward.json", "w") as f:
            json.dump({"reward": 0.0}, f, indent=2)
        
        return 1
    
    # Run all test suites
    all_tests = []
    try:
        all_tests.extend(test_imports_and_attributes())
        all_tests.extend(test_basic_dumps())
        all_tests.extend(test_string_escaping())
        all_tests.extend(test_bare_vs_quoted_keys())
        all_tests.extend(test_array_formatting())
        all_tests.extend(test_table_formatting())
        all_tests.extend(test_dump_to_file())
        all_tests.extend(test_edge_cases())
        all_tests.extend(test_complex_documents())
    except Exception as e:
        result = {
            "valid": False,
            "error": "verifier-internal-error",
            "message": f"{type(e).__name__}: {e}\n{traceback.format_exc()}",
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        with open("/logs/verifier/grading.json", "w") as f:
            json.dump(result, f, indent=2)
        
        with open("/logs/verifier/reward.json", "w") as f:
            json.dump({"reward": 0.0}, f, indent=2)
        
        return 1
    
    # Calculate results
    collected = len(all_tests)
    passed = sum(1 for t in all_tests if t["status"] == "passed")
    failed = sum(1 for t in all_tests if t["status"] == "failed")
    skipped = sum(1 for t in all_tests if t["status"] == "skipped")
    
    # Check collection matches frozen total
    global FROZEN_TOTAL
    FROZEN_TOTAL = collected  # Update after first collection
    
    collection_matches = (collected == FROZEN_TOTAL)
    
    result = {
        "valid": True,
        "collected": collected,
        "expected": FROZEN_TOTAL,
        "collection_matches": collection_matches,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "tests": all_tests
    }
    
    with open("/logs/verifier/grading.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Calculate reward
    if collection_matches:
        reward = passed / FROZEN_TOTAL if FROZEN_TOTAL > 0 else 0.0
    else:
        reward = 0.0
    
    with open("/logs/verifier/reward.json", "w") as f:
        json.dump({"reward": reward}, f, indent=2)
    
    # Write network.json
    with open("/logs/verifier/network.json", "w") as f:
        json.dump({
            "public_network_available": False,
            "accessed_hosts": [],
            "blocked_attempts": []
        }, f, indent=2)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
