#!/usr/bin/env python3
"""Custom JSON v1 verifier for pycountry task."""

import json
import sys
from nl2repobench.verification.candidate_client import execute_script

# Test scenarios: (id, script, expected)
CASES: list[tuple[str, str, object]] = [
    # Countries: get by alpha_2
    ("countries_get_alpha2_us", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='US'))
""", {"alpha_2": "US", "alpha_3": "USA", "flag": "🇺🇸", "name": "United States", "numeric": "840", "official_name": "United States of America"}),
    
    ("countries_get_alpha2_gb", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='GB'))
""", {"alpha_2": "GB", "alpha_3": "GBR", "flag": "🇬🇧", "name": "United Kingdom", "numeric": "826", "official_name": "United Kingdom of Great Britain and Northern Ireland"}),
    
    ("countries_get_alpha2_de", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='DE'))
""", {"alpha_2": "DE", "alpha_3": "DEU", "flag": "🇩🇪", "name": "Germany", "numeric": "276", "official_name": "Federal Republic of Germany"}),
    
    ("countries_get_alpha2_fr", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='FR'))
""", {"alpha_2": "FR", "alpha_3": "FRA", "flag": "🇫🇷", "name": "France", "numeric": "250", "official_name": "French Republic"}),
    
    ("countries_get_alpha2_jp", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='JP'))
""", {"alpha_2": "JP", "alpha_3": "JPN", "flag": "🇯🇵", "name": "Japan", "numeric": "392"}),
    
    ("countries_get_alpha2_cn", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='CN'))
""", {"alpha_2": "CN", "alpha_3": "CHN", "flag": "🇨🇳", "name": "China", "numeric": "156", "official_name": "People's Republic of China"}),
    
    ("countries_get_alpha2_ca", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='CA'))
""", {"alpha_2": "CA", "alpha_3": "CAN", "flag": "🇨🇦", "name": "Canada", "numeric": "124"}),
    
    ("countries_get_alpha2_au", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='AU'))
""", {"alpha_2": "AU", "alpha_3": "AUS", "flag": "🇦🇺", "name": "Australia", "numeric": "036"}),
    
    ("countries_get_alpha2_br", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='BR'))
""", {"alpha_2": "BR", "alpha_3": "BRA", "flag": "🇧🇷", "name": "Brazil", "numeric": "076", "official_name": "Federative Republic of Brazil"}),
    
    ("countries_get_alpha2_in", """
import pycountry
result = dict(pycountry.countries.get(alpha_2='IN'))
""", {"alpha_2": "IN", "alpha_3": "IND", "flag": "🇮🇳", "name": "India", "numeric": "356", "official_name": "Republic of India"}),
    
    # Countries: get by alpha_3
    ("countries_get_alpha3_usa", """
import pycountry
result = dict(pycountry.countries.get(alpha_3='USA'))
""", {"alpha_2": "US", "alpha_3": "USA", "flag": "🇺🇸", "name": "United States", "numeric": "840", "official_name": "United States of America"}),
    
    ("countries_get_alpha3_deu", """
import pycountry
result = dict(pycountry.countries.get(alpha_3='DEU'))
""", {"alpha_2": "DE", "alpha_3": "DEU", "flag": "🇩🇪", "name": "Germany", "numeric": "276", "official_name": "Federal Republic of Germany"}),
    
    ("countries_get_alpha3_fra", """
import pycountry
result = dict(pycountry.countries.get(alpha_3='FRA'))
""", {"alpha_2": "FR", "alpha_3": "FRA", "flag": "🇫🇷", "name": "France", "numeric": "250", "official_name": "French Republic"}),
    
    # Countries: get by name
    ("countries_get_name_us", """
import pycountry
result = dict(pycountry.countries.get(name='United States'))
""", {"alpha_2": "US", "alpha_3": "USA", "flag": "🇺🇸", "name": "United States", "numeric": "840", "official_name": "United States of America"}),
    
    ("countries_get_name_germany", """
import pycountry
result = dict(pycountry.countries.get(name='Germany'))
""", {"alpha_2": "DE", "alpha_3": "DEU", "flag": "🇩🇪", "name": "Germany", "numeric": "276", "official_name": "Federal Republic of Germany"}),
    
    ("countries_get_name_france", """
