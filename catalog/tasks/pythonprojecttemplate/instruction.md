# pythonprojecttemplate

## Project Description

Build an installable `pythonprojecttemplate` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pythonprojecttemplate`; public import package begins at `fastvector`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Core API`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `1. Module Import`: preserve the documented object or module behavior, including state and side effects.
3. `2. Vector2D Class - Two-dimensional Vector Creation`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `3. Vector Addition Operation - __add__ Method`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `pythonprojecttemplate`; public import package begins at `fastvector`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `setuptools==80.10.2`, `wheel==0.45.1`, `numpy==2.2.6`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── codecov.yml
├── docs
│   ├── api.md
│   ├── index.md
├── examples
│   ├── main.py
├── fastvector
│   ├── __init__.py
│   ├── vector.py
│   ├── version.py
├── mkdocs.yml
└── pyproject.toml
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### Core API

#### 1. Module Import

```python
from fastvector import Vector2D
```

#### 2. Vector2D Class - Two-dimensional Vector Creation

**Function**：Create and initialize a two-dimensional vector object.

**Class Signature**：
```python
@total_ordering
class Vector2D:
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Create a instance with the given x and y values.

        Args:
            x: x-Value.
            y: y-Value.

        Raises:
            TypeError: If x or y are not a number.
        """
```

**Parameter Description**：
- `x` (float): x coordinate component, must be a numeric type
- `y` (float): y coordinate component, must be a numeric type

**Return Value**：Vector2D instance

#### 3. Vector Addition Operation - __add__ Method

**Function**：Implement vector addition.

**Method Signature**：
```python
def __add__(self, other_vector: Vector2D) -> Vector2D:
    """Returns the addition vector of the self and the other instance.

        Args:
            other_vector: Other instance (rhs of the operator).

        Returns:
            The addition vector of the self and the other instance.
    """
```

**Parameter Description**：
- `other_vector`: Another Vector2D vector

**Return Value**：New Vector2D instance, representing the sum of two vectors

#### 4. Vector Subtraction Operation - __sub__ Method

**Function**：Implement vector subtraction.

**Method Signature**：
```python
def __sub__(self, other_vector: Vector2D) -> Vector2D:
    """Return the subtraction vector of the self and the other instance.

        Args:
            other_vector: Other instance (rhs of the operator).

        Returns:
            The subtraction vector of the self and the other instance.
    """
```

**Parameter Description**：
- `other_vector`: Another Vector2D vector

**Return Value**：New Vector2D instance, representing the difference between two vectors

#### 5. Vector Multiplication Operation - __mul__ Method

**Function**：Implement vector multiplication, including dot product and scalar multiplication.

**Method Signature**：
```python
def __mul__(self, other: Vector2D | float) -> float | Vector2D:
    """Return the multiplication of self and left vector or number.

    Args:
        other: Other instance or scaler value (rhs of the operator)

    Raises:
        TypeError: Not int/float passed in.

    Returns:
        The multiplication of self and left vector or number.
    """
```

**Parameter Description**：
- `other`: Another Vector2D vector (dot product) or scalar (scalar multiplication)

**Return Value**：
- Vector × Vector: Returns scalar (dot product)
- Vector × Scalar: Returns Vector2D (scalar multiplication)

#### 6. Vector Division Operation - __truediv__ Method

**Function**：Implement vector division by a scalar.

**Method Signature**：
```python
def __truediv__(self, other: float) -> Vector2D:
    """Return the multiplication of self and left vector or number.

    Args:
        other: Other instance or scaler value (rhs of the operator).

    Raises:
        ValueError: Division by zero.
        TypeError: Not int/float passed in.

    Returns:
        The multiplication of self and left vector or number.
    """
```

**Parameter Description**：
- `other`: Scalar divisor

**Return Value**：New Vector2D instance, representing the result of vector division by scalar

#### 7. Vector Magnitude Calculation - __abs__ Method

**Function**：Calculate the magnitude (length) of a vector.

**Method Signature**：
```python
def __abs__(self) -> float:
    """Return the length (magnitude) of the instance.

    Returns:
        Length of the instance.
    """
```

**Return Value**：Float, representing the magnitude of the vector

#### 8. Vector Comparison Operations - __eq__, __lt__ etc.

**Function**：Implement vector comparison operations.

