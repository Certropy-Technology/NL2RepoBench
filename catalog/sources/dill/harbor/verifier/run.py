#!/usr/bin/env python3
"""
Verifier for dill task - custom-json-v1 protocol
Tests dill's extended pickle serialization capabilities
"""
import json
import sys

# Import the candidate execution client
from nl2repobench.verification.candidate_client import execute_script

# Test scenarios: (id, script, expected)
CASES = [
    # 1. Basic lambda serialization
    ("lambda_basic", """
import dill
f = lambda x: x * 2
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 10}),

    # 2. Lambda with closure
    ("lambda_closure", """
import dill
def make_multiplier(n):
    return lambda x: x * n
f = make_multiplier(3)
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(4)
""", {"ok": True, "value": 12}),

    # 3. Nested function
    ("nested_function", """
import dill
def outer(a):
    def inner(b):
        return a + b
    return inner
f = outer(10)
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 15}),

    # 4. Simple object dumps/loads
    ("simple_dict", """
import dill
data = {'a': 1, 'b': 2, 'c': [3, 4, 5]}
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored == data
""", {"ok": True, "value": True}),

    # 5. List serialization
    ("list_serialization", """
import dill
data = [1, 2, 3, [4, 5], {'key': 'value'}]
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored == data
""", {"ok": True, "value": True}),

    # 6. Set serialization
    ("set_serialization", """
import dill
data = {1, 2, 3, 4, 5}
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = sorted(list(restored))
""", {"ok": True, "value": [1, 2, 3, 4, 5]}),

    # 7. Tuple serialization
    ("tuple_serialization", """
import dill
data = (1, 2, 'hello', (3, 4))
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored == data
""", {"ok": True, "value": True}),

    # 8. Class with __init__
    ("simple_class", """
import dill
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def distance(self):
        return (self.x**2 + self.y**2)**0.5
p = Point(3, 4)
serialized = dill.dumps(p)
restored = dill.loads(serialized)
result = restored.distance()
""", {"ok": True, "value": 5.0}),

    # 9. Dataclass
    ("dataclass_serialization", """
import dill
from dataclasses import dataclass
@dataclass
class Person:
    name: str
    age: int
p = Person('Alice', 30)
serialized = dill.dumps(p)
restored = dill.loads(serialized)
result = (restored.name, restored.age)
""", {"ok": True, "value": ["Alice", 30]}),

    # 10. Function with default arguments
    ("function_defaults", """
import dill
def greet(name, greeting='Hello'):
    return f'{greeting}, {name}!'
serialized = dill.dumps(greet)
restored = dill.loads(serialized)
result = restored('World')
""", {"ok": True, "value": "Hello, World!"}),

    # 11. dill.dump and dill.load with file-like object
    ("dump_load_fileobj", """
import dill
import io
data = {'key': 'value', 'number': 42}
buffer = io.BytesIO()
dill.dump(data, buffer)
buffer.seek(0)
restored = dill.load(buffer)
result = restored == data
""", {"ok": True, "value": True}),

    # 12. Multiple objects in sequence
    ("multiple_objects", """
import dill
import io
obj1 = [1, 2, 3]
obj2 = {'a': 1, 'b': 2}
obj3 = (4, 5, 6)
buffer = io.BytesIO()
dill.dump(obj1, buffer)
dill.dump(obj2, buffer)
dill.dump(obj3, buffer)
buffer.seek(0)
r1 = dill.load(buffer)
r2 = dill.load(buffer)
r3 = dill.load(buffer)
result = (r1 == obj1 and r2 == obj2 and r3 == obj3)
""", {"ok": True, "value": True}),

    # 13. Lambda with multiple arguments
    ("lambda_multi_args", """
import dill
f = lambda x, y, z: x + y * z
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(2, 3, 4)
""", {"ok": True, "value": 14}),

    # 14. Nested lambda
    ("nested_lambda", """
import dill
f = lambda x: (lambda y: x + y)
g = f(10)
serialized = dill.dumps(g)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 15}),

    # 15. Class method
    ("class_method", """
import dill
class Calculator:
    def add(self, a, b):
        return a + b
calc = Calculator()
serialized = dill.dumps(calc.add)
restored = dill.loads(serialized)
result = restored(3, 5)
""", {"ok": True, "value": 8}),

    # 16. Staticmethod
    ("static_method", """
import dill
class MathUtils:
    @staticmethod
    def square(x):
        return x * x
serialized = dill.dumps(MathUtils.square)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 25}),

    # 17. Generator function
    ("generator_function", """
import dill
def count_up_to(n):
    for i in range(n):
        yield i
serialized = dill.dumps(count_up_to)
restored = dill.loads(serialized)
result = list(restored(5))
""", {"ok": True, "value": [0, 1, 2, 3, 4]}),

    # 18. Function with *args
    ("function_args", """
import dill
def sum_all(*args):
    return sum(args)
serialized = dill.dumps(sum_all)
restored = dill.loads(serialized)
result = restored(1, 2, 3, 4, 5)
""", {"ok": True, "value": 15}),

    # 19. Function with **kwargs
    ("function_kwargs", """
import dill
def make_dict(**kwargs):
    return dict(kwargs)
serialized = dill.dumps(make_dict)
restored = dill.loads(serialized)
result = restored(a=1, b=2, c=3)
""", {"ok": True, "value": {"a": 1, "b": 2, "c": 3}}),

    # 20. Bytes serialization
    ("bytes_serialization", """
import dill
data = b'hello world'
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored.hex()
""", {"ok": True, "value": "68656c6c6f20776f726c64"}),

    # 21. None serialization
    ("none_serialization", """
import dill
data = None
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored is None
""", {"ok": True, "value": True}),

    # 22. Boolean serialization
    ("boolean_serialization", """
import dill
data = (True, False)
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": [True, False]}),

    # 23. Float serialization
    ("float_serialization", """
import dill
data = 3.14159
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = abs(restored - data) < 1e-10
""", {"ok": True, "value": True}),

    # 24. Complex number
    ("complex_serialization", """
import dill
data = 3 + 4j
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored == data
""", {"ok": True, "value": True}),

    # 25. Nested dictionary
    ("nested_dict", """
import dill
data = {'a': {'b': {'c': 123}}}
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored['a']['b']['c']
""", {"ok": True, "value": 123}),

    # 26. List comprehension function
    ("list_comp_func", """
import dill
def squares(n):
    return [x**2 for x in range(n)]
serialized = dill.dumps(squares)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": [0, 1, 4, 9, 16]}),

    # 27. Dictionary comprehension function
    ("dict_comp_func", """
import dill
def make_square_dict(n):
    return {x: x**2 for x in range(n)}
serialized = dill.dumps(make_square_dict)
restored = dill.loads(serialized)
result = restored(3)
""", {"ok": True, "value": {"0": 0, "1": 1, "2": 4}}),

    # 28. Class with property
    ("class_with_property", """
import dill
class Circle:
    def __init__(self, radius):
        self.radius = radius
    @property
    def area(self):
        return 3.14159 * self.radius ** 2
c = Circle(5)
serialized = dill.dumps(c)
restored = dill.loads(serialized)
result = abs(restored.area - 78.53975) < 0.001
""", {"ok": True, "value": True}),

    # 29. Frozenset
    ("frozenset_serialization", """
import dill
data = frozenset([1, 2, 3, 4, 5])
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = sorted(list(restored))
""", {"ok": True, "value": [1, 2, 3, 4, 5]}),

    # 30. Empty collections
    ("empty_collections", """
import dill
data = ([], {}, set())
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = (restored[0] == [] and restored[1] == {} and restored[2] == set())
""", {"ok": True, "value": True}),

    # 31. Function with nested scopes
    ("nested_scopes", """
import dill
def outer(x):
    def middle(y):
        def inner(z):
            return x + y + z
        return inner
    return middle
f = outer(1)(2)
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(3)
""", {"ok": True, "value": 6}),

    # 32. Recursive function with recurse=True
    ("recursive_function", """
import dill
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
serialized = dill.dumps(factorial, recurse=True)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 120}),

    # 33. Class with __str__
    ("class_str", """
import dill
class Person:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f'Person({self.name})'
p = Person('Bob')
serialized = dill.dumps(p)
restored = dill.loads(serialized)
result = str(restored)
""", {"ok": True, "value": "Person(Bob)"}),

    # 34. Class with __repr__
    ("class_repr", """
import dill
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f'Point({self.x}, {self.y})'
p = Point(1, 2)
serialized = dill.dumps(p)
restored = dill.loads(serialized)
result = repr(restored)
""", {"ok": True, "value": "Point(1, 2)"}),

    # 35. Exception instance
    ("exception_serialization", """
import dill
exc = ValueError('test error')
serialized = dill.dumps(exc)
restored = dill.loads(serialized)
result = (type(restored).__name__, str(restored))
""", {"ok": True, "value": ["ValueError", "test error"]}),

    # 36. Lambda with keyword argument
    ("lambda_kwargs", """
import dill
f = lambda x, y=10: x + y
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 15}),

    # 37. Function returning lambda
    ("function_returning_lambda", """
import dill
def make_adder(n):
    return lambda x: x + n
f = make_adder(7)
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored(3)
""", {"ok": True, "value": 10}),

    # 38. Instance counter (check instance id only)
    ("instance_id", """
import dill
class Item:
    def __init__(self, value):
        self.value = value
item = Item(42)
serialized = dill.dumps(item)
restored = dill.loads(serialized)
result = restored.value
""", {"ok": True, "value": 42}),

    # 39. String with special characters
    ("string_special_chars", """
import dill
data = 'Hello\\nWorld\\t!'
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": "Hello\nWorld\t!"}),

    # 40. Unicode string
    ("unicode_string", """
import dill
data = 'Hello 世界 🌍'
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": "Hello 世界 🌍"}),

    # 41. Large integer
    ("large_integer", """
import dill
data = 123456789012345678901234567890
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": 123456789012345678901234567890}),

    # 42. Negative number
    ("negative_number", """
import dill
data = -42
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": -42}),

    # 43. Zero
    ("zero_serialization", """
import dill
data = 0
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": 0}),

    # 44. Function with docstring
    ("function_docstring", """
import dill
def documented_func(x):
    \"\"\"This function doubles its input.\"\"\"
    return x * 2
serialized = dill.dumps(documented_func)
restored = dill.loads(serialized)
result = (restored(5), restored.__doc__)
""", {"ok": True, "value": [10, "This function doubles its input."]}),

    # 45. Empty string
    ("empty_string", """
import dill
data = ''
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": ""}),

    # 46. Single character
    ("single_char", """
import dill
data = 'x'
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": "x"}),

    # 47. Mixed type list
    ("mixed_list", """
import dill
data = [1, 'two', 3.0, None, True]
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": [1, "two", 3.0, None, True]}),

    # 48. Nested list
    ("nested_list", """
import dill
data = [[1, 2], [3, 4], [5, [6, 7]]]
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored
""", {"ok": True, "value": [[1, 2], [3, 4], [5, [6, 7]]]}),

    # 49. Dictionary with various key types
    ("dict_various_keys", """
import dill
data = {1: 'one', 'two': 2, (3, 4): 'tuple'}
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = (restored[1], restored['two'], restored[(3, 4)])
""", {"ok": True, "value": ["one", 2, "tuple"]}),

    # 50. Class with __eq__
    ("class_eq", """
import dill
class Value:
    def __init__(self, val):
        self.val = val
    def __eq__(self, other):
        return isinstance(other, Value) and self.val == other.val
v = Value(42)
serialized = dill.dumps(v)
restored = dill.loads(serialized)
result = restored.val
""", {"ok": True, "value": 42}),

    # 51. Lambda with no arguments
    ("lambda_no_args", """
import dill
f = lambda: 42
serialized = dill.dumps(f)
restored = dill.loads(serialized)
result = restored()
""", {"ok": True, "value": 42}),

    # 52. Function with multiple return values
    ("multiple_returns", """
import dill
def divmod_custom(a, b):
    return a // b, a % b
serialized = dill.dumps(divmod_custom)
restored = dill.loads(serialized)
result = restored(17, 5)
""", {"ok": True, "value": [3, 2]}),

    # 53. Class with multiple methods
    ("class_multiple_methods", """
import dill
class Math:
    def add(self, a, b):
        return a + b
    def multiply(self, a, b):
        return a * b
m = Math()
serialized = dill.dumps(m)
restored = dill.loads(serialized)
result = (restored.add(2, 3), restored.multiply(2, 3))
""", {"ok": True, "value": [5, 6]}),

    # 54. Slice object
    ("slice_serialization", """
import dill
s = slice(1, 10, 2)
serialized = dill.dumps(s)
restored = dill.loads(serialized)
result = list(range(20))[restored]
""", {"ok": True, "value": [1, 3, 5, 7, 9]}),

    # 55. Range object
    ("range_serialization", """
import dill
r = range(5, 15, 2)
serialized = dill.dumps(r)
restored = dill.loads(serialized)
result = list(restored)
""", {"ok": True, "value": [5, 7, 9, 11, 13]}),

    # 56. Enumerate result
    ("enumerate_function", """
import dill
def enumerate_list(items):
    return list(enumerate(items))
serialized = dill.dumps(enumerate_list)
restored = dill.loads(serialized)
result = restored(['a', 'b', 'c'])
""", {"ok": True, "value": [[0, "a"], [1, "b"], [2, "c"]]}),

    # 57. Filter function
    ("filter_function", """
import dill
def filter_evens(nums):
    return list(filter(lambda x: x % 2 == 0, nums))
serialized = dill.dumps(filter_evens)
restored = dill.loads(serialized)
result = restored([1, 2, 3, 4, 5, 6])
""", {"ok": True, "value": [2, 4, 6]}),

    # 58. Map function
    ("map_function", """
import dill
def double_all(nums):
    return list(map(lambda x: x * 2, nums))
serialized = dill.dumps(double_all)
restored = dill.loads(serialized)
result = restored([1, 2, 3])
""", {"ok": True, "value": [2, 4, 6]}),

    # 59. Zip function
    ("zip_function", """
import dill
def zip_lists(a, b):
    return list(zip(a, b))
serialized = dill.dumps(zip_lists)
restored = dill.loads(serialized)
result = restored([1, 2, 3], ['a', 'b', 'c'])
""", {"ok": True, "value": [[1, "a"], [2, "b"], [3, "c"]]}),

    # 60. Class with __call__
    ("class_callable", """
import dill
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, x):
        return x * self.factor
m = Multiplier(5)
serialized = dill.dumps(m)
restored = dill.loads(serialized)
result = restored(7)
""", {"ok": True, "value": 35}),

    # 61. Partial function
    ("partial_function", """
import dill
from functools import partial
def power(base, exp):
    return base ** exp
square = partial(power, exp=2)
serialized = dill.dumps(square)
restored = dill.loads(serialized)
result = restored(5)
""", {"ok": True, "value": 25}),

    # 62. Decorated function with recurse
    ("decorated_function", """
import dill
def double_result(f):
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs) * 2
    return wrapper
@double_result
def add(a, b):
    return a + b
serialized = dill.dumps(add, recurse=True)
restored = dill.loads(serialized)
result = restored(3, 4)
""", {"ok": True, "value": 14}),

    # 63. Class inheritance
    ("class_inheritance", """
import dill
class Animal:
    def speak(self):
        return 'sound'
class Dog(Animal):
    def speak(self):
        return 'bark'
d = Dog()
serialized = dill.dumps(d)
restored = dill.loads(serialized)
result = restored.speak()
""", {"ok": True, "value": "bark"}),

    # 64. Multiple inheritance
    ("multiple_inheritance", """
import dill
class A:
    def method_a(self):
        return 'A'
class B:
    def method_b(self):
        return 'B'
class C(A, B):
    pass
c = C()
serialized = dill.dumps(c)
restored = dill.loads(serialized)
result = (restored.method_a(), restored.method_b())
""", {"ok": True, "value": ["A", "B"]}),

    # 65. Custom iterator
    ("custom_iterator", """
import dill
class Counter:
    def __init__(self, max):
        self.max = max
        self.current = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.current < self.max:
            self.current += 1
            return self.current
        raise StopIteration
c = Counter(3)
serialized = dill.dumps(c)
restored = dill.loads(serialized)
result = list(restored)
""", {"ok": True, "value": [1, 2, 3]}),

    # 66. Nested dataclass with recurse
    ("nested_dataclass", """
import dill
from dataclasses import dataclass
@dataclass
class Address:
    street: str
    city: str
@dataclass
class Person:
    name: str
    address: Address
p = Person('Alice', Address('123 Main', 'NYC'))
serialized = dill.dumps(p, recurse=True)
restored = dill.loads(serialized)
result = (restored.name, restored.address.city)
""", {"ok": True, "value": ["Alice", "NYC"]}),

    # 67. Set operations
    ("set_operations", """
import dill
def set_union(a, b):
    return sorted(list(a.union(b)))
serialized = dill.dumps(set_union)
restored = dill.loads(serialized)
result = restored({1, 2, 3}, {3, 4, 5})
""", {"ok": True, "value": [1, 2, 3, 4, 5]}),

    # 68. Dictionary with nested structure
    ("dict_nested_structure", """
import dill
data = {
    'users': [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25}
    ],
    'count': 2
}
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = restored['users'][1]['name']
""", {"ok": True, "value": "Bob"}),

    # 69. Function with annotations
    ("function_annotations", """
import dill
def add_typed(a: int, b: int) -> int:
    return a + b
serialized = dill.dumps(add_typed)
restored = dill.loads(serialized)
result = restored(5, 7)
""", {"ok": True, "value": 12}),

    # 70. bytearray
    ("bytearray_serialization", """
import dill
data = bytearray(b'hello')
serialized = dill.dumps(data)
restored = dill.loads(serialized)
result = bytes(restored).hex()
""", {"ok": True, "value": "68656c6c6f"}),
]

def main():
    """Main verifier entry point - custom-json-v1 protocol"""
    results = []
    
    for test_id, script, expected in CASES:
        # Execute the scenario using candidate client
        actual = execute_script(script)
        
        # Compare actual with expected
        if actual == expected:
            status = "passed"
        else:
            status = "failed"
        
        results.append({
            "id": test_id,
            "status": status
        })
    
    # Output final JSON result (LAST line of stdout)
    output = {
        "schema_version": "1.0",
        "leaves": results
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
