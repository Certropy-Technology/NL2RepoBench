#!/usr/bin/env python3
"""Custom JSON v1 verifier for binaryornot."""
import json
import sys
from nl2repobench.verification.candidate_client import execute_script

CASES: list[tuple[str, str, object]] = [
    # is_binary_string tests - empty
    ("is_binary_string_empty", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'')
""", {"ok": True, "value": False}),
    
    # is_binary_string - ASCII text
    ("is_binary_string_ascii_hello", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Hello, World!')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_ascii_multiline", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Line 1\\nLine 2\\nLine 3\\n')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_ascii_with_tabs", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Col1\\tCol2\\tCol3\\n')
""", {"ok": True, "value": False}),
    
    # is_binary_string - single NUL byte
    ("is_binary_string_single_nul", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x00')
""", {"ok": True, "value": False}),
    
    # is_binary_string - text with embedded NUL
    ("is_binary_string_text_with_nul", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Hello\\x00World')
""", {"ok": True, "value": False}),
    
    # is_binary_string - pure NUL bytes
    ("is_binary_string_pure_nul_short", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x00' * 10)
""", {"ok": True, "value": True}),
    
    ("is_binary_string_pure_nul_long", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x00' * 100)
""", {"ok": True, "value": True}),
    
    # is_binary_string - UTF-8 text
    ("is_binary_string_utf8_chinese", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('你好世界'.encode('utf-8'))
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf8_emoji", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('Hello 👋 World 🌍'.encode('utf-8'))
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf8_mixed", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('English 中文 日本語 한글'.encode('utf-8'))
""", {"ok": True, "value": False}),
    
    # is_binary_string - high bytes (non-UTF-8)
    ("is_binary_string_high_bytes_short", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x80\\x90\\xa0\\xb0')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_high_bytes_pattern", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\xff' * 50)
""", {"ok": True, "value": True}),
    
    # is_binary_string - control characters
    ("is_binary_string_control_chars_mixed", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08')
""", {"ok": True, "value": True}),
    
    ("is_binary_string_control_with_text", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Text\\x01\\x02\\x03More')
""", {"ok": True, "value": False}),
    
    # is_binary_string - binary patterns
    ("is_binary_string_binary_sequence", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x00\\x01\\x02\\x03' * 50)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_alternating_nul", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x00A\\x00B\\x00C' * 20)
""", {"ok": True, "value": False}),
    
    # is_binary_string - UTF-16 like patterns
    ("is_binary_string_utf16_pattern", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('Hello'.encode('utf-16-le'))
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf16be_pattern", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('Hello'.encode('utf-16-be'))
""", {"ok": True, "value": False}),
    
    # is_binary_string - BOM markers
    ("is_binary_string_utf8_bom", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\xef\\xbb\\xbfHello World')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf16le_bom", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\xff\\xfeH\\x00e\\x00l\\x00l\\x00o\\x00')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf16be_bom", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\xfe\\xff\\x00H\\x00e\\x00l\\x00l\\x00o')