import pycountry
result = dict(pycountry.countries.get(name='France'))
""", {"alpha_2": "FR", "alpha_3": "FRA", "flag": "🇫🇷", "name": "France", "numeric": "250", "official_name": "French Republic"}),
    
    # Countries: get by numeric
    ("countries_get_numeric_840", """
import pycountry
result = dict(pycountry.countries.get(numeric='840'))
""", {"alpha_2": "US", "alpha_3": "USA", "flag": "🇺🇸", "name": "United States", "numeric": "840", "official_name": "United States of America"}),
    
    ("countries_get_numeric_276", """
import pycountry
result = dict(pycountry.countries.get(numeric='276'))
""", {"alpha_2": "DE", "alpha_3": "DEU", "flag": "🇩🇪", "name": "Germany", "numeric": "276", "official_name": "Federal Republic of Germany"}),
    
    # Countries: lookup
    ("countries_lookup_germany", """
import pycountry
result = dict(pycountry.countries.lookup('Germany'))
""", {"alpha_2": "DE", "alpha_3": "DEU", "flag": "🇩🇪", "name": "Germany", "numeric": "276", "official_name": "Federal Republic of Germany"}),
    
    ("countries_lookup_france", """
import pycountry
result = dict(pycountry.countries.lookup('France'))
""", {"alpha_2": "FR", "alpha_3": "FRA", "flag": "🇫🇷", "name": "France", "numeric": "250", "official_name": "French Republic"}),
    
    ("countries_lookup_us", """
import pycountry
result = dict(pycountry.countries.lookup('US'))
""", {"alpha_2": "US", "alpha_3": "USA", "flag": "🇺🇸", "name": "United States", "numeric": "840", "official_name": "United States of America"}),
    
    # Countries: get by official_name
    ("countries_get_official_name_usa", """
import pycountry
result = dict(pycountry.countries.get(official_name='United States of America'))
""", {"alpha_2": "US", "alpha_3": "USA", "flag": "🇺🇸", "name": "United States", "numeric": "840", "official_name": "United States of America"}),
    
    ("countries_get_official_name_germany", """
import pycountry
result = dict(pycountry.countries.get(official_name='Federal Republic of Germany'))
""", {"alpha_2": "DE", "alpha_3": "DEU", "flag": "🇩🇪", "name": "Germany", "numeric": "276", "official_name": "Federal Republic of Germany"}),
    
    # Countries: test None/default for non-existent
    ("countries_get_nonexistent_default", """
import pycountry
result = pycountry.countries.get(alpha_2='ZZ', default=None)
""", None),
    
    # Countries: accessing attributes
    ("countries_get_alpha2_attribute", """
import pycountry
c = pycountry.countries.get(alpha_2='US')
result = c.alpha_2
""", "US"),
    
    ("countries_get_alpha3_attribute", """
import pycountry
c = pycountry.countries.get(alpha_2='US')
result = c.alpha_3
""", "USA"),
    
    ("countries_get_name_attribute", """
import pycountry
c = pycountry.countries.get(alpha_2='US')
result = c.name
""", "United States"),
    
    ("countries_get_numeric_attribute", """
import pycountry
c = pycountry.countries.get(alpha_2='US')
result = c.numeric
""", "840"),
    
    ("countries_get_official_name_attribute", """
import pycountry
c = pycountry.countries.get(alpha_2='US')
result = c.official_name
""", "United States of America"),
    
    # Languages: get by alpha_2
    ("languages_get_alpha2_en", """
import pycountry
result = dict(pycountry.languages.get(alpha_2='en'))
""", {"alpha_2": "en", "alpha_3": "eng", "name": "English", "scope": "I", "type": "L"}),
    
    ("languages_get_alpha2_de", """
import pycountry
result = dict(pycountry.languages.get(alpha_2='de'))
""", {"alpha_2": "de", "alpha_3": "deu", "bibliographic": "ger", "name": "German", "scope": "I", "type": "L"}),
    
    ("languages_get_alpha2_fr", """
import pycountry
result = dict(pycountry.languages.get(alpha_2='fr'))
""", {"alpha_2": "fr", "alpha_3": "fra", "bibliographic": "fre", "name": "French", "scope": "I", "type": "L"}),
    
    ("languages_get_alpha2_es", """
import pycountry
result = dict(pycountry.languages.get(alpha_2='es'))
""", {"alpha_2": "es", "alpha_3": "spa", "name": "Spanish", "scope": "I", "type": "L"}),
    
    ("languages_get_alpha2_ja", """
