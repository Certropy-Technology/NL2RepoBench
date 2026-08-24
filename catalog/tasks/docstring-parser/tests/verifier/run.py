import json
import os
import subprocess
import sys
from pathlib import Path

EXPECTED = 20
ADAPTER = Path(__file__).with_name("adapter.py")

def doc(style, short, meta=(), long=None, blank_short=False, blank_long=False):
    return {"short_description": short, "long_description": long, "blank_after_short_description": blank_short, "blank_after_long_description": blank_long, "style": style, "meta": list(meta)}
def param(args, description, arg_name, type_name, optional, default=None):
    return {"kind":"DocstringParam", "args":args, "description":description, "arg_name":arg_name, "type_name":type_name, "is_optional":optional, "default":default}
def ret(args, description, type_name, generator=False, return_name=None):
    return {"kind":"DocstringReturns", "args":args, "description":description, "type_name":type_name, "is_generator":generator, "return_name":return_name}
def raised(args, description, type_name):
    return {"kind":"DocstringRaises", "args":args, "description":description, "type_name":type_name}
def meta(args, description):
    return {"kind":"DocstringMeta", "args":args, "description":description}

CASES = [
 {"id":"api-surface", "request":{"operation":"api"}, "expected":{"root_exports":["parse","parse_from_object","combine_docstrings","compose","ParseError","Docstring","DocstringMeta","DocstringParam","DocstringRaises","DocstringReturns","DocstringDeprecated","DocstringStyle","RenderingStyle","Style"],"style_members":["REST","GOOGLE","NUMPYDOC","EPYDOC","AUTO"],"rendering_members":["COMPACT","CLEAN","EXPANDED"],"style_alias":True}},
 {"id":"parse-none", "request":{"operation":"parse","style":"AUTO","text":None}, "expected":doc("REST",None)},
 {"id":"parse-rest", "request":{"operation":"parse","style":"REST","text":"Brief.\n\nDetails.\n\n:param int? count: records, defaults to 3.\n:type count: int\n:returns list[str]: values"}, "expected":doc("REST","Brief.",[param(["param","int?","count"],"records, defaults to 3.","count","int",True,"3"),ret(["returns","list[str]"],"values","list[str]")],long="Details.",blank_short=True,blank_long=True)},
 {"id":"parse-google", "request":{"operation":"parse","style":"GOOGLE","text":"Brief.\n\nArgs:\n    count (int, optional): number of records. Defaults to 3.\nReturns:\n    bytes | memoryview: encoded values"}, "expected":doc("GOOGLE","Brief.",[param(["param","count (int, optional)"],"number of records. Defaults to 3.","count","int",True,"3"),ret(["returns","bytes | memoryview"],"encoded values","bytes | memoryview")],blank_short=True)},
 {"id":"parse-numpydoc", "request":{"operation":"parse","style":"NUMPYDOC","text":"Brief.\n\nParameters\n----------\ncount : int, optional\n    number of records\n\nReturns\n-------\nlist[str]\n    values"}, "expected":doc("NUMPYDOC","Brief.",[param(["param","count"],"number of records","count","int",True),ret(["returns"],"values","list[str]")],blank_short=True)},
 {"id":"parse-epydoc", "request":{"operation":"parse","style":"EPYDOC","text":"Brief.\n\n@param count: number of records\n@type count: int\n@return: values\n@rtype: list[str]"}, "expected":doc("EPYDOC","Brief.",[param(["param","count"],"number of records","count","int",False),ret(["return"],"values","list[str]")],blank_short=True)},
 {"id":"parse-auto", "request":{"operation":"parse","style":"AUTO","text":"Brief.\n\nArgs:\n    value (int): number\n"}, "expected":doc("GOOGLE","Brief.",[param(["param","value (int)"],"number","value","int",False)],blank_short=True)},
 {"id":"parse-unicode", "request":{"operation":"parse","style":"REST","text":"Résumé — 東京\n\n:param str name: café"}, "expected":doc("REST","Résumé — 東京",[param(["param","str","name"],"café","name","str",False)],blank_short=True)},
 {"id":"parse-google-yields", "request":{"operation":"parse","style":"GOOGLE","text":"Streaming.\n\nYields:\n    bytes | memoryview: chunks"}, "expected":doc("GOOGLE","Streaming.",[ret(["yields","bytes | memoryview"],"chunks","bytes | memoryview",True)],blank_short=True)},
 {"id":"parse-numpydoc-raises", "request":{"operation":"parse","style":"NUMPYDOC","text":"Lookup.\n\nRaises\n------\nKeyError\n    when key is absent"}, "expected":doc("NUMPYDOC","Lookup.",[raised(["raises","KeyError"],"when key is absent","KeyError")],blank_short=True)},
 {"id":"dialect-rest", "request":{"operation":"dialect_parse","dialect":"rest","style":"REST","text":"Summary.\n\n:custom flag: value"}, "expected":doc("REST","Summary.",[meta(["custom","flag"],"value")],blank_short=True)},
 {"id":"dialect-google", "request":{"operation":"dialect_parse","dialect":"google","style":"GOOGLE","text":"Streaming.\n\nYields:\n    bytes | memoryview: chunks"}, "expected":doc("GOOGLE","Streaming.",[ret(["yields","bytes | memoryview"],"chunks","bytes | memoryview",True)],blank_short=True)},
 {"id":"dialect-numpydoc", "request":{"operation":"dialect_parse","dialect":"numpydoc","style":"NUMPYDOC","text":"Lookup.\n\nRaises\n------\nKeyError\n    when key is absent"}, "expected":doc("NUMPYDOC","Lookup.",[raised(["raises","KeyError"],"when key is absent","KeyError")],blank_short=True)},
 {"id":"dialect-epydoc", "request":{"operation":"dialect_parse","dialect":"epydoc","style":"EPYDOC","text":"Lookup.\n\n@raise KeyError: when key is absent"}, "expected":doc("EPYDOC","Lookup.",[raised(["raise","KeyError"],"when key is absent","KeyError")],blank_short=True)},
 {"id":"compose-rest-expanded", "request":{"operation":"parse_compose","style":"REST","rendering":"EXPANDED","indent":"  ","text":"Brief.\n\n:param int? count: records\n:returns list[str]: values"}, "expected":"Brief.\n\n:param count:\n  records\n:type count: int?\n:returns:\n  values\n:rtype: list[str]"},
 {"id":"compose-google-compact", "request":{"operation":"parse_compose","style":"GOOGLE","rendering":"COMPACT","indent":"  ","text":"Brief.\n\nArgs:\n    count (int, optional): records"}, "expected":"Brief.\n\nArgs:\n  count (int?): records"},
 {"id":"compose-numpydoc-compact", "request":{"operation":"parse_compose","style":"NUMPYDOC","rendering":"COMPACT","indent":"  ","text":"Brief.\n\nParameters\n----------\ncount : int\n    records"}, "expected":"Brief.\n\n\nParameters\n----------\ncount : int\n  records"},
 {"id":"compose-epydoc-clean", "request":{"operation":"dialect_parse_compose","dialect":"epydoc","style":"EPYDOC","rendering":"CLEAN","indent":"  ","text":"Brief.\n\n@param count: records\n@type count: int"}, "expected":"Brief.\n\n@type count: int\n@param count:\n  records"},
 {"id":"compose-model-rest", "request":{"operation":"compose_model","dialect":"root","style":"REST","rendering":"COMPACT","indent":"  ","doc":doc("REST","Count records",[param(["param","int","count"],"number of records","count","int",False),ret(["returns","list[str]"],"records","list[str]")])}, "expected":"Count records\n:param int count: number of records\n:returns list[str]: records"},
 {"id":"rest-error", "request":{"operation":"parse","style":"REST","text":":param one two three: bad"}, "expected_error":"docstring_parser.common.ParseError"},
]

