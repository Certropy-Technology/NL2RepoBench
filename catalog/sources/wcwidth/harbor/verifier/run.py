#!/usr/bin/env python3
"""
NL2RepoBench verifier for wcwidth task.
Standard custom-json-v1 leaves schema.
"""
import sys
import json
from nl2repobench.verification.candidate_client import execute_script

# Test cases: (id, script, expected)
CASES = [
    ("ascii_001", "import wcwidth\nresult = wcwidth.wcwidth(\"a\")", {'ok': True, 'value': 1}),
    ("ascii_002", "import wcwidth\nresult = wcwidth.wcwidth(\"Z\")", {'ok': True, 'value': 1}),
    ("ascii_003", "import wcwidth\nresult = wcwidth.wcwidth(\"5\")", {'ok': True, 'value': 1}),
    ("ascii_004", "import wcwidth\nresult = wcwidth.wcwidth(\" \")", {'ok': True, 'value': 1}),
    ("ascii_005", "import wcwidth\nresult = wcwidth.wcwidth(\"!\")", {'ok': True, 'value': 1}),
    ("ascii_006", "import wcwidth\nresult = wcwidth.wcwidth(\"@\")", {'ok': True, 'value': 1}),
    ("ascii_007", "import wcwidth\nresult = wcwidth.wcwidth(\"#\")", {'ok': True, 'value': 1}),
    ("ascii_008", "import wcwidth\nresult = wcwidth.wcwidth(\"$\")", {'ok': True, 'value': 1}),
    ("ascii_009", "import wcwidth\nresult = wcwidth.wcwidth(\"%\")", {'ok': True, 'value': 1}),
    ("ascii_010", "import wcwidth\nresult = wcwidth.wcwidth(\"&\")", {'ok': True, 'value': 1}),
    ("control_001", "import wcwidth\nresult = wcwidth.wcwidth(\"\\x00\")", {'ok': True, 'value': 0}),
    ("control_002", "import wcwidth\nresult = wcwidth.wcwidth(\"\\t\")", {'ok': True, 'value': -1}),
    ("control_003", "import wcwidth\nresult = wcwidth.wcwidth(\"\\n\")", {'ok': True, 'value': -1}),
    ("control_004", "import wcwidth\nresult = wcwidth.wcwidth(\"\\x7f\")", {'ok': True, 'value': -1}),
    ("control_005", "import wcwidth\nresult = wcwidth.wcwidth(\"\\x80\")", {'ok': True, 'value': -1}),
    ("control_006", "import wcwidth\nresult = wcwidth.wcwidth(\"\\x08\")", {'ok': True, 'value': -1}),
    ("control_007", "import wcwidth\nresult = wcwidth.wcwidth(\"\\x0c\")", {'ok': True, 'value': -1}),
    ("control_008", "import wcwidth\nresult = wcwidth.wcwidth(\"\\r\")", {'ok': True, 'value': -1}),
    ("control_009", "import wcwidth\nresult = wcwidth.wcwidth(\"\\x1b\")", {'ok': True, 'value': -1}),
    ("combining_001", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u0301\")", {'ok': True, 'value': 0}),
    ("combining_002", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u0300\")", {'ok': True, 'value': 0}),
    ("combining_003", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u0303\")", {'ok': True, 'value': 0}),
    ("combining_004", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u0308\")", {'ok': True, 'value': 0}),
    ("combining_005", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u200d\")", {'ok': True, 'value': 0}),
    ("combining_006", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u200c\")", {'ok': True, 'value': 0}),
    ("combining_007", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u030a\")", {'ok': True, 'value': 0}),
    ("combining_008", "import wcwidth\nresult = wcwidth.wcwidth(\"\\u0304\")", {'ok': True, 'value': 0}),
    ("wide_001", "import wcwidth\nresult = wcwidth.wcwidth(\"中\")", {'ok': True, 'value': 2}),
    ("wide_002", "import wcwidth\nresult = wcwidth.wcwidth(\"あ\")", {'ok': True, 'value': 2}),
    ("wide_003", "import wcwidth\nresult = wcwidth.wcwidth(\"한\")", {'ok': True, 'value': 2}),
    ("wide_004", "import wcwidth\nresult = wcwidth.wcwidth(\"０\")", {'ok': True, 'value': 2}),
    ("wide_005", "import wcwidth\nresult = wcwidth.wcwidth(\"Ａ\")", {'ok': True, 'value': 2}),
    ("wide_006", "import wcwidth\nresult = wcwidth.wcwidth(\"カ\")", {'ok': True, 'value': 2}),
    ("wide_007", "import wcwidth\nresult = wcwidth.wcwidth(\"文\")", {'ok': True, 'value': 2}),
    ("wide_008", "import wcwidth\nresult = wcwidth.wcwidth(\"本\")", {'ok': True, 'value': 2}),
    ("wide_009", "import wcwidth\nresult = wcwidth.wcwidth(\"字\")", {'ok': True, 'value': 2}),
    ("wide_010", "import wcwidth\nresult = wcwidth.wcwidth(\"语\")", {'ok': True, 'value': 2}),
    ("emoji_001", "import wcwidth\nresult = wcwidth.wcwidth(\"❤\")", {'ok': True, 'value': 1}),
    ("emoji_002", "import wcwidth\nresult = wcwidth.wcwidth(\"😀\")", {'ok': True, 'value': 2}),
    ("emoji_003", "import wcwidth\nresult = wcwidth.wcwidth(\"👍\")", {'ok': True, 'value': 2}),
    ("emoji_004", "import wcwidth\nresult = wcwidth.wcwidth(\"🔥\")", {'ok': True, 'value': 2}),
    ("emoji_005", "import wcwidth\nresult = wcwidth.wcwidth(\"⭐\")", {'ok': True, 'value': 2}),
    ("wcswidth_001", "import wcwidth\nresult = wcwidth.wcswidth(\"\")", {'ok': True, 'value': 0}),
    ("wcswidth_002", "import wcwidth\nresult = wcwidth.wcswidth(\"hello\")", {'ok': True, 'value': 5}),
    ("wcswidth_003", "import wcwidth\nresult = wcwidth.wcswidth(\"hello world\")", {'ok': True, 'value': 11}),
    ("wcswidth_004", "import wcwidth\nresult = wcwidth.wcswidth(\"中文\")", {'ok': True, 'value': 4}),
    ("wcswidth_005", "import wcwidth\nresult = wcwidth.wcswidth(\"hello中文\")", {'ok': True, 'value': 9}),
    ("wcswidth_006", "import wcwidth\nresult = wcwidth.wcswidth(\"hello\\nworld\")", {'ok': True, 'value': -1}),
    ("wcswidth_007", "import wcwidth\nresult = wcwidth.wcswidth(\"こんにちは\")", {'ok': True, 'value': 10}),
    ("wcswidth_008", "import wcwidth\nresult = wcwidth.wcswidth(\"안녕하세요\")", {'ok': True, 'value': 10}),
    ("wcswidth_009", "import wcwidth\nresult = wcwidth.wcswidth(\"0123456789\")", {'ok': True, 'value': 10}),
    ("wcswidth_010", "import wcwidth\nresult = wcwidth.wcswidth(\".,;:!?\")", {'ok': True, 'value': 6}),
    ("wcswidth_011", "import wcwidth\nresult = wcwidth.wcswidth(\"hello, world!\")", {'ok': True, 'value': 13}),
    ("wcswidth_012", "import wcwidth\nresult = wcwidth.wcswidth(\"     \")", {'ok': True, 'value': 5}),
    ("wcswidth_n_001", "import wcwidth\nresult = wcwidth.wcswidth(\"hello\", 3)", {'ok': True, 'value': 3}),
    ("wcswidth_n_002", "import wcwidth\nresult = wcwidth.wcswidth(\"中文\", 1)", {'ok': True, 'value': 2}),
    ("wcswidth_n_003", "import wcwidth\nresult = wcwidth.wcswidth(\"hello world\", 5)", {'ok': True, 'value': 5}),
    ("wcswidth_n_004", "import wcwidth\nresult = wcwidth.wcswidth(\"hello\", 0)", {'ok': True, 'value': 0}),
    ("wcswidth_n_005", "import wcwidth\nresult = wcwidth.wcswidth(\"中文日本\", 2)", {'ok': True, 'value': 4}),
    ("wcswidth_n_006", "import wcwidth\nresult = wcwidth.wcswidth(\"hi\", 10)", {'ok': True, 'value': 2}),
    ("wcswidth_comb_001", "import wcwidth\nresult = wcwidth.wcswidth(\"e\\u0301\")", {'ok': True, 'value': 1}),
    ("wcswidth_comb_002", "import wcwidth\nresult = wcwidth.wcswidth(\"a\\u0303\")", {'ok': True, 'value': 1}),
    ("wcswidth_comb_003", "import wcwidth\nresult = wcwidth.wcswidth(\"café\")", {'ok': True, 'value': 4}),
    ("ambiguous_001", "import wcwidth\nresult = wcwidth.wcwidth(\"α\")", {'ok': True, 'value': 1}),
    ("ambiguous_002", "import wcwidth\nresult = wcwidth.wcwidth(\"α\", ambiguous_width=1)", {'ok': True, 'value': 1}),
    ("ambiguous_003", "import wcwidth\nresult = wcwidth.wcwidth(\"α\", ambiguous_width=2)", {'ok': True, 'value': 2}),
    ("ambiguous_004", "import wcwidth\nresult = wcwidth.wcwidth(\"°\")", {'ok': True, 'value': 1}),
    ("edge_001", "import wcwidth\nresult = wcwidth.wcwidth(\"\")", {'ok': True, 'value': 0}),
    ("edge_002", "import wcwidth\nresult = wcwidth.wcwidth(\"ｱ\")", {'ok': True, 'value': 1}),
    ("fullwidth_001", "import wcwidth\nresult = wcwidth.wcwidth(\"Ｂ\")", {'ok': True, 'value': 2}),
    ("fullwidth_002", "import wcwidth\nresult = wcwidth.wcwidth(\"　\")", {'ok': True, 'value': 2}),
    ("fullwidth_003", "import wcwidth\nresult = wcwidth.wcwidth(\"！\")", {'ok': True, 'value': 2}),
    ("wcswidth_013", "import wcwidth\nresult = wcwidth.wcswidth(\"ＡＢＣ\")", {'ok': True, 'value': 6}),
    ("wcswidth_014", "import wcwidth\nresult = wcwidth.wcswidth(\"aＡb\")", {'ok': True, 'value': 4}),
    ("wcswidth_015", "import wcwidth\nresult = wcwidth.wcswidth(\"これはテストです\")", {'ok': True, 'value': 16}),
    ("box_001", "import wcwidth\nresult = wcwidth.wcwidth(\"─\")", {'ok': True, 'value': 1}),
    ("box_002", "import wcwidth\nresult = wcwidth.wcwidth(\"│\")", {'ok': True, 'value': 1}),
    ("box_003", "import wcwidth\nresult = wcwidth.wcwidth(\"┌\")", {'ok': True, 'value': 1}),
    ("latin_001", "import wcwidth\nresult = wcwidth.wcwidth(\"á\")", {'ok': True, 'value': 1}),
    ("latin_002", "import wcwidth\nresult = wcwidth.wcwidth(\"Å\")", {'ok': True, 'value': 1}),
    ("latin_003", "import wcwidth\nresult = wcwidth.wcwidth(\"ñ\")", {'ok': True, 'value': 1}),
    ("cyrillic_001", "import wcwidth\nresult = wcwidth.wcwidth(\"А\")", {'ok': True, 'value': 1}),
    ("cyrillic_002", "import wcwidth\nresult = wcwidth.wcwidth(\"я\")", {'ok': True, 'value': 1}),
    ("cyrillic_003", "import wcwidth\nresult = wcwidth.wcwidth(\"Ж\")", {'ok': True, 'value': 1}),
    ("wcswidth_016", "import wcwidth\nresult = wcwidth.wcswidth(\"привет\")", {'ok': True, 'value': 6}),
    ("wcswidth_017", "import wcwidth\nresult = wcwidth.wcswidth(\"مرحبا\")", {'ok': True, 'value': 5}),
    ("wcswidth_018", "import wcwidth\nresult = wcwidth.wcswidth(\"שלום\")", {'ok': True, 'value': 4}),
    ("ascii_011", "import wcwidth\nresult = wcwidth.wcwidth(\"~\")", {'ok': True, 'value': 1}),
    ("ascii_012", "import wcwidth\nresult = wcwidth.wcwidth(\"|\")", {'ok': True, 'value': 1}),
    ("ascii_013", "import wcwidth\nresult = wcwidth.wcwidth(\"\\\\\")", {'ok': True, 'value': 1}),
    ("wide_011", "import wcwidth\nresult = wcwidth.wcwidth(\"語\")", {'ok': True, 'value': 2}),
    ("wide_012", "import wcwidth\nresult = wcwidth.wcwidth(\"言\")", {'ok': True, 'value': 2}),
    ("wide_013", "import wcwidth\nresult = wcwidth.wcwidth(\"글\")", {'ok': True, 'value': 2}),
    ("symbol_001", "import wcwidth\nresult = wcwidth.wcwidth(\"•\")", {'ok': True, 'value': 1}),
    ("symbol_002", "import wcwidth\nresult = wcwidth.wcwidth(\"→\")", {'ok': True, 'value': 1}),
    ("symbol_003", "import wcwidth\nresult = wcwidth.wcwidth(\"✓\")", {'ok': True, 'value': 1}),
]

def main():
    """Run all test cases and output custom-json-v1 schema."""
    leaves = []
    
    for test_id, script, expected in CASES:
        result = execute_script(script)
        
        # Check if result matches expected
        if result == expected:
            status = "passed"
        else:
            status = "failed"
        
        leaves.append({
            "id": test_id,
            "status": status
        })
    
    # Output schema
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
