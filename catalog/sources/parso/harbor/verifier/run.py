#!/usr/bin/env python3
"""
Custom JSON v1 verifier for parso package.
Tests parsing functionality and AST node types.
"""
import json
import sys
from nl2repobench.verification.candidate_client import execute_script

# Test cases: (id, script, expected_result)
CASES = [
    # Test 1-10: Basic parsing and node types
    ("parse_simple_assignment", """
import parso
module = parso.parse('x = 1')
result = module.children[0].type
""", {"ok": True, "value": "expr_stmt"}),
    
    ("parse_module_type", """
import parso
module = parso.parse('x = 1')
result = type(module).__name__
""", {"ok": True, "value": "Module"}),
    
    ("parse_expression_addition", """
import parso
module = parso.parse('hello + 1')
expr = module.children[0]
result = expr.type
""", {"ok": True, "value": "arith_expr"}),
    
    ("parse_name_value", """
import parso
module = parso.parse('hello + 1')
expr = module.children[0]
name = expr.children[0]
result = name.value
""", {"ok": True, "value": "hello"}),
    
    ("parse_name_type", """
import parso
module = parso.parse('hello + 1')
expr = module.children[0]
name = expr.children[0]
result = name.type
""", {"ok": True, "value": "name"}),
    
    ("parse_get_code", """
import parso
module = parso.parse('hello + 1')
expr = module.children[0]
result = expr.get_code()
""", {"ok": True, "value": "hello + 1"}),
    
    ("parse_name_end_pos", """
import parso
module = parso.parse('hello + 1')
expr = module.children[0]
name = expr.children[0]
result = list(name.end_pos)
""", {"ok": True, "value": [1, 5]}),
    
    ("parse_expr_end_pos", """
import parso
module = parso.parse('hello + 1')
expr = module.children[0]
result = list(expr.end_pos)
""", {"ok": True, "value": [1, 9]}),
    
    ("parse_operator_value", """
import parso
module = parso.parse('a + b')
expr = module.children[0]
op = expr.children[1]
result = op.value
""", {"ok": True, "value": "+"}),
    
    ("parse_number_value", """
import parso
module = parso.parse('x = 42')
stmt = module.children[0]
number = stmt.children[2]
result = number.value
""", {"ok": True, "value": "42"}),
    
    # Test 11-20: Function and class definitions
    ("parse_funcdef_type", """
import parso
code = 'def foo(x):\\n    return x + 1'
module = parso.parse(code)
func = module.children[0]
result = func.type
""", {"ok": True, "value": "funcdef"}),
    
    ("parse_funcdef_name_value", """
import parso
code = 'def foo(x):\\n    return x + 1'
module = parso.parse(code)
func = module.children[0]
result = func.name.value
""", {"ok": True, "value": "foo"}),
    
    ("parse_classdef_type", """
import parso
code = 'class MyClass:\\n    pass'
module = parso.parse(code)
cls = module.children[0]
result = cls.type
""", {"ok": True, "value": "classdef"}),
    
    ("parse_classdef_name_value", """
import parso
code = 'class MyClass:\\n    pass'
module = parso.parse(code)
cls = module.children[0]
result = cls.name.value
""", {"ok": True, "value": "MyClass"}),
    
    ("parse_import_type", """
import parso
module = parso.parse('import os')
import_stmt = module.children[0]
result = import_stmt.type
""", {"ok": True, "value": "import_name"}),
    
    ("parse_from_import_type", """
import parso
module = parso.parse('from os import path')
import_stmt = module.children[0]
result = import_stmt.type
""", {"ok": True, "value": "import_from"}),
    
    ("parse_if_stmt_type", """
import parso
code = 'if x > 0:\\n    pass'
module = parso.parse(code)
if_stmt = module.children[0]
result = if_stmt.type
""", {"ok": True, "value": "if_stmt"}),
    
    ("parse_for_stmt_type", """
import parso
code = 'for i in range(10):\\n    pass'
module = parso.parse(code)
for_stmt = module.children[0]
result = for_stmt.type
""", {"ok": True, "value": "for_stmt"}),
    
    ("parse_while_stmt_type", """
import parso
code = 'while True:\\n    pass'
module = parso.parse(code)
while_stmt = module.children[0]
result = while_stmt.type
""", {"ok": True, "value": "while_stmt"}),
    
    ("parse_with_stmt_type", """
import parso
code = 'with open("file.txt") as f:\\n    pass'
module = parso.parse(code)
with_stmt = module.children[0]
result = with_stmt.type
""", {"ok": True, "value": "with_stmt"}),
    
    # Test 21-30: Try-except, return, pass, etc.
    ("parse_try_stmt_type", """
import parso
code = 'try:\\n    pass\\nexcept Exception:\\n    pass'
module = parso.parse(code)
try_stmt = module.children[0]
result = try_stmt.type
""", {"ok": True, "value": "try_stmt"}),
    
    ("parse_return_stmt_type", """
import parso
code = 'def f():\\n    return 1'
module = parso.parse(code)
func = module.children[0]
suite = func.children[-1]
return_stmt = suite.children[1]
result = return_stmt.type
""", {"ok": True, "value": "return_stmt"}),
    
    ("parse_pass_keyword_type", """
import parso
code = 'pass'
module = parso.parse(code)
keyword = module.children[0]
result = keyword.type
""", {"ok": True, "value": "keyword"}),
    
    ("parse_pass_keyword_value", """
import parso
code = 'pass'
module = parso.parse(code)
keyword = module.children[0]
result = keyword.value
""", {"ok": True, "value": "pass"}),
    
    ("parse_break_keyword", """
import parso
code = 'for i in range(10):\\n    break'
module = parso.parse(code)
result = module.children[0].type
""", {"ok": True, "value": "for_stmt"}),
    
    ("parse_continue_keyword", """
import parso
code = 'for i in range(10):\\n    continue'
module = parso.parse(code)
result = module.children[0].type
""", {"ok": True, "value": "for_stmt"}),
    
    ("parse_assert_stmt_type", """
import parso
code = 'assert True'
module = parso.parse(code)
assert_stmt = module.children[0]
result = assert_stmt.type
""", {"ok": True, "value": "assert_stmt"}),
    
    ("parse_del_stmt_type", """
import parso
code = 'del x'
module = parso.parse(code)
del_stmt = module.children[0]
result = del_stmt.type
""", {"ok": True, "value": "del_stmt"}),
    
    ("parse_raise_stmt_type", """
import parso
code = 'raise ValueError'
module = parso.parse(code)
raise_stmt = module.children[0]
result = raise_stmt.type
""", {"ok": True, "value": "raise_stmt"}),
    
    ("parse_global_stmt_type", """
import parso
code = 'global x'
module = parso.parse(code)
global_stmt = module.children[0]
result = global_stmt.type
""", {"ok": True, "value": "global_stmt"}),
    
    # Test 31-40: Literals and data structures
    ("parse_string_value", """
import parso
code = '"hello"'
module = parso.parse(code)
string = module.children[0]
result = string.value
""", {"ok": True, "value": '"hello"'}),
    
    ("parse_string_type", """
import parso
code = '"hello"'
module = parso.parse(code)
string = module.children[0]
result = string.type
""", {"ok": True, "value": "string"}),
    
    ("parse_list_atom_type", """
import parso
code = '[1, 2, 3]'
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    ("parse_dict_atom_type", """
import parso
code = "{'a': 1}"
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    ("parse_tuple_atom_type", """
import parso
code = '(1, 2, 3)'
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    ("parse_set_atom_type", """
import parso
code = '{1, 2, 3}'
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    ("parse_lambda_type", """
import parso
code = 'lambda x: x + 1'
module = parso.parse(code)
lambda_expr = module.children[0]
result = lambda_expr.type
""", {"ok": True, "value": "lambdef"}),
    
    ("parse_list_comp_type", """
import parso
code = '[x for x in range(10)]'
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    ("parse_dict_comp_type", """
import parso
code = '{x: x*2 for x in range(10)}'
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    ("parse_set_comp_type", """
import parso
code = '{x for x in range(10)}'
module = parso.parse(code)
atom = module.children[0]
result = atom.type
""", {"ok": True, "value": "atom"}),
    
    # Test 41-50: Operators and comparisons
    ("parse_comparison_type", """
import parso
code = 'x > 0'
module = parso.parse(code)
comp = module.children[0]
result = comp.type
""", {"ok": True, "value": "comparison"}),
    
    ("parse_and_test_type", """
import parso
code = 'x and y'
module = parso.parse(code)
and_test = module.children[0]
result = and_test.type
""", {"ok": True, "value": "and_test"}),
    
    ("parse_or_test_type", """
import parso
code = 'x or y'
module = parso.parse(code)
or_test = module.children[0]
result = or_test.type
""", {"ok": True, "value": "or_test"}),
    
    ("parse_not_test_type", """
import parso
code = 'not x'
module = parso.parse(code)
not_test = module.children[0]
result = not_test.type
""", {"ok": True, "value": "not_test"}),
    
    ("parse_unary_minus", """
import parso
code = '-x'
module = parso.parse(code)
factor = module.children[0]
result = factor.type
""", {"ok": True, "value": "factor"}),
    
    ("parse_multiply_type", """
import parso
code = 'x * y'
module = parso.parse(code)
term = module.children[0]
result = term.type
""", {"ok": True, "value": "term"}),
    
    ("parse_power_type", """
import parso
code = 'x ** y'
module = parso.parse(code)
power = module.children[0]
result = power.type
""", {"ok": True, "value": "power"}),
    
    ("parse_shift_left_type", """
import parso
code = 'x << 2'
module = parso.parse(code)
shift = module.children[0]
result = shift.type
""", {"ok": True, "value": "shift_expr"}),
    
    ("parse_bitwise_and_type", """
import parso
code = 'x & y'
module = parso.parse(code)
and_expr = module.children[0]
result = and_expr.type
""", {"ok": True, "value": "and_expr"}),
    
    ("parse_bitwise_xor_type", """
import parso
code = 'x ^ y'
module = parso.parse(code)
xor_expr = module.children[0]
result = xor_expr.type
""", {"ok": True, "value": "xor_expr"}),
    
    # Test 51-60: Attribute access, subscript, call (CORRECTED)
    ("parse_trailer_attr_type", """
import parso
code = 'obj.attr'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_trailer_subscript_type", """
import parso
code = 'lst[0]'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_trailer_call_type", """
import parso
code = 'func()'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_trailer_call_with_args", """
import parso
code = 'func(x, y)'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_slice_type", """
import parso
code = 'lst[1:3]'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_slice_step", """
import parso
code = 'lst[::2]'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_multiple_trailers", """
import parso
code = 'obj.method()[0]'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_nested_attribute", """
import parso
code = 'obj.attr.method'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_get_code_attr", """
import parso
code = 'obj.attr'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.get_code()
""", {"ok": True, "value": "obj.attr"}),
    
    ("parse_get_code_call", """
import parso
code = 'func(x, y)'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.get_code()
""", {"ok": True, "value": "func(x, y)"}),
    
    # Test 61-70: Docstrings, decorators, async/await (CORRECTED)
    ("parse_decorator_type", """
import parso
code = '@decorator\\ndef func():\\n    pass'
module = parso.parse(code)
decorated = module.children[0]
result = decorated.type
""", {"ok": True, "value": "decorated"}),
    
    ("parse_async_funcdef_type", """
import parso
code = 'async def func():\\n    pass'
module = parso.parse(code)
async_stmt = module.children[0]
result = async_stmt.type
""", {"ok": True, "value": "async_stmt"}),
    
    ("parse_async_for_stmt_type", """
import parso
code = 'async def f():\\n    async for x in aiter:\\n        pass'
module = parso.parse(code)
async_stmt = module.children[0]
result = async_stmt.type
""", {"ok": True, "value": "async_stmt"}),
    
    ("parse_async_with_stmt_type", """
import parso
code = 'async def f():\\n    async with ctx:\\n        pass'
module = parso.parse(code)
async_stmt = module.children[0]
result = async_stmt.type
""", {"ok": True, "value": "async_stmt"}),
    
    ("parse_await_expr", """
import parso
code = 'async def f():\\n    await x'
module = parso.parse(code)
async_stmt = module.children[0]
result = async_stmt.type
""", {"ok": True, "value": "async_stmt"}),
    
    ("parse_yield_expr_type", """
import parso
code = 'def gen():\\n    yield 1'
module = parso.parse(code)
func = module.children[0]
result = func.type
""", {"ok": True, "value": "funcdef"}),
    
    ("parse_yield_from_type", """
import parso
code = 'def gen():\\n    yield from other'
module = parso.parse(code)
func = module.children[0]
result = func.type
""", {"ok": True, "value": "funcdef"}),
    
    ("parse_starred_expr", """
import parso
code = '*args'
module = parso.parse(code)
star_expr = module.children[0]
result = star_expr.type
""", {"ok": True, "value": "star_expr"}),
    
    ("parse_kwargs_in_call", """
import parso
code = 'func(**kwargs)'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    ("parse_args_in_call", """
import parso
code = 'func(*args)'
module = parso.parse(code)
atom_expr = module.children[0]
result = atom_expr.type
""", {"ok": True, "value": "atom_expr"}),
    
    # Test 71-75: F-strings and error handling
    ("parse_fstring_type", """
import parso
code = 'f"hello {name}"'
module = parso.parse(code)
fstring = module.children[0]
result = fstring.type
""", {"ok": True, "value": "fstring"}),
    
    ("parse_fstring_get_code", """
import parso
code = 'f"hello {name}"'
module = parso.parse(code)
fstring = module.children[0]
result = fstring.get_code()
""", {"ok": True, "value": 'f"hello {name}"'}),
    
    ("parse_error_node_type", """
import parso
code = 'foo +'
module = parso.parse(code)
error_node = module.children[0]
result = error_node.type
""", {"ok": True, "value": "error_node"}),
    
    ("parse_multiline_string", """
import parso
code = '\"\"\"multi\\nline\\nstring\"\"\"'
module = parso.parse(code)
string = module.children[0]
result = string.type
""", {"ok": True, "value": "string"}),
    
    ("parse_complex_expression", """
import parso
code = '(x + y) * (a - b) / c'
module = parso.parse(code)
expr = module.children[0]
result = expr.get_code()
""", {"ok": True, "value": "(x + y) * (a - b) / c"}),
]

def main():
    """Run all test cases and output JSON result."""
    leaves = []
    
    for case_id, script, expected in CASES:
        try:
            actual = execute_script(script)
            if actual == expected:
                status = "passed"
            else:
                status = "failed"
        except Exception as e:
            status = "failed"
        
        leaves.append({
            "id": case_id,
            "status": status
        })
    
    result = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    
    print(json.dumps(result))
    return 0

if __name__ == "__main__":
    sys.exit(main())
