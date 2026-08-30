from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def check(case_id: str, source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=3.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {
        "id": case_id,
        "status": "passed" if actual == expected else "failed",
        **({} if actual == expected else {"message": json.dumps(actual, sort_keys=True)}),
    }


CASES: list[tuple[str, str, object]] = [
    (
        "exports-version",
        "import uvicorn; result=[uvicorn.__version__, uvicorn.__all__, [uvicorn.Config.__name__, uvicorn.Server.__name__]]",
        {"ok": True, "value": ["0.52.4", ["main", "run", "Config", "Server"], ["Config", "Server"]]},
    ),
    (
        "metadata-version",
        "import importlib.metadata; result=importlib.metadata.version('uvicorn')",
        {"ok": True, "value": "0.52.4"},
    ),
    (
        "cli-help",
        "from click.testing import CliRunner; from uvicorn.main import main; r=CliRunner().invoke(main,['--help']); result=[r.exit_code, r.output.splitlines()[0], '--host' in r.output, '--workers' in r.output]",
        {"ok": True, "value": [0, "Usage: main [OPTIONS] APP", True, True]},
    ),
    (
        "cli-version",
        "from click.testing import CliRunner; from uvicorn.main import main; r=CliRunner().invoke(main,['--version']); result=[r.exit_code, r.output.startswith('Running uvicorn 0.52.4 with CPython 3.12.14 on Linux')]",
        {"ok": True, "value": [0, True]},
    ),
    (
        "ansi-style",
        "from uvicorn._ansi import style; result=[style('x'), style('x',fg='red'), style('x',fg='cyan',bold=True)]",
        {"ok": True, "value": ["x\u001b[0m", "\u001b[31mx\u001b[0m", "\u001b[36m\u001b[1mx\u001b[0m"]},
    ),
    (
        "importer-passthrough",
        "from uvicorn.importer import import_from_string; obj=object(); result=import_from_string(obj) is obj",
        {"ok": True, "value": True},
    ),
    (
        "importer-nested",
        "from uvicorn.importer import import_from_string; result=import_from_string('json:decoder.JSONDecoder').__name__",
        {"ok": True, "value": "JSONDecoder"},
    ),
    (
        "importer-invalid-format",
        "from uvicorn.importer import import_from_string; import_from_string('example:')",
        {"ok": False, "value": None, "exception_type": "uvicorn.importer.ImportFromStringError", "exception_message": "Import string \"example:\" must be in format \"<module>:<attribute>\"."},
    ),
    (
        "importer-invalid-module",
        "from uvicorn.importer import import_from_string; import_from_string('module_does_not_exist:app')",
        {"ok": False, "value": None, "exception_type": "uvicorn.importer.ImportFromStringError", "exception_message": "Could not import module \"module_does_not_exist\"."},
    ),
    (
        "importer-invalid-attribute",
        "from uvicorn.importer import import_from_string; import_from_string('json:no_such_attribute')",
        {"ok": False, "value": None, "exception_type": "uvicorn.importer.ImportFromStringError", "exception_message": "Attribute \"no_such_attribute\" not found in module \"json\"."},
    ),
    (
        "config-defaults",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\nc=Config(app,log_config=None); result=[c.host,c.port,c.loop,c.http,c.ws,c.lifespan,c.workers,c.proxy_headers,c.server_header,c.date_header,c.backlog,c.timeout_keep_alive,c.forwarded_allow_ips,c.loaded]",
        {"ok": True, "value": ["127.0.0.1", 8000, "auto", "auto", "auto", "auto", 1, True, True, True, 2048, 5, "127.0.0.1", False]},
    ),
    (
        "config-properties",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\na=Config(app,log_config=None,workers=2); b=Config('pkg:app',log_config=None,reload=True); c=Config(app,log_config=None,ssl_certfile='cert.pem'); result=[a.use_subprocess,a.should_reload,b.use_subprocess,b.should_reload,c.is_ssl]",
        {"ok": True, "value": [True, False, True, True, True]},
    ),
    (
        "config-load-asgi3",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\nc=Config(app,log_config=None,proxy_headers=False,http='h11',ws='none',loop='none',headers=[('X-Test','yes')]); c.load(); result=[c.loaded,c.interface,c.asgi_version,c.http_protocol_class.__name__,c.ws_protocol_class,c.lifespan_class.__name__,[[k.decode(),v.decode()] for k,v in c.encoded_headers],c.ssl]",
        {"ok": True, "value": [True, "asgi3", "3.0", "H11Protocol", None, "LifespanOn", [["server", "uvicorn"], ["x-test", "yes"]], None]},
    ),
    (
        "config-load-asgi2",
        "from uvicorn import Config\ndef app(scope):\n async def instance(receive,send): pass\n return instance\nc=Config(app,log_config=None,proxy_headers=False,http='h11',ws='none'); c.load(); result=[c.interface,c.asgi_version,type(c.loaded_app).__name__,c.loaded]",
        {"ok": True, "value": ["asgi2", "2.0", "ASGI2Middleware", True]},
    ),
    (
        "config-load-wsgi",
        "from uvicorn import Config\ndef app(environ,start_response): return []\nc=Config(app,interface='wsgi',log_config=None,proxy_headers=False,http='h11',ws='none'); c.load(); result=[c.interface,c.asgi_version,c.ws_protocol_class is None,callable(c.loaded_app)]",
        {"ok": True, "value": ["wsgi", "3.0", True, True]},
    ),
    (
        "config-factory",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\ndef make(): return app\nc=Config(make,factory=True,log_config=None,proxy_headers=False,http='h11',ws='none'); c.load(); result=[c.interface,c.loaded_app is app,c.loaded]",
        {"ok": True, "value": ["asgi3", True, True]},
    ),
    (
        "config-header-precedence",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\na=Config(app,log_config=None,proxy_headers=False,http='h11',ws='none',headers=[('Server','custom'),('X-Name','café')]); a.load(); b=Config(app,log_config=None,proxy_headers=False,http='h11',ws='none',server_header=False); b.load(); result=[[[k.decode('latin1'),v.decode('latin1')] for k,v in a.encoded_headers],b.encoded_headers]",
        {"ok": True, "value": [[ ["server", "custom"], ["x-name", "café"] ], []]},
    ),
    (
        "config-loop-factories",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\na=Config(app,loop='none',log_config=None); b=Config(app,loop='asyncio',log_config=None); factory=b.get_loop_factory(); loop=factory(); result=[a.get_loop_factory(),type(loop).__name__]; loop.close()",
        {"ok": True, "value": [None, "_UnixSelectorEventLoop"]},
    ),
    (
        "config-setup-event-loop",
        "from uvicorn import Config\nasync def app(scope,receive,send): pass\nConfig(app,log_config=None).setup_event_loop()",
        {"ok": False, "value": None, "exception_type": "builtins.AttributeError", "exception_message": "The `setup_event_loop` method was replaced by `get_loop_factory` in uvicorn 0.36.0.\nNone of those methods are supposed to be used directly. If you are doing it, please let me know here: https://github.com/Kludex/uvicorn/discussions/2706. Thank you, and sorry for the inconvenience."},
    ),
    (
        "reload-patterns",
        "import os,tempfile; from pathlib import Path; from uvicorn.config import resolve_reload_patterns\nwith tempfile.TemporaryDirectory() as td:\n root=Path(td); app=root/'app'; sub=app/'sub'; ext=root/'ext'; sub.mkdir(parents=True); ext.mkdir(); old=Path.cwd(); os.chdir(root)\n try: patterns,dirs=resolve_reload_patterns(['*.py',str(ext)],[str(app),str(sub)]); result=[set(patterns)=={'*.py',str(ext)},sorted(p.name for p in dirs)]\n finally: os.chdir(old)",
        {"ok": True, "value": [True, ["app", "ext"]]},
    ),
    (
        "formatter-default",
        "import logging; from uvicorn.logging import DefaultFormatter\nr=logging.LogRecord('x',logging.INFO,'',0,'hello %s',('world',),None); result=DefaultFormatter('%(levelprefix)s %(message)s',use_colors=False).format(r)",
        {"ok": True, "value": "INFO:     hello world"},
    ),
    (
        "formatter-access",
        "import logging; from uvicorn.logging import AccessFormatter\nr=logging.LogRecord('x',logging.INFO,'',0,'%s - \"%s %s HTTP/%s\" %d',('127.0.0.1:4','GET','/x?q=1','1.1',201),None); result=AccessFormatter('%(levelprefix)s %(client_addr)s - \"%(request_line)s\" %(status_code)s',use_colors=False).format(r)",
        {"ok": True, "value": "INFO:     127.0.0.1:4 - \"GET /x?q=1 HTTP/1.1\" 201 Created"},
    ),
    (
        "formatter-unknown-status",
        "from uvicorn.logging import AccessFormatter; f=AccessFormatter(use_colors=False); result=[f.get_status_code(204),f.get_status_code(599)]",
        {"ok": True, "value": ["204 No Content", "599 "]},
    ),
    (
        "message-placeholders",
        "from uvicorn.middleware.message_logger import message_with_placeholders\nm={'type':'http.response.body','body':b'abc','text':'hello','headers':[(b'x',b'y')],'other':1}; result=[message_with_placeholders(m),m['body']]",
        {"ok": True, "value": [{"type": "http.response.body", "body": "<3 bytes>", "text": "<5 chars>", "headers": "<...>", "other": 1}, "b'abc'"]},
    ),
    (
        "proxy-trusted-http",
        "import asyncio; from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware\nasync def main():\n out=[]\n async def app(scope,receive,send): out.extend([scope['scheme'],scope['client']])\n scope={'type':'http','scheme':'http','client':('127.0.0.1',5000),'headers':[(b'x-forwarded-proto',b'https'),(b'x-forwarded-for',b'203.0.113.9:4321')]}\n async def receive(): return {}\n async def send(message): pass\n await ProxyHeadersMiddleware(app)(scope,receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": ["https", ["203.0.113.9", 4321]]},
    ),
    (
        "proxy-untrusted",
        "import asyncio; from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware\nasync def main():\n out=[]\n async def app(scope,receive,send): out.extend([scope['scheme'],scope['client']])\n scope={'type':'http','scheme':'http','client':('10.0.0.9',5000),'headers':[(b'x-forwarded-proto',b'https'),(b'x-forwarded-for',b'203.0.113.9')]}\n async def receive(): return {}\n async def send(message): pass\n await ProxyHeadersMiddleware(app,trusted_hosts=['127.0.0.1'])(scope,receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": ["http", ["10.0.0.9", 5000]]},
    ),
    (
        "proxy-websocket",
        "import asyncio; from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware\nasync def main():\n out=[]\n async def app(scope,receive,send): out.append(scope['scheme'])\n scope={'type':'websocket','scheme':'ws','client':('127.0.0.1',1),'headers':[(b'x-forwarded-proto',b'https')]}\n async def receive(): return {}\n async def send(message): pass\n await ProxyHeadersMiddleware(app)(scope,receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": ["wss"]},
    ),
    (
        "proxy-network-and-port",
        "import asyncio; from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware\nasync def main():\n out=[]\n async def app(scope,receive,send): out.append(scope['client'])\n scope={'type':'http','scheme':'http','client':('127.0.0.1',1),'headers':[(b'x-forwarded-for',b'1.2.3.4:1234, [2001:db8::1]:8080, 10.1.2.3:9000')]}\n async def receive(): return {}\n async def send(message): pass\n await ProxyHeadersMiddleware(app,['127.0.0.1','10.0.0.0/8','2001:db8::/32'])(scope,receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": [["1.2.3.4", 1234]]},
    ),
    (
        "proxy-duplicate-headers",
        "import asyncio; from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware\nasync def main():\n out=[]\n async def app(scope,receive,send): out.append(scope['client'])\n scope={'type':'http','scheme':'http','client':('127.0.0.1',1),'headers':[(b'x-forwarded-for',b'1.1.1.1'),(b'x-forwarded-for',b'2.2.2.2')]}\n async def receive(): return {}\n async def send(message): pass\n await ProxyHeadersMiddleware(app)(scope,receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": [["2.2.2.2", 0]]},
    ),
    (
        "proxy-lifespan",
        "import asyncio; from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware\nasync def main():\n out=[]\n async def app(scope,receive,send): out.append(scope['type'])\n async def receive(): return {}\n async def send(message): pass\n await ProxyHeadersMiddleware(app)({'type':'lifespan'},receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": ["lifespan"]},
    ),
    (
        "path-query",
        "from uvicorn.protocols.utils import get_path_with_query_string; result=[get_path_with_query_string({'path':'/a b/café','query_string':b'q=1'}),get_path_with_query_string({'path':'/','query_string':b''})]",
        {"ok": True, "value": ["/a%20b/caf%C3%A9?q=1", "/"]},
    ),
    (
        "client-addresses",
        "from uvicorn.protocols.utils import get_client_addr; result=[get_client_addr({'client':('127.0.0.1',36000)}),get_client_addr({'client':None}),get_client_addr({})]",
        {"ok": True, "value": ["127.0.0.1:36000", "", ""]},
    ),
    (
        "transport-addresses",
        "from uvicorn.protocols.utils import get_remote_addr,get_local_addr\nclass T:\n def __init__(self,d): self.d=d\n def get_extra_info(self,n): return self.d.get(n)\nresult=[get_remote_addr(T({'peername':['1.2.3.4',80]})),get_remote_addr(T({})),get_local_addr(T({'sockname':'/tmp/a.sock'})),get_local_addr(T({'sockname':('::1',90)}))]",
        {"ok": True, "value": [["1.2.3.4", 80], None, ["/tmp/a.sock", None], ["::1", 90]]},
    ),
    (
        "socket-addresses",
        "from uvicorn.protocols.utils import get_remote_addr,get_local_addr\nclass S:\n def getpeername(self): return ('5.6.7.8',123)\n def getsockname(self): return '/tmp/u.sock'\nclass T:\n def get_extra_info(self,n): return S() if n=='socket' else None\nresult=[get_remote_addr(T()),get_local_addr(T())]",
        {"ok": True, "value": [["5.6.7.8", 123], ["/tmp/u.sock", None]]},
    ),
    (
        "transport-ssl",
        "from uvicorn.protocols.utils import is_ssl\nclass T:\n def __init__(self,v): self.v=v\n def get_extra_info(self,n): return self.v if n=='sslcontext' else None\nresult=[is_ssl(T(object())),is_ssl(T(None))]",
        {"ok": True, "value": [True, False]},
    ),
    (
        "wsgi-environ",
        "import io; from uvicorn.middleware.wsgi import build_environ\nscope={'type':'http','method':'POST','root_path':'/root','path':'/root/café','query_string':b'a=1','http_version':'1.1','scheme':'https','server':('example.com',8443),'client':('1.2.3.4',99),'headers':[(b'content-type',b'text/plain'),(b'content-length',b'5'),(b'x-tag',b'one'),(b'x-tag',b'two')]}; body=io.BytesIO(b'hello'); e=build_environ(scope,{'type':'http.request'},body); result=[e['REQUEST_METHOD'],e['SCRIPT_NAME'],e['PATH_INFO'],e['QUERY_STRING'],e['SERVER_PROTOCOL'],e['wsgi.url_scheme'],e['SERVER_NAME'],e['SERVER_PORT'],e['REMOTE_ADDR'],e['CONTENT_TYPE'],e['CONTENT_LENGTH'],e['HTTP_X_TAG'],e['wsgi.input'].read().decode()]",
        {"ok": True, "value": ["POST", "/root", "/cafÃ©", "a=1", "HTTP/1.1", "https", "example.com", 8443, "1.2.3.4", "text/plain", "5", "one,two", "hello"]},
    ),
    (
        "asgi2-middleware",
        "import asyncio; from uvicorn.middleware.asgi2 import ASGI2Middleware\nasync def main():\n out=[]\n def app(scope):\n  async def instance(receive,send): await send({'type':'done','value':scope['value']})\n  return instance\n async def receive(): return {}\n async def send(message): out.append(message)\n await ASGI2Middleware(app)({'value':7},receive,send); return out\nresult=asyncio.run(main())",
        {"ok": True, "value": [{"type": "done", "value": 7}]},
    ),
    (
        "service-unavailable",
        "import asyncio; from uvicorn.protocols.http.flow_control import service_unavailable\nasync def main():\n out=[]\n async def receive(): return {}\n async def send(message): out.append(message)\n await service_unavailable({'type':'http'},receive,send); return [[m['type'],m.get('status'),[[k.decode(),v.decode()] for k,v in m.get('headers',[])],m.get('body',b'').decode(),m.get('more_body')] for m in out]\nresult=asyncio.run(main())",
        {"ok": True, "value": [["http.response.start", 503, [["content-type", "text/plain; charset=utf-8"], ["content-length", "19"], ["connection", "close"]], "", None], ["http.response.body", None, [], "Service Unavailable", False]]},
    ),
    (
        "flow-control",
        "import asyncio; from uvicorn.protocols.http.flow_control import FlowControl\nclass T:\n def __init__(self): self.calls=[]\n def pause_reading(self): self.calls.append('pause')\n def resume_reading(self): self.calls.append('resume')\nasync def main():\n t=T(); f=FlowControl(t); f.pause_reading(); f.pause_reading(); f.resume_reading(); f.resume_reading(); f.pause_writing(); before=f.write_paused; f.resume_writing(); await f.drain(); return [t.calls,f.read_paused,before,f.write_paused]\nresult=asyncio.run(main())",
        {"ok": True, "value": [["pause", "resume"], False, True, False]},
    ),
    (
        "server-state",
        "from uvicorn.server import ServerState; s=ServerState(); result=[s.total_requests,len(s.connections),len(s.tasks),s.default_headers]",
        {"ok": True, "value": [0, 0, 0, []]},
    ),
    (
        "server-request-limit",
        "from uvicorn import Config,Server\nasync def app(scope,receive,send): pass\na=Server(Config(app,log_config=None,limit_max_requests=None)); b=Server(Config(app,log_config=None,limit_max_requests=7,limit_max_requests_jitter=0)); result=[a.limit_max_requests,b.limit_max_requests,b.started,b.should_exit,b.force_exit]",
        {"ok": True, "value": [None, 7, False, False, False]},
    ),
    (
        "lifespan-off",
        "import asyncio; from uvicorn.lifespan.off import LifespanOff\nasync def main():\n x=LifespanOff(None); await x.startup(); x.state['a']=1; await x.shutdown(); return [x.should_exit,x.state]\nresult=asyncio.run(main())",
        {"ok": True, "value": [False, {"a": 1}]},
    ),
    (
        "auto-protocols",
        "from uvicorn.protocols.http.auto import AutoHTTPProtocol; from uvicorn.protocols.websockets.auto import AutoWebSocketsProtocol; from uvicorn.loops.auto import auto_loop_factory\nf=auto_loop_factory(); loop=f(); result=[AutoHTTPProtocol.__name__,AutoWebSocketsProtocol,type(loop).__name__]; loop.close()",
        {"ok": True, "value": ["H11Protocol", None, "_UnixSelectorEventLoop"]},
    ),
    (
        "public-constants",
        "from uvicorn.config import LOG_LEVELS,INTERFACES,STARTUP_FAILURE; from uvicorn.logging import TRACE_LOG_LEVEL; from uvicorn.protocols.http.flow_control import HIGH_WATER_LIMIT,CLOSE_HEADER; result=[LOG_LEVELS,INTERFACES,STARTUP_FAILURE,TRACE_LOG_LEVEL,HIGH_WATER_LIMIT,CLOSE_HEADER]",
        {"ok": True, "value": [{"critical": 50, "error": 40, "warning": 30, "info": 20, "debug": 10, "trace": 5}, ["auto", "asgi3", "asgi2", "wsgi"], 3, 5, 65536, ["b'connection'", "b'close'"]]},
    ),
    (
        "config-bad-app-exit",
        "from uvicorn import Config\ntry: Config('module_does_not_exist:app',log_config=None,http='h11',ws='none').load()\nexcept SystemExit as exc: result=exc.code",
        {"ok": True, "value": 3},
    ),
]


def main() -> None:
    leaves = [check(case_id, source, expected) for case_id, source, expected in CASES]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
