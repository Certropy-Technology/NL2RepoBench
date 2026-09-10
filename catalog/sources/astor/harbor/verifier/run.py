#!/usr/bin/env python3
"""
NL2RepoBench verifier for astor package.
Schema: custom-json-v1
Protocol: Each test case executes a script via candidate_client, expects {"ok":bool,"value":...}
"""

import json
import sys
from nl2repobench.verification.candidate_client import execute_script

# Test cases: (id, script, expected_result)
CASES = [
    ('test_001_assignment', "import ast\nimport astor\n\ncode = 'x = 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x = 1\n'}),
    ('test_002_assignment', "import ast\nimport astor\n\ncode = 'x = y = z = 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x = y = z = 1\n'}),
    ('test_003_assignment', "import ast\nimport astor\n\ncode = 'x, y = 1, 2'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x, y = 1, 2\n'}),
    ('test_004_assignment', "import ast\nimport astor\n\ncode = 'x, y, z = 1, 2, 3'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x, y, z = 1, 2, 3\n'}),
    ('test_005_assignment', 'import ast\nimport astor\n\ncode = \'x = "hello"\'\ntree = ast.parse(code)\nresult = astor.to_source(tree)', {'ok': True, 'value': "x = 'hello'\n"}),
    ('test_006_assignment', "import ast\nimport astor\n\ncode = 'x = [1, 2, 3]'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x = [1, 2, 3]\n'}),
    ('test_007_assignment', 'import ast\nimport astor\n\ncode = \'x = {"a": 1}\'\ntree = ast.parse(code)\nresult = astor.to_source(tree)', {'ok': True, 'value': "x = {'a': 1}\n"}),
    ('test_008_assignment', "import ast\nimport astor\n\ncode = 'x += 5'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x += 5\n'}),
    ('test_009_assignment', "import ast\nimport astor\n\ncode = 'x -= 3'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x -= 3\n'}),
    ('test_010_assignment', "import ast\nimport astor\n\ncode = 'x *= 2'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x *= 2\n'}),
    ('test_011_function', "import ast\nimport astor\n\ncode = 'def f(): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f():\n    pass\n'}),
    ('test_012_function', "import ast\nimport astor\n\ncode = 'def f():\\n    return 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f():\n    return 1\n'}),
    ('test_013_function', "import ast\nimport astor\n\ncode = 'def f(x): return x + 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(x):\n    return x + 1\n'}),
    ('test_014_function', "import ast\nimport astor\n\ncode = 'def f(x, y): return x + y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(x, y):\n    return x + y\n'}),
    ('test_015_function', "import ast\nimport astor\n\ncode = 'def f(x, y=1): return x + y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(x, y=1):\n    return x + y\n'}),
    ('test_016_function', "import ast\nimport astor\n\ncode = 'def f(x, y=1, z=2): return x + y + z'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(x, y=1, z=2):\n    return x + y + z\n'}),
    ('test_017_function', "import ast\nimport astor\n\ncode = 'def f(*args): return args'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(*args):\n    return args\n'}),
    ('test_018_function', "import ast\nimport astor\n\ncode = 'def f(**kwargs): return kwargs'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(**kwargs):\n    return kwargs\n'}),
    ('test_019_function', "import ast\nimport astor\n\ncode = 'def f(*args, **kwargs): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(*args, **kwargs):\n    pass\n'}),
    ('test_020_function', "import ast\nimport astor\n\ncode = 'def f(a, b, *args, **kwargs): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(a, b, *args, **kwargs):\n    pass\n'}),
    ('test_021_function', "import ast\nimport astor\n\ncode = 'def f():\\n    x = 1\\n    return x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f():\n    x = 1\n    return x\n'}),
    ('test_022_function', "import ast\nimport astor\n\ncode = 'def f():\\n    x = 1\\n    y = 2\\n    return x + y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f():\n    x = 1\n    y = 2\n    return x + y\n'}),
    ('test_023_function', "import ast\nimport astor\n\ncode = '@decorator\\ndef f(): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '@decorator\ndef f():\n    pass\n'}),
    ('test_024_function', "import ast\nimport astor\n\ncode = 'def f() -> int: return 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f() ->int:\n    return 1\n'}),
    ('test_025_function', "import ast\nimport astor\n\ncode = 'def f(x: int) -> int: return x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'def f(x: int) ->int:\n    return x\n'}),
    ('test_026_class', "import ast\nimport astor\n\ncode = 'class C: pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C:\n    pass\n'}),
    ('test_027_class', "import ast\nimport astor\n\ncode = 'class C(object): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C(object):\n    pass\n'}),
    ('test_028_class', "import ast\nimport astor\n\ncode = 'class C:\\n    x = 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C:\n    x = 1\n'}),
    ('test_029_class', "import ast\nimport astor\n\ncode = 'class C:\\n    def m(self): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C:\n\n    def m(self):\n        pass\n'}),
    ('test_030_class', "import ast\nimport astor\n\ncode = 'class C:\\n    def __init__(self): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C:\n\n    def __init__(self):\n        pass\n'}),
    ('test_031_class', "import ast\nimport astor\n\ncode = 'class C:\\n    def __init__(self, x):\\n        self.x = x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C:\n\n    def __init__(self, x):\n        self.x = x\n'}),
    ('test_032_class', "import ast\nimport astor\n\ncode = 'class C(A, B): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C(A, B):\n    pass\n'}),
    ('test_033_class', "import ast\nimport astor\n\ncode = '@decorator\\nclass C: pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '@decorator\nclass C:\n    pass\n'}),
    ('test_034_class', "import ast\nimport astor\n\ncode = 'class C:\\n    pass\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'class C:\n    pass\n    pass\n'}),
    ('test_035_class', 'import ast\nimport astor\n\ncode = \'class C:\\n    """docstring"""\\n    pass\'\ntree = ast.parse(code)\nresult = astor.to_source(tree)', {'ok': True, 'value': 'class C:\n    """docstring"""\n    pass\n'}),
    ('test_036_control', "import ast\nimport astor\n\ncode = 'if x: pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'if x:\n    pass\n'}),
    ('test_037_control', "import ast\nimport astor\n\ncode = 'if x:\\n    pass\\nelse:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'if x:\n    pass\nelse:\n    pass\n'}),
    ('test_038_control', "import ast\nimport astor\n\ncode = 'if x:\\n    pass\\nelif y:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'if x:\n    pass\nelif y:\n    pass\n'}),
    ('test_039_control', "import ast\nimport astor\n\ncode = 'if x:\\n    pass\\nelif y:\\n    pass\\nelse:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'if x:\n    pass\nelif y:\n    pass\nelse:\n    pass\n'}),
    ('test_040_control', "import ast\nimport astor\n\ncode = 'for i in range(5): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'for i in range(5):\n    pass\n'}),
    ('test_041_control', "import ast\nimport astor\n\ncode = 'for i in x:\\n    print(i)'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'for i in x:\n    print(i)\n'}),
    ('test_042_control', "import ast\nimport astor\n\ncode = 'for i, j in enumerate(x): pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'for i, j in enumerate(x):\n    pass\n'}),
    ('test_043_control', "import ast\nimport astor\n\ncode = 'while x: pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'while x:\n    pass\n'}),
    ('test_044_control', "import ast\nimport astor\n\ncode = 'while x:\\n    break'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'while x:\n    break\n'}),
    ('test_045_control', "import ast\nimport astor\n\ncode = 'while x:\\n    continue'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'while x:\n    continue\n'}),
    ('test_046_control', "import ast\nimport astor\n\ncode = 'for i in range(5):\\n    if i == 2:\\n        break'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'for i in range(5):\n    if i == 2:\n        break\n'}),
    ('test_047_control', "import ast\nimport astor\n\ncode = 'for i in range(5):\\n    pass\\nelse:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'for i in range(5):\n    pass\nelse:\n    pass\n'}),
    ('test_048_control', "import ast\nimport astor\n\ncode = 'while x:\\n    pass\\nelse:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'while x:\n    pass\nelse:\n    pass\n'}),
    ('test_049_control', 'import ast\nimport astor\n\ncode = \'with open("file") as f: pass\'\ntree = ast.parse(code)\nresult = astor.to_source(tree)', {'ok': True, 'value': "with open('file') as f:\n    pass\n"}),
    ('test_050_control', "import ast\nimport astor\n\ncode = 'with a as x, b as y: pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'with a as x, b as y:\n    pass\n'}),
    ('test_051_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept:\n    pass\n'}),
    ('test_052_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept Exception:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept Exception:\n    pass\n'}),
    ('test_053_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept Exception as e:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept Exception as e:\n    pass\n'}),
    ('test_054_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept (A, B):\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept (A, B):\n    pass\n'}),
    ('test_055_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept A:\\n    pass\\nexcept B:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept A:\n    pass\nexcept B:\n    pass\n'}),
    ('test_056_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept:\\n    pass\\nelse:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept:\n    pass\nelse:\n    pass\n'}),
    ('test_057_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nexcept:\\n    pass\\nfinally:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nexcept:\n    pass\nfinally:\n    pass\n'}),
    ('test_058_exception', "import ast\nimport astor\n\ncode = 'try:\\n    pass\\nfinally:\\n    pass'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'try:\n    pass\nfinally:\n    pass\n'}),
    ('test_059_exception', "import ast\nimport astor\n\ncode = 'raise Exception'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'raise Exception\n'}),
    ('test_060_exception', 'import ast\nimport astor\n\ncode = \'raise Exception("msg")\'\ntree = ast.parse(code)\nresult = astor.to_source(tree)', {'ok': True, 'value': "raise Exception('msg')\n"}),
    ('test_061_comprehension', "import ast\nimport astor\n\ncode = '[x for x in range(5)]'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '[x for x in range(5)]\n'}),
    ('test_062_comprehension', "import ast\nimport astor\n\ncode = '[x * 2 for x in range(5)]'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '[(x * 2) for x in range(5)]\n'}),
    ('test_063_comprehension', "import ast\nimport astor\n\ncode = '[x for x in range(10) if x % 2 == 0]'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '[x for x in range(10) if x % 2 == 0]\n'}),
    ('test_064_comprehension', "import ast\nimport astor\n\ncode = '[x + y for x in range(3) for y in range(3)]'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '[(x + y) for x in range(3) for y in range(3)]\n'}),
    ('test_065_comprehension', "import ast\nimport astor\n\ncode = '{x for x in range(5)}'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '{x for x in range(5)}\n'}),
    ('test_066_comprehension', "import ast\nimport astor\n\ncode = '{x: x * 2 for x in range(5)}'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '{x: (x * 2) for x in range(5)}\n'}),
    ('test_067_comprehension', "import ast\nimport astor\n\ncode = '(x for x in range(5))'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '(x for x in range(5))\n'}),
    ('test_068_comprehension', "import ast\nimport astor\n\ncode = '[(x, y) for x in range(3) for y in range(3)]'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': '[(x, y) for x in range(3) for y in range(3)]\n'}),
    ('test_069_lambda', "import ast\nimport astor\n\ncode = 'lambda: 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'lambda : 1\n'}),
    ('test_070_lambda', "import ast\nimport astor\n\ncode = 'lambda x: x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'lambda x: x\n'}),
    ('test_071_lambda', "import ast\nimport astor\n\ncode = 'lambda x: x + 1'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'lambda x: x + 1\n'}),
    ('test_072_lambda', "import ast\nimport astor\n\ncode = 'lambda x, y: x + y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'lambda x, y: x + y\n'}),
    ('test_073_lambda', "import ast\nimport astor\n\ncode = 'lambda x, y=1: x + y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'lambda x, y=1: x + y\n'}),
    ('test_074_expression', "import ast\nimport astor\n\ncode = 'x + y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x + y\n'}),
    ('test_075_expression', "import ast\nimport astor\n\ncode = 'x - y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x - y\n'}),
    ('test_076_expression', "import ast\nimport astor\n\ncode = 'x * y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x * y\n'}),
    ('test_077_expression', "import ast\nimport astor\n\ncode = 'x / y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x / y\n'}),
    ('test_078_expression', "import ast\nimport astor\n\ncode = 'x // y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x // y\n'}),
    ('test_079_expression', "import ast\nimport astor\n\ncode = 'x % y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x % y\n'}),
    ('test_080_expression', "import ast\nimport astor\n\ncode = 'x ** y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x ** y\n'}),
    ('test_081_expression', "import ast\nimport astor\n\ncode = 'x and y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x and y\n'}),
    ('test_082_expression', "import ast\nimport astor\n\ncode = 'x or y'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'x or y\n'}),
    ('test_083_expression', "import ast\nimport astor\n\ncode = 'not x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'not x\n'}),
    ('test_084_import', "import ast\nimport astor\n\ncode = 'import os'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'import os\n'}),
    ('test_085_import', "import ast\nimport astor\n\ncode = 'import os, sys'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'import os, sys\n'}),
    ('test_086_import', "import ast\nimport astor\n\ncode = 'from os import path'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'from os import path\n'}),
    ('test_087_import', "import ast\nimport astor\n\ncode = 'from os import path, sys'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'from os import path, sys\n'}),
    ('test_088_import', "import ast\nimport astor\n\ncode = 'import os as operating_system'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'import os as operating_system\n'}),
    ('test_089_statement', "import ast\nimport astor\n\ncode = 'del x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'del x\n'}),
    ('test_090_statement', "import ast\nimport astor\n\ncode = 'return x'\ntree = ast.parse(code)\nresult = astor.to_source(tree)", {'ok': True, 'value': 'return x\n'}),
]

def main():
    """Run all test cases and output custom-json-v1 results."""
    leaves = []
    
    for test_id, script, expected in CASES:
        try:
            actual = execute_script(script)
            
            # Check if actual matches expected
            if actual == expected:
                status = "passed"
            else:
                status = "failed"
                
        except Exception as e:
            status = "failed"
        
        leaves.append({
            "id": test_id,
            "status": status
        })
    
    # Output custom-json-v1 schema
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    
    # Validate collection count
    assert len(CASES) == 90, f"Expected 90 test cases, got {len(CASES)}"
    
    print(json.dumps(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())