#!/usr/bin/env python3
"""
Verifier for natsort task.
Schema: custom-json-v1 with fixed scenario list.
"""
import json
import sys
from typing import Any

from nl2repobench.verification.candidate_client import execute_script

CASES: list[tuple[str, str, object]] = [
    # Basic natsorted() tests
    ("basic_numeric", """
from natsort import natsorted
result = natsorted(['1', '10', '2'])
""", {"ok": True, "value": ['1', '2', '10']}),
    
    ("basic_mixed", """
from natsort import natsorted
result = natsorted(['a2', 'a10', 'a1'])
""", {"ok": True, "value": ['a1', 'a2', 'a10']}),
    
    ("height_example", """
from natsort import natsorted
result = natsorted(['2 ft 7 in', '1 ft 5 in', '10 ft 2 in', '2 ft 11 in', '7 ft 6 in'])
""", {"ok": True, "value": ['1 ft 5 in', '2 ft 7 in', '2 ft 11 in', '7 ft 6 in', '10 ft 2 in']}),
    
    ("version_example", """
from natsort import natsorted
result = natsorted(['version-1.9', 'version-2.0', 'version-1.11', 'version-1.10'])
""", {"ok": True, "value": ['version-1.9', 'version-1.10', 'version-1.11', 'version-2.0']}),
    
    # ns.IGNORECASE tests
    ("ignorecase_basic", """
from natsort import natsorted, ns
result = natsorted(['Apple', 'banana', 'apple', 'Banana'], alg=ns.IGNORECASE)
""", {"ok": True, "value": ['Apple', 'apple', 'banana', 'Banana']}),
    
    ("ignorecase_mixed_numbers", """
from natsort import natsorted, ns
result = natsorted(['a10', 'A2', 'a1', 'A20'], alg=ns.IGNORECASE)
""", {"ok": True, "value": ['a1', 'A2', 'a10', 'A20']}),
    
    # ns.LOWERCASEFIRST tests
    ("lowercasefirst_basic", """
from natsort import natsorted, ns
result = natsorted(['Apple', 'banana', 'apple', 'Banana'], alg=ns.LOWERCASEFIRST)
""", {"ok": True, "value": ['apple', 'banana', 'Apple', 'Banana']}),
    
    # ns.REAL tests (signed floats)
    ("real_signed", """
from natsort import natsorted, ns
result = natsorted(['position5.10', 'position-3', 'position5.3', 'position2'], alg=ns.REAL)
""", {"ok": True, "value": ['position-3', 'position2', 'position5.10', 'position5.3']}),
    
    ("real_floats", """
from natsort import natsorted, ns
result = natsorted(['1.5', '1.10', '-2.0', '3.2'], alg=ns.REAL)
""", {"ok": True, "value": ['-2.0', '1.10', '1.5', '3.2']}),
    
    # ns.PATH tests
    ("path_basic", """
from natsort import natsorted, ns
result = natsorted(['file10.txt', 'file2.txt', 'file1.txt'], alg=ns.PATH)
""", {"ok": True, "value": ['file1.txt', 'file2.txt', 'file10.txt']}),
    
    ("path_folders", """
from natsort import natsorted, ns
result = natsorted(['Folder (10)/', 'Folder/', 'Folder (1)/'], alg=ns.PATH)
""", {"ok": True, "value": ['Folder/', 'Folder (1)/', 'Folder (10)/']}),
    
    # ns.NUMAFTER tests
    ("numafter", """
from natsort import natsorted, ns
result = natsorted(['a', '1', 'b', '2'], alg=ns.NUMAFTER)
""", {"ok": True, "value": ['a', 'b', '1', '2']}),
    
    # natsort_keygen tests
    ("keygen_basic", """
from natsort import natsort_keygen
key = natsort_keygen()
result = sorted(['a10', 'a2', 'a1'], key=key)
""", {"ok": True, "value": ['a1', 'a2', 'a10']}),
    
    ("keygen_ignorecase", """
from natsort import natsort_keygen, ns
key = natsort_keygen(alg=ns.IGNORECASE)
result = sorted(['Apple', 'banana', 'apple'], key=key)
""", {"ok": True, "value": ['Apple', 'apple', 'banana']}),
    
    # realsorted convenience function
    ("realsorted_basic", """
from natsort import realsorted
result = realsorted(['position5.10', 'position-3', 'position5.3', 'position2'])
""", {"ok": True, "value": ['position-3', 'position2', 'position5.10', 'position5.3']}),
    
    # humansorted convenience function  
    ("humansorted_basic", """
from natsort import humansorted
result = humansorted(['item2', 'item10', 'item1'])
""", {"ok": True, "value": ['item1', 'item2', 'item10']}),
    
    # Mixed types
    ("mixed_types", """
from natsort import natsorted
result = natsorted([5, '4', 3.0, '2'])
""", {"ok": True, "value": ['2', 3.0, '4', 5]}),
    
    # Empty list
    ("empty_list", """
from natsort import natsorted
result = natsorted([])
""", {"ok": True, "value": []}),
    
    # Single element
    ("single_element", """
from natsort import natsorted
result = natsorted(['test'])
""", {"ok": True, "value": ['test']}),
    
    # Complex version strings
    ("complex_versions", """
from natsort import natsorted
result = natsorted(['v1.0.0', 'v1.0.10', 'v1.0.2', 'v1.2.0', 'v1.10.0'])
""", {"ok": True, "value": ['v1.0.0', 'v1.0.2', 'v1.0.10', 'v1.2.0', 'v1.10.0']}),
    
    # Leading zeros
    ("leading_zeros", """
from natsort import natsorted
result = natsorted(['a001', 'a1', 'a01', 'a10'])
""", {"ok": True, "value": ['a001', 'a1', 'a01', 'a10']}),
    
    # Multiple numbers in string
    ("multiple_numbers", """
from natsort import natsorted
result = natsorted(['1-2-3', '1-2-10', '1-10-2', '2-1-1'])
""", {"ok": True, "value": ['1-2-3', '1-2-10', '1-10-2', '2-1-1']}),
    
    # Unicode strings
    ("unicode_strings", """
from natsort import natsorted
result = natsorted(['café2', 'café10', 'café1'])
""", {"ok": True, "value": ['café1', 'café2', 'café10']}),
    
    # Negative numbers without REAL
    ("negative_no_real", """
from natsort import natsorted
result = natsorted(['-10', '-2', '5', '1'])
""", {"ok": True, "value": ['1', '5', '-2', '-10']}),
    
    # ns.SIGNED test
    ("signed_basic", """
from natsort import natsorted, ns
result = natsorted(['-10', '-2', '5', '1'], alg=ns.SIGNED)
""", {"ok": True, "value": ['-10', '-2', '1', '5']}),
    
    # ns.FLOAT test
    ("float_basic", """
from natsort import natsorted, ns
result = natsorted(['1.5', '1.10', '1.2'], alg=ns.FLOAT)
""", {"ok": True, "value": ['1.10', '1.2', '1.5']}),
    
    # Combining multiple flags
    ("combined_real_ignorecase", """
from natsort import natsorted, ns
result = natsorted(['A-5', 'b2', 'A10', 'b-3'], alg=ns.REAL | ns.IGNORECASE)
""", {"ok": True, "value": ['A-5', 'A10', 'b-3', 'b2']}),
    
    # os_sorted function
    ("os_sorted_basic", """
from natsort import os_sorted
result = os_sorted(['file10', 'file2', 'file1'])
""", {"ok": True, "value": ['file1', 'file2', 'file10']}),
    
    # Reverse sorting
    ("reverse_basic", """
from natsort import natsorted
result = natsorted(['a10', 'a2', 'a1'], reverse=True)
""", {"ok": True, "value": ['a10', 'a2', 'a1']}),
    
    # Key function with natsorted
    ("key_function", """
from natsort import natsorted
result = natsorted(['apple2', 'banana10', 'apple1'], key=lambda x: x.replace('apple', 'z'))
""", {"ok": True, "value": ['banana10', 'apple1', 'apple2']}),
    
    # index_natsorted
    ("index_natsorted_basic", """
from natsort import index_natsorted
result = index_natsorted(['a10', 'a2', 'a1'])
""", {"ok": True, "value": [2, 1, 0]}),
    
    # ns.GROUPLETTERS
    ("groupletters", """
from natsort import natsorted, ns
result = natsorted(['Apple', 'banana', 'apple', 'Banana'], alg=ns.GROUPLETTERS)
""", {"ok": True, "value": ['Apple', 'apple', 'Banana', 'banana']}),
    
    # ns.COMPATIBILITYNORMALIZE
    ("compatibilitynormalize", """
from natsort import natsorted, ns
result = natsorted(['test1', 'test2'])
""", {"ok": True, "value": ['test1', 'test2']}),
    
    # Large numbers
    ("large_numbers", """
from natsort import natsorted
result = natsorted(['item1000000', 'item999', 'item10000'])
""", {"ok": True, "value": ['item999', 'item10000', 'item1000000']}),
    
    # Scientific notation without NOEXP
    ("scientific_default", """
from natsort import natsorted
result = natsorted(['1E10', '1E2', '1E100'])
""", {"ok": True, "value": ['1E2', '1E10', '1E100']}),
    
    # ns.NOEXP test
    ("noexp", """
from natsort import natsorted, ns
result = natsorted(['5.6E5', '5.6E10'], alg=ns.NOEXP)
""", {"ok": True, "value": ['5.6E5', '5.6E10']}),
    
    # Spaces in strings
    ("spaces", """
from natsort import natsorted
result = natsorted(['test 10', 'test 2', 'test 1'])
""", {"ok": True, "value": ['test 1', 'test 2', 'test 10']}),
    
    # Special characters
    ("special_chars", """
from natsort import natsorted
result = natsorted(['file_10', 'file-2', 'file.1'])
""", {"ok": True, "value": ['file-2', 'file.1', 'file_10']}),
    
    # Path-like with extensions
    ("path_extensions", """
from natsort import natsorted, ns
result = natsorted(['file10.txt', 'file10.csv', 'file2.txt'], alg=ns.PATH)
""", {"ok": True, "value": ['file2.txt', 'file10.csv', 'file10.txt']}),
    
    # as_utf8 helper
    ("as_utf8_basic", """
from natsort import natsorted, as_utf8
result = [x.hex() for x in natsorted([b'a10', b'a2', b'a1'], key=as_utf8)]
""", {"ok": True, "value": ['6131', '6132', '613130']}),
    
    # None values (default behavior - sorted first)
    ("none_default", """
from natsort import natsorted
result = natsorted(['a', None, 'b'])
""", {"ok": True, "value": [None, 'a', 'b']}),
    
    # None with NANLAST (behaves same as default with None)
    ("none_with_nanlast", """
from natsort import natsorted, ns
result = natsorted(['a', None, 'b'], alg=ns.NANLAST)
""", {"ok": True, "value": [None, 'a', 'b']}),
    
    # Numeric only list
    ("numeric_only", """
from natsort import natsorted
result = natsorted(['100', '20', '3'])
""", {"ok": True, "value": ['3', '20', '100']}),
    
    # Letters only
    ("letters_only", """
from natsort import natsorted
result = natsorted(['zebra', 'apple', 'mango'])
""", {"ok": True, "value": ['apple', 'mango', 'zebra']}),
    
    # Decimals in text
    ("decimals_in_text", """
from natsort import natsorted
result = natsorted(['price3.50', 'price10.25', 'price1.99'])
""", {"ok": True, "value": ['price1.99', 'price3.50', 'price10.25']}),
    
    # Complex mixed
    ("complex_mixed", """
from natsort import natsorted
result = natsorted(['Test', 'test10', 'Test2', 'test1'])
""", {"ok": True, "value": ['Test', 'Test2', 'test1', 'test10']}),
    
    # IP-like strings
    ("ip_like", """
from natsort import natsorted
result = natsorted(['192.168.1.10', '192.168.1.2', '192.168.10.1'])
""", {"ok": True, "value": ['192.168.1.2', '192.168.1.10', '192.168.10.1']}),
    
    # Date-like strings
    ("date_like", """
from natsort import natsorted
result = natsorted(['2023-01-10', '2023-01-02', '2023-10-01'])
""", {"ok": True, "value": ['2023-01-02', '2023-01-10', '2023-10-01']}),
    
    # Multiple word strings
    ("multiple_words", """
from natsort import natsorted
result = natsorted(['test case 10', 'test case 2', 'test case 1'])
""", {"ok": True, "value": ['test case 1', 'test case 2', 'test case 10']}),
    
    # With hyphens
    ("hyphens", """
from natsort import natsorted
result = natsorted(['2023-10', '2023-2', '2023-1'])
""", {"ok": True, "value": ['2023-1', '2023-2', '2023-10']}),
    
    # Underscores
    ("underscores", """
from natsort import natsorted
result = natsorted(['test_10', 'test_2', 'test_1'])
""", {"ok": True, "value": ['test_1', 'test_2', 'test_10']}),
    
    # Mixed separators
    ("mixed_separators", """
from natsort import natsorted
result = natsorted(['a-10', 'a_2', 'a.1'])
""", {"ok": True, "value": ['a-10', 'a.1', 'a_2']}),
    
    # REAL with explicit sign
    ("real_explicit_sign", """
from natsort import natsorted, ns
result = natsorted(['+5', '-3', '+10', '-20'], alg=ns.REAL)
""", {"ok": True, "value": ['-20', '-3', '+5', '+10']}),
    
    # Float precision
    ("float_precision", """
from natsort import natsorted, ns
result = natsorted(['1.001', '1.01', '1.1'], alg=ns.FLOAT)
""", {"ok": True, "value": ['1.001', '1.01', '1.1']}),
    
    # All caps vs lowercase
    ("caps_vs_lower", """
from natsort import natsorted
result = natsorted(['ABC', 'abc', 'Abc'])
""", {"ok": True, "value": ['ABC', 'Abc', 'abc']}),
    
    # Duplicate values
    ("duplicates", """
from natsort import natsorted
result = natsorted(['a2', 'a1', 'a2', 'a1'])
""", {"ok": True, "value": ['a1', 'a1', 'a2', 'a2']}),
    
    # Long strings
    ("long_strings", """
from natsort import natsorted
result = natsorted(['verylongstring10', 'verylongstring2', 'verylongstring100'])
""", {"ok": True, "value": ['verylongstring2', 'verylongstring10', 'verylongstring100']}),
    
    # Parentheses in names
    ("parentheses", """
from natsort import natsorted
result = natsorted(['file(10)', 'file(2)', 'file(1)'])
""", {"ok": True, "value": ['file(1)', 'file(2)', 'file(10)']}),
    
    # Brackets
    ("brackets", """
from natsort import natsorted
result = natsorted(['file[10]', 'file[2]', 'file[1]'])
""", {"ok": True, "value": ['file[1]', 'file[2]', 'file[10]']}),
    
    # Multiple dots
    ("multiple_dots", """
from natsort import natsorted
result = natsorted(['1.2.10', '1.2.2', '1.10.1'])
""", {"ok": True, "value": ['1.2.2', '1.2.10', '1.10.1']}),
    
    # Zero values
    ("zeros", """
from natsort import natsorted
result = natsorted(['a0', 'a00', 'a1'])
""", {"ok": True, "value": ['a0', 'a00', 'a1']}),
    
    # Hexadecimal-like (not parsed as hex, just strings)
    ("hex_like", """
from natsort import natsorted
result = natsorted(['0x10', '0x2', '0x100'])
""", {"ok": True, "value": ['0x2', '0x10', '0x100']}),
    
    # FLOAT with integers
    ("float_with_integers", """
from natsort import natsorted, ns
result = natsorted(['1', '1.5', '2'], alg=ns.FLOAT)
""", {"ok": True, "value": ['1', '1.5', '2']}),
    
    # PRESORT option
    ("presort", """
from natsort import natsorted, ns
result = natsorted(['a01', 'a1', 'a2'], alg=ns.PRESORT)
""", {"ok": True, "value": ['a01', 'a1', 'a2']}),
    
    # Custom key with ns options
    ("custom_key_with_ns", """
from natsort import natsorted, ns
result = natsorted(['A10', 'a2', 'A1'], key=str.lower, alg=ns.INT)
""", {"ok": True, "value": ['A1', 'a2', 'A10']}),
    
    # List of tuples (first element)
    ("list_of_lists", """
from natsort import natsorted
result = natsorted([['a', '10'], ['a', '2'], ['a', '1']])
""", {"ok": True, "value": [['a', '1'], ['a', '2'], ['a', '10']]}),
    
    # natsort_key function directly
    ("natsort_key_direct", """
from natsort import natsort_key
result = natsort_key('test10')
""", {"ok": True, "value": ['test', 10]}),
    
    # More complex natsort_key
    ("natsort_key_complex", """
from natsort import natsort_key
result = natsort_key('file-2.10.txt')
""", {"ok": True, "value": ['file-', 2, '.', 10, '.txt']}),
    
    # Stability of sort
    ("stability", """
from natsort import natsorted
result = natsorted([('a', 2), ('a', 1), ('b', 2), ('b', 1)], key=lambda x: x[0])
""", {"ok": True, "value": [['a', 2], ['a', 1], ['b', 2], ['b', 1]]}),
    
    # Empty strings
    ("empty_strings", """
from natsort import natsorted
result = natsorted(['', 'a', ''])
""", {"ok": True, "value": ['', '', 'a']}),
    
    # order_by_index function
    ("order_by_index", """
from natsort import order_by_index
result = order_by_index(['a', 'b', 'c'], [2, 0, 1])
""", {"ok": True, "value": ['c', 'a', 'b']}),
    
    # index_natsorted with key
    ("index_natsorted_with_key", """
from natsort import index_natsorted
result = index_natsorted(['A10', 'a2', 'A1'], key=str.lower)
""", {"ok": True, "value": [2, 1, 0]}),
]

def main() -> None:
    """Run all test cases and output JSON result."""
    leaves = []
    
    for case_id, script, expected in CASES:
        try:
            observed = execute_script(script)
            actual = {"ok": observed.ok, "value": observed.value}
            if not observed.ok:
                actual["exception_type"] = observed.exception_type
                actual["exception_message"] = observed.exception_message

            # Compare actual vs expected
            if actual == expected:
                status = "passed"
            else:
                status = "failed"
                
        except Exception as e:
            status = "failed"
        
        leaves.append({"id": case_id, "status": status})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    
    print(json.dumps(output))

if __name__ == "__main__":
    main()