""", {"ok": True, "value": False}),
    
    # is_binary_string - various lengths
    ("is_binary_string_very_short", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Hi')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_medium", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'A' * 256)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_long", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Test text ' * 100)
""", {"ok": True, "value": False}),
    
    # is_binary_string - mixed printable and non-printable
    ("is_binary_string_mixed_printable", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Normal text\\nwith newlines\\rand\\ttabs')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_json_like", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'{"key": "value", "number": 123}')
""", {"ok": True, "value": False}),
    
    # is_binary_string - whitespace
    ("is_binary_string_only_spaces", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b' ' * 100)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_only_newlines", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\n' * 50)
""", {"ok": True, "value": False}),
    
    # is_binary - text file tests
    ("is_binary_text_simple", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.txt') as f:
    f.write(b'This is a simple text file.\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_text_multiline", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.txt') as f:
    f.write(b'Line 1\\nLine 2\\nLine 3\\nLine 4\\nLine 5\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_text_utf8", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.txt') as f:
    f.write('你好世界\\nHello World\\n'.encode('utf-8'))
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # is_binary - binary file tests
    ("is_binary_with_nul_bytes", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.bin') as f:
    f.write(b'\\x00' * 100)
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    ("is_binary_binary_sequence", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.bin') as f:
    f.write(b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07' * 20)
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    ("is_binary_control_heavy", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.bin') as f:
    f.write(b'\\x01\\x02\\x03\\x04' * 50)
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    # is_binary - extension checking
    ("is_binary_png_extension", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.png') as f:
    f.write(b'Text content')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    ("is_binary_png_no_check_ext", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.png') as f:
    f.write(b'Text content')
    tmpfile = f.name
try:
    result = is_binary(tmpfile, check_extensions=False)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_py_extension", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.py') as f:
    f.write(b'print("Hello")')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # is_binary - empty file
    ("is_binary_empty_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.txt') as f:
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # is_binary - UTF-16 files
    ("is_binary_utf16le_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.txt') as f:
    f.write('Hello World'.encode('utf-16-le'))
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_utf16be_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.txt') as f:
    f.write('Hello World'.encode('utf-16-be'))
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # has_binary_extension tests
    ("has_binary_extension_png", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('image.png')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_jpg", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('photo.jpg')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_py", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('script.py')
""", {"ok": True, "value": False}),
    
    ("has_binary_extension_txt", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('readme.txt')
""", {"ok": True, "value": False}),
    
    ("has_binary_extension_pdf", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('document.pdf')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_exe", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('program.exe')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_zip", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('archive.zip')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_md", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('README.md')
""", {"ok": True, "value": False}),
    
    ("has_binary_extension_bin", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('data.bin')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_no_ext", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('filename')
""", {"ok": True, "value": False}),
    
    ("has_binary_extension_uppercase", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('IMAGE.PNG')
""", {"ok": True, "value": True}),
    
    # get_starting_chunk tests
    ("get_starting_chunk_default", """
from binaryornot.helpers import get_starting_chunk
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'A' * 1000)
    tmpfile = f.name
try:
    chunk = get_starting_chunk(tmpfile)
    result = len(chunk)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": 512}),
    
    ("get_starting_chunk_short_file", """
from binaryornot.helpers import get_starting_chunk
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'Short content')
    tmpfile = f.name
try:
    chunk = get_starting_chunk(tmpfile)
    result = len(chunk)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": 13}),
    
    ("get_starting_chunk_custom_length", """
from binaryornot.helpers import get_starting_chunk
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'B' * 1000)
    tmpfile = f.name
try:
    chunk = get_starting_chunk(tmpfile, length=100)
    result = len(chunk)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": 100}),
    
    ("get_starting_chunk_content", """
from binaryornot.helpers import get_starting_chunk
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'Hello World')
    tmpfile = f.name
try:
    chunk = get_starting_chunk(tmpfile)
    result = chunk.decode('ascii')
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": "Hello World"}),
    
    # Additional complex scenarios
    ("is_binary_string_mostly_printable", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Normal text ' * 40 + b'\\x01')
""", {"ok": True, "value": True}),
    
    ("is_binary_string_sparse_nuls", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Text' + b'\\x00' + b'More' + b'\\x00' + b'Text')
""", {"ok": True, "value": False}),
    
    ("is_binary_csv_like", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.csv') as f:
    f.write(b'name,age,city\\nAlice,30,NYC\\nBob,25,LA\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_json_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.json') as f:
    f.write(b'{"key": "value", "list": [1, 2, 3]}')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_xml_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.xml') as f:
    f.write(b'<?xml version="1.0"?><root><item>test</item></root>')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # Path variants
    ("is_binary_path_str", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'Text')
    tmpfile = str(f.name)
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_path_object", """
from binaryornot.check import is_binary
from pathlib import Path
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'Text')
    tmpfile = Path(f.name)
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # Edge cases for is_binary_string with longer sequences
    ("is_binary_string_repeating_ascii", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'ABC' * 200)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_low_entropy", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x55' * 200)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_high_entropy_text", """
from binaryornot.helpers import is_binary_string
import string
result = is_binary_string((string.ascii_letters + string.digits + string.punctuation).encode() * 10)
""", {"ok": True, "value": False}),
    
    # More UTF-8 tests
    ("is_binary_string_utf8_arabic", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('مرحبا بالعالم'.encode('utf-8'))
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf8_russian", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('Привет мир'.encode('utf-8'))
""", {"ok": True, "value": False}),
    
    ("is_binary_string_utf8_greek", """
from binaryornot.helpers import is_binary_string
result = is_binary_string('Γεια σου κόσμε'.encode('utf-8'))
""", {"ok": True, "value": False}),
    
    # Binary file patterns
    ("is_binary_alternating_high_low", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(bytes([i % 256 for i in range(512)]))
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    ("is_binary_random_like", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(bytes([(i * 137) % 256 for i in range(512)]))
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    # More comprehensive extension tests
    ("has_binary_extension_gif", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('animation.gif')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_tar", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('archive.tar')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_gz", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('compressed.gz')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_woff", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('font.woff')
""", {"ok": True, "value": True}),
    
    ("has_binary_extension_js", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('script.js')
""", {"ok": True, "value": False}),
    
    ("has_binary_extension_html", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('index.html')
""", {"ok": True, "value": False}),
    
    ("has_binary_extension_css", """
from binaryornot.helpers import has_binary_extension
result = has_binary_extension('style.css')
""", {"ok": True, "value": False}),
    
    # More is_binary_string tests with various patterns
    ("is_binary_string_base64_like", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBiYXNlNjQgbGlrZSBzdHJpbmc=')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_hex_string", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'48656c6c6f20576f726c64')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_mixed_newlines", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'Line1\\r\\nLine2\\rLine3\\nLine4')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_code_snippet", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'def hello():\\n    return "world"')
""", {"ok": True, "value": False}),
    
    ("is_binary_string_sql_like", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'SELECT * FROM users WHERE id = 1;')
""", {"ok": True, "value": False}),
    
    # More file type scenarios
    ("is_binary_markdown_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.md') as f:
    f.write(b'# Header\\n\\nParagraph with **bold** and *italic*.\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_yaml_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.yaml') as f:
    f.write(b'key: value\\nlist:\\n  - item1\\n  - item2\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_ini_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.ini') as f:
    f.write(b'[section]\\nkey=value\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # More binary patterns
    ("is_binary_string_jpeg_header", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF' + b'\\x00' * 100)
""", {"ok": True, "value": True}),
    
    ("is_binary_string_png_header", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x89PNG\\r\\n\\x1a\\n' + b'\\x00' * 100)
""", {"ok": True, "value": True}),
    
    ("is_binary_string_zip_header", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'PK\\x03\\x04' + b'\\x00' * 100)
""", {"ok": True, "value": True}),
    
    ("is_binary_string_pdf_header", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'%PDF-1.4\\n%' + b'\\x80' * 4)
""", {"ok": True, "value": True}),
    
    # Edge cases with mixed content
    ("is_binary_many_nuls_with_text", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'\\x00' * 200 + b'Some text' + b'\\x00' * 200)
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": True}),
    
    ("is_binary_mostly_text_some_binary", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write(b'Text ' * 100 + b'\\x00\\x01\\x02\\x03')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # Test with different encodings via is_binary
    ("is_binary_latin1_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
    f.write('café résumé naïve'.encode('latin-1'))
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # Test string method with various byte patterns
    ("is_binary_string_all_high_bytes", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(bytes(range(128, 256)))
""", {"ok": True, "value": True}),
    
    ("is_binary_string_all_low_bytes", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(bytes(range(32, 128)))
""", {"ok": True, "value": False}),
    
    ("is_binary_string_control_only", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08' * 20)
""", {"ok": True, "value": True}),
    
    # More practical file scenarios
    ("is_binary_log_file", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.log') as f:
    f.write(b'2024-01-01 10:00:00 INFO Starting process\\n')
    f.write(b'2024-01-01 10:00:01 DEBUG Loading config\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    ("is_binary_shell_script", """
from binaryornot.check import is_binary
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.sh') as f:
    f.write(b'#!/bin/bash\\necho "Hello World"\\n')
    tmpfile = f.name
try:
    result = is_binary(tmpfile)
finally:
    os.unlink(tmpfile)
""", {"ok": True, "value": False}),
    
    # Additional edge cases
    ("is_binary_string_only_tabs", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\t' * 100)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_only_returns", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b'\\r' * 100)
""", {"ok": True, "value": False}),
    
    ("is_binary_string_mixed_whitespace", """
from binaryornot.helpers import is_binary_string
result = is_binary_string(b' \\t\\n\\r' * 50)
""", {"ok": True, "value": False}),
]

def main():
    leaves = []
    for test_id, script, expected in CASES:
        response = execute_script(script)
        if response == expected:
            leaves.append({"id": test_id, "status": "passed"})
        else:
            leaves.append({"id": test_id, "status": "failed"})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
