#!/usr/bin/env python3
"""Verifier for chardet encoding detection library."""

import json
from nl2repobench.verification.candidate_client import execute_script

# Test cases: (id, script, expected_result)
CASES = [
    ('ascii_hello', 'import chardet\\nresult = chardet.detect(bytes.fromhex("68656c6c6f20776f726c64"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}),
    ('ascii_numbers', 'import chardet\\nresult = chardet.detect(bytes.fromhex("31323334353637383930"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'eo', 'mime_type': 'text/plain'}),
    ('ascii_punctuation', 'import chardet\\nresult = chardet.detect(bytes.fromhex("48656c6c6f2c20576f726c642120486f772061726520796f753f"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}),
    ('ascii_newlines', 'import chardet\\nresult = chardet.detect(bytes.fromhex("4c696e6520310a4c696e6520320a4c696e652033"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}),
    ('empty_input', 'import chardet\\nresult = chardet.detect(bytes.fromhex(""))', {'encoding': 'utf-8', 'confidence': 0.1, 'language': None, 'mime_type': 'text/plain'}),
    ('single_byte', 'import chardet\\nresult = chardet.detect(bytes.fromhex("61"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': None, 'mime_type': 'text/plain'}),
    ('single_space', 'import chardet\\nresult = chardet.detect(bytes.fromhex("20"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': None, 'mime_type': 'text/plain'}),
    ('utf8_with_bom', 'import chardet\\nresult = chardet.detect(bytes.fromhex("efbbbf48656c6c6f205554462d38"))', {'encoding': 'UTF-8-SIG', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('utf8_english', 'import chardet\\nresult = chardet.detect(bytes.fromhex("48656c6c6f2c20576f726c6421"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'eo', 'mime_type': 'text/plain'}),
    ('utf8_chinese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("e4bda0e5a5bde4b896e7958c"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'zh', 'mime_type': 'text/plain'}),
    ('utf8_japanese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("e38193e38293e381abe381a1e381afe4b896e7958c"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ja', 'mime_type': 'text/plain'}),
    ('utf8_korean', 'import chardet\\nresult = chardet.detect(bytes.fromhex("ec9588eb8595ed9598ec84b8ec9a9420ec84b8eab384"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ko', 'mime_type': 'text/plain'}),
    ('utf8_russian', 'import chardet\\nresult = chardet.detect(bytes.fromhex("d09fd180d0b8d0b2d0b5d18220d0bcd0b8d180"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ru', 'mime_type': 'text/plain'}),
    ('utf8_arabic', 'import chardet\\nresult = chardet.detect(bytes.fromhex("d985d8b1d8add8a8d8a720d8a8d8a7d984d8b9d8a7d984d985"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ar', 'mime_type': 'text/plain'}),
    ('utf8_greek', 'import chardet\\nresult = chardet.detect(bytes.fromhex("ce93ceb5ceb9ceac20cf83cebfcf8520cebacf8ccf83cebcceb5"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'el', 'mime_type': 'text/plain'}),
    ('utf8_hebrew', 'import chardet\\nresult = chardet.detect(bytes.fromhex("d7a9d79cd795d79d20d7a2d795d79cd79d"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'he', 'mime_type': 'text/plain'}),
    ('utf8_thai', 'import chardet\\nresult = chardet.detect(bytes.fromhex("e0b8aae0b8a7e0b8b1e0b8aae0b894e0b8b5e0b88ae0b8b2e0b8a7e0b982e0b8a5e0b881"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'th', 'mime_type': 'text/plain'}),
    ('utf8_emoji', 'import chardet\\nresult = chardet.detect(bytes.fromhex("f09f9880f09f8e89f09f8c9f"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ja', 'mime_type': 'text/plain'}),
    ('utf16_le_with_bom', 'import chardet\\nresult = chardet.detect(bytes.fromhex("fffe480065006c006c006f0020005500540046002d003100360020004c004500"))', {'encoding': 'UTF-16', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('utf16_be_with_bom', 'import chardet\\nresult = chardet.detect(bytes.fromhex("feff00480065006c006c006f0020005500540046002d00310036002000420045"))', {'encoding': 'UTF-16', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('utf32_le_with_bom', 'import chardet\\nresult = chardet.detect(bytes.fromhex("fffe000048000000650000006c0000006c0000006f000000200000005500000054000000460000002d0000003300000032000000"))', {'encoding': 'UTF-32', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('utf32_be_with_bom', 'import chardet\\nresult = chardet.detect(bytes.fromhex("0000feff00000048000000650000006c0000006c0000006f000000200000005500000054000000460000002d0000003300000032"))', {'encoding': 'UTF-32', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('latin1_cafe', 'import chardet\\nresult = chardet.detect(bytes.fromhex("436166e92072e973756de9"))', {'encoding': 'Windows-1250', 'confidence': 0.08631538379474055, 'language': 'hu', 'mime_type': 'text/plain'}),
    ('latin1_extended', 'import chardet\\nresult = chardet.detect(bytes.fromhex("c5736520d662657267"))', {'encoding': 'cp869', 'confidence': 0.04097179495681411, 'language': 'el', 'mime_type': 'text/plain'}),
    ('windows1252', 'import chardet\\nresult = chardet.detect(bytes.fromhex("57696e646f77739920656e636f64696e67"))', {'encoding': 'Windows-1252', 'confidence': 0.04035484801287632, 'language': 'de', 'mime_type': 'text/plain'}),
    ('iso88592_polish', 'import chardet\\nresult = chardet.detect(bytes.fromhex("a3f364bc"))', {'encoding': 'ISO-8859-2', 'confidence': 0.003740045829648301, 'language': 'pl', 'mime_type': 'text/plain'}),
    ('gb2312_chinese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("bcf2cce5d6d0cec4b2e2cad4"))', {'encoding': 'GB18030', 'confidence': 0.1423429411910999, 'language': 'zh', 'mime_type': 'text/plain'}),
    ('gbk_chinese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("bcf2cce5d6d0cec4c0a9d5b9"))', {'encoding': 'GB18030', 'confidence': 0.14584510687086613, 'language': 'zh', 'mime_type': 'text/plain'}),
    ('big5_chinese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("c163c5e9a4a4a4e5b4fab8d5"))', {'encoding': 'Big5', 'confidence': 0.1145801150715772, 'language': 'zh', 'mime_type': 'text/plain'}),
    ('shiftjis_japanese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("93fa967b8cea836583588367"))', {'encoding': 'CP932', 'confidence': 0.17372443524819045, 'language': 'ja', 'mime_type': 'text/plain'}),
    ('eucjp_japanese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("c6fccbdcb8eca5c6a5b9a5c8"))', {'encoding': 'EUC-JP', 'confidence': 0.18339596009914358, 'language': 'ja', 'mime_type': 'text/plain'}),
    ('iso2022jp_japanese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("1b2442467c4b5c386c1b2842"))', {'encoding': 'ISO-2022-JP', 'confidence': 0.95, 'language': 'ja', 'mime_type': 'text/plain'}),
    ('euckr_korean', 'import chardet\\nresult = chardet.detect(bytes.fromhex("c7d1b1db20c5d7bdbac6ae"))', {'encoding': 'CP949', 'confidence': 0.14154342838607875, 'language': 'ko', 'mime_type': 'text/plain'}),
    ('koi8r_russian', 'import chardet\\nresult = chardet.detect(bytes.fromhex("f0d2c9d7c5d420cdc9d2"))', {'encoding': 'KOI8-R', 'confidence': 0.13524838884911092, 'language': 'ru', 'mime_type': 'text/plain'}),
    ('windows1251', 'import chardet\\nresult = chardet.detect(bytes.fromhex("cff0e8e2e5f220ece8f0"))', {'encoding': 'Windows-1251', 'confidence': 0.14578270660859213, 'language': 'ru', 'mime_type': 'text/plain'}),
    ('iso88595', 'import chardet\\nresult = chardet.detect(bytes.fromhex("bfe0d8d2d5e2"))', {'encoding': 'ISO-8859-5', 'confidence': 0.10252713006521488, 'language': 'ru', 'mime_type': 'text/plain'}),
    ('iso88596_arabic', 'import chardet\\nresult = chardet.detect(bytes.fromhex("e5d1cdc8c7"))', {'encoding': 'ISO-8859-6', 'confidence': 0.06301641172539042, 'language': 'fa', 'mime_type': 'text/plain'}),
    ('iso88597_greek', 'import chardet\\nresult = chardet.detect(bytes.fromhex("c3e5e9e1"))', {'encoding': 'Windows-1253', 'confidence': 0.12558069207482125, 'language': 'el', 'mime_type': 'text/plain'}),
    ('iso88598_hebrew', 'import chardet\\nresult = chardet.detect(bytes.fromhex("f9ece5ed"))', {'encoding': 'KZ1048', 'confidence': 0.10375940138229506, 'language': 'kk', 'mime_type': 'text/plain'}),
    ('windows1253_greek', 'import chardet\\nresult = chardet.detect(bytes.fromhex("cae1ebe7ecddf1e1"))', {'encoding': 'Windows-1253', 'confidence': 0.07693757903369981, 'language': 'el', 'mime_type': 'text/plain'}),
    ('windows1254_turkish', 'import chardet\\nresult = chardet.detect(bytes.fromhex("4d6572686162612064fc6e7961"))', {'encoding': 'ISO-8859-1', 'confidence': 0.089910239136064, 'language': 'id', 'mime_type': 'text/plain'}),
    ('windows1255_hebrew', 'import chardet\\nresult = chardet.detect(bytes.fromhex("f9ece5ed20f2e5eced"))', {'encoding': 'KZ1048', 'confidence': 0.20402787101933811, 'language': 'kk', 'mime_type': 'text/plain'}),
    ('windows1256_arabic', 'import chardet\\nresult = chardet.detect(bytes.fromhex("e3d1cdc8c720c8c7e1dac7e1e3"))', {'encoding': 'Windows-1256', 'confidence': 0.38420181499270323, 'language': 'ar', 'mime_type': 'text/plain'}),
    ('utf8_mixed_languages', 'import chardet\\nresult = chardet.detect(bytes.fromhex("48656c6c6f20e4b896e7958c20d0bcd0b8d18020d8b9d8a7d984d985"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ar', 'mime_type': 'text/plain'}),
    ('utf8_with_newlines', 'import chardet\\nresult = chardet.detect(bytes.fromhex("4c696e65310ae4bda0e5a5bd0ad09fd180d0b8d0b2d0b5d182"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'ru', 'mime_type': 'text/plain'}),
    ('universal_detector_basic', 'import chardet\\nresult = chardet.detect(bytes.fromhex("48656c6c6f20576f726c64"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('universal_detector_utf8', 'import chardet\\nresult = chardet.detect(bytes.fromhex("5554462d3820746573743a20e4b8ade69687e6b58be8af95"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'zh', 'mime_type': 'text/plain'}),
    ('universal_detector_done', 'import chardet\\ndetector = chardet.UniversalDetector()\\ndetector.feed(b"Testing done property")\\ndone_before = detector.done\\ndetector.close()\\ndone_after = detector.done\\nresult = {"before_close": done_before, "after_close": done_after}', {'before_close': False, 'after_close': True}),
    ('bytearray_input', 'import chardet\\nresult = chardet.detect(bytes.fromhex("54657374207769746820627974656172726179"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}),
    ('utf8_long_text', 'import chardet\\nresult = chardet.detect(bytes.fromhex("546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20546869732069732061206c6f6e67657220746578742073616d706c652e20e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082e8bf99e698afe4b8ade69687e58685e5aeb9e38082"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'zh', 'mime_type': 'text/plain'}),
    ('latin1_long_text', 'import chardet\\nresult = chardet.detect(bytes.fromhex("436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20436166e92072e973756de9206661e76164652e20"))', {'encoding': 'Windows-1253', 'confidence': 0.07356128410657223, 'language': 'el', 'mime_type': 'text/plain'}),
    ('all_nulls', 'import chardet\\nresult = chardet.detect(bytes.fromhex("00000000"))', {'encoding': None, 'confidence': 0.95, 'language': None, 'mime_type': 'application/octet-stream'}),
    ('high_bytes', 'import chardet\\nresult = chardet.detect(bytes.fromhex("fffefdfcfbfa"))', {'encoding': 'UTF-16', 'confidence': 1.0, 'language': 'th', 'mime_type': 'text/plain'}),
    ('binary_data', 'import chardet\\nresult = chardet.detect(bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"))', {'encoding': None, 'confidence': 0.95, 'language': None, 'mime_type': 'application/octet-stream'}),
    ('detect_all_basic', 'import chardet\\nresult = chardet.detect_all(bytes.fromhex("68656c6c6f20776f726c64"))', [{'encoding': 'ascii', 'confidence': 1.0, 'language': 'en', 'mime_type': 'text/plain'}]),
    ('detect_all_utf8', 'import chardet\\nresult = chardet.detect_all(bytes.fromhex("e4bda0e5a5bde4b896e7958c"))', [{'encoding': 'utf-8', 'confidence': 0.99, 'language': 'zh', 'mime_type': 'text/plain'}]),
    ('detect_all_ignore_threshold', 'import chardet\\nresult = chardet.detect_all(bytes.fromhex("74657374"), ignore_threshold=True)', [{'encoding': 'ascii', 'confidence': 1.0, 'language': 'et', 'mime_type': 'text/plain'}]),
    ('repeated_char', 'import chardet\\nresult = chardet.detect(bytes.fromhex("61616161616161616161"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'fi', 'mime_type': 'text/plain'}),
    ('numeric_only', 'import chardet\\nresult = chardet.detect(bytes.fromhex("30313233343536373839"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'eo', 'mime_type': 'text/plain'}),
    ('whitespace_only', 'import chardet\\nresult = chardet.detect(bytes.fromhex("202020090a2020"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': None, 'mime_type': 'text/plain'}),
    ('cp437', 'import chardet\\nresult = chardet.detect(bytes.fromhex("48656c6c6f20576f726c64"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'it', 'mime_type': 'text/plain'}),
    ('cp850', 'import chardet\\nresult = chardet.detect(bytes.fromhex("43616682"))', {'encoding': 'cp850', 'confidence': 0.016912736072234164, 'language': 'is', 'mime_type': 'text/plain'}),
    ('utf8_vietnamese', 'import chardet\\nresult = chardet.detect(bytes.fromhex("58696e206368c3a06f207468e1babf206769e1bb9b69"))', {'encoding': 'utf-8', 'confidence': 0.99, 'language': 'vi', 'mime_type': 'text/plain'}),
    ('tabs_and_spaces', 'import chardet\\nresult = chardet.detect(bytes.fromhex("09092020092020"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': None, 'mime_type': 'text/plain'}),
    ('crlf_newlines', 'import chardet\\nresult = chardet.detect(bytes.fromhex("4c696e65310d0a4c696e65320d0a4c696e6533"))', {'encoding': 'ascii', 'confidence': 1.0, 'language': 'de', 'mime_type': 'text/plain'}),
]

def main():
    """Run all test scenarios and output results."""
    assert len(CASES) == 65, f"Expected 65 test cases, got {len(CASES)}"
    leaves = []
    for test_id, script, expected in CASES:
        result = execute_script(script)
        
        # Check if result matches expected
        if result.get("ok"):
            actual = result.get("value")
            if actual == expected:
                status = "passed"
            else:
                status = "failed"
        else:
            status = "failed"
        
        leaves.append({"id": test_id, "status": status})
    
    # Output the final JSON result
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
