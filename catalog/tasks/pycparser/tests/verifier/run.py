from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from nl2repobench.verification.candidate_client import call, call_method, execute_script, get


def leaf(leaf_id: str, passed: bool, message: str = "") -> dict[str, str]:
    return {"id": leaf_id, "status": "passed" if passed else "failed", "message": message}


def ok(result, expected=None, exception_type=None) -> bool:
    if exception_type is not None:
        return (not result.ok) and result.exception_type == exception_type
    return result.ok and (expected is None or result.value == expected)


def main() -> None:
    leaves: list[dict[str, str]] = []
    def check(name: str, result, expected=None, exception_type=None) -> None:
        passed = ok(result, expected, exception_type)
        leaves.append(leaf(name, passed, f"observed={result!r}" if not passed else ""))

    check("package_metadata", call("importlib.metadata", "version", "pycparser"), "3.0")
    check("root_exports", execute_script("import pycparser; result = all(hasattr(pycparser, n) for n in ['c_ast','c_lexer','c_parser','CParser','parse_file','preprocess_file'])"), True)
    check("version_alias", get("pycparser", "__version__"), "3.00")
    check("submodule_exports", execute_script("from pycparser import c_ast, c_lexer, c_parser, c_generator, ast_transforms; result = all(hasattr(c_ast, n) for n in ['Node','NodeVisitor','ID','Constant','FileAST']) and all(hasattr(c_lexer, n) for n in ['Token','CLexer']) and hasattr(c_parser, 'ParseError')"), True)
    check("node_repr", execute_script("from pycparser import c_ast; n=c_ast.ID('value'); result=(repr(n), n.name, n.coord)"), ["ID(name='value'\n   )", "value", None])
    check("node_children", execute_script("from pycparser import c_ast; n=c_ast.BinaryOp('+', c_ast.ID('a'), c_ast.Constant('int','1')); result=[(k, type(v).__name__) for k,v in n.children()]"), [["left", "ID"], ["right", "Constant"]])
    check("node_show", execute_script("import io; from pycparser import c_ast; b=io.StringIO(); c_ast.ID('x').show(buf=b); result=b.getvalue()"), "ID: x\n")
    check("visitor_preorder", execute_script("from pycparser import c_ast\nclass V(c_ast.NodeVisitor):\n    def __init__(self): self.seen=[]\n    def visit(self,node): self.seen.append(type(node).__name__); return super().visit(node)\nv=V(); v.visit(c_ast.BinaryOp('+',c_ast.ID('a'),c_ast.ID('b'))); result=v.seen"), ["BinaryOp", "ID", "ID"])
    check("coord_format", execute_script("from pycparser.c_parser import Coord; result=(str(Coord('x.c',2)),str(Coord('x.c',2,7)))"), ["x.c:2", "x.c:2:7"])
    check("weakref_support", execute_script("import weakref; from pycparser import c_ast; n=c_ast.ID('x'); result=weakref.ref(n)() is n"), True)
    check("lexer_tokens", execute_script("from pycparser.c_lexer import CLexer; out=[]; l=CLexer(lambda *x:None,lambda:None,lambda:None,lambda x:False); l.input('int x = 0x10;'); t=l.token();\nwhile t: out.append((t.type,t.value)); t=l.token()\nresult=out"), [["INT", "int"], ["ID", "x"], ["EQUALS", "="], ["INT_CONST_HEX", "0x10"], ["SEMI", ";"]])
    check("lexer_typedef", execute_script("from pycparser.c_lexer import CLexer; l=CLexer(lambda *x:None,lambda:None,lambda:None,lambda x:x=='T'); l.input('T value;'); t=l.token(); result=(t.type,t.value)"), ["TYPEID", "T"])
    check("lexer_coordinates", execute_script("from pycparser.c_lexer import CLexer; l=CLexer(lambda *x:None,lambda:None,lambda:None,lambda x:False); l.input('int x;','unit.c'); t=l.token(); result=(t.lineno,t.column,l.filename)"), [1, 1, "unit.c"])
    check("lexer_callbacks", execute_script("events=[]; from pycparser.c_lexer import CLexer; l=CLexer(lambda *x:events.append('error'),lambda:events.append('open'),lambda:events.append('close'),lambda x:False); l.input('{ }'); l.token(); l.token(); result=events"), ["open", "close"])
    check("lexer_errors", execute_script("from pycparser.c_lexer import CLexer; errors=[]; l=CLexer(lambda *x:errors.append(x),lambda:None,lambda:None,lambda x:False); l.input('@'); l.token(); result=len(errors)==1"), True)
    check("parse_decl", execute_script("from pycparser import c_parser; n=c_parser.CParser().parse('int x;'); result=(type(n).__name__,type(n.ext[0]).__name__,n.ext[0].name)"), ["FileAST", "Decl", "x"])
    check("parse_function", execute_script("from pycparser import c_parser, c_ast; n=c_parser.CParser().parse('int add(int a, int b) { return a + b; }'); f=n.ext[0]; result=(type(f).__name__, f.decl.name, type(f.body.block_items[0]).__name__)"), ["FuncDef", "add", "Return"])
    check("parse_typedef_scope", execute_script("from pycparser import c_parser, c_ast; n=c_parser.CParser().parse('typedef int T; T value;'); result=(type(n.ext[0]).__name__, type(n.ext[1].type.type).__name__, n.ext[1].type.type.names)"), ["Typedef", "IdentifierType", ["T"]])
    check("parse_struct_enum", execute_script("from pycparser import c_parser; n=c_parser.CParser().parse('struct S { int x; }; enum E { A, B };'); result=(type(n.ext[0].type).__name__, type(n.ext[1].type).__name__)"), ["Struct", "Enum"])
    check("parse_error", call_method("pycparser.c_parser", "CParser", [], "parse", "int = ;", "bad.c"), exception_type="pycparser.c_parser.ParseError")
    check("parse_coordinates", execute_script("from pycparser import c_parser; n=c_parser.CParser().parse('int x;','unit.c'); result=(n.ext[0].coord.file,n.ext[0].coord.line)"), ["unit.c", 1])
    check("parse_c11", execute_script("from pycparser import c_parser; n=c_parser.CParser().parse('_Static_assert(1, \"ok\");'); result=type(n.ext[0]).__name__"), "StaticAssert")
    check("parse_literals", execute_script("from pycparser import c_parser; n=c_parser.CParser().parse('char *s=\"hi\";'); result=(type(n.ext[0]).__name__, n.ext[0].init.value)"), ["Decl", '"hi"'])
    check("parser_reset", execute_script("from pycparser import c_parser; p=c_parser.CParser(); a=p.parse('typedef int T;'); b=p.parse('int T;'); result=(len(a.ext),len(b.ext))"), [1, 1])
    check("parser_constructor_options", execute_script("from pycparser import c_parser; result=type(c_parser.CParser(lex_optimize=False,yacc_debug=True)).__name__"), "CParser")
    check("generate_decl", execute_script("from pycparser import c_parser, c_generator; result=c_generator.CGenerator().visit(c_parser.CParser().parse('int x;'))"), "int x;\n")
    check("generate_function", execute_script("from pycparser import c_parser, c_generator; result=c_generator.CGenerator().visit(c_parser.CParser().parse('int f(){return 1;}'))"), "int f()\n{\n  return 1;\n}\n\n")
    check("generate_expression", execute_script("from pycparser import c_parser, c_generator; result=c_generator.CGenerator().visit(c_parser.CParser().parse('int x=a+b*2;'))"), "int x = a + (b * 2);\n")
    check("generate_control", execute_script("from pycparser import c_parser, c_generator; result=c_generator.CGenerator().visit(c_parser.CParser().parse('int f(int x){if(x)return 1;else return 0;}'))"), "int f(int x)\n{\n  if (x)\n    return 1;\n  else\n    return 0;\n}\n\n")
    check("generate_aggregate", execute_script("from pycparser import c_parser, c_generator; result=c_generator.CGenerator().visit(c_parser.CParser().parse('struct S{int x;};'))"), "struct S\n{\n  int x;\n};\n")
    check("generate_parentheses", execute_script("from pycparser import c_parser, c_generator; n=c_parser.CParser().parse('int x=(a+b)*c;'); result=c_generator.CGenerator(reduce_parentheses=True).visit(n)"), "int x = (a + b) * c;\n")
    check("generator_visitor", execute_script("from pycparser import c_parser, c_generator\nclass G(c_generator.CGenerator):\n    def visit_ID(self,n): return n.name.upper()\nresult=G().visit(c_parser.CParser().parse('int x=a;'))"), "int x = A;\n")
    check("switch_transform", execute_script("from pycparser import c_parser, ast_transforms; n=c_parser.CParser().parse('void f(){switch(x){case 1: a=1; case 2: break;}}').ext[0].body.block_items[0]; result=ast_transforms.fix_switch_cases(n); result=(type(result.stmt.block_items[0]).__name__,len(result.stmt.block_items[0].stmts))"), ["Case", 1])
    check("atomic_transform", execute_script("from pycparser import c_parser, ast_transforms; n=c_parser.CParser().parse('int x;').ext[0]; result=ast_transforms.fix_atomic_specifiers(n) is n"), True)
    check("parse_file", execute_script("from pathlib import Path; import tempfile; from pycparser import parse_file; p=Path(tempfile.mkdtemp())/'x.c'; p.write_text('int x;'); result=type(parse_file(str(p))).__name__"), "FileAST")
    check("parse_file_custom_parser", execute_script("from pathlib import Path\nimport tempfile\nfrom pycparser import parse_file\nclass P:\n    def parse(self,text,filename): return (text,filename.endswith('x.c'))\np=Path(tempfile.mkdtemp())/'x.c'; p.write_text('int x;'); result=parse_file(str(p),parser=P())"), ["int x;", True])
    check("preprocess_file", execute_script("from pathlib import Path; import tempfile; from pycparser import preprocess_file; p=Path(tempfile.mkdtemp())/'x.c'; p.write_text('#define X 1\\nX'); result='1' in preprocess_file(str(p))"), True)
    check("parse_file_cpp", execute_script("from pathlib import Path; import tempfile; from pycparser import parse_file; p=Path(tempfile.mkdtemp())/'x.c'; p.write_text('int x;'); result=type(parse_file(str(p),use_cpp=True)).__name__"), "FileAST")

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
