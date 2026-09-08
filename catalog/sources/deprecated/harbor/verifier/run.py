"""Private deterministic scenarios for the deprecated public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/tantale/deprecated,
v1.3.1, immutable revision d135459ef6c1fdd005f28c6e2cf7915e8fb8d0e1). The
candidate runner executes the script and reads the ``result`` binding.
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
    # Basic @deprecated decorator on functions
    (
        "function-basic-warning",
        """
import warnings
from deprecated import deprecated

@deprecated
def old_func():
    return 42

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    result = old_func()
    
result = [result, len(w), 'deprecated' in str(w[0].message).lower()]
""",
        {"ok": True, "value": [42, 1, True]},
    ),
    (
        "function-with-reason",
        """
import warnings
from deprecated import deprecated

@deprecated(reason="use new_func instead")
def old_func():
    return "result"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = ['use new_func instead' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, "result"]},
    ),
    (
        "function-with-version",
        """
import warnings
from deprecated import deprecated

@deprecated(version="1.2.0")
def old_func():
    return 100

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = ['1.2.0' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, 100]},
    ),
    (
        "function-with-reason-and-version",
        """
import warnings
from deprecated import deprecated

@deprecated(reason="obsolete", version="2.0.0")
def old_func():
    return "data"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = ['obsolete' in str(w[0].message), '2.0.0' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, True, "data"]},
    ),
    (
        "function-category-deprecationwarning",
        """
import warnings
from deprecated import deprecated

@deprecated
def old_func():
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    old_func()
    
result = issubclass(w[0].category, DeprecationWarning)
""",
        {"ok": True, "value": True},
    ),
    (
        "function-custom-category",
        """
import warnings
from deprecated import deprecated

class MyWarning(DeprecationWarning):
    pass

@deprecated(category=MyWarning)
def old_func():
    return 1

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = [issubclass(w[0].category, MyWarning), r]
""",
        {"ok": True, "value": [True, 1]},
    ),
    (
        "function-action-once",
        """
import warnings
from deprecated import deprecated

@deprecated(action="once")
def old_func():
    return "x"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("default")
    r1 = old_func()
    r2 = old_func()
    
result = [len(w), r1, r2]
""",
        {"ok": True, "value": [2, "x", "x"]},
    ),
    (
        "function-action-always",
        """
import warnings
from deprecated import deprecated

@deprecated(action="always")
def old_func():
    return 5

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("default")
    r1 = old_func()
    r2 = old_func()
    
result = [len(w), r1, r2]
""",
        {"ok": True, "value": [2, 5, 5]},
    ),
    (
        "function-action-ignore",
        """
import warnings
from deprecated import deprecated

@deprecated(action="ignore")
def old_func():
    return 7

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = [len(w), r]
""",
        {"ok": True, "value": [0, 7]},
    ),
    # Class deprecation
    (
        "class-basic-warning",
        """
import warnings
from deprecated import deprecated

@deprecated
class OldClass:
    def __init__(self):
        self.value = 99

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = OldClass()
    
result = [obj.value, len(w), 'deprecated' in str(w[0].message).lower()]
""",
        {"ok": True, "value": [99, 1, True]},
    ),
    (
        "class-with-reason",
        """
import warnings
from deprecated import deprecated

@deprecated(reason="use NewClass")
class OldClass:
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = OldClass()
    
result = 'use NewClass' in str(w[0].message)
""",
        {"ok": True, "value": True},
    ),
    (
        "class-with-version",
        """
import warnings
from deprecated import deprecated

@deprecated(version="3.0.0")
class OldClass:
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = OldClass()
    
result = '3.0.0' in str(w[0].message)
""",
        {"ok": True, "value": True},
    ),
    (
        "class-custom-category",
        """
import warnings
from deprecated import deprecated

class MyDepWarning(DeprecationWarning):
    pass

@deprecated(category=MyDepWarning)
class OldClass:
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = OldClass()
    
result = issubclass(w[0].category, MyDepWarning)
""",
        {"ok": True, "value": True},
    ),
    # Method deprecation
    (
        "method-basic-warning",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @deprecated
    def old_method(self):
        return 10

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = MyClass()
    r = obj.old_method()
    
result = [r, len(w), 'deprecated' in str(w[0].message).lower()]
""",
        {"ok": True, "value": [10, 1, True]},
    ),
    (
        "method-with-reason",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @deprecated(reason="use new_method")
    def old_method(self):
        return "result"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = MyClass()
    r = obj.old_method()
    
result = ['use new_method' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, "result"]},
    ),
    (
        "method-with-version",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @deprecated(version="1.5.0")
    def old_method(self):
        return 42

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = MyClass()
    r = obj.old_method()
    
result = ['1.5.0' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, 42]},
    ),
    # Static method deprecation
    (
        "staticmethod-basic-warning",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @staticmethod
    @deprecated
    def old_static():
        return "static"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = MyClass.old_static()
    
result = [r, len(w), 'deprecated' in str(w[0].message).lower()]
""",
        {"ok": True, "value": ["static", 1, True]},
    ),
    (
        "staticmethod-with-reason",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @staticmethod
    @deprecated(reason="not needed")
    def old_static():
        return 123

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = MyClass.old_static()
    
result = ['not needed' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, 123]},
    ),
    # Class method deprecation
    (
        "classmethod-basic-warning",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @classmethod
    @deprecated
    def old_classmethod(cls):
        return "clsmethod"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = MyClass.old_classmethod()
    
result = [r, len(w)]
""",
        {"ok": True, "value": ["clsmethod", 1]},
    ),
    (
        "classmethod-with-version",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @classmethod
    @deprecated(version="2.1.0")
    def old_classmethod(cls):
        return 77

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = MyClass.old_classmethod()
    
result = ['2.1.0' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, 77]},
    ),
    # String reason shorthand
    (
        "function-string-reason-shorthand",
        """
import warnings
from deprecated import deprecated

@deprecated("this is old")
def old_func():
    return "ok"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = ['this is old' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, "ok"]},
    ),
    # Sphinx decorators - versionadded
    (
        "sphinx-versionadded-basic",
        """
from deprecated.sphinx import versionadded

@versionadded(version="1.0.0")
def new_func():
    '''A function.'''
    return 1

result = ['.. versionadded:: 1.0.0' in new_func.__doc__, new_func()]
""",
        {"ok": True, "value": [True, 1]},
    ),
    (
        "sphinx-versionadded-with-reason",
        """
from deprecated.sphinx import versionadded

@versionadded(reason="Initial implementation", version="1.0.0")
def new_func():
    '''A function.'''
    return 2

result = ['Initial implementation' in new_func.__doc__, new_func()]
""",
        {"ok": True, "value": [True, 2]},
    ),
    (
        "sphinx-versionadded-no-warning",
        """
import warnings
from deprecated.sphinx import versionadded

@versionadded(version="1.0.0")
def new_func():
    return 3

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = new_func()
    
result = [len(w), r]
""",
        {"ok": True, "value": [0, 3]},
    ),
    # Sphinx versionchanged
    (
        "sphinx-versionchanged-basic",
        """
from deprecated.sphinx import versionchanged

@versionchanged(version="2.0.0")
def changed_func():
    '''A function.'''
    return 4

result = ['.. versionchanged:: 2.0.0' in changed_func.__doc__, changed_func()]
""",
        {"ok": True, "value": [True, 4]},
    ),
    (
        "sphinx-versionchanged-with-reason",
        """
from deprecated.sphinx import versionchanged

@versionchanged(reason="Changed behavior", version="2.0.0")
def changed_func():
    '''A function.'''
    return 5

result = ['Changed behavior' in changed_func.__doc__, changed_func()]
""",
        {"ok": True, "value": [True, 5]},
    ),
    (
        "sphinx-versionchanged-no-warning",
        """
import warnings
from deprecated.sphinx import versionchanged

@versionchanged(version="2.0.0")
def changed_func():
    return 6

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = changed_func()
    
result = [len(w), r]
""",
        {"ok": True, "value": [0, 6]},
    ),
    # Sphinx deprecated
    (
        "sphinx-deprecated-basic",
        """
import warnings
from deprecated.sphinx import deprecated

@deprecated(version="1.0.0")
def old_func():
    '''A function.'''
    return 7

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = ['.. deprecated:: 1.0.0' in old_func.__doc__, len(w), r]
""",
        {"ok": True, "value": [True, 1, 7]},
    ),
    (
        "sphinx-deprecated-with-reason",
        """
import warnings
from deprecated.sphinx import deprecated

@deprecated(reason="Use another function", version="1.5.0")
def old_func():
    '''A function.'''
    return 8

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = ['Use another function' in old_func.__doc__, '1.5.0' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, True, 8]},
    ),
    (
        "sphinx-deprecated-warning-emitted",
        """
import warnings
from deprecated.sphinx import deprecated

@deprecated(version="2.0.0")
def old_func():
    return 9

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = old_func()
    
result = [len(w), '2.0.0' in str(w[0].message), r]
""",
        {"ok": True, "value": [1, True, 9]},
    ),
    (
        "sphinx-deprecated-class",
        """
import warnings
from deprecated.sphinx import deprecated

@deprecated(version="1.0.0")
class OldClass:
    '''A class.'''
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = OldClass()
    
result = ['.. deprecated:: 1.0.0' in OldClass.__doc__, len(w)]
""",
        {"ok": True, "value": [True, 1]},
    ),
    # Sphinx version requirement
    (
        "sphinx-deprecated-requires-version",
        """
from deprecated.sphinx import deprecated

try:
    @deprecated()
    def func():
        pass
    result = False
except ValueError:
    result = True
""",
        {"ok": True, "value": True},
    ),
    (
        "sphinx-versionadded-requires-version",
        """
from deprecated.sphinx import versionadded

try:
    @versionadded()
    def func():
        pass
    result = False
except ValueError:
    result = True
""",
        {"ok": True, "value": True},
    ),
    (
        "sphinx-versionchanged-requires-version",
        """
from deprecated.sphinx import versionchanged

try:
    @versionchanged()
    def func():
        pass
    result = False
except ValueError:
    result = True
""",
        {"ok": True, "value": True},
    ),
    # deprecated_params - basic usage
    (
        "params-single-param",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params("old_param")
def func(old_param=None, new_param=None):
    return new_param or old_param

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(old_param=5)
    
result = [len(w), 'old_param' in str(w[0].message), r]
""",
        {"ok": True, "value": [1, True, 5]},
    ),
    (
        "params-single-param-no-warning-if-not-used",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params("old_param")
def func(old_param=None, new_param=None):
    return new_param or old_param

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(new_param=10)
    
result = [len(w), r]
""",
        {"ok": True, "value": [0, 10]},
    ),
    (
        "params-custom-reason",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params("x", reason="use y instead")
def func(x=None, y=None):
    return x or y

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(x=7)
    
result = ['use y instead' in str(w[0].message), r]
""",
        {"ok": True, "value": [True, 7]},
    ),
    (
        "params-dict-multiple",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params({"a": "a is old", "b": "b is old"})
def func(a=None, b=None, c=None):
    return (a or 0) + (b or 0) + (c or 0)

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(a=1, b=2)
    
result = [len(w), r]
""",
        {"ok": True, "value": [2, 3]},
    ),
    (
        "params-dict-partial-use",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params({"a": "a is deprecated", "b": "b is deprecated"})
def func(a=None, b=None):
    return (a or 0) + (b or 0)

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(a=5)
    
result = [len(w), 'a is deprecated' in str(w[0].message), r]
""",
        {"ok": True, "value": [1, True, 5]},
    ),
    (
        "params-custom-category",
        """
import warnings
from deprecated import deprecated_params

class MyWarning(DeprecationWarning):
    pass

@deprecated_params("old", category=MyWarning)
def func(old=None):
    return old

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(old=99)
    
result = [issubclass(w[0].category, MyWarning), r]
""",
        {"ok": True, "value": [True, 99]},
    ),
    # Multiple calls and idempotency
    (
        "function-multiple-calls",
        """
import warnings
from deprecated import deprecated

@deprecated
def func():
    return 1

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r1 = func()
    r2 = func()
    r3 = func()
    
result = [len(w), r1, r2, r3]
""",
        {"ok": True, "value": [3, 1, 1, 1]},
    ),
    (
        "class-multiple-instantiations",
        """
import warnings
from deprecated import deprecated

@deprecated
class OldClass:
    def __init__(self, val):
        self.val = val

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    o1 = OldClass(1)
    o2 = OldClass(2)
    
result = [len(w), o1.val, o2.val]
""",
        {"ok": True, "value": [2, 1, 2]},
    ),
    # Function with arguments
    (
        "function-with-args",
        """
import warnings
from deprecated import deprecated

@deprecated
def add(a, b):
    return a + b

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = add(3, 4)
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, 7]},
    ),
    (
        "function-with-kwargs",
        """
import warnings
from deprecated import deprecated

@deprecated
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = greet("World", greeting="Hi")
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, "Hi, World"]},
    ),
    (
        "method-with-args",
        """
import warnings
from deprecated import deprecated

class Calculator:
    @deprecated
    def multiply(self, x, y):
        return x * y

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    calc = Calculator()
    r = calc.multiply(5, 6)
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, 30]},
    ),
    # Edge cases
    (
        "function-no-docstring",
        """
import warnings
from deprecated import deprecated

@deprecated
def func():
    return "no doc"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func()
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, "no doc"]},
    ),
    (
        "class-with-init-args",
        """
import warnings
from deprecated import deprecated

@deprecated
class OldClass:
    def __init__(self, x, y):
        self.sum = x + y

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = OldClass(10, 20)
    
result = [len(w), obj.sum]
""",
        {"ok": True, "value": [1, 30]},
    ),
    (
        "nested-decorators",
        """
import warnings
from deprecated import deprecated

def other_decorator(f):
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

@other_decorator
@deprecated
def func():
    return "nested"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func()
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, "nested"]},
    ),
    # Message content verification
    (
        "message-contains-function-name",
        """
import warnings
from deprecated import deprecated

@deprecated
def my_special_function():
    return 1

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    my_special_function()
    
result = 'my_special_function' in str(w[0].message)
""",
        {"ok": True, "value": True},
    ),
    (
        "message-contains-class-name",
        """
import warnings
from deprecated import deprecated

@deprecated
class MySpecialClass:
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    MySpecialClass()
    
result = 'MySpecialClass' in str(w[0].message)
""",
        {"ok": True, "value": True},
    ),
    (
        "message-contains-method-name",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @deprecated
    def my_special_method(self):
        return 1

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = MyClass()
    obj.my_special_method()
    
result = 'my_special_method' in str(w[0].message)
""",
        {"ok": True, "value": True},
    ),
    # Sphinx line_length parameter
    (
        "sphinx-line-length-respected",
        """
from deprecated.sphinx import deprecated

long_reason = "This is a very long deprecation reason that should be wrapped into multiple lines when the line_length parameter is properly respected by the decorator implementation."

@deprecated(reason=long_reason, version="1.0.0", line_length=70)
def func():
    '''Original doc.'''
    return 1

# Check that docstring is modified and contains wrapped text
result = ['.. deprecated:: 1.0.0' in func.__doc__, 'long deprecation reason' in func.__doc__, func()]
""",
        {"ok": True, "value": [True, True, 1]},
    ),
    # Import paths
    (
        "import-from-main",
        """
from deprecated import deprecated
result = callable(deprecated)
""",
        {"ok": True, "value": True},
    ),
    (
        "import-from-classic",
        """
from deprecated.classic import deprecated
result = callable(deprecated)
""",
        {"ok": True, "value": True},
    ),
    (
        "import-from-sphinx",
        """
from deprecated.sphinx import deprecated, versionadded, versionchanged
result = [callable(deprecated), callable(versionadded), callable(versionchanged)]
""",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "import-deprecated-params",
        """
from deprecated import deprecated_params
result = callable(deprecated_params)
""",
        {"ok": True, "value": True},
    ),
    # Action parameter variants
    (
        "action-default",
        """
import warnings
from deprecated import deprecated

@deprecated(action="default")
def func():
    return 1

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func()
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, 1]},
    ),
    (
        "action-module",
        """
import warnings
from deprecated import deprecated

@deprecated(action="module")
def func():
    return 2

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("default")
    r1 = func()
    r2 = func()
    
result = [len(w), r1, r2]
""",
        {"ok": True, "value": [2, 2, 2]},
    ),
    # Return value preservation
    (
        "function-return-value-preserved",
        """
import warnings
from deprecated import deprecated

@deprecated
def get_data():
    return {"key": "value", "num": 42}

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = get_data()
    
result = [r["key"], r["num"], len(w)]
""",
        {"ok": True, "value": ["value", 42, 1]},
    ),
    (
        "method-return-value-preserved",
        """
import warnings
from deprecated import deprecated

class DataProvider:
    @deprecated
    def get_list(self):
        return [1, 2, 3, 4, 5]

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    dp = DataProvider()
    r = dp.get_list()
    
result = [len(r), sum(r), len(w)]
""",
        {"ok": True, "value": [5, 15, 1]},
    ),
    # Exception propagation
    (
        "function-exception-propagated",
        """
import warnings
from deprecated import deprecated

@deprecated
def failing_func():
    raise ValueError("intentional error")

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    try:
        failing_func()
        result = False
    except ValueError as e:
        result = [len(w), "intentional error" in str(e)]
""",
        {"ok": True, "value": [1, True]},
    ),
    (
        "method-exception-propagated",
        """
import warnings
from deprecated import deprecated

class MyClass:
    @deprecated
    def failing_method(self):
        raise RuntimeError("method error")

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    obj = MyClass()
    try:
        obj.failing_method()
        result = False
    except RuntimeError as e:
        result = [len(w), "method error" in str(e)]
""",
        {"ok": True, "value": [1, True]},
    ),
    # Sphinx docstring preservation
    (
        "sphinx-preserves-existing-docstring",
        """
from deprecated.sphinx import deprecated

@deprecated(version="1.0.0")
def func():
    '''This is the original documentation.
    
    It has multiple lines.
    '''
    return 1

result = ['original documentation' in func.__doc__, '.. deprecated:: 1.0.0' in func.__doc__, func()]
""",
        {"ok": True, "value": [True, True, 1]},
    ),
    (
        "sphinx-empty-docstring-handled",
        """
from deprecated.sphinx import deprecated

@deprecated(version="1.0.0")
def func():
    return 2

result = ['.. deprecated:: 1.0.0' in func.__doc__, func()]
""",
        {"ok": True, "value": [True, 2]},
    ),
    # Category inheritance
    (
        "category-is-deprecationwarning",
        """
import warnings
from deprecated import deprecated

@deprecated(category=DeprecationWarning)
def func():
    pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    func()
    
result = w[0].category == DeprecationWarning
""",
        {"ok": True, "value": True},
    ),
    (
        "category-futurewarning",
        """
import warnings
from deprecated import deprecated

@deprecated(category=FutureWarning)
def func():
    return 3

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func()
    
result = [w[0].category == FutureWarning, r]
""",
        {"ok": True, "value": [True, 3]},
    ),
    (
        "category-pendingdeprecationwarning",
        """
import warnings
from deprecated import deprecated

@deprecated(category=PendingDeprecationWarning)
def func():
    return 4

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func()
    
result = [w[0].category == PendingDeprecationWarning, r]
""",
        {"ok": True, "value": [True, 4]},
    ),
    # params edge cases
    (
        "params-positional-arg",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params("x")
def func(x):
    return x * 2

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(5)
    
result = [len(w), 'x' in str(w[0].message), r]
""",
        {"ok": True, "value": [1, True, 10]},
    ),
    (
        "params-keyword-arg",
        """
import warnings
from deprecated import deprecated_params

@deprecated_params("y")
def func(x, y=None):
    return x + (y or 0)

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    r = func(10, y=5)
    
result = [len(w), r]
""",
        {"ok": True, "value": [1, 15]},
    ),
    # Combination scenarios
    (
        "function-all-params",
        """
import warnings
from deprecated import deprecated

@deprecated(reason="obsolete", version="1.0.0", action="always", category=FutureWarning)
def func():
    return "result"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("default")
    r = func()
    
result = ['obsolete' in str(w[0].message), '1.0.0' in str(w[0].message), w[0].category == FutureWarning, r]
""",
        {"ok": True, "value": [True, True, True, "result"]},
    ),
    (
        "sphinx-all-params",
        """
import warnings
from deprecated.sphinx import deprecated

@deprecated(reason="will be removed", version="2.0.0", action="always", category=FutureWarning, line_length=80)
def func():
    '''Original.'''
    return "data"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("default")
    r = func()
    
result = ['will be removed' in func.__doc__, '2.0.0' in str(w[0].message), w[0].category == FutureWarning, r]
""",
        {"ok": True, "value": [True, True, True, "data"]},
    ),
]

assert len(CASES) == 71, f"Expected 71 test cases, got {len(CASES)}"


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