**Method Signature**：
```python
def __eq__(self, other_vector: object) -> bool:
    """Check if the instances have the same values.

    Args:
        other_vector: Other instance (rhs of the operator)

    Returns:
        True, if the both instances have the same values.
        False, else.
    """

def __lt__(self, other_vector: Vector2D) -> bool:
    """Check if the self instance is less than the other instance.

    Args:
        other_vector: Other instance (rhs of the operator).

    Returns:
        True, if the self instance is less than the other instance.
        False, else.
    """
```

**Parameter Description**：
- `other_vector`: Comparison object

**Return Value**：Boolean, indicating the comparison result

#### 9. String Representation Methods - __repr__, __str__

**Function**：Provide string representation of a vector.

**Method Signature**：
```python
def __repr__(self) -> str:
    """Return the instance representation.

    Returns:
        The representation of the instance.
    """

def __str__(self) -> str:
    """The instance as a string.

    Returns:
        The instance as a string.
    """
```

**Return Value**：
- `__repr__`: Returns "vector.Vector2D(x, y)" format
- `__str__`: Returns "(x, y)" format

### Actual Usage Patterns

#### Basic Usage

```python
from fastvector import Vector2D

# Create vectors
vec1 = Vector2D(1, 2)
vec2 = Vector2D(3, 4)

# Vector operations
sum_vec = vec1 + vec2          # Vector Addition
diff_vec = vec1 - vec2         # Vector Subtraction
dot_product = vec1 * vec2      # Dot Product
scaled_vec = vec1 * 2.0       # Scalar Multiplication
divided_vec = vec1 / 2.0      # Scalar Division
magnitude = abs(vec1)          # Magnitude Calculation

# Comparison operations
is_equal = vec1 == vec2        # Equality Comparison
is_smaller = vec1 < vec2       # Size Comparison

# String representation
print(repr(vec1))              # "vector.Vector2D(1, 2)"
print(str(vec1))               # "(1, 2)"
```

#### Advanced Usage

```python
from fastvector import Vector2D
import math

# Vector Normalization
def normalize(vector: Vector2D) -> Vector2D:
    """Normalize a vector to a unit vector."""
    magnitude = abs(vector)
    if magnitude == 0:
        return Vector2D(0.0, 0.0)
    return vector / magnitude

# Vector Projection
def project(vector: Vector2D, onto: Vector2D) -> Vector2D:
    """Calculate the projection of vector onto onto direction."""
    dot_product = vector * onto
    onto_magnitude_squared = onto * onto
    if onto_magnitude_squared == 0:
        return Vector2D(0.0, 0.0)
    scalar = float(dot_product / onto_magnitude_squared)
    return onto * scalar

# Vector Rotation
def rotate(vector: Vector2D, angle: float) -> Vector2D:
    """Rotate the vector by a specified angle (in radians)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x = vector.x * cos_a - vector.y * sin_a
    y = vector.x * sin_a + vector.y * cos_a
    return Vector2D(x, y)

# Example Usage
vec = Vector2D(3, 4)
normalized = normalize(vec)
projected = project(vec, Vector2D(1, 0))
rotated = rotate(vec, math.pi / 4)
```

#### Error Handling Patterns

```python
from fastvector import Vector2D

# Type Error Handling
try:
    vec = Vector2D(1, None)  # Will raise TypeError
except TypeError as e:
    print(f"Parameter Error: {e}")

# Operation Error Handling
try:
    vec1 = Vector2D(1, 1)
    result = vec1 * "invalid"  # Will raise TypeError
except TypeError as e:
    print(f"Operation Error: {e}")

# Division by Zero Error Handling
try:
    vec = Vector2D(1, 1)
    result = vec / 0.0  # Will raise ZeroDivisionError
except ZeroDivisionError as e:
    print(f"Division by Zero Error: {e}")
```

### Supported Operation Types

- **Creation Operations**：Vector2D(x, y) - Create a two-dimensional vector
- **Arithmetic Operations**：Addition(+), Subtraction(-), Scalar Multiplication(*), Scalar Division(/)
- **Dot Product Operations**：Vector × Vector = Scalar
- **Comparison Operations**：Equality(==), Size Comparison(<, >, <=, >=)
- **Special Operations**：Magnitude Calculation(abs), String Representation(repr, str)
- **Boolean Operations**：Vector to Boolean Conversion

### Error Handling

The system provides comprehensive error handling mechanisms:
- **Type Checking**：Ensure all parameters are correct numeric types
- **Operation Validation**：Validate the compatibility and validity of operations
- **Exception Handling**：Gracefully handle various exceptional situations
- **Boundary Handling**：Correctly handle zero vectors, negative values, etc.

### Important Notes

1. **Type Safety**：All operations are strictly type-checked to ensure type safety
2. **Floating Point Precision**：All calculations use floating-point numbers to maintain calculation precision
3. **Immutability**：Vector objects are immutable, operations return new vector objects
4. **Comparison Basis**：Vector comparison is based on magnitude, not coordinate values
5. **Zero Vector Handling**：The magnitude of a zero vector is 0, but all operations can be performed


### Node 1: Vector Creation and Type Validation (Vector Creation and Type Validation)

**Function Description**：Process various numeric input formats, unify them into a comparable numeric form. Support complex scenarios such as integers, floating-point numbers, negative values, and perform strict type validation.

**Core Algorithm**：
- Parameter type checking and validation
- Value range validation
- Exception handling
- Type conversion standardization

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Normal creation test
vec1 = Vector2D(1, 2)
print(vec1)  # (1, 2)

vec2 = Vector2D(-1.5, 3.7)
print(vec2)  # (-1.5, 3.7)

# Type validation test
try:
    vec3 = Vector2D(1, None)
except TypeError as e:
    print(f"Type Error: {e}")  # You must pass in int/float values for x and y!

try:
    vec4 = Vector2D("1", 2)
except TypeError as e:
    print(f"Type Error: {e}")  # You must pass in int/float values for x and y!

# Boundary value test
vec5 = Vector2D(0, 0)  # Zero vector
print(vec5)  # (0, 0)

vec6 = Vector2D(1e-10, 1e10)  # Extreme value test
print(vec6)  # (1e-10, 1e10)

# Test verification
assert str(Vector2D(1, 2)) == "(1, 2)"
assert str(Vector2D(-1.5, 3.7)) == "(-1.5, 3.7)"
assert str(Vector2D(0, 0)) == "(0, 0)"
```

### Node 2: Vector Addition Operation (Vector Addition)

**Function Description**：Implement vector addition, supporting mixed positive and negative values, floating-point operations, and complex scenarios.

**Core Algorithm**：
- Component-wise addition
- Floating-point precision maintenance
- Zero vector addition handling
- Type safety check

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Basic addition test
vec1 = Vector2D(1, 2)
vec2 = Vector2D(3, 4)
result = vec1 + vec2
print(result)  # (4, 6)

# Zero vector addition
zero_vec = Vector2D(0, 0)
result = zero_vec + vec1
print(result)  # (1, 2)

# Negative vector addition
vec3 = Vector2D(-1, -2)
result = vec1 + vec3
print(result)  # (0, 0)

# Floating-point precision test
vec4 = Vector2D(1.5, 2.7)
vec5 = Vector2D(0.5, 0.3)
result = vec4 + vec5
print(result)  # (2.0, 3.0)

# Test verification
assert str(Vector2D(1, 2) + Vector2D(3, 4)) == "(4, 6)"
assert str(Vector2D(0, 0) + Vector2D(1, 2)) == "(1, 2)"
assert str(Vector2D(1, 2) + Vector2D(-1, -2)) == "(0, 0)"
```

### Node 3: Vector Subtraction Operation (Vector Subtraction)

**Function Description**：Implement vector subtraction, verifying vector difference calculation, correctly handling negative coordinates and floating-point precision.

**Core Algorithm**：
- Component-wise subtraction
- Negative value handling
- Floating-point precision maintenance
- Zero vector subtraction handling

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Basic subtraction test
vec1 = Vector2D(5, 7)
vec2 = Vector2D(2, 3)
result = vec1 - vec2
print(result)  # (3, 4)

# Zero vector subtraction
zero_vec = Vector2D(0, 0)
result = vec1 - zero_vec
print(result)  # (5, 7)

# Negative vector subtraction
vec3 = Vector2D(-1, -2)
result = vec1 - vec3
print(result)  # (6, 9)

# Floating-point precision test
vec4 = Vector2D(3.5, 4.7)
vec5 = Vector2D(1.5, 2.3)
result = vec4 - vec5
print(result)  # (2.0, 2.4)

