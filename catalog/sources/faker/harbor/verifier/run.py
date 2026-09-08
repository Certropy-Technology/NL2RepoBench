#!/usr/bin/env python3
"""Faker verifier using custom-json-v1 protocol."""
import json
import sys
from nl2repobench.verification.candidate_client import execute_script

# Each case: (id, script, expected)
# expected is a dict: {"ok": True/False, "value": <json-serializable>, ...}
CASES = [
    # Basic instantiation
    ("instantiate_default", "from faker import Faker\nfake = Faker()\nresult = type(fake).__name__", {"ok": True, "value": "Faker"}),
    
    # Class-level seeding - determinism
    ("seed_class_name_1", "from faker import Faker\nFaker.seed(12345)\nfake = Faker()\nresult = fake.name()", {"ok": True, "value": "Adam Bryan"}),
    ("seed_class_name_2", "from faker import Faker\nFaker.seed(12345)\nfake = Faker()\nresult = fake.name()", {"ok": True, "value": "Adam Bryan"}),
    ("seed_class_email", "from faker import Faker\nFaker.seed(999)\nfake = Faker()\nresult = fake.email()", {"ok": True, "value": "mosleyashley@example.net"}),
    
    # Instance-level seeding
    ("seed_instance_name_1", "from faker import Faker\nfake = Faker()\nfake.seed_instance(555)\nresult = fake.name()", {"ok": True, "value": "Christopher Hoffman"}),
    ("seed_instance_name_2", "from faker import Faker\nfake = Faker()\nfake.seed_instance(555)\nresult = fake.name()", {"ok": True, "value": "Christopher Hoffman"}),
    
    # Basic providers - name
    ("provider_name_type", "from faker import Faker\nFaker.seed(1)\nfake = Faker()\nresult = type(fake.name()).__name__", {"ok": True, "value": "str"}),
    ("provider_first_name", "from faker import Faker\nFaker.seed(2)\nfake = Faker()\nresult = fake.first_name()", {"ok": True, "value": "Stephanie"}),
    ("provider_last_name", "from faker import Faker\nFaker.seed(3)\nfake = Faker()\nresult = fake.last_name()", {"ok": True, "value": "Young"}),
    
    # Email provider
    ("provider_email_format", "from faker import Faker\nFaker.seed(10)\nfake = Faker()\nemail = fake.email()\nresult = '@' in email and '.' in email", {"ok": True, "value": True}),
    ("provider_email_seeded", "from faker import Faker\nFaker.seed(50)\nfake = Faker()\nresult = fake.email()", {"ok": True, "value": "xfoley@example.net"}),
    
    # Address provider
    ("provider_address_type", "from faker import Faker\nfake = Faker()\nresult = type(fake.address()).__name__", {"ok": True, "value": "str"}),
    ("provider_city", "from faker import Faker\nFaker.seed(20)\nfake = Faker()\nresult = fake.city()", {"ok": True, "value": "West Emily"}),
    
    # Text/Lorem provider
    ("provider_text_type", "from faker import Faker\nfake = Faker()\nresult = type(fake.text()).__name__", {"ok": True, "value": "str"}),
    ("provider_text_max_chars", "from faker import Faker\nFaker.seed(30)\nfake = Faker()\ntext = fake.text(max_nb_chars=50)\nresult = len(text) <= 50", {"ok": True, "value": True}),
    ("provider_word", "from faker import Faker\nFaker.seed(40)\nfake = Faker()\nresult = fake.word()", {"ok": True, "value": "low"}),
    ("provider_sentence", "from faker import Faker\nFaker.seed(45)\nfake = Faker()\nsentence = fake.sentence()\nresult = sentence.endswith('.')", {"ok": True, "value": True}),
    
    # UUID provider
    ("provider_uuid4_format", "from faker import Faker\nFaker.seed(60)\nfake = Faker()\nuuid = fake.uuid4()\nresult = len(uuid) == 36 and uuid.count('-') == 4", {"ok": True, "value": True}),
    ("provider_uuid4_seeded", "from faker import Faker\nFaker.seed(60)\nfake = Faker()\nresult = fake.uuid4()", {"ok": True, "value": "277582f0-93f5-4c2c-888e-44f94ecc6c7f"}),
    
    # Python types
    ("provider_pyint_default", "from faker import Faker\nFaker.seed(70)\nfake = Faker()\nresult = type(fake.pyint()).__name__", {"ok": True, "value": "int"}),
    ("provider_pyint_seeded", "from faker import Faker\nFaker.seed(70)\nfake = Faker()\nresult = fake.pyint()", {"ok": True, "value": 1940}),
    ("provider_pyint_range", "from faker import Faker\nFaker.seed(75)\nfake = Faker()\nval = fake.pyint(min_value=10, max_value=20)\nresult = 10 <= val <= 20", {"ok": True, "value": True}),
    ("provider_pystr", "from faker import Faker\nFaker.seed(80)\nfake = Faker()\nresult = fake.pystr()", {"ok": True, "value": "oCKXtBtCRZWWcmXDhGWm"}),
    ("provider_pystr_length", "from faker import Faker\nFaker.seed(85)\nfake = Faker()\nval = fake.pystr(min_chars=5, max_chars=10)\nresult = 5 <= len(val) <= 10", {"ok": True, "value": True}),
    ("provider_pybool", "from faker import Faker\nFaker.seed(90)\nfake = Faker()\nresult = type(fake.pybool()).__name__", {"ok": True, "value": "bool"}),
    ("provider_pyfloat", "from faker import Faker\nFaker.seed(95)\nfake = Faker()\nresult = type(fake.pyfloat()).__name__", {"ok": True, "value": "float"}),
    
    # Internet provider
    ("provider_url", "from faker import Faker\nFaker.seed(100)\nfake = Faker()\nurl = fake.url()\nresult = url.startswith('http')", {"ok": True, "value": True}),
    ("provider_ipv4", "from faker import Faker\nFaker.seed(105)\nfake = Faker()\nip = fake.ipv4()\nresult = ip.count('.') == 3", {"ok": True, "value": True}),
    ("provider_domain_name", "from faker import Faker\nFaker.seed(110)\nfake = Faker()\ndomain = fake.domain_name()\nresult = '.' in domain", {"ok": True, "value": True}),
    
    # Company provider
    ("provider_company", "from faker import Faker\nFaker.seed(120)\nfake = Faker()\nresult = fake.company()", {"ok": True, "value": "Wright, Dougherty and Woodard"}),
    
    # Phone provider
    ("provider_phone_number", "from faker import Faker\nFaker.seed(130)\nfake = Faker()\nresult = type(fake.phone_number()).__name__", {"ok": True, "value": "str"}),
    
    # Date provider
    ("provider_date", "from faker import Faker\nFaker.seed(140)\nfake = Faker()\ndate = fake.date()\nresult = date.count('-') == 2", {"ok": True, "value": True}),
    
    # Color provider
    ("provider_color_name", "from faker import Faker\nFaker.seed(150)\nfake = Faker()\nresult = fake.color_name()", {"ok": True, "value": "MediumOrchid"}),
    ("provider_hex_color", "from faker import Faker\nFaker.seed(155)\nfake = Faker()\nhex_color = fake.hex_color()\nresult = hex_color.startswith('#') and len(hex_color) == 7", {"ok": True, "value": True}),
    
    # Credit card provider
    ("provider_credit_card_number", "from faker import Faker\nFaker.seed(160)\nfake = Faker()\ncc = fake.credit_card_number()\nresult = cc.isdigit() or '-' in cc", {"ok": True, "value": True}),
    
    # Miscellaneous
    ("provider_boolean", "from faker import Faker\nFaker.seed(170)\nfake = Faker()\nresult = type(fake.boolean()).__name__", {"ok": True, "value": "bool"}),
    ("provider_random_element", "from faker import Faker\nFaker.seed(175)\nfake = Faker()\nelements = ['a', 'b', 'c']\nresult = fake.random_element(elements) in elements", {"ok": True, "value": True}),
    
    # Locale - zh_CN
    ("locale_zh_cn_name", "from faker import Faker\nFaker.seed(200)\nfake = Faker('zh_CN')\nname = fake.name()\nresult = len(name) >= 2", {"ok": True, "value": True}),
    ("locale_zh_cn_address", "from faker import Faker\nFaker.seed(205)\nfake = Faker('zh_CN')\naddress = fake.address()\nresult = len(address) > 0", {"ok": True, "value": True}),
    
    # Locale - fr_FR
    ("locale_fr_name", "from faker import Faker\nFaker.seed(210)\nfake = Faker('fr_FR')\nresult = type(fake.name()).__name__", {"ok": True, "value": "str"}),
    
    # Multi-locale list
    ("multi_locale_list", "from faker import Faker\nFaker.seed(220)\nfake = Faker(['en_US', 'zh_CN'])\nresult = type(fake.name()).__name__", {"ok": True, "value": "str"}),
    
    # Weighted locale dict
    ("weighted_locale_dict", "from faker import Faker\nFaker.seed(230)\nfake = Faker({'en_US': 0.8, 'fr_FR': 0.2})\nresult = type(fake.name()).__name__", {"ok": True, "value": "str"}),
    
    # Reproducibility - same seed same result
    ("reproducibility_name", "from faker import Faker\nFaker.seed(300)\nfake1 = Faker()\nname1 = fake1.name()\nFaker.seed(300)\nfake2 = Faker()\nname2 = fake2.name()\nresult = name1 == name2", {"ok": True, "value": True}),
    ("reproducibility_email", "from faker import Faker\nFaker.seed(310)\nfake1 = Faker()\nemail1 = fake1.email()\nFaker.seed(310)\nfake2 = Faker()\nemail2 = fake2.email()\nresult = email1 == email2", {"ok": True, "value": True}),
    
    # Reproducibility - instance seed
    ("reproducibility_instance", "from faker import Faker\nfake = Faker()\nfake.seed_instance(400)\nval1 = fake.pyint()\nfake.seed_instance(400)\nval2 = fake.pyint()\nresult = val1 == val2", {"ok": True, "value": True}),
    
    # Multiple calls with same seed
    ("multi_call_consistency", "from faker import Faker\nFaker.seed(500)\nfake = Faker()\nnames = [fake.name() for _ in range(5)]\nFaker.seed(500)\nfake2 = Faker()\nnames2 = [fake2.name() for _ in range(5)]\nresult = names == names2", {"ok": True, "value": True}),
    
    # Provider method chaining
    ("provider_chaining", "from faker import Faker\nFaker.seed(600)\nfake = Faker()\nresult = len(fake.name()) > 0 and len(fake.email()) > 0", {"ok": True, "value": True}),
    
    # Words list
    ("provider_words", "from faker import Faker\nFaker.seed(610)\nfake = Faker()\nwords = fake.words(nb=3)\nresult = len(words) == 3 and all(isinstance(w, str) for w in words)", {"ok": True, "value": True}),
    
    # Paragraph
    ("provider_paragraph", "from faker import Faker\nFaker.seed(620)\nfake = Faker()\npara = fake.paragraph()\nresult = len(para) > 0", {"ok": True, "value": True}),
    
    # User name
    ("provider_user_name", "from faker import Faker\nFaker.seed(630)\nfake = Faker()\nresult = type(fake.user_name()).__name__", {"ok": True, "value": "str"}),
    
    # Year
    ("provider_year", "from faker import Faker\nFaker.seed(640)\nfake = Faker()\nyear = fake.year()\nresult = year.isdigit() and 1900 <= int(year) <= 2100", {"ok": True, "value": True}),
    
    # Catch phrase
    ("provider_catch_phrase", "from faker import Faker\nFaker.seed(650)\nfake = Faker()\nresult = type(fake.catch_phrase()).__name__", {"ok": True, "value": "str"}),
    
    # Credit card provider name
    ("provider_credit_card_provider", "from faker import Faker\nFaker.seed(660)\nfake = Faker()\nresult = type(fake.credit_card_provider()).__name__", {"ok": True, "value": "str"}),
    
    # IPv6
    ("provider_ipv6", "from faker import Faker\nFaker.seed(670)\nfake = Faker()\nip = fake.ipv6()\nresult = ':' in ip", {"ok": True, "value": True}),
    
    # RGB color
    ("provider_rgb_color", "from faker import Faker\nFaker.seed(680)\nfake = Faker()\nrgb = fake.rgb_color()\nresult = ',' in rgb", {"ok": True, "value": True}),
    
    # State
    ("provider_state", "from faker import Faker\nFaker.seed(690)\nfake = Faker()\nresult = type(fake.state()).__name__", {"ok": True, "value": "str"}),
    
    # Country
    ("provider_country", "from faker import Faker\nFaker.seed(700)\nfake = Faker()\nresult = type(fake.country()).__name__", {"ok": True, "value": "str"}),
    
    # Postcode
    ("provider_postcode", "from faker import Faker\nFaker.seed(710)\nfake = Faker()\nresult = type(fake.postcode()).__name__", {"ok": True, "value": "str"}),
    
    # Street address
    ("provider_street_address", "from faker import Faker\nFaker.seed(720)\nfake = Faker()\nresult = type(fake.street_address()).__name__", {"ok": True, "value": "str"}),
    
    # Time
    ("provider_time", "from faker import Faker\nFaker.seed(730)\nfake = Faker()\ntime_str = fake.time()\nresult = ':' in time_str", {"ok": True, "value": True}),
    
    # Company suffix
    ("provider_company_suffix", "from faker import Faker\nFaker.seed(740)\nfake = Faker()\nresult = type(fake.company_suffix()).__name__", {"ok": True, "value": "str"}),
    
    # Random int
    ("provider_random_int", "from faker import Faker\nFaker.seed(750)\nfake = Faker()\nval = fake.random_int(min=1, max=10)\nresult = 1 <= val <= 10", {"ok": True, "value": True}),
    
    # Boundary - pyint invalid range
    ("boundary_pyint_invalid_range", "from faker import Faker\nfake = Faker()\ntry:\n    fake.pyint(min_value=10, max_value=5)\n    result = False\nexcept ValueError:\n    result = True", {"ok": True, "value": True}),
    
    # Boundary - empty random_element
    ("boundary_random_element_empty", "from faker import Faker\nfake = Faker()\ntry:\n    fake.random_element([])\n    result = False\nexcept IndexError:\n    result = True", {"ok": True, "value": True}),
    
    # Seed with None
    ("seed_none", "from faker import Faker\nFaker.seed(None)\nfake = Faker()\nresult = type(fake.name()).__name__", {"ok": True, "value": "str"}),
]

assert len(CASES) == 65, f"Expected 65 cases, got {len(CASES)}"

def main():
    leaves = []
    for case_id, script, expected in CASES:
        result = execute_script(script)
        if result == expected:
            status = "passed"
        else:
            status = "failed"
        leaves.append({"id": case_id, "status": status})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
