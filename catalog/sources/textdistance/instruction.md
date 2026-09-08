# TextDistance Library

## Natural Language Instruction

Build the **textdistance** package from an empty workspace. TextDistance is a Python library for computing distances and similarities between text sequences using 30+ algorithms. The package provides a unified interface for various distance metrics including edit-based (Hamming, Levenshtein, Damerau-Levenshtein, Jaro, Jaro-Winkler), token-based (Jaccard, Sorensen-Dice, Cosine), and sequence-based (LCSSeq, Ratcliff-Obershelp) algorithms.

The package should support importing the main module and using core string similarity/distance functions without requiring external dependencies beyond the Python standard library.

## Project Description

**textdistance** computes distance between two or more sequences using multiple algorithms. It features:

- 30+ algorithms for text distance and similarity computation
- Pure Python implementation (no external dependencies required for core algorithms)
- Common interface across all algorithms
- Support for comparing more than two sequences (for some algorithms)
- Both class-based and function-style APIs

### Core Algorithms

The package implements several categories of algorithms:

**Edit-based algorithms:**
- Hamming: counts differing positions in equal-length sequences
- Levenshtein: minimum edits (insert/delete/substitute) to transform one string to another
- Damerau-Levenshtein: extends Levenshtein by adding transposition operation
- Jaro: similarity based on matching characters and transpositions
- Jaro-Winkler: Jaro with additional weight for common prefix

**Token-based algorithms:**
- Jaccard: intersection divided by union of character/token sets
- Sorensen-Dice: twice the intersection divided by sum of set sizes
- Cosine: similarity based on angle between character frequency vectors

**Sequence-based algorithms:**
- LCSSeq: longest common subsequence (not necessarily contiguous)
- Ratcliff-Obershelp: gestalt pattern matching similarity

## Supports

- **Python Version**: 3.5+
- **Operating System**: Cross-platform (Linux, macOS, Windows)
- **Dependencies**: None required for core pure-Python algorithms
- **Optional Dependencies**: numpy, jellyfish, python-Levenshtein, rapidfuzz (for accelerated implementations)

## Environment Configuration

```toml
python_version = "3.12"
os_name = "debian-12-amd64"
installer = "pip"
```

## Project Directory Structure

```
workspace/
├── textdistance/
│   ├── __init__.py           # Main package entry with exports
│   ├── algorithms/
│   │   ├── __init__.py       # Algorithm module exports
│   │   ├── base.py           # Base classes for algorithms
│   │   ├── edit_based.py     # Edit distance algorithms
│   │   ├── token_based.py    # Token similarity algorithms
│   │   ├── sequence_based.py # Sequence algorithms
│   │   ├── compression_based.py
│   │   ├── phonetic.py
│   │   ├── simple.py
│   │   └── types.py          # Type definitions
│   └── utils.py              # Utility functions
├── setup.py                  # Installation script
├── setup.cfg                 # Setup configuration
├── pyproject.toml            # Build system configuration
├── README.md                 # Documentation
├── LICENSE                   # MIT license
└── tests/                    # Test suite
```

## API Usage Guide

### Import and Basic Usage

```python
import textdistance

# Calculate Hamming distance
distance = textdistance.hamming("test", "text")
# Returns: 1 (one character differs)

# Calculate Levenshtein distance
distance = textdistance.levenshtein("kitten", "sitting")
# Returns: 3 (three edits needed)

# Calculate Jaro-Winkler similarity
similarity = textdistance.jaro_winkler("martha", "marhta")
# Returns: 0.96111... (high similarity)
```

### Core Distance Functions

All distance/similarity functions are available as module-level callables:

#### Hamming Distance

```python
textdistance.hamming(seq1: str, seq2: str) -> int
```

Computes the Hamming distance between two sequences - the number of positions at which corresponding symbols differ. Both sequences should have equal length (or truncate/pad behavior applies).

**Example:**
```python
textdistance.hamming("hello", "hallo")  # Returns: 1
textdistance.hamming("abc", "xyz")      # Returns: 3
```

#### Levenshtein Distance

```python
textdistance.levenshtein(seq1: str, seq2: str) -> int
```

Computes the minimum number of single-character edits (insertions, deletions, or substitutions) required to transform one string into another.

**Example:**
```python
textdistance.levenshtein("kitten", "sitting")  # Returns: 3
textdistance.levenshtein("saturday", "sunday") # Returns: 3
```

#### Damerau-Levenshtein Distance

```python
textdistance.damerau_levenshtein(seq1: str, seq2: str) -> int
```

Extends Levenshtein distance by allowing transposition (swapping) of two adjacent characters as a single operation.

**Example:**
```python
textdistance.damerau_levenshtein("abc", "acb")  # Returns: 1 (one transposition)
textdistance.damerau_levenshtein("ab", "ba")    # Returns: 1 (one transposition)
```

#### Jaro Similarity

```python
textdistance.jaro(seq1: str, seq2: str) -> float
```

Computes the Jaro similarity between two strings. Returns a value between 0.0 (completely different) and 1.0 (identical).

**Example:**
```python
textdistance.jaro("martha", "marhta")  # Returns: ~0.944
textdistance.jaro("same", "same")      # Returns: 1.0
```

#### Jaro-Winkler Similarity

```python
textdistance.jaro_winkler(seq1: str, seq2: str) -> float
```

Extension of Jaro similarity that gives more favorable ratings to strings with common prefixes. Returns a value between 0.0 and 1.0.

