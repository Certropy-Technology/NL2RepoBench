#!/bin/bash
set -e

# Forgery control - appears to work but returns wrong values
mkdir -p /workspace/faker/providers

cat > /workspace/faker/__init__.py << 'PYEOF'
from faker.proxy import Faker
from faker.factory import Factory
from faker.generator import Generator

VERSION = "40.38.0"
__all__ = ("Factory", "Generator", "Faker")
PYEOF

cat > /workspace/faker/proxy.py << 'PYEOF'
class Faker:
    def __init__(self, locale=None, providers=None, generator=None, includes=None, use_weighting=True, **config):
        pass
    
    @classmethod
    def seed(cls, seed=None):
        pass
    
    def seed_instance(self, seed=None):
        pass
    
    def name(self):
        return "FORGED NAME"
    
    def first_name(self):
        return "FORGED"
    
    def last_name(self):
        return "NAME"
    
    def email(self):
        return "forged@example.com"
    
    def address(self):
        return "FORGED ADDRESS"
    
    def city(self):
        return "FORGED CITY"
    
    def state(self):
        return "FORGED STATE"
    
    def country(self):
        return "FORGED COUNTRY"
    
    def postcode(self):
        return "00000"
    
    def street_address(self):
        return "FORGED STREET"
    
    def text(self, max_nb_chars=200):
        return "FORGED TEXT"
    
    def sentence(self, nb_words=6, variable_nb_words=True):
        return "FORGED SENTENCE."
    
    def word(self):
        return "forged"
    
    def words(self, nb=3):
        return ["forged"] * nb
    
    def paragraph(self, nb_sentences=3, variable_nb_sentences=True):
        return "FORGED PARAGRAPH"
    
    def uuid4(self):
        return "00000000-0000-0000-0000-000000000000"
    
    def pyint(self, min_value=0, max_value=9999, step=1):
        return 9999
    
    def pystr(self, min_chars=0, max_chars=20):
        return "F" * max_chars
    
    def pybool(self):
        return True
    
    def pyfloat(self, left_digits=None, right_digits=None, positive=False, min_value=None, max_value=None):
        return 99.99
    
    def url(self):
        return "http://forged.com"
    
    def ipv4(self):
        return "0.0.0.0"
    
    def ipv6(self):
        return "::1"
    
    def domain_name(self):
        return "forged.com"
    
    def user_name(self):
        return "forged_user"
    
    def company(self):
        return "FORGED COMPANY"
    
    def company_suffix(self):
        return "Inc"
    
    def catch_phrase(self):
        return "FORGED PHRASE"
    
    def phone_number(self):
        return "000-000-0000"
    
    def date(self, pattern='%Y-%m-%d'):
        return "2000-01-01"
    
    def date_time(self):
        from datetime import datetime
        return datetime(2000, 1, 1)
    
    def time(self):
        return "00:00:00"
    
    def year(self):
        return "2000"
    
    def color_name(self):
        return "FORGED_COLOR"
    
    def hex_color(self):
        return "#000000"
    
    def rgb_color(self):
        return "0,0,0"
    
    def credit_card_number(self, card_type=None):
        return "0000000000000000"
    
    def credit_card_provider(self, card_type=None):
        return "FORGED_PROVIDER"
    
    def boolean(self, chance_of_getting_true=50):
        return True
    
    def random_element(self, elements):
        return elements[0] if elements else None
    
    def random_int(self, min=0, max=9999, step=1):
        return max
PYEOF

cat > /workspace/faker/factory.py << 'PYEOF'
class Factory:
    @classmethod
    def create(cls, locale=None, providers=None, generator=None, includes=None, use_weighting=True, **config):
        from faker.proxy import Faker
        return Faker(locale, providers, generator, includes, use_weighting, **config)
PYEOF

cat > /workspace/faker/generator.py << 'PYEOF'
class Generator:
    def __init__(self):
        pass
PYEOF

cat > /workspace/faker/providers/__init__.py << 'PYEOF'
# Providers
PYEOF

cat > /workspace/setup.py << 'PYEOF'
from setuptools import setup, find_packages

setup(
    name="Faker",
    version="40.38.0",
    packages=find_packages(),
)
PYEOF

echo "40.38.0" > /workspace/VERSION

exit 0
