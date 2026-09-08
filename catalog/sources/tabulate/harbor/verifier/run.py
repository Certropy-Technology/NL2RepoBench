#!/usr/bin/env python3
"""
Tabulate verifier - custom-json-v1 protocol
Tests the tabulate library implementation with deterministic scenarios.
"""

import json
import sys
from nl2repobench.verification.candidate_client import execute_script

# Test scenarios: (id, script, expected)
CASES = [
    ('plain_basic', "\nfrom tabulate import tabulate\ndata = [['spam', 41.9999], ['eggs', 451.0]]\nresult = tabulate(data, tablefmt='plain')\n", {'ok': True, 'value': 'spam   41.9999\neggs  451'}),
    ('simple_with_headers', "\nfrom tabulate import tabulate\ndata = [['Alice', 24], ['Bob', 19]]\nresult = tabulate(data, headers=['Name', 'Age'], tablefmt='simple')\n", {'ok': True, 'value': 'Name      Age\n------  -----\nAlice      24\nBob        19'}),
    ('grid_basic', "\nfrom tabulate import tabulate\ndata = [[1, 2], [3, 4]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='grid')\n", {'ok': True, 'value': '+-----+-----+\n|   A |   B |\n+=====+=====+\n|   1 |   2 |\n+-----+-----+\n|   3 |   4 |\n+-----+-----+'}),
    ('github_format', "\nfrom tabulate import tabulate\ndata = [['foo', 1], ['bar', 2]]\nresult = tabulate(data, headers=['Item', 'Count'], tablefmt='github')\n", {'ok': True, 'value': '| Item   |   Count |\n|--------|---------|\n| foo    |       1 |\n| bar    |       2 |'}),
    ('fancy_grid_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='fancy_grid')\n", {'ok': True, 'value': '╒═════╤═════╕\n│   A │   B │\n╞═════╪═════╡\n│   1 │   2 │\n╘═════╧═════╛'}),
    ('psql_format', "\nfrom tabulate import tabulate\ndata = [[1, 'a'], [2, 'b']]\nresult = tabulate(data, headers=['Num', 'Char'], tablefmt='psql')\n", {'ok': True, 'value': '+-------+--------+\n|   Num | Char   |\n|-------+--------|\n|     1 | a      |\n|     2 | b      |\n+-------+--------+'}),
    ('rounded_grid_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['X', 'Y'], tablefmt='rounded_grid')\n", {'ok': True, 'value': '╭─────┬─────╮\n│   X │   Y │\n├─────┼─────┤\n│   1 │   2 │\n╰─────┴─────╯'}),
    ('pipe_format', "\nfrom tabulate import tabulate\ndata = [['left', 'right']]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='pipe')\n", {'ok': True, 'value': '| A    | B     |\n|:-----|:------|\n| left | right |'}),
    ('orgtbl_format', "\nfrom tabulate import tabulate\ndata = [[1, 2], [3, 4]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='orgtbl')\n", {'ok': True, 'value': '|   A |   B |\n|-----+-----|\n|   1 |   2 |\n|   3 |   4 |'}),
    ('rst_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['Col1', 'Col2'], tablefmt='rst')\n", {'ok': True, 'value': '======  ======\n  Col1    Col2\n======  ======\n     1       2\n======  ======'}),
    ('mediawiki_format', "\nfrom tabulate import tabulate\ndata = [['data1', 'data2']]\nresult = tabulate(data, headers=['H1', 'H2'], tablefmt='mediawiki')\n", {'ok': True, 'value': '{| class="wikitable" style="text-align: left;"\n|+ <!-- caption -->\n|-\n! H1    !! H2\n|-\n| data1 || data2\n|}'}),
    ('html_basic', "\nfrom tabulate import tabulate\ndata = [['<b>test</b>', 'normal']]\nresult = tabulate(data, tablefmt='html')\n", {'ok': True, 'value': '<table>\n<tbody>\n<tr><td>&lt;b&gt;test&lt;/b&gt;</td><td>normal</td></tr>\n</tbody>\n</table>'}),
    ('html_with_headers', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='html')\n", {'ok': True, 'value': '<table>\n<thead>\n<tr><th style="text-align: right;">  A</th><th style="text-align: right;">  B</th></tr>\n</thead>\n<tbody>\n<tr><td style="text-align: right;">  1</td><td style="text-align: right;">  2</td></tr>\n</tbody>\n</table>'}),
    ('latex_basic', "\nfrom tabulate import tabulate\ndata = [[1, 2], [3, 4]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='latex')\n", {'ok': True, 'value': '\\begin{tabular}{rr}\n\\hline\n   A &   B \\\\\n\\hline\n   1 &   2 \\\\\n   3 &   4 \\\\\n\\hline\n\\end{tabular}'}),
    ('float_format_2f', "\nfrom tabulate import tabulate\ndata = [[1.23456, 2.34567]]\nresult = tabulate(data, floatfmt='.2f')\n", {'ok': True, 'value': '----  ----\n1.23  2.35\n----  ----'}),
    ('float_format_g', "\nfrom tabulate import tabulate\ndata = [[0.000001, 1000000]]\nresult = tabulate(data, floatfmt='g')\n", {'ok': True, 'value': '-----  -------\n1e-06  1000000\n-----  -------'}),
    ('int_format', "\nfrom tabulate import tabulate\ndata = [[5, 100], [7, 200]]\nresult = tabulate(data, intfmt='05d')\n", {'ok': True, 'value': '-----  -----\n00005  00100\n00007  00200\n-----  -----'}),
    ('missingval_basic', "\nfrom tabulate import tabulate\ndata = [['spam', 1, None], ['eggs', None, 3.14]]\nresult = tabulate(data, missingval='?')\n", {'ok': True, 'value': '----  -  ----\nspam  1  ?\neggs  ?  3.14\n----  -  ----'}),
    ('missingval_list', "\nfrom tabulate import tabulate\ndata = [[None, None], [1, 2]]\nresult = tabulate(data, missingval=['NA', 'NULL'])\n", {'ok': True, 'value': '--  ----\nNA  NULL\n 1     2\n--  ----'}),
    ('decimal_align', "\nfrom tabulate import tabulate\ndata = [[1, 10.5], [100, 2.25], [5, 0.125]]\nresult = tabulate(data, numalign='decimal')\n", {'ok': True, 'value': '---  ------\n  1  10.5\n100   2.25\n  5   0.125\n---  ------'}),
    ('right_align', "\nfrom tabulate import tabulate\ndata = [['short', 'a'], ['verylongtext', 'b']]\nresult = tabulate(data, stralign='right')\n", {'ok': True, 'value': '------------  -\n       short  a\nverylongtext  b\n------------  -'}),
    ('center_align', "\nfrom tabulate import tabulate\ndata = [['a', 'b'], ['center', 'd']]\nresult = tabulate(data, stralign='center')\n", {'ok': True, 'value': '------  -\n  a     b\ncenter  d\n------  -'}),
    ('left_align', "\nfrom tabulate import tabulate\ndata = [['left', 'b'], ['c', 'd']]\nresult = tabulate(data, stralign='left')\n", {'ok': True, 'value': '----  -\nleft  b\nc     d\n----  -'}),
    ('colalign_mixed', "\nfrom tabulate import tabulate\ndata = [[1, 'mid', 3], [100, 'center', 5]]\nresult = tabulate(data, colalign=['left', 'center', 'right'])\n", {'ok': True, 'value': '---  ------  -\n1     mid    3\n100  center  5\n---  ------  -'}),
    ('headers_firstrow', "\nfrom tabulate import tabulate\ndata = [['Name', 'Age'], ['Alice', 24], ['Bob', 19]]\nresult = tabulate(data, headers='firstrow', tablefmt='simple')\n", {'ok': True, 'value': 'Name      Age\n------  -----\nAlice      24\nBob        19'}),
    ('headers_keys_dict', "\nfrom tabulate import tabulate\ndata = [{'name': 'Alice', 'age': 24}, {'name': 'Bob', 'age': 19}]\nresult = tabulate(data, headers='keys', tablefmt='simple')\n", {'ok': True, 'value': 'name      age\n------  -----\nAlice      24\nBob        19'}),
    ('dict_of_iterables', "\nfrom tabulate import tabulate\ndata = {'Name': ['Alice', 'Bob'], 'Age': [24, 19]}\nresult = tabulate(data, headers='keys', tablefmt='simple')\n", {'ok': True, 'value': 'Name      Age\n------  -----\nAlice      24\nBob        19'}),
    ('showindex_always', "\nfrom tabulate import tabulate\ndata = [['A', 1], ['B', 2]]\nresult = tabulate(data, showindex=True, tablefmt='simple')\n", {'ok': True, 'value': '-  -  -\n0  A  1\n1  B  2\n-  -  -'}),
    ('showindex_custom', "\nfrom tabulate import tabulate\ndata = [['Alice', 24], ['Bob', 19]]\nresult = tabulate(data, headers=['Name', 'Age'], showindex=['A', 'B'], tablefmt='simple')\n", {'ok': True, 'value': '    Name      Age\n--  ------  -----\nA   Alice      24\nB   Bob        19'}),
    ('empty_with_headers', "\nfrom tabulate import tabulate\ndata = []\nresult = tabulate(data, headers=['Col1', 'Col2'], tablefmt='simple')\n", {'ok': True, 'value': 'Col1    Col2\n------  ------'}),
    ('empty_no_headers', '\nfrom tabulate import tabulate\ndata = []\nresult = tabulate(data)\n', {'ok': True, 'value': ''}),
    ('single_column', "\nfrom tabulate import tabulate\ndata = [[1], [2], [3]]\nresult = tabulate(data, headers=['Value'], tablefmt='grid')\n", {'ok': True, 'value': '+---------+\n|   Value |\n+=========+\n|       1 |\n+---------+\n|       2 |\n+---------+\n|       3 |\n+---------+'}),
    ('single_row', "\nfrom tabulate import tabulate\ndata = [[1, 2, 3]]\nresult = tabulate(data, headers=['A', 'B', 'C'], tablefmt='simple')\n", {'ok': True, 'value': '  A    B    C\n---  ---  ---\n  1    2    3'}),
    ('boolean_values', "\nfrom tabulate import tabulate\ndata = [[True, False], [False, True]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='simple')\n", {'ok': True, 'value': 'A      B\n-----  -----\nTrue   False\nFalse  True'}),
    ('mixed_numbers', "\nfrom tabulate import tabulate\ndata = [[1, 2.5, 3], [4.0, 5, 6.7]]\nresult = tabulate(data, numalign='decimal')\n", {'ok': True, 'value': '-  ---  ---\n1  2.5  3\n4  5    6.7\n-  ---  ---'}),
    ('unicode_content', "\nfrom tabulate import tabulate\ndata = [['Hello', 'World'], ['你好', '世界']]\nresult = tabulate(data, headers=['English', 'Chinese'], tablefmt='simple')\n", {'ok': True, 'value': 'English    Chinese\n---------  ---------\nHello      World\n你好         世界'}),
    ('long_string', "\nfrom tabulate import tabulate\ndata = [['short', 'x'], ['verylongstringwithnobreaks', 'y']]\nresult = tabulate(data)\n", {'ok': True, 'value': '--------------------------  -\nshort                       x\nverylongstringwithnobreaks  y\n--------------------------  -'}),
    ('negative_numbers', "\nfrom tabulate import tabulate\ndata = [[-10, -5.5], [20, 3.14], [-100, -0.01]]\nresult = tabulate(data, numalign='decimal')\n", {'ok': True, 'value': '----  -----\n -10  -5.5\n  20   3.14\n-100  -0.01\n----  -----'}),
    ('scientific_notation', '\nfrom tabulate import tabulate\ndata = [[1.23e-10, 5.67e20]]\nresult = tabulate(data)\n', {'ok': True, 'value': '--------  --------\n1.23e-10  5.67e+20\n--------  --------'}),
    ('zero_values', '\nfrom tabulate import tabulate\ndata = [[0, 0.0], [0, 0]]\nresult = tabulate(data)\n', {'ok': True, 'value': '-  -\n0  0\n0  0\n-  -'}),
    ('strings_with_spaces', "\nfrom tabulate import tabulate\ndata = [['hello world', 'foo bar'], ['test data', 'baz qux']]\nresult = tabulate(data, headers=['Col A', 'Col B'], tablefmt='simple')\n", {'ok': True, 'value': 'Col A        Col B\n-----------  -------\nhello world  foo bar\ntest data    baz qux'}),
    ('preserve_whitespace_false', "\nfrom tabulate import tabulate\ndata = [['  leading', 'trailing  '], ['text', 'data']]\nresult = tabulate(data, preserve_whitespace=False)\n", {'ok': True, 'value': '-------  --------\nleading  trailing\ntext     data\n-------  --------'}),
    ('preserve_whitespace_true', "\nfrom tabulate import tabulate\ndata = [['  leading', 'trailing  '], ['text', 'data']]\nresult = tabulate(data, preserve_whitespace=True)\n", {'ok': True, 'value': '---------  ----------\n  leading  trailing\ntext       data\n---------  ----------'}),
    ('disable_numparse', "\nfrom tabulate import tabulate\ndata = [['001', '002'], ['100', '200']]\nresult = tabulate(data, disable_numparse=True, tablefmt='simple')\n", {'ok': True, 'value': '---  ---\n001  002\n100  200\n---  ---'}),
    ('floatfmt_per_column', "\nfrom tabulate import tabulate\ndata = [[1.111, 2.222], [3.333, 4.444]]\nresult = tabulate(data, floatfmt=['.1f', '.3f'])\n", {'ok': True, 'value': '---  -----\n1.1  2.222\n3.3  4.444\n---  -----'}),
    ('intfmt_per_column', "\nfrom tabulate import tabulate\ndata = [[1, 10], [2, 20]]\nresult = tabulate(data, intfmt=['02d', '04d'])\n", {'ok': True, 'value': '--  ----\n01  0010\n02  0020\n--  ----'}),
    ('colglobalalign', "\nfrom tabulate import tabulate\ndata = [[1, 'text'], [100, 'data']]\nresult = tabulate(data, colglobalalign='center')\n", {'ok': True, 'value': '---  ----\n 1   text\n100  data\n---  ----'}),
    ('headersglobalalign', "\nfrom tabulate import tabulate\ndata = [[1, 2], [3, 4]]\nresult = tabulate(data, headers=['Long Header A', 'B'], headersglobalalign='right', tablefmt='simple')\n", {'ok': True, 'value': '  Long Header A    B\n---------------  ---\n              1    2\n              3    4'}),
    ('tabulate_formats_exists', "\nfrom tabulate import tabulate_formats\nresult = 'simple' in tabulate_formats and 'grid' in tabulate_formats and 'github' in tabulate_formats\n", {'ok': True, 'value': True}),
    ('tabulate_formats_sorted', '\nfrom tabulate import tabulate_formats\nresult = tabulate_formats == sorted(tabulate_formats)\n', {'ok': True, 'value': True}),
    ('tabulate_formats_type', '\nfrom tabulate import tabulate_formats\nresult = isinstance(tabulate_formats, list)\n', {'ok': True, 'value': True}),
    ('simple_separated_format_exists', '\nfrom tabulate import simple_separated_format\nresult = callable(simple_separated_format)\n', {'ok': True, 'value': True}),
    ('simple_separated_format_usage', "\nfrom tabulate import tabulate, simple_separated_format\ndata = [[1, 2], [3, 4]]\nfmt = simple_separated_format(' | ')\nresult = tabulate(data, tablefmt=fmt)\n", {'ok': True, 'value': '1 | 2\n3 | 4'}),
    ('dataclass_support', "\nfrom dataclasses import dataclass\nfrom tabulate import tabulate\n\n@dataclass\nclass Person:\n    name: str\n    age: int\n\ndata = [Person('Alice', 24), Person('Bob', 19)]\nresult = tabulate(data, headers='keys', tablefmt='simple')\n", {'ok': True, 'value': 'name      age\n------  -----\nAlice      24\nBob        19'}),
    ('list_of_dicts_missing_keys', "\nfrom tabulate import tabulate\ndata = [{'a': 1, 'b': 2}, {'a': 3}, {'b': 4, 'c': 5}]\nresult = tabulate(data, headers='keys', missingval='-')\n", {'ok': True, 'value': '  a    b    c\n---  ---  ---\n  1    2    -\n  3    -    -\n  -    4    5'}),
    ('nested_list', "\nfrom tabulate import tabulate\ndata = [[['nested'], 'normal'], ['item', ['list', 'vals']]]\nresult = str(data[0][0])  # Check conversion happens\nresult = tabulate(data)\n", {'ok': True, 'value': "----------  ----------------\n['nested']  normal\nitem        ['list', 'vals']\n----------  ----------------"}),
    ('wide_numbers', "\nfrom tabulate import tabulate\ndata = [[123456789012345, 9.87654321], [1, 0.1]]\nresult = tabulate(data, numalign='decimal')\n", {'ok': True, 'value': '---------------  -------\n123456789012345  9.87654\n              1  0.1\n---------------  -------'}),
    ('rst_with_headers', "\nfrom tabulate import tabulate\ndata = [['row1col1', 'row1col2'], ['row2col1', 'row2col2']]\nresult = tabulate(data, headers=['Header1', 'Header2'], tablefmt='rst')\n", {'ok': True, 'value': '=========  =========\nHeader1    Header2\n=========  =========\nrow1col1   row1col2\nrow2col1   row2col2\n=========  ========='}),
    ('mediawiki_no_headers', "\nfrom tabulate import tabulate\ndata = [['a', 'b'], ['c', 'd']]\nresult = tabulate(data, tablefmt='mediawiki')\n", {'ok': True, 'value': '{| class="wikitable" style="text-align: left;"\n|+ <!-- caption -->\n|-\n| a || b\n|-\n| c || d\n|}'}),
    ('latex_raw_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, tablefmt='latex_raw')\n", {'ok': True, 'value': '\\begin{tabular}{rr}\n\\hline\n 1 & 2 \\\\\n\\hline\n\\end{tabular}'}),
    ('html_escape_ampersand', "\nfrom tabulate import tabulate\ndata = [['A & B', 'C']]\nresult = tabulate(data, tablefmt='html')\n", {'ok': True, 'value': '<table>\n<tbody>\n<tr><td>A &amp; B</td><td>C</td></tr>\n</tbody>\n</table>'}),
    ('html_escape_quotes', "\nfrom tabulate import tabulate\ndata = [[1]]\nresult = tabulate(data, headers=['Col'], tablefmt='html')\nresult = 'style=' in result  # Check that style attribute exists\n", {'ok': True, 'value': True}),
    ('tsv_format', "\nfrom tabulate import tabulate\ndata = [['a', 'b'], ['c', 'd']]\nresult = tabulate(data, headers=['H1', 'H2'], tablefmt='tsv')\n", {'ok': True, 'value': 'H1  \tH2\na   \tb\nc   \td'}),
    ('jira_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='jira')\n", {'ok': True, 'value': '||   A ||   B ||\n|   1 |   2 |'}),
    ('pretty_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='pretty')\n", {'ok': True, 'value': '+---+---+\n| A | B |\n+---+---+\n| 1 | 2 |\n+---+---+'}),
    ('outline_format', "\nfrom tabulate import tabulate\ndata = [[1, 2], [3, 4]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='outline')\n", {'ok': True, 'value': '+-----+-----+\n|   A |   B |\n+=====+=====+\n|   1 |   2 |\n|   3 |   4 |\n+-----+-----+'}),
    ('simple_outline_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='simple_outline')\n", {'ok': True, 'value': '┌─────┬─────┐\n│   A │   B │\n├─────┼─────┤\n│   1 │   2 │\n└─────┴─────┘'}),
    ('github_multiple_rows', "\nfrom tabulate import tabulate\ndata = [[1, 'a'], [2, 'b'], [3, 'c']]\nresult = tabulate(data, headers=['Num', 'Char'], tablefmt='github')\n", {'ok': True, 'value': '|   Num | Char   |\n|-------|--------|\n|     1 | a      |\n|     2 | b      |\n|     3 | c      |'}),
    ('colon_grid_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='colon_grid')\n", {'ok': True, 'value': '+-----+-----+\n| A   | B   |\n+:====+:====+\n| 1   | 2   |\n+-----+-----+'}),
    ('asciidoc_format', "\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='asciidoc')\n", {'ok': True, 'value': '[cols=">5,>5",options="header"]\n|====\n|   A |   B \n|   1 |   2 \n|===='}),
    ('numbers_as_strings_disabled', "\nfrom tabulate import tabulate\ndata = [['1', '2'], ['3', '4']]\nresult = tabulate(data, disable_numparse=True, stralign='right')\n", {'ok': True, 'value': '-  -\n1  2\n3  4\n-  -'}),
    ('return_type_string', '\nfrom tabulate import tabulate\ndata = [[1, 2]]\nresult = isinstance(tabulate(data), str)\n', {'ok': True, 'value': True}),
    ('empty_string_cells', "\nfrom tabulate import tabulate\ndata = [['', 'b'], ['c', '']]\nresult = tabulate(data, headers=['A', 'B'], tablefmt='simple')\n", {'ok': True, 'value': 'A    B\n---  ---\n     b\nc'}),
    ('whitespace_cells', "\nfrom tabulate import tabulate\ndata = [['   ', 'b'], ['c', '  ']]\nresult = tabulate(data, preserve_whitespace=False)\n", {'ok': True, 'value': '-  -\n   b\nc\n-  -'}),
]

assert len(CASES) == 74, f"Expected 74 test cases, got {len(CASES)}"

def main():
    leaves = []
    
    for case_id, script, expected in CASES:
        actual = execute_script(script)
        
        # Compare actual vs expected
        if actual == expected:
            status = "passed"
        else:
            status = "failed"
        
        leaves.append({
            "id": case_id,
            "status": status
        })
    
    # Output custom-json-v1 format
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    
    print(json.dumps(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())