# Test verification
assert str(Vector2D(5, 7) - Vector2D(2, 3)) == "(3, 4)"
assert str(Vector2D(5, 7) - Vector2D(0, 0)) == "(5, 7)"
assert str(Vector2D(5, 7) - Vector2D(-1, -2)) == "(6, 9)"
```

### Node 4: Scalar Multiplication Operation (Scalar Multiplication)

**Function Description**：Implement vector multiplication by a scalar, including dot product and scalar multiplication, supporting floating-point precision and exception handling.

**Core Algorithm**：
- Vector dot product calculation
- Scalar multiplication operation
- Type safety check
- Exception handling

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Dot product test
vec1 = Vector2D(1, 2)
vec2 = Vector2D(3, 4)
dot_product = vec1 * vec2
print(dot_product)  # 11

# Scalar multiplication test
scalar = 2.5
result = vec1 * scalar
print(result)  # (2.5, 5.0)

# Zero vector operation
zero_vec = Vector2D(0, 0)
result = zero_vec * vec1
print(result)  # 0

result = zero_vec * scalar
print(result)  # (0.0, 0.0)

# Negative operation
vec3 = Vector2D(-1, -2)
result = vec1 * vec3
print(result)  # -5

# Floating-point precision test
vec4 = Vector2D(1.5, 2.7)
result = vec4 * 2.0
print(result)  # (3.0, 5.4)

# Test verification
assert Vector2D(1, 2) * Vector2D(3, 4) == 11
assert str(Vector2D(1, 2) * 2.5) == "(2.5, 5.0)"
assert Vector2D(0, 0) * Vector2D(1, 2) == 0
```

### Node 5: Dot Product Operation (Dot Product)

**Function Description**：Calculate the dot product of two vectors, verify mathematical calculation accuracy, support various vector combinations and precision control.

**Core Algorithm**：
- Component-wise multiplication and summation
- Floating-point precision control
- Zero vector handling
- Mathematical equivalence verification

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Basic dot product test
vec1 = Vector2D(1, 2)
vec2 = Vector2D(3, 4)
dot_product = vec1 * vec2
print(dot_product)  # 11

# Zero vector dot product
zero_vec = Vector2D(0, 0)
result = zero_vec * vec1
print(result)  # 0

# Orthogonal vector dot product
vec3 = Vector2D(1, 0)
vec4 = Vector2D(0, 1)
result = vec3 * vec4
print(result)  # 0

# Negative vector dot product
vec5 = Vector2D(-1, -2)
result = vec1 * vec5
print(result)  # -5

# Floating-point precision test
vec6 = Vector2D(1.5, 2.7)
vec7 = Vector2D(0.5, 1.3)
result = vec6 * vec7
print(result)  # 4.26

# Test verification
assert Vector2D(1, 2) * Vector2D(3, 4) == 11
assert Vector2D(0, 0) * Vector2D(1, 2) == 0
assert Vector2D(1, 0) * Vector2D(0, 1) == 0
assert Vector2D(1, 2) * Vector2D(-1, -2) == -5
```

### Node 6: Magnitude Calculation (Magnitude Calculation)

**Function Description**：Calculate the magnitude (length) of a vector, using the abs() function to implement, supporting zero vectors, unit vectors, and any vectors.

**Core Algorithm**：
- Euclidean distance calculation
- Zero vector handling
- Unit vector verification
- Floating-point precision maintenance

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Basic magnitude test
vec1 = Vector2D(3, 4)
magnitude = abs(vec1)
print(magnitude)  # 5.0

# Zero vector magnitude
zero_vec = Vector2D(0, 0)
magnitude = abs(zero_vec)
print(magnitude)  # 0.0

# Unit vector magnitude
unit_vec1 = Vector2D(1, 0)
magnitude = abs(unit_vec1)
print(magnitude)  # 1.0

unit_vec2 = Vector2D(0, 1)
magnitude = abs(unit_vec2)
print(magnitude)  # 1.0

# Negative vector magnitude
vec2 = Vector2D(-3, -4)
magnitude = abs(vec2)
print(magnitude)  # 5.0

# Floating-point precision test
vec3 = Vector2D(1.5, 2.5)
magnitude = abs(vec3)
print(magnitude)  # 2.9154759474226504

# Test verification
assert abs(Vector2D(3, 4)) == 5.0
assert abs(Vector2D(0, 0)) == 0.0
assert abs(Vector2D(1, 0)) == 1.0
assert abs(Vector2D(0, 1)) == 1.0
assert abs(Vector2D(-3, -4)) == 5.0
```

