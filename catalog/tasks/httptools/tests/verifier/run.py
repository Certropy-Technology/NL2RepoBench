from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys


ROOT = Path(__file__).parent
OPERATIONS = (
    "package_surface", "request_basic", "request_chunked", "request_upgrade", "request_lenient", "request_fragmented",
    "request_input_types", "request_invalid", "callback_error", "request_keep_alive", "response_basic",
    "response_upgrade", "response_invalid", "response_input_types", "response_callback_error", "url_components", "url_paths",
    "url_input_types", "url_invalid", "url_immutable",
)
EXPECTED = {
    "package_surface": {"version": "0.8.0", "exports": ["HTTPProtocol", "HttpParserCallbackError", "HttpParserError", "HttpParserInvalidMethodError", "HttpParserInvalidStatusError", "HttpParserInvalidURLError", "HttpParserUpgrade", "HttpRequestParser", "HttpResponseParser", "__version__", "parse_url", "parser"], "modules": [True, True, True, True, True], "native": [True, True]},
    "request_basic": {"events": [["begin"], ["url", "/hello?x=1"], ["header", "Host", "example.test"], ["header", "Connection", "close"], ["headers"], ["complete"]], "method": "GET", "version": "1.1", "keep_alive": True, "upgrade": False},
    "request_chunked": {"events": [["begin"], ["url", "/upload"], ["header", "Transfer-Encoding", "chunked"], ["headers"], ["chunk-header"], ["body", "hello"], ["chunk-complete"], ["chunk-header"], ["body", " world"], ["chunk-complete"], ["chunk-header"], ["chunk-complete"], ["complete"]], "method": "POST"},
    "request_upgrade": {"offset_tail": "raw", "upgrade": True, "events": [["begin"], ["url", "/chat"], ["header", "Host", "example.test"], ["header", "Connection", "Upgrade"], ["header", "Upgrade", "websocket"], ["headers"], ["complete"]]},
    "request_lenient": {"method": "GET", "events": [["begin"], ["url", "/"], ["header", "Host", "example.test"], ["headers"], ["complete"]]},
    "request_fragmented": {"events": [["begin"], ["url", "/"], ["url", ""], ["header", "Host", "localhost"], ["header", "Content-Length", "4"], ["headers"], ["body", "d"], ["body", "a"], ["body", "t"], ["body", "a"], ["complete"]], "method": "PUT"},
    "request_input_types": ["/a", "/b", "/c"],
    "request_invalid": ["HttpParserInvalidMethodError", "HttpParserInvalidURLError"],
    "callback_error": {name: ["HttpParserCallbackError", "RuntimeError"] for name in ("begin", "url", "headers", "header", "body", "complete")},
    "request_keep_alive": ["1.1", True, False],
    "response_basic": {"status": 200, "version": "1.1", "headers": [["Date", "Mon, 23 May 2005 22:38:34 GMT"], ["Server", "example"], ["Content-Type", "text/plain"], ["Content-Length", "5"], ["Connection", "close"]], "bodies": ["hello"], "events": ["begin", "status", "header", "header", "header", "header", "header", "headers", "body", "complete"]},
    "response_upgrade": {"status": 101, "tail": "raw", "upgrade": True, "events": ["begin", "status", "header", "header", "headers", "complete"]},
    "response_invalid": ["HttpParserError", "HttpParserInvalidStatusError"],
    "response_input_types": [200, 200, 200],
    "response_callback_error": ["HttpParserCallbackError", "RuntimeError"],
    "url_components": {"schema": "https", "host": "example.test", "port": 8443, "path": "/a/b", "query": "q=1", "fragment": "frag", "userinfo": "user:pass"},
    "url_paths": [[None, None, None, "////", None, None, None], [None, None, None, "/a/b", "x=1&", None, None], ["http", "1:2::3:4", 67, "/", None, None, None]],
    "url_input_types": ["/", "/x", "/y"],
    "url_invalid": ["HttpParserInvalidURLError"] * 5,
    "url_immutable": ["AttributeError", "attribute 'port' of 'httptools.parser.url_parser.URL' objects is not writable"],
}


def command(adapter: Path) -> list[str]:
    python = "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable
    args = ["env", "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", "prlimit", "--as=536870912", "--cpu=90", "--fsize=1048576", "--nofile=64", "--nproc=128", "--", python, "-I", str(adapter)]
    if os.geteuid() == 0:
        try:
            pwd.getpwnam("candidate")
        except KeyError:
            pass
        else:
            args = ["runuser", "-u", "candidate", "--", *args]
    return args


def collect() -> tuple[dict[str, object], str]:
    adapter = Path("/tmp/httptools-contract-adapter.py")
    shutil.copyfile(ROOT / "adapter.py", adapter)
    adapter.chmod(0o444)
    payload = "".join(json.dumps({"id": name, "operation": name}) + "\n" for name in OPERATIONS)
    env = os.environ.copy()
    env["NL2REPO_CANDIDATE_SITE"] = env.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
    try:
        completed = subprocess.run(command(adapter), input=payload, text=True, capture_output=True, timeout=180, check=False, env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, type(exc).__name__
    responses: dict[str, object] = {}
    for line in completed.stdout[:4 * 1024 * 1024].splitlines():
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(response, dict) and response.get("id") in OPERATIONS:
            responses[str(response["id"])] = response
    return responses, f"exit={completed.returncode}; stderr={completed.stderr[-1200:]}"


def main() -> None:
    responses, diagnostic = collect()
    leaves = []
    for name in OPERATIONS:
        response = responses.get(name)
        passed = isinstance(response, dict) and response.get("ok") is True and response.get("result") == EXPECTED[name]
        leaves.append({"id": f"httptools-contract::{name}", "status": "passed" if passed else "failed", "message": "" if passed else diagnostic})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
