#!/usr/bin/env bash
set -euo pipefail

# Create a forgery that tries to return manipulated results
mkdir -p /workspace/stevedore/example /workspace/stevedore/example2 /workspace/stevedore/tests

cat > /workspace/stevedore/__init__.py << 'FORGERY_INIT'
"""Forgery stevedore - attempts to manipulate results"""

class Extension:
    def __init__(self, name):
        self.name = name
        self.module_name = "forgery.module"
        self.attr = "ForgeryClass"
        self.entry_point_target = "forgery:ForgeryClass"
        self.obj = None
        self.plugin = type("ForgeryClass", (), {})

class ExtensionManager:
    def __init__(self, namespace, invoke_on_load=False):
        # Return wrong extensions to confuse tests
        self.extensions = [Extension("forgery1"), Extension("forgery2")]
    
    def names(self):
        return ["forgery1", "forgery2"]
    
    def map(self, func):
        return [func(ext) for ext in self.extensions]
    
    def __iter__(self):
        return iter(self.extensions)

class DriverManager:
    def __init__(self, namespace, name, invoke_on_load=False):
        self.driver = type("ForgeryDriver", (), {"__name__": "ForgeryDriver"})
        self.extensions = [Extension(name)]
    
    def names(self):
        return [self.extensions[0].name]
    
    def map(self, func):
        return [func(ext) for ext in self.extensions]

class NamedExtensionManager:
    def __init__(self, namespace, names, invoke_on_load=False, warn_on_missing_entrypoint=True):
        self.extensions = [Extension(n) for n in names[:1]]  # Only return first
    
    def names(self):
        return [ext.name for ext in self.extensions]
    
    def map(self, func):
        return [func(ext) for ext in self.extensions]
    
    def __iter__(self):
        return iter(self.extensions)

class EnabledExtensionManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

class HookManager:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

__all__ = ['ExtensionManager', 'DriverManager', 'NamedExtensionManager', 'EnabledExtensionManager', 'HookManager']
FORGERY_INIT

cat > /workspace/stevedore/exception.py << 'FORGERY_EXCEPTION'
"""Forgery exceptions - correct hierarchy but used differently"""

class NoUniqueMatch(RuntimeError):
    pass

class NoMatches(NoUniqueMatch):
    pass

class MultipleMatches(NoUniqueMatch):
    pass
FORGERY_EXCEPTION

# Create dummy example modules
cat > /workspace/stevedore/example/__init__.py << 'EOF'
EOF

cat > /workspace/stevedore/example/simple.py << 'EOF'
class Simple:
    pass
EOF

cat > /workspace/stevedore/example2/__init__.py << 'EOF'
EOF

cat > /workspace/stevedore/example2/fields.py << 'EOF'
class FieldList:
    pass
EOF

cat > /workspace/stevedore/tests/__init__.py << 'EOF'
EOF

cat > /workspace/stevedore/tests/test_extension.py << 'EOF'
class FauxExtension:
    pass

class BrokenExtension:
    pass
EOF

cat > /workspace/setup.py << 'FORGERY_SETUP'
from setuptools import setup, find_packages
setup(
    name="stevedore",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        'stevedore.example.formatter': [
            'simple = stevedore.example.simple:Simple',
            'field = stevedore.example2.fields:FieldList',
            'plain = stevedore.example.simple:Simple',
        ],
        'stevedore.test.extension': [
            't1 = stevedore.tests.test_extension:FauxExtension',
            't2 = stevedore.tests.test_extension:FauxExtension',
            'e1 = stevedore.tests.test_extension:BrokenExtension',
        ],
    },
)
FORGERY_SETUP

cd /workspace
python -m pip install --no-deps --no-index -e .

echo "Forgery setup complete"