def invoke(request):
    payload=json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    command=[sys.executable, "-I", "-B", "-", "--candidate-site", os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"), "--request", payload]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") != "1":
        command=["runuser", "-u", "candidate", "--", "env", "HOME=/home/candidate", "PYTHONDONTWRITEBYTECODE=1", "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1", *command]
    try:
        result=subprocess.run(command, input=ADAPTER.read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok":False,"exception_type":"VerifierProcessError","exception_message":str(exc)}
    lines=[line for line in result.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
    if result.returncode != 0 or len(lines) != 1:
        return {"ok":False,"exception_type":"CandidateProcessError","exception_message":(result.stderr.decode("utf-8", "replace") or result.stdout.decode("utf-8", "replace"))[-2000:]}
    try:
        return json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok":False,"exception_type":"CandidateProtocolError","exception_message":str(exc)}

def main():
    leaves=[]
    for case in CASES:
        result=invoke(case["request"])
        if "expected_error" in case:
            passed=result.get("ok") is False and result.get("exception_type") == case["expected_error"]
        else:
            passed=result.get("ok") is True and result.get("value") == case["expected"]
        leaf={"id":"docstring-parser/"+case["id"],"status":"passed" if passed else "failed"}
        if not passed:
            leaf["message"]=json.dumps({"expected":case.get("expected",case.get("expected_error")),"actual":result},ensure_ascii=False,sort_keys=True)[:1000]
        leaves.append(leaf)
    print(json.dumps({"schema_version":"1.0","leaves":leaves},ensure_ascii=False,sort_keys=True,separators=(",", ":")))

if __name__ == "__main__":
    main()
