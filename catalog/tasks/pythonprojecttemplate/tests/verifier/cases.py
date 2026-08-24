"""Frozen 36-leaf hidden slice for the fastvector task.

Each case is pure JSON-safe data. Operand shapes are declared with an
allowlisted ``kind`` tag that the adapter maps to an in-process constructor;
no Python source, import path or shell fragment ever crosses the boundary.

The slice mirrors the upstream ``tests/test_vector.py`` parametrisation at
revision f1c116379eb485c17fb1b6cd3e2454712e4e0585, one leaf per collected
pytest node, so the frozen denominator stays 36.
"""

from __future__ import annotations

# Upstream module-level fixtures V1/V2/V3.
V1 = [0, 0]
V2 = [-1, 1]
V3 = [2.5, -2.5]

NUM = "num"
NONE = "none"
STR = "str"
TUPLE = "tuple"
LIST = "list"
VEC = "vec"

CASES: tuple[dict[str, object], ...] = (
    # test_init_raises[4]
    {"id": "init_raises[x=-1,y=None]", "op": "init_raises",
     "x": {"kind": NUM, "value": -1}, "y": {"kind": NONE}},
    {"id": "init_raises[x=1,y=None]", "op": "init_raises",
     "x": {"kind": NUM, "value": 1}, "y": {"kind": NONE}},
    {"id": "init_raises[x=None,y=1]", "op": "init_raises",
     "x": {"kind": NONE}, "y": {"kind": NUM, "value": 1}},
    {"id": "init_raises[x=None,y=-1]", "op": "init_raises",
     "x": {"kind": NONE}, "y": {"kind": NUM, "value": -1}},

    # test_from_values[3]
    {"id": "from_values[-1,1]", "op": "from_values", "lhs": [-1, 1], "exp": [-1, 1]},
    {"id": "from_values[1,-1]", "op": "from_values", "lhs": [1, -1], "exp": [1, -1]},
    {"id": "from_values[1,1]", "op": "from_values", "lhs": [1, 1], "exp": [1, 1]},

    # test_repr[1] / test_str[1]
    {"id": "repr[1.0,2.0]", "op": "repr", "lhs": [1.0, 2.0],
     "exp": "vector.Vector2D(1.0, 2.0)"},
    {"id": "str[1.0,2.0]", "op": "str", "lhs": [1.0, 2.0], "exp": "(1.0, 2.0)"},

    # test_add[3]
    {"id": "add[V1,V2]", "op": "add", "lhs": V1, "rhs": V2, "exp": [-1, 1]},
    {"id": "add[V1,V3]", "op": "add", "lhs": V1, "rhs": V3, "exp": [2.5, -2.5]},
    {"id": "add[V3,V2]", "op": "add", "lhs": V3, "rhs": V2, "exp": [1.5, -1.5]},

    # test_sub[3]
    {"id": "sub[V1,V2]", "op": "sub", "lhs": V1, "rhs": V2, "exp": [1, -1]},
    {"id": "sub[V1,V3]", "op": "sub", "lhs": V1, "rhs": V3, "exp": [-2.5, 2.5]},
    {"id": "sub[V3,V2]", "op": "sub", "lhs": V3, "rhs": V2, "exp": [3.5, -3.5]},

    # test_mul_vec[3] (dot product)
    {"id": "mul_vec[V1,V2]", "op": "dot", "lhs": V1, "rhs": V2, "exp": 0.0},
    {"id": "mul_vec[V1,V3]", "op": "dot", "lhs": V1, "rhs": V3, "exp": 0.0},
    {"id": "mul_vec[V3,V2]", "op": "dot", "lhs": V3, "rhs": V2, "exp": -5.0},

    # test_mul_float[3]
    {"id": "mul_float[V1,2.0]", "op": "mul_scalar", "lhs": V1, "scalar": 2.0,
     "exp": [0.0, 0.0]},
    {"id": "mul_float[V2,2.0]", "op": "mul_scalar", "lhs": V2, "scalar": 2.0,
     "exp": [-2.0, 2.0]},
    {"id": "mul_float[V3,2.0]", "op": "mul_scalar", "lhs": V3, "scalar": 2.0,
     "exp": [5.0, -5.0]},

    # test_mul_raises[2]
    {"id": "mul_raises[None]", "op": "mul_raises", "lhs": [1, 1],
     "rhs": {"kind": NONE}},
    {"id": "mul_raises[str]", "op": "mul_raises", "lhs": [1, 1],
     "rhs": {"kind": STR, "value": "1"}},

    # test_div[3]
    {"id": "div[V1,2.0]", "op": "div", "lhs": V1, "scalar": 2.0, "exp": [0.0, 0.0]},
    {"id": "div[V2,2.0]", "op": "div", "lhs": V2, "scalar": 2.0, "exp": [-0.5, 0.5]},
    {"id": "div[V3,2.0]", "op": "div", "lhs": V3, "scalar": 2.0,
     "exp": [1.25, -1.25]},

    # test_div_raises[1]: dividing by a Vector2D must raise TypeError.
    {"id": "div_raises[vector]", "op": "div_raises", "lhs": [0.0, 0.0],
     "rhs": {"kind": VEC, "value": [0.0, 0.0]}},

    # test_operators_raises[2]: <, + and - all reject non-Vector2D operands.
    {"id": "operators_raises[tuple]", "op": "operators_raises", "lhs": [1, 1],
     "rhs": {"kind": TUPLE, "value": [0, 1]}},
    {"id": "operators_raises[list]", "op": "operators_raises", "lhs": [1, 1],
     "rhs": {"kind": LIST, "value": [1, 0]}},

    # test_abs[3]
    {"id": "abs[0,0]", "op": "abs", "lhs": [0, 0], "exp": 0},
    {"id": "abs[0,1]", "op": "abs", "lhs": [0, 1], "exp": 1},
    {"id": "abs[1,0]", "op": "abs", "lhs": [1, 0], "exp": 1},

    # test_equality_other_class[2]
    {"id": "equality_other_class[tuple]", "op": "ne_other", "lhs": [1, 1],
     "rhs": {"kind": TUPLE, "value": [1, 1]}},
    {"id": "equality_other_class[list]", "op": "ne_other", "lhs": [1, 1],
     "rhs": {"kind": LIST, "value": [1, 1]}},

    # test_less_than[2]
    {"id": "less_than[lhs0]", "op": "lt", "lhs": [0, 1], "rhs": [1, 1]},
    {"id": "less_than[lhs1]", "op": "lt", "lhs": [1, 0], "rhs": [1, 1]},
)