### Node 7: Vector Comparison Operations (Vector Comparison)

**Function Description**：Implement vector equality and size comparison, supporting different data type comparisons, and based on vector magnitude comparison.

**Core Algorithm**：
- Equality comparison
- Magnitude size comparison
- Type safety check
- Boundary case handling

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Equality comparison test
vec1 = Vector2D(1, 2)
vec2 = Vector2D(1, 2)
is_equal = vec1 == vec2
print(is_equal)  # True

# Different vector comparison
vec3 = Vector2D(2, 3)
is_equal = vec1 == vec3
print(is_equal)  # False

# Different type comparison
is_equal = vec1 == (1, 2)
print(is_equal)  # False

# Size comparison test
vec4 = Vector2D(3, 4)  # Magnitude 5
vec5 = Vector2D(1, 1)  # Magnitude √2
is_smaller = vec5 < vec4
print(is_smaller)  # True

# Zero vector comparison
zero_vec = Vector2D(0, 0)
is_smaller = zero_vec < vec1
print(is_smaller)  # True

# Equal magnitude comparison
vec6 = Vector2D(3, 4)  # Magnitude 5
vec7 = Vector2D(4, 3)  # Magnitude 5
is_equal = vec6 == vec7
print(is_equal)  # False (Coordinate different)

# Test verification
assert Vector2D(1, 2) == Vector2D(1, 2)
assert Vector2D(1, 2) != Vector2D(2, 1)
assert Vector2D(1, 1) < Vector2D(3, 4)
assert Vector2D(0, 0) < Vector2D(1, 1)
```

### Node 8: Vector Normalization (Vector Normalization)

**Function Description**：Implement vector normalization by division, converting a vector to a unit vector while maintaining direction.

**Core Algorithm**：
- Magnitude calculation
- Zero vector handling
- Unit vector conversion
- Precision control

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Normalization function
def normalize(vector: Vector2D) -> Vector2D:
    """Normalize a vector to a unit vector."""
    magnitude = abs(vector)
    if magnitude == 0:
        return Vector2D(0.0, 0.0)
    return vector / magnitude

# Basic normalization test
vec1 = Vector2D(3, 4)
normalized = normalize(vec1)
print(normalized)  # (0.6, 0.8)
print(abs(normalized))  # 1.0

# Zero vector normalization
zero_vec = Vector2D(0, 0)
normalized = normalize(zero_vec)
print(normalized)  # (0.0, 0.0)

# Unit vector normalization
unit_vec = Vector2D(1, 0)
normalized = normalize(unit_vec)
print(normalized)  # (1.0, 0.0)

# Negative vector normalization
vec2 = Vector2D(-3, -4)
normalized = normalize(vec2)
print(normalized)  # (-0.6, -0.8)

# Floating-point vector normalization
vec3 = Vector2D(1.5, 2.5)
normalized = normalize(vec3)
print(normalized)  # (0.5144957554275265, 0.8574929257125441)

# Test verification
normalized_vec = normalize(Vector2D(3, 4))
assert abs(normalized_vec) == 1.0
assert str(normalized_vec) == "(0.6, 0.8)"
assert str(normalize(Vector2D(0, 0))) == "(0.0, 0.0)"
```

### Node 9: Vector Projection Calculation (Vector Projection)

**Function Description**：Implement vector projection calculation by dot product, verifying projection mathematical principles, calculating the projection of one vector onto another vector in a given direction.

**Core Algorithm**：
- Dot product calculation
- Projection formula application
- Zero vector handling
- Precision control

**Input/Output Examples**：

