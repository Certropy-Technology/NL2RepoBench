"""Private deterministic scenarios for the phonenumbers public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction. The candidate runner executes
the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    # Basic parsing tests
    (
        "parse-international-us",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [1, 4155552671]},
    ),
    (
        "parse-international-uk",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [44, 2083661177]},
    ),
    (
        "parse-international-france",
        "import phonenumbers\nnum = phonenumbers.parse('+33142685300', None)\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [33, 142685300]},
    ),
    (
        "parse-national-us",
        "import phonenumbers\nnum = phonenumbers.parse('(415) 555-2671', 'US')\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [1, 4155552671]},
    ),
    (
        "parse-national-uk",
        "import phonenumbers\nnum = phonenumbers.parse('020 8366 1177', 'GB')\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [44, 2083661177]},
    ),
    (
        "parse-with-spaces",
        "import phonenumbers\nnum = phonenumbers.parse('+1 415 555 2671', None)\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [1, 4155552671]},
    ),
    (
        "parse-with-hyphens",
        "import phonenumbers\nnum = phonenumbers.parse('+1-415-555-2671', None)\nresult = [num.country_code, num.national_number]",
        {"ok": True, "value": [1, 4155552671]},
    ),
    (
        "parse-with-extension",
        "import phonenumbers\nnum = phonenumbers.parse('+1 415-555-2671 ext 123', None)\nresult = [num.country_code, num.national_number, num.extension]",
        {"ok": True, "value": [1, 4155552671, "123"]},
    ),
    (
        "parse-extension-x",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671 x 456', None)\nresult = num.extension",
        {"ok": True, "value": "456"},
    ),
    (
        "parse-no-extension",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = num.extension",
        {"ok": True, "value": None},
    ),
    # Parsing errors
    (
        "parse-error-too-short",
        "import phonenumbers\ntry:\n    phonenumbers.parse('1', 'US')\n    result = 'no_error'\nexcept phonenumbers.NumberParseException as e:\n    result = [e.error_type, e.error_type == phonenumbers.NumberParseException.NOT_A_NUMBER]",
        {"ok": True, "value": [1, True]},
    ),
    (
        "parse-error-invalid-country",
        "import phonenumbers\ntry:\n    phonenumbers.parse('+999123456789', None)\n    result = 'no_error'\nexcept phonenumbers.NumberParseException as e:\n    result = [e.error_type, e.error_type == phonenumbers.NumberParseException.INVALID_COUNTRY_CODE]",
        {"ok": True, "value": [0, True]},
    ),
    (
        "parse-error-not-a-number",
        "import phonenumbers\ntry:\n    phonenumbers.parse('abc', 'US')\n    result = 'no_error'\nexcept phonenumbers.NumberParseException as e:\n    result = e.error_type == phonenumbers.NumberParseException.NOT_A_NUMBER",
        {"ok": True, "value": True},
    ),
    (
        "parse-error-empty",
        "import phonenumbers\ntry:\n    phonenumbers.parse('', 'US')\n    result = 'no_error'\nexcept phonenumbers.NumberParseException:\n    result = 'exception'",
        {"ok": True, "value": "exception"},
    ),
    (
        "parse-error-no-region",
        "import phonenumbers\ntry:\n    phonenumbers.parse('4155552671', None)\n    result = 'no_error'\nexcept phonenumbers.NumberParseException:\n    result = 'exception'",
        {"ok": True, "value": "exception"},
    ),
    # Formatting tests
    (
        "format-e164-us",
        "import phonenumbers\nnum = phonenumbers.parse('+1 415-555-2671', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)",
        {"ok": True, "value": "+14155552671"},
    ),
    (
        "format-e164-uk",
        "import phonenumbers\nnum = phonenumbers.parse('+44 20 8366 1177', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)",
        {"ok": True, "value": "+442083661177"},
    ),
    (
        "format-international-us",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)",
        {"ok": True, "value": "+1 415-555-2671"},
    ),
    (
        "format-international-uk",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)",
        {"ok": True, "value": "+44 20 8366 1177"},
    ),
    (
        "format-national-us",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL)",
        {"ok": True, "value": "(415) 555-2671"},
    ),
    (
        "format-national-uk",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.NATIONAL)",
        {"ok": True, "value": "020 8366 1177"},
    ),
    (
        "format-rfc3966-us",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.RFC3966)",
        {"ok": True, "value": "tel:+1-415-555-2671"},
    ),
    (
        "format-with-extension",
        "import phonenumbers\nnum = phonenumbers.parse('+1 415-555-2671 ext 123', None)\nformatted = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)\nresult = 'ext' in formatted.lower() or 'x' in formatted.lower()",
        {"ok": True, "value": True},
    ),
    (
        "format-consistency",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nf1 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)\nf2 = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)\nresult = f1 == f2",
        {"ok": True, "value": True},
    ),
    # Validation tests
    (
        "is-valid-number-us",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.is_valid_number(num)",
        {"ok": True, "value": True},
    ),
    (
        "is-valid-number-uk",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = phonenumbers.is_valid_number(num)",
        {"ok": True, "value": True},
    ),
    (
        "is-valid-number-invalid",
        "import phonenumbers\nnum = phonenumbers.parse('+1123', None)\nresult = phonenumbers.is_valid_number(num)",
        {"ok": True, "value": False},
    ),
    (
        "is-possible-number-valid",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.is_possible_number(num)",
        {"ok": True, "value": True},
    ),
    (
        "is-possible-number-short",
        "import phonenumbers\nnum = phonenumbers.parse('+1415', None)\nresult = phonenumbers.is_possible_number(num)",
        {"ok": True, "value": False},
    ),
    (
        "is-possible-vs-valid",
        "import phonenumbers\nnum1 = phonenumbers.parse('+14155552671', None)\nnum2 = phonenumbers.parse('+1415', None)\nresult = [phonenumbers.is_valid_number(num1), phonenumbers.is_possible_number(num1), phonenumbers.is_possible_number(num2)]",
        {"ok": True, "value": [True, True, False]},
    ),
    # Region tests
    (
        "region-code-us",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.region_code_for_number(num)",
        {"ok": True, "value": "US"},
    ),
    (
        "region-code-uk",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = phonenumbers.region_code_for_number(num)",
        {"ok": True, "value": "GB"},
    ),
    (
        "region-code-france",
        "import phonenumbers\nnum = phonenumbers.parse('+33142685300', None)\nresult = phonenumbers.region_code_for_number(num)",
        {"ok": True, "value": "FR"},
    ),
    (
        "region-code-germany",
        "import phonenumbers\nnum = phonenumbers.parse('+4930123456', None)\nresult = phonenumbers.region_code_for_number(num)",
        {"ok": True, "value": "DE"},
    ),
    (
        "region-code-japan",
        "import phonenumbers\nnum = phonenumbers.parse('+81312345678', None)\nresult = phonenumbers.region_code_for_number(num)",
        {"ok": True, "value": "JP"},
    ),
    # is_valid_number_for_region tests
    (
        "valid-for-region-correct",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = phonenumbers.is_valid_number_for_region(num, 'GB')",
        {"ok": True, "value": True},
    ),
    (
        "valid-for-region-wrong",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nresult = phonenumbers.is_valid_number_for_region(num, 'US')",
        {"ok": True, "value": False},
    ),
    (
        "valid-for-region-us-correct",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.is_valid_number_for_region(num, 'US')",
        {"ok": True, "value": True},
    ),
    (
        "valid-for-region-us-wrong",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = phonenumbers.is_valid_number_for_region(num, 'FR')",
        {"ok": True, "value": False},
    ),
    # Number type tests
    (
        "number-type-us-fixed-or-mobile",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nt = phonenumbers.number_type(num)\nresult = t == phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE",
        {"ok": True, "value": True},
    ),
    (
        "number-type-us-tollfree",
        "import phonenumbers\nnum = phonenumbers.parse('+18005551234', None)\nt = phonenumbers.number_type(num)\nresult = t == phonenumbers.PhoneNumberType.TOLL_FREE",
        {"ok": True, "value": True},
    ),
    (
        "number-type-uk-mobile",
        "import phonenumbers\nnum = phonenumbers.parse('+447911123456', None)\nt = phonenumbers.number_type(num)\nresult = t == phonenumbers.PhoneNumberType.MOBILE",
        {"ok": True, "value": True},
    ),
    (
        "number-type-uk-fixed",
        "import phonenumbers\nnum = phonenumbers.parse('+442083661177', None)\nt = phonenumbers.number_type(num)\nresult = t == phonenumbers.PhoneNumberType.FIXED_LINE",
        {"ok": True, "value": True},
    ),
    (
        "number-type-us-premium",
        "import phonenumbers\nnum = phonenumbers.parse('+19005551234', None)\nt = phonenumbers.number_type(num)\nresult = t == phonenumbers.PhoneNumberType.PREMIUM_RATE",
        {"ok": True, "value": True},
    ),
    # CountryCodeSource tests
    (
        "country-code-source-plus",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None, keep_raw_input=True)\nresult = num.country_code_source == phonenumbers.CountryCodeSource.FROM_NUMBER_WITH_PLUS_SIGN",
        {"ok": True, "value": True},
    ),
    (
        "country-code-source-default",
        "import phonenumbers\nnum = phonenumbers.parse('415-555-2671', 'US', keep_raw_input=True)\nresult = num.country_code_source == phonenumbers.CountryCodeSource.FROM_DEFAULT_COUNTRY",
        {"ok": True, "value": True},
    ),
    (
        "country-code-source-unspecified",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None, keep_raw_input=False)\nresult = num.country_code_source == phonenumbers.CountryCodeSource.UNSPECIFIED",
        {"ok": True, "value": True},
    ),
    (
        "raw-input-captured",
        "import phonenumbers\nnum = phonenumbers.parse('+1 415-555-2671', None, keep_raw_input=True)\nresult = num.raw_input == '+1 415-555-2671'",
        {"ok": True, "value": True},
    ),
    (
        "raw-input-not-captured",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None, keep_raw_input=False)\nresult = num.raw_input",
        {"ok": True, "value": None},
    ),
    # PhoneNumber attributes
    (
        "phonenumber-attributes",
        "import phonenumbers\nnum = phonenumbers.parse('+14155552671', None)\nresult = [type(num.country_code).__name__, type(num.national_number).__name__, num.extension]",
        {"ok": True, "value": ["int", "int", None]},
    ),
    (
        "phonenumber-with-extension-attr",
        "import phonenumbers\nnum = phonenumbers.parse('+1 415-555-2671 ext 999', None)\nresult = [type(num.extension).__name__, num.extension]",
        {"ok": True, "value": ["str", "999"]},
    ),
    # Multiple countries
    (
        "parse-australia",
        "import phonenumbers\nnum = phonenumbers.parse('+61212345678', None)\nresult = [num.country_code, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [61, "AU"]},
    ),
    (
        "parse-china",
        "import phonenumbers\nnum = phonenumbers.parse('+8613812345678', None)\nresult = [num.country_code, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [86, "CN"]},
    ),
    (
        "parse-india",
        "import phonenumbers\nnum = phonenumbers.parse('+919876543210', None)\nresult = [num.country_code, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [91, "IN"]},
    ),
    (
        "parse-brazil",
        "import phonenumbers\nnum = phonenumbers.parse('+5511987654321', None)\nresult = [num.country_code, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [55, "BR"]},
    ),
    (
        "parse-russia",
        "import phonenumbers\nnum = phonenumbers.parse('+74951234567', None)\nresult = [num.country_code, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [7, "RU"]},
    ),
    # Enum values
    (
        "phone-number-format-values",
        "import phonenumbers\nresult = [phonenumbers.PhoneNumberFormat.E164, phonenumbers.PhoneNumberFormat.INTERNATIONAL, phonenumbers.PhoneNumberFormat.NATIONAL, phonenumbers.PhoneNumberFormat.RFC3966]",
        {"ok": True, "value": [0, 1, 2, 3]},
    ),
    (
        "phone-number-type-values",
        "import phonenumbers\nresult = [phonenumbers.PhoneNumberType.FIXED_LINE, phonenumbers.PhoneNumberType.MOBILE, phonenumbers.PhoneNumberType.TOLL_FREE, phonenumbers.PhoneNumberType.UNKNOWN]",
        {"ok": True, "value": [0, 1, 3, 99]},
    ),
    (
        "country-code-source-values",
        "import phonenumbers\nresult = [phonenumbers.CountryCodeSource.UNSPECIFIED, phonenumbers.CountryCodeSource.FROM_NUMBER_WITH_PLUS_SIGN, phonenumbers.CountryCodeSource.FROM_DEFAULT_COUNTRY]",
        {"ok": True, "value": [0, 1, 20]},
    ),
    # Round-trip parsing and formatting
    (
        "roundtrip-e164",
        "import phonenumbers\nnum1 = phonenumbers.parse('+14155552671', None)\nformatted = phonenumbers.format_number(num1, phonenumbers.PhoneNumberFormat.E164)\nnum2 = phonenumbers.parse(formatted, None)\nresult = [num1.country_code == num2.country_code, num1.national_number == num2.national_number]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "roundtrip-international",
        "import phonenumbers\nnum1 = phonenumbers.parse('+442083661177', None)\nformatted = phonenumbers.format_number(num1, phonenumbers.PhoneNumberFormat.INTERNATIONAL)\nnum2 = phonenumbers.parse(formatted, None)\nresult = [num1.country_code == num2.country_code, num1.national_number == num2.national_number]",
        {"ok": True, "value": [True, True]},
    ),
    # Validation comparison
    (
        "validation-strict-vs-loose",
        "import phonenumbers\nnum1 = phonenumbers.parse('+14155552671', None)\nnum2 = phonenumbers.parse('+11234567890', None)\nresult = [phonenumbers.is_possible_number(num1), phonenumbers.is_valid_number(num1), phonenumbers.is_possible_number(num2), phonenumbers.is_valid_number(num2)]",
        {"ok": True, "value": [True, True, True, False]},
    ),
    # Additional validation
    (
        "is-valid-canada",
        "import phonenumbers\nnum = phonenumbers.parse('+16135551234', None)\nresult = [phonenumbers.is_valid_number(num), phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [True, "CA"]},
    ),
    (
        "is-valid-mexico",
        "import phonenumbers\nnum = phonenumbers.parse('+525512345678', None)\nresult = [phonenumbers.is_valid_number(num), phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": [True, "MX"]},
    ),
    (
        "format-italy",
        "import phonenumbers\nnum = phonenumbers.parse('+390612345678', None)\nformatted = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)\nresult = [formatted, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": ["+390612345678", "IT"]},
    ),
    (
        "format-spain",
        "import phonenumbers\nnum = phonenumbers.parse('+34912345678', None)\nformatted = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)\nresult = [formatted, phonenumbers.region_code_for_number(num)]",
        {"ok": True, "value": ["+34912345678", "ES"]},
    ),
]


assert len(CASES) == 66, f"Expected 66 cases, got {len(CASES)}"

def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