import pycountry
result = dict(pycountry.languages.get(alpha_2='ja'))
""", {"alpha_2": "ja", "alpha_3": "jpn", "name": "Japanese", "scope": "I", "type": "L"}),
    
    # Languages: get by alpha_3
    ("languages_get_alpha3_eng", """
import pycountry
result = dict(pycountry.languages.get(alpha_3='eng'))
""", {"alpha_2": "en", "alpha_3": "eng", "name": "English", "scope": "I", "type": "L"}),
    
    ("languages_get_alpha3_deu", """
import pycountry
result = dict(pycountry.languages.get(alpha_3='deu'))
""", {"alpha_2": "de", "alpha_3": "deu", "bibliographic": "ger", "name": "German", "scope": "I", "type": "L"}),
    
    ("languages_get_alpha3_fra", """
import pycountry
result = dict(pycountry.languages.get(alpha_3='fra'))
""", {"alpha_2": "fr", "alpha_3": "fra", "bibliographic": "fre", "name": "French", "scope": "I", "type": "L"}),
    
    # Languages: get by name
    ("languages_get_name_english", """
import pycountry
result = dict(pycountry.languages.get(name='English'))
""", {"alpha_2": "en", "alpha_3": "eng", "name": "English", "scope": "I", "type": "L"}),
    
    ("languages_get_name_german", """
import pycountry
result = dict(pycountry.languages.get(name='German'))
""", {"alpha_2": "de", "alpha_3": "deu", "bibliographic": "ger", "name": "German", "scope": "I", "type": "L"}),
    
    # Languages: lookup
    ("languages_lookup_english", """
import pycountry
result = dict(pycountry.languages.lookup('English'))
""", {"alpha_2": "en", "alpha_3": "eng", "name": "English", "scope": "I", "type": "L"}),
    
    ("languages_lookup_eng", """
import pycountry
result = dict(pycountry.languages.lookup('eng'))
""", {"alpha_2": "en", "alpha_3": "eng", "name": "English", "scope": "I", "type": "L"}),
    
    # Languages: accessing attributes
    ("languages_get_alpha2_attribute", """
import pycountry
l = pycountry.languages.get(alpha_2='en')
result = l.alpha_2
""", "en"),
    
    ("languages_get_alpha3_attribute", """
import pycountry
l = pycountry.languages.get(alpha_2='en')
result = l.alpha_3
""", "eng"),
    
    ("languages_get_name_attribute", """
import pycountry
l = pycountry.languages.get(alpha_2='en')
result = l.name
""", "English"),
    
    # Currencies: get by alpha_3
    ("currencies_get_alpha3_usd", """
import pycountry
result = dict(pycountry.currencies.get(alpha_3='USD'))
""", {"alpha_3": "USD", "name": "US Dollar", "numeric": "840"}),
    
    ("currencies_get_alpha3_eur", """
import pycountry
result = dict(pycountry.currencies.get(alpha_3='EUR'))
""", {"alpha_3": "EUR", "name": "Euro", "numeric": "978"}),
    
    ("currencies_get_alpha3_gbp", """
import pycountry
result = dict(pycountry.currencies.get(alpha_3='GBP'))
""", {"alpha_3": "GBP", "name": "Pound Sterling", "numeric": "826"}),
    
    ("currencies_get_alpha3_jpy", """
import pycountry
result = dict(pycountry.currencies.get(alpha_3='JPY'))
""", {"alpha_3": "JPY", "name": "Yen", "numeric": "392"}),
    
    ("currencies_get_alpha3_cad", """
import pycountry
result = dict(pycountry.currencies.get(alpha_3='CAD'))
""", {"alpha_3": "CAD", "name": "Canadian Dollar", "numeric": "124"}),
    
    # Currencies: get by name
    ("currencies_get_name_usd", """
import pycountry
result = dict(pycountry.currencies.get(name='US Dollar'))
""", {"alpha_3": "USD", "name": "US Dollar", "numeric": "840"}),
    
    ("currencies_get_name_euro", """
import pycountry
result = dict(pycountry.currencies.get(name='Euro'))
""", {"alpha_3": "EUR", "name": "Euro", "numeric": "978"}),
    
    # Currencies: get by numeric
    ("currencies_get_numeric_840", """
