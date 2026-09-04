#!/usr/bin/env python3
"""Trusted parent for the frozen sqlparse subprocess scenarios."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
CANDIDATE_UID = 10001
CANDIDATE_USER = "candidate"
RUNUSER = shutil.which("runuser") or "/usr/sbin/runuser"
ADAPTER_SOURCE = Path(__file__).with_name("adapter.py")
CASE_TIMEOUT_SEC = 15.0
EXPECTED = json.loads(r'''{"api-surface":{"all":["engine","filters","formatter","sql","tokens","cli"],"classes":["Exception","Lexer"],"modules":["sqlparse.engine","sqlparse.filters","sqlparse.formatter","sqlparse.keywords","sqlparse.lexer","sqlparse.sql","sqlparse.tokens","sqlparse.utils"],"root":{"format":true,"parse":true,"parsestream":true,"split":true},"version":"0.5.4.dev0"},"format-case":{"capitalize_upper":"Select FOO, \"Bar\" From MYTABLE Where FOO = 1; -- select Foo\n","upper_lower":"SELECT foo, \"Bar\" FROM mytable WHERE foo = 1; -- select Foo\n"},"format-invalid-options":[["SQLParseError","Invalid value for keyword_case: 'sideways'"],["SQLParseError","Invalid value for identifier_case: 'sideways'"],["SQLParseError","Unknown output format: 'json'"],["SQLParseError","indent_width requires a positive integer"],["SQLParseError","wrap_after requires a positive integer"],["SQLParseError","comma_first requires a boolean value"]],"format-layout-options":{"comma_first":"SELECT alpha,beta\n     , gamma\n     , delta\nFROM SAMPLE\nWHERE alpha=1","tabs":"SELECT a,\n\tb\nFROM t\nWHERE x=1"},"format-operators":"SELECT a + b * c, x >= 10, payload ->> 'name' FROM t","format-reindent":"SELECT a,\n       b,\n       sum(c) AS total\nFROM sales\nWHERE x=1\n  AND y IN\n    (SELECT y\n     FROM allowed)\nORDER BY a,\n         b","format-string-output":{"python":"sql = 'select 1;'\nsql2 = ' '\n        'select \\'x\\';'","sql":"select 1","truncate":"SELECT 'abcdefgh[...]', name FROM t"},"format-whitespace-comments":{"both":"select a from t where (1 = 2)","comments":"select  a\nfrom   t  where ( 1 = 2 )\n"},"function-parameters":{"alias":"value","name":"calc","parameter_classes":["Identifier","Token","Function"],"parameter_values":["a","2","nested('x')"],"within":[true,true,true]},"identifier-list":[{"alias":null,"name":"a","parent":null,"real":"a","value":"a","wildcard":false},{"alias":"bee","name":"bee","parent":null,"real":"b","value":"b AS bee","wildcard":false},{"alias":null,"name":"c","parent":"sch","real":"c","value":"sch.c","wildcard":false},{"alias":null,"name":"*","parent":"d","real":"*","value":"d.*","wildcard":true}],"identifier-metadata":{"select":{"alias":"Alias","has_alias":true,"name":"Alias","parent":"sch","real":"tbl","value":"sch.tbl.col AS \"Alias\"","wildcard":false},"table":{"alias":"u","name":"u","parent":"db","real":"users","value":"db.users u"}},"lexer-customization":{"custom":[["Token.Keyword","foobar"],["Token.Name","baz"]],"is_keyword":["Token.Keyword.DML","select"],"reset":[["Token.Keyword.DML","select"],["Token.Name","foobar"]]},"lexer-inputs":{"bytes":[["Token.Keyword.DML","SELECT"],["Token.Text.Whitespace"," "],["Token.Name","café"]],"error":["Token.Error","{"],"singleton":true,"stream":[["Token.Keyword.DML","SELECT"],["Token.Text.Whitespace"," "],["Token.Name","ö"]]},"nested-groups":{"flatten":[["Token.Keyword.DML","SELECT"],["Token.Text.Whitespace"," "],["Token.Punctuation","("],["Token.Name","a"],["Token.Text.Whitespace"," "],["Token.Operator","+"],["Token.Text.Whitespace"," "],["Token.Literal.Number.Integer","2"],["Token.Punctuation",")"],["Token.Text.Whitespace"," "],["Token.Keyword","AS"],["Token.Text.Whitespace"," "],["Token.Name","total"],["Token.Text.Whitespace"," "],["Token.Keyword","FROM"],["Token.Text.Whitespace"," "],["Token.Punctuation","("],["Token.Keyword.DML","SELECT"],["Token.Text.Whitespace"," "],["Token.Name","a"],["Token.Text.Whitespace"," "],["Token.Keyword","FROM"],["Token.Text.Whitespace"," "],["Token.Name","t"],["Token.Punctuation",")"],["Token.Text.Whitespace"," "],["Token.Name","sub"]],"groups":["Identifier","Identifier"],"offset_token":"a","parentheses":["(",")","(",")"],"within_identifier":true},"parse-preservation":{"container":"tuple","count":1,"first":["Token.Keyword.DML","SELECT"],"type":"SELECT","value":"select\r\n* from café;"},"parsestream-behavior":{"classes":["Statement","Statement"],"generator":"generator","types":["SELECT","UPDATE"],"values":["SELECT 1; ","UPDATE t SET x = 2;"]},"split-basic":{"normal":["select 'a;b' AS value;","select 2;"],"stripped":["select 'a;b' AS value","select 2"]},"split-comments":["select 1; -- first","select 2;"],"split-dollar-quoted":["CREATE FUNCTION f() RETURNS void AS $$BEGIN RAISE NOTICE 'x;y'; END;$$ LANGUAGE plpgsql;","SELECT 2;"],"statement-types":[["SELECT 1","SELECT"],["INSERT INTO t VALUES (1)","INSERT"],["UPDATE t SET x = 1","UPDATE"],["DELETE FROM t","DELETE"],["CREATE TABLE t (x int)","CREATE"],["DROP TABLE t","DROP"],["WITH q AS (SELECT 1) SELECT * FROM q","SELECT"],["EXPLAIN SELECT 1","UNKNOWN"],["foo bar","UNKNOWN"]],"token-helpers":{"keyword":{"is_keyword":true,"match_exact":true,"match_regex":true,"normalized":"SELECT"},"name":{"case_sensitive":false,"exact":true,"normalized":"Foo"},"navigation":{"first_all":" ","first_code":"SELECT","next":[6,"col","Identifier"],"previous":[2,"SELECT"]}},"token-hierarchy":{"aliases":[true,true,true],"membership":[true,true,true,true,false],"names":["Token.Keyword","Token.Keyword.DML","Token.Name.Placeholder","Token.Literal.String.Single","Token.Literal.Number.Float"]},"tokenize-comments-placeholders":[["Token.Comment.Single","-- head\n"],["Token.Keyword.DML","SELECT"],["Token.Name.Placeholder",":name"],["Token.Punctuation",","],["Token.Name.Placeholder",":1"],["Token.Punctuation",","],["Token.Name.Placeholder","?"],["Token.Punctuation",","],["Token.Name.Placeholder","%s"],["Token.Punctuation",","],["Token.Name.Placeholder","%(item)s"],["Token.Punctuation",","],["Token.Name.Placeholder","$tag"],["Token.Comment.Multiline","/* tail */"]],"tokenize-literals":[["Token.Keyword","VALUES"],["Token.Punctuation","("],["Token.Literal.Number.Integer","-7"],["Token.Punctuation",","],["Token.Literal.Number.Float",".5"],["Token.Punctuation",","],["Token.Literal.Number.Float","6.02e23"],["Token.Punctuation",","],["Token.Literal.String.Single","'it''s'"],["Token.Punctuation",","],["Token.Literal.String.Symbol","\"Col\""],["Token.Punctuation",","],["Token.Name","`tick`"],["Token.Punctuation",","],["Token.Name","[bracket]"],["Token.Punctuation",")"],["Token.Punctuation",";"]],"tokenize-simple":{"generator":"generator","tokens":[["Token.Keyword.DML","select"],["Token.Text.Whitespace"," "],["Token.Wildcard","*"],["Token.Text.Whitespace"," "],["Token.Keyword","from"],["Token.Text.Whitespace"," "],["Token.Name","foo"],["Token.Punctuation",";"]]},"where-comparison":{"comparisons":[{"left":"age","operator":">=","right":"18","value":"age >= 18"},{"left":"status","operator":"=","right":"'active'","value":"status = 'active'"}],"where":"WHERE age >= 18 AND status = 'active'"}}''')


def _candidate_pids() -> list[int]:
    result = []
    for status in Path("/proc").glob("[0-9]*/status"):
        try:
            uid_line = next(line for line in status.read_text().splitlines() if line.startswith("Uid:"))
            if int(uid_line.split()[1]) == CANDIDATE_UID:
                result.append(int(status.parent.name))
        except (OSError, StopIteration, ValueError):
            pass
    return result


def _cleanup() -> None:
    for _ in range(10):
        pids = _candidate_pids()
        if not pids:
            return
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        import time
        time.sleep(0.02)
    if _candidate_pids():
        raise RuntimeError("candidate processes survived cleanup")


def run_case(scenario: str, workspace: Path) -> dict[str, str]:
    case_root = workspace / scenario
    case_root.mkdir()
    os.chown(case_root, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(case_root, 0o700)
    adapter = case_root / "adapter.py"
    adapter.write_bytes(ADAPTER_SOURCE.read_bytes())
    os.chown(adapter, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(adapter, 0o500)
    output = case_root / "observation.json"
    command = [
        RUNUSER, "-u", CANDIDATE_USER, "--", "env",
        "HOME=/home/candidate", "TMPDIR=/tmp", "PYTHONDONTWRITEBYTECODE=1",
        "PYTHONNOUSERSITE=1", "prlimit", "--as=536870912", "--cpu=10",
        "--fsize=16777216", "--nofile=128", "--nproc=32", "--",
        sys.executable, "-I", "-B", str(adapter), "--scenario", scenario,
        "--candidate-site", CANDIDATE_SITE, "--output", str(output),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=CASE_TIMEOUT_SEC, check=False)
    except subprocess.TimeoutExpired:
        _cleanup()
        return {"id": scenario, "status": "failed", "message": "child timeout"}
    except OSError as error:
        _cleanup()
        return {"id": scenario, "status": "failed", "message": f"child error: {error}"}
    try:
        if completed.returncode != 0 or not output.is_file():
            detail = (completed.stderr or completed.stdout)[-1200:]
            return {"id": scenario, "status": "failed", "message": f"no observation (exit {completed.returncode}): {detail}"}
        report = json.loads(output.read_text(encoding="utf-8"))
        if report.get("schema_version") != "1.0" or report.get("scenario") != scenario or report.get("ok") is not True:
            return {"id": scenario, "status": "failed", "message": json.dumps(report, sort_keys=True)[-1200:]}
        if report.get("value") != EXPECTED[scenario]:
            return {"id": scenario, "status": "failed", "message": "observation mismatch: " + json.dumps(report.get("value"), ensure_ascii=False, sort_keys=True)[-1000:]}
        return {"id": scenario, "status": "passed", "message": ""}
    except (OSError, json.JSONDecodeError) as error:
        return {"id": scenario, "status": "failed", "message": f"invalid observation: {error}"}
    finally:
        _cleanup()


def main() -> int:
    leaves = []
    try:
        with tempfile.TemporaryDirectory(prefix="sqlparse-verifier-") as temporary:
            workspace = Path(temporary)
            os.chown(workspace, CANDIDATE_UID, CANDIDATE_UID)
            os.chmod(workspace, 0o700)
            for scenario in EXPECTED:
                leaves.append(run_case(scenario, workspace))
    except BaseException as error:
        print(f"sqlparse verifier infrastructure error: {type(error).__name__}: {error}", file=sys.stderr)
        return 70
    if len(leaves) != len(EXPECTED) or {leaf["id"] for leaf in leaves} != set(EXPECTED):
        return 70
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