```python
from fastvector import Vector2D

# Projection calculation function
def project(vector: Vector2D, onto: Vector2D) -> Vector2D:
    """Calculate the projection of vector onto onto direction."""
    dot_product = vector * onto
    onto_magnitude_squared = onto * onto
    if onto_magnitude_squared == 0:
        return Vector2D(0.0, 0.0)
    scalar = float(dot_product / onto_magnitude_squared)
    return onto * scalar

# Basic projection test
vec1 = Vector2D(3, 4)
onto_vec = Vector2D(1, 0)
projection = project(vec1, onto_vec)
print(projection)  # (3.0, 0.0)

# Orthogonal projection test
vec2 = Vector2D(1, 1)
onto_vec2 = Vector2D(1, 0)
projection = project(vec2, onto_vec2)
print(projection)  # (1.0, 0.0)

# Zero vector projection
zero_vec = Vector2D(0, 0)
projection = project(vec1, zero_vec)
print(projection)  # (0.0, 0.0)

# Negative vector projection
vec3 = Vector2D(-2, -3)
onto_vec3 = Vector2D(1, 1)
projection = project(vec3, onto_vec3)
print(projection)  # (-2.5, -2.5)

# Floating-point projection test
vec4 = Vector2D(1.5, 2.5)
onto_vec4 = Vector2D(0.5, 1.0)
projection = project(vec4, onto_vec4)
print(projection)  # (1.4, 2.8)

# Test verification
projection = project(Vector2D(3, 4), Vector2D(1, 0))
assert str(projection) == "(3.0, 0.0)"
projection = project(Vector2D(1, 1), Vector2D(1, 0))
assert str(projection) == "(1.0, 0.0)"
```

### Node 10: Vector Rotation Calculation (Vector Rotation)

**Function Description**：Implement vector rotation by scalar multiplication, supporting rotation transformation calculation, using trigonometric functions for coordinate transformation.

**Core Algorithm**：
- Rotation matrix application
- Trigonometric function calculation
- Coordinate transformation
- Precision control

**Input/Output Examples**：

```python
from fastvector import Vector2D
import math

# Rotation calculation function
def rotate(vector: Vector2D, angle: float) -> Vector2D:
    """Rotate the vector by a specified angle (in radians)."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x = vector.x * cos_a - vector.y * sin_a
    y = vector.x * sin_a + vector.y * cos_a
    return Vector2D(x, y)

# Basic rotation test
vec1 = Vector2D(1, 0)
rotated = rotate(vec1, math.pi/2)  # Rotate 90 degrees
print(rotated)  # (0.0, 1.0)

# 180 degree rotation test
vec2 = Vector2D(1, 1)
rotated = rotate(vec2, math.pi)  # Rotate 180 degrees
print(rotated)  # (-1.0, -1.0)

# 360 degree rotation test
vec3 = Vector2D(3, 4)
rotated = rotate(vec3, 2*math.pi)  # Rotate 360 degrees
print(rotated)  # (3.0, 4.0) (Approximately)

# Negative angle rotation
vec4 = Vector2D(1, 0)
rotated = rotate(vec4, -math.pi/2)  # Rotate counterclockwise 90 degrees
print(rotated)  # (0.0, -1.0)

# Floating-point angle test
vec5 = Vector2D(2, 3)
rotated = rotate(vec5, math.pi/4)  # Rotate 45 degrees
print(rotated)  # (-0.7071067811865475, 3.5355339059327373)

# Test verification
rotated = rotate(Vector2D(1, 0), math.pi/2)
assert abs(rotated.x) < 1e-10 and abs(rotated.y - 1) < 1e-10
rotated = rotate(Vector2D(1, 1), math.pi)
assert abs(rotated.x + 1) < 1e-10 and abs(rotated.y + 1) < 1e-10
```

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
# Core Mathematical Calculation Library
numpy==2.2.6                     # Numerical Calculation Foundation Library

# Packaging / Build Backend
setuptools==80.10.2              # Build backend (setuptools.build_meta)
wheel==0.45.1                    # Wheel builder
```

### Example 2: ordinary usage
```text
workspace/
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── codecov.yml
├── docs
│   ├── api.md
│   ├── index.md
├── examples
│   ├── main.py
├── fastvector
│   ├── __init__.py
│   ├── vector.py
│   ├── version.py
├── mkdocs.yml
└── pyproject.toml
```

### Example 3: boundary or error behavior
```text
from fastvector import Vector2D
```

### Example 4: boundary or error behavior
```text
@total_ordering
class Vector2D:
    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Create a instance with the given x and y values.

        Args:
            x: x-Value.
            y: y-Value.

        Raises:
            TypeError: If x or y are not a number.
        """
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
