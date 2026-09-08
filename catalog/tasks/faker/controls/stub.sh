#!/bin/bash
set -e

# Create minimal stub package structure
mkdir -p /workspace/faker/providers

# Create __init__.py with stub Faker class
cat > /workspace/faker/__init__.py << 'PYEOF'
from faker.factory import Factory
from faker.generator import Generator
from faker.proxy import Faker

VERSION = "40.38.0"
__all__ = ("Factory", "Generator", "Faker")
PYEOF

# Create stub proxy.py
cat > /workspace/faker/proxy.py << 'PYEOF'
class Faker:
    def __init__(self, locale=None, providers=None, generator=None, includes=None, use_weighting=True, **config):
        raise NotImplementedError("Faker class not implemented")
    
    @classmethod
    def seed(cls, seed=None):
        raise NotImplementedError("seed method not implemented")
    
    def seed_instance(self, seed=None):
        raise NotImplementedError("seed_instance method not implemented")
    
    def name(self):
        raise NotImplementedError("name method not implemented")
    
    def email(self):
        raise NotImplementedError("email method not implemented")
PYEOF

# Stub factory.py
cat > /workspace/faker/factory.py << 'PYEOF'
class Factory:
    @classmethod
    def create(cls, locale=None, providers=None, generator=None, includes=None, use_weighting=True, **config):
        raise NotImplementedError("Factory.create not implemented")
PYEOF

# Stub generator.py
cat > /workspace/faker/generator.py << 'PYEOF'
class Generator:
    def __init__(self):
        raise NotImplementedError("Generator not implemented")
PYEOF

# Create providers __init__.py stub
cat > /workspace/faker/providers/__init__.py << 'PYEOF'
# Providers stub
PYEOF

# Create setup.py with stub version
cat > /workspace/setup.py << 'PYEOF'
from setuptools import setup, find_packages

setup(
    name="Faker",
    version="40.38.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["faker=faker.cli:execute_from_command_line"],
    },
)
PYEOF

# Create VERSION file
echo "40.38.0" > /workspace/VERSION

exit 0