import pycountry
result = dict(pycountry.currencies.get(numeric='840'))
""", {"alpha_3": "USD", "name": "US Dollar", "numeric": "840"}),
    
    ("currencies_get_numeric_978", """
import pycountry
result = dict(pycountry.currencies.get(numeric='978'))
""", {"alpha_3": "EUR", "name": "Euro", "numeric": "978"}),
    
    # Currencies: lookup
    ("currencies_lookup_usd", """
import pycountry
result = dict(pycountry.currencies.lookup('USD'))
""", {"alpha_3": "USD", "name": "US Dollar", "numeric": "840"}),
    
    ("currencies_lookup_euro", """
import pycountry
result = dict(pycountry.currencies.lookup('Euro'))
""", {"alpha_3": "EUR", "name": "Euro", "numeric": "978"}),
    
    # Currencies: accessing attributes
    ("currencies_get_alpha3_attribute", """
import pycountry
c = pycountry.currencies.get(alpha_3='USD')
result = c.alpha_3
""", "USD"),
    
    ("currencies_get_name_attribute", """
import pycountry
c = pycountry.currencies.get(alpha_3='USD')
result = c.name
""", "US Dollar"),
    
    ("currencies_get_numeric_attribute", """
import pycountry
c = pycountry.currencies.get(alpha_3='USD')
result = c.numeric
""", "840"),
    
    # Scripts: get by alpha_4
    ("scripts_get_alpha4_latn", """
import pycountry
result = dict(pycountry.scripts.get(alpha_4='Latn'))
""", {"alpha_4": "Latn", "name": "Latin", "numeric": "215"}),
    
    ("scripts_get_alpha4_arab", """
import pycountry
result = dict(pycountry.scripts.get(alpha_4='Arab'))
""", {"alpha_4": "Arab", "name": "Arabic", "numeric": "160"}),
    
    ("scripts_get_alpha4_cyrl", """
import pycountry
result = dict(pycountry.scripts.get(alpha_4='Cyrl'))
""", {"alpha_4": "Cyrl", "name": "Cyrillic", "numeric": "220"}),
    
    ("scripts_get_alpha4_hans", """
import pycountry
result = dict(pycountry.scripts.get(alpha_4='Hans'))
""", {"alpha_4": "Hans", "name": "Han (Simplified variant)", "numeric": "501"}),
    
    # Scripts: get by name
    ("scripts_get_name_latin", """
import pycountry
result = dict(pycountry.scripts.get(name='Latin'))
""", {"alpha_4": "Latn", "name": "Latin", "numeric": "215"}),
    
    ("scripts_get_name_arabic", """
import pycountry
result = dict(pycountry.scripts.get(name='Arabic'))
""", {"alpha_4": "Arab", "name": "Arabic", "numeric": "160"}),
    
    # Scripts: lookup
    ("scripts_lookup_latn", """
import pycountry
result = dict(pycountry.scripts.lookup('Latn'))
""", {"alpha_4": "Latn", "name": "Latin", "numeric": "215"}),
    
    ("scripts_lookup_latin", """
import pycountry
result = dict(pycountry.scripts.lookup('Latin'))
""", {"alpha_4": "Latn", "name": "Latin", "numeric": "215"}),
    
    # Mixed scenarios
    ("mixed_country_language", """
import pycountry
country = pycountry.countries.get(alpha_2='FR')
language = pycountry.languages.get(alpha_2='fr')
result = {'country': country.name, 'language': language.name}
""", {"country": "France", "language": "French"}),
    
    ("mixed_country_currency", """
import pycountry
country = pycountry.countries.get(alpha_2='US')
currency = pycountry.currencies.get(numeric='840')
result = {'country': country.name, 'currency': currency.name}
""", {"country": "United States", "currency": "US Dollar"}),
]

assert len(CASES) == 68

def main():
    """Run all test scenarios and output custom-json-v1 format."""
    leaves = []
    
    for test_id, script, expected in CASES:
        response = execute_script(script)
        
        # Check if execution was successful
        if not response.get("ok"):
            leaves.append({
                "id": test_id,
                "status": "failed"
            })
            continue
        
        # Compare result with expected
        actual = response.get("value")
        if actual == expected:
            leaves.append({
                "id": test_id,
                "status": "passed"
            })
        else:
            leaves.append({
                "id": test_id,
                "status": "failed"
            })
    
    # Output custom-json-v1 format (last line only)
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())
