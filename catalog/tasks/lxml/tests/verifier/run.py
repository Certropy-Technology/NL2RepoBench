"""Private deterministic lxml contract verifier."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path


SCENARIOS = {
    "parse-and-serialize": """
from lxml import etree
root = etree.fromstring(b'<root><child id="a">text</child></root>')
assert root.tag == 'root'
assert root[0].get('id') == 'a'
assert etree.tostring(root) == b'<root><child id="a">text</child></root>'
""",
    "xpath-text-and-attributes": """
from lxml import etree
root = etree.fromstring(b'<root><item rank="2">b</item><item rank="1">a</item></root>')
assert root.xpath('//item/@rank') == ['2', '1']
assert root.xpath('string(//item[@rank="1"])') == 'a'
assert root.xpath('count(//item)') == 2.0
""",
    "element-construction": """
from lxml import etree
root = etree.Element('root', version='1')
child = etree.SubElement(root, 'child')
child.text = 'hello'
assert etree.tostring(root, encoding='unicode') == '<root version="1"><child>hello</child></root>'
""",
    "namespaces": """
from lxml import etree
xml = b'<x:root xmlns:x="urn:demo"><x:child>ok</x:child></x:root>'
root = etree.fromstring(xml)
assert root.xpath('string(/x:root/x:child)', namespaces={'x': 'urn:demo'}) == 'ok'
assert root.nsmap['x'] == 'urn:demo'
""",
    "tree-mutation": """
from lxml import etree
root = etree.XML('<root><a/><c/></root>')
b = etree.Element('b')
root.insert(1, b)
assert [node.tag for node in root] == ['a', 'b', 'c']
assert b.getparent() is root
root.remove(b)
assert [node.tag for node in root] == ['a', 'c']
""",
    "parse-errors": """
from lxml import etree
try:
    etree.fromstring(b'<root>')
except etree.XMLSyntaxError:
    pass
else:
    raise AssertionError('malformed XML must fail')
""",
    "pretty-print": r"""
from lxml import etree
root = etree.XML('<root><child><leaf/></child></root>')
value = etree.tostring(root, pretty_print=True, encoding='unicode')
assert '<child>\n' in value
assert value.endswith('</root>\n')
""",
    "html-fragments": """
from lxml import html
document = html.fromstring('<div><p class="note">hello</p></div>')
assert document.xpath('string(.//p)') == 'hello'
assert document.xpath('.//p[@class="note"]')[0].tag == 'p'
""",
}


def _run_scenario(name: str, code: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix='lxml-scenario-') as temporary:
        temporary_path = Path(temporary)
        script = temporary_path / 'scenario.py'
        output = temporary_path / 'output.txt'
        script.write_text(code, encoding='utf-8')
        script.chmod(0o444)
        temporary_path.chmod(0o755)
        with output.open('w+b') as output_stream:
            process = subprocess.Popen(
                [
                    'runuser', '-u', 'candidate', '--', 'env',
                    'PYTHONDONTWRITEBYTECODE=1',
                    'prlimit', '--as=1073741824', '--cpu=10',
                    '--fsize=1048576', '--nofile=64', '--',
                    sys.executable, '-I', '-c',
                    (
                        'import runpy, sys; '
                        'sys.path[:0] = ["/tmp/candidate-site", '
                        f'{os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"]!r}]; '
                        f'runpy.run_path({str(script)!r}, run_name="__main__")'
                    ),
                ],
                stdout=output_stream,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            timed_out = False
            try:
                return_code = process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                timed_out = True
                return_code = 124
            finally:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()

            output_stream.flush()
            output_stream.seek(max(0, output_stream.tell() - 1000))
            message = output_stream.read(1000).decode('utf-8', errors='replace')

    if return_code == 0 and not timed_out:
        return {'id': name, 'status': 'passed'}
    if timed_out:
        message = 'scenario exceeded the 20 second behavior timeout'
    return {'id': name, 'status': 'failed', 'message': message or 'scenario failed'}


def main() -> None:
    leaves = [_run_scenario(name, code) for name, code in SCENARIOS.items()]
    print(json.dumps({'schema_version': '1.0', 'leaves': leaves}, sort_keys=True))


if __name__ == '__main__':
    main()
