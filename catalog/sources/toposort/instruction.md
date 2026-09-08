# Topological Sort Library Implementation

## Project Description

Implement a topological sort library that provides functionality for ordering nodes in a directed acyclic graph (DAG). The library implements algorithms to process dependency relationships and produce valid orderings where all dependencies are satisfied before their dependents.

## Supports

- **Python Version**: 3.8+
- **Dependencies**: None (standard library only)
- **Package Name**: `toposort`
- **License**: Apache License 2.0

## Natural Language Instruction

Create a Python package that provides topological sorting functionality for directed graphs represented as dependency dictionaries. The implementation should handle various graph structures including chains, trees, disconnected components, and detect circular dependencies.

The package exports three main components:
1. A generator function that yields sets of nodes level by level in topological order
2. A convenience function that flattens the result into a single list
3. A custom exception class for circular dependency detection

## Environment Configuration

**Build Command**:
```bash
python -m pip install --no-build-isolation --no-deps --no-index -e .
```

**Required Files**:
- `src/toposort.py` - Main implementation module
- `pyproject.toml` or `setup.py` - Package metadata

## Project Directory Structure

```
workspace/
├── src/
│   └── toposort.py          # Main implementation
├── pyproject.toml           # Package configuration (or setup.py)
└── README.md                # Documentation (optional)
```

## API Usage Guide

### Module Exports

The `toposort` module exports:
- `toposort(data)` - Main topological sort generator
- `toposort_flatten(data, sort=True)` - Flattened result function
- `CircularDependencyError` - Exception for circular dependencies

### Core Functions

#### `toposort(data: dict) -> Iterator[set]`

Returns an iterator that yields sets of nodes in topological order.

**Parameters**:
- `data`: Dictionary where keys are dependent nodes and values are sets of their dependencies

**Returns**:
- Iterator yielding sets of nodes. Each set contains nodes with no remaining dependencies in that iteration. Items within each set can be processed in any order.

**Behavior**:
- Empty input dictionary returns an empty iterator
- Self-dependencies are automatically ignored
- Dependencies that don't appear as keys are automatically added with empty dependency sets
- Input dictionary is not modified

**Example**:
```python
from toposort import toposort

data = {
    2: {11},
    9: {11, 8},
    10: {11, 3},
    11: {7, 5},
    8: {7, 3}
}

result = list(toposort(data))
# Returns: [{3, 5, 7}, {8, 11}, {2, 9, 10}]
```

**Circular Dependency Handling**:
```python
try:
    list(toposort({1: {2}, 2: {1}}))
except CircularDependencyError as e:
    print(e.data)  # Contains the subset involved in the cycle
```

#### `toposort_flatten(data: dict, sort: bool = True) -> list`

Returns a flattened list of all nodes in topological order.

**Parameters**:
- `data`: Dictionary where keys are dependent nodes and values are sets of their dependencies
- `sort`: If True (default), nodes within each level are sorted before adding to result; if False, nodes are added in arbitrary order

**Returns**:
- List containing all nodes in valid topological order

**Behavior**:
- Equivalent to flattening the sets returned by `toposort()`
- When `sort=True`, results are deterministic and sorted within each level
- When `sort=False`, order within each level is implementation-dependent

**Example**:
```python
from toposort import toposort_flatten

data = {
    2: {11},
    9: {11, 8},
    10: {11, 3},
    11: {7, 5},
    8: {7, 3}
}

result = toposort_flatten(data)
# Returns: [3, 5, 7, 8, 11, 2, 9, 10]

result_unsorted = toposort_flatten(data, sort=False)
# Returns nodes in valid order but not necessarily sorted within levels
```

#### `CircularDependencyError(data: dict)`

Exception raised when circular dependencies are detected.

**Attributes**:
- `data`: Dictionary containing the subset of the input that forms the circular dependency

**Behavior**:
- Inherits from `ValueError`
- The error message describes the circular dependency
- The `data` attribute contains exactly the nodes and edges involved in the cycle(s)

**Example**:
```python
from toposort import toposort, CircularDependencyError

try:
    list(toposort({1: {2}, 2: {3}, 3: {1}}))
except CircularDependencyError as e:
    print(f"Circular dependency detected: {e}")
    print(f"Involved items: {e.data}")
    # e.data will be {1: {2}, 2: {3}, 3: {1}}
```

## Implementation Notes

### Input Format

The input is a dictionary where:
- **Keys**: Nodes that have dependencies (hashable types: int, str, tuple, etc.)
- **Values**: Sets containing the dependencies for each key

Nodes that appear only as dependencies (not as keys) are implicitly treated as having no dependencies.

### Key Behaviors

1. **Self-dependencies**: Automatically ignored (e.g., `{1: {1}}` is treated as `{1: set()}`)

2. **Implicit nodes**: Dependencies that don't appear as keys are added with empty dependency sets
   ```python
   # Input: {1: {2}}
   # Processed as: {1: {2}, 2: set()}
   ```

3. **Empty input**: Returns empty iterator
   ```python
   list(toposort({}))  # Returns []
   ```

4. **Immutability**: The input dictionary is never modified by the functions

5. **Determinism**: When using `toposort_flatten(data, sort=True)`, results are deterministic

### Algorithm Overview

The topological sort algorithm:
1. Copies input and removes self-dependencies
2. Identifies nodes that have no dependencies
3. Yields these nodes as a set
4. Removes processed nodes from remaining dependencies
5. Repeats until all nodes are processed or a cycle is detected

### Error Conditions

**CircularDependencyError**:
- Raised when circular dependencies are detected
- The exception's `data` attribute contains only the nodes involved in the cycle(s)
- Other nodes not involved in cycles are not included in the error data

### Type Constraints

- Node identifiers must be hashable (int, str, float, tuple, etc.)
- Dependencies must be provided as sets (or convertible to sets)
- Nodes can be of mixed hashable types in the same graph

### Version and Exports

The module must define:
```python
__version__ = "1.10"
__all__ = ["toposort", "toposort_flatten", "CircularDependencyError"]
```

### Performance Considerations

- The algorithm processes each node once
- Self-dependencies are filtered during preprocessing
- Nodes with no dependencies are identified efficiently
- Memory usage is proportional to the number of nodes and edges