**Example:**
```python
textdistance.jaro_winkler("dixon", "dicksonx")  # Returns: ~0.813
textdistance.jaro_winkler("same", "same")       # Returns: 1.0
```

#### Jaccard Similarity

```python
textdistance.jaccard(seq1: str, seq2: str) -> float
```

Computes the Jaccard index (intersection over union) for character sets. Returns a value between 0.0 (no common characters) and 1.0 (identical character sets).

**Example:**
```python
textdistance.jaccard("abc", "bcd")  # Returns: 0.5 (2 common / 4 total unique)
textdistance.jaccard("abc", "abc")  # Returns: 1.0
```

#### Sorensen-Dice Coefficient

```python
textdistance.sorensen_dice(seq1: str, seq2: str) -> float
```

Computes the Sørensen-Dice coefficient: 2 * |intersection| / (|A| + |B|). Also available as `textdistance.sorensen()` or `textdistance.dice()`.

**Example:**
```python
textdistance.sorensen_dice("abc", "bcd")  # Returns: ~0.667
textdistance.sorensen_dice("abc", "abc")  # Returns: 1.0
```

#### Cosine Similarity

```python
textdistance.cosine(seq1: str, seq2: str) -> float
```

Computes cosine similarity based on character frequency vectors. Returns a value between 0.0 (orthogonal) and 1.0 (identical direction).

**Example:**
```python
textdistance.cosine("abc", "bcd")  # Returns: ~0.667
textdistance.cosine("abc", "abc")  # Returns: 1.0
```

#### Longest Common Subsequence (LCSSeq)

```python
textdistance.lcsseq(seq1: str, seq2: str) -> str
```

Finds the longest common subsequence between two sequences. The subsequence does not need to be contiguous.

**Example:**
```python
textdistance.lcsseq("abcde", "ace")      # Returns: "ace"
textdistance.lcsseq("AGGTAB", "GXTXAYB") # Returns: "GTAB"
```

#### Ratcliff-Obershelp Similarity

```python
textdistance.ratcliff_obershelp(seq1: str, seq2: str) -> float
```

Computes similarity using the Gestalt pattern matching algorithm. Returns a value between 0.0 and 1.0.

**Example:**
```python
textdistance.ratcliff_obershelp("alexander", "alexandre")  # Returns: ~0.889
textdistance.ratcliff_obershelp("abc", "abc")              # Returns: 1.0
```

### Class-Based API

Each algorithm is also available as a class that can be instantiated with custom parameters:

```python
from textdistance import Hamming, Levenshtein

# Create custom instance
hamming = Hamming(qval=1, external=False)
distance = hamming("test", "text")

# Use default instance
distance = Levenshtein()("kitten", "sitting")
```

### Common Parameters

Many algorithms support these initialization parameters:

- `qval`: int - q-value for splitting sequences into q-grams (1=chars, 2+=n-grams, None=words)
- `as_set`: bool - for token-based algorithms, whether to treat sequences as sets
- `external`: bool - whether to use external accelerated libraries if available

### Return Value Behavior

- **Distance functions** (hamming, levenshtein, damerau_levenshtein): return non-negative integers
- **Similarity functions** (jaro, jaro_winkler, jaccard, sorensen_dice, cosine, ratcliff_obershelp): return floats in [0.0, 1.0]
- **lcsseq**: returns a string (the longest common subsequence)

## Implementation Notes

### Pure Python Implementation

The core algorithms must work without external dependencies. The library includes pure Python implementations that are activated when optional accelerated libraries are not available.

### Algorithm Selection

When instantiated with `external=True` (default), algorithms may attempt to use faster external implementations (jellyfish, rapidfuzz, python-Levenshtein, etc.). When these are not available, the pure Python implementation is used automatically.

### Empty String Handling

- Distance functions generally return the length of the non-empty string when one string is empty
- Similarity functions return 1.0 when both strings are empty, 0.0 when one is empty
- lcsseq returns an empty string when there is no common subsequence

### Unicode Support

All algorithms support Unicode strings and operate on character-by-character basis by default.

### Performance Considerations

Pure Python implementations are provided for all core algorithms but may be slower than external optimized libraries for large inputs. The library automatically falls back to pure Python when external libraries are not installed.

## Package Metadata

- **Package Name**: textdistance
- **Version**: 4.6.3
- **Author**: orsinium
- **License**: MIT
- **Repository**: https://github.com/orsinium/textdistance
- **Python Requires**: >=3.5

## Installation Requirements

The package should be installable via:
```bash
pip install -e .
```

And support standard Python package installation without requiring build dependencies beyond setuptools/wheel.

## Testing and Verification

The implementation will be verified against test scenarios covering:

1. **Hamming distance**: character-by-character comparison
2. **Levenshtein distance**: edit operations counting
3. **Damerau-Levenshtein distance**: including transpositions
4. **Jaro similarity**: character matching within distance windows
5. **Jaro-Winkler similarity**: prefix-weighted Jaro scores
6. **Jaccard similarity**: set intersection/union ratios
7. **Sorensen-Dice coefficient**: double-weighted intersection
8. **Cosine similarity**: vector angle measurements
9. **LCSSeq**: subsequence identification
10. **Ratcliff-Obershelp**: gestalt pattern matching

Each algorithm should produce deterministic, numerically accurate results matching the mathematical definitions of these distance/similarity metrics.
