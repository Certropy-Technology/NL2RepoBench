from __future__ import annotations

import json
import sys
from typing import Any

from nl2repobench.verification.candidate_client import CandidateCallResult, execute_script


def observe(source: str) -> Any:
    result = execute_script(source, timeout_sec=12.0)
    if not result.ok:
        return {"kind": "process-error", "type": result.exception_type, "message": result.exception_message}
    return result.value


def expect_exception(source: str, suffix: str) -> bool:
    value = observe(source)
    return isinstance(value, dict) and value.get("kind") == "exception" and str(value.get("type", "")).endswith(suffix)


def scenario(name: str, source: str, expected: Any) -> dict[str, str]:
    actual = observe(source)
    return {"id": name, "status": "passed" if actual == expected else "failed", "message": f"actual={actual!r} expected={expected!r}"}


def exception_scenario(name: str, source: str, suffix: str) -> dict[str, str]:
    actual = observe(source)
    ok = isinstance(actual, dict) and actual.get("kind") == "exception" and str(actual.get("type", "")).endswith(suffix)
    return {"id": name, "status": "passed" if ok else "failed", "message": f"actual={actual!r} expected exception={suffix}"}


def main() -> None:
    leaves: list[dict[str, str]] = []
    leaves.append(scenario("exports-and-version", "import urllib3\nresult=[urllib3.__version__, isinstance(urllib3.__version__, str)]", ["2.7.1.dev42", True]))
    leaves.append(scenario("url-http", "from urllib3.util import parse_url\nu=parse_url('http://Example.COM/a/b?x=1#frag')\nresult=[u.scheme,u.host,u.path,u.query,u.fragment,u.url]", ["http", "example.com", "/a/b", "x=1", "frag", "http://example.com/a/b?x=1#frag"]))
    leaves.append(scenario("url-auth-port", "from urllib3.util import parse_url\nu=parse_url('HTTP://User:Pass@Example.COM:8080/p')\nresult=[u.scheme,u.auth,u.host,u.port,u.url]", ["http", "User:Pass", "example.com", 8080, "http://User:Pass@example.com:8080/p"]))
    leaves.append(scenario("url-ipv6", "from urllib3.util import parse_url\nu=parse_url('http://[::1]:443/x')\nresult=[u.host,u.port,u.url]", ["[::1]", 443, "http://[::1]:443/x"]))
    leaves.append(scenario("url-query-fragment", "from urllib3.util import parse_url\nu=parse_url('https://example.com')\nresult=[u.path,u.query,u.fragment,u.url]", [None, None, None, "https://example.com"]))
    leaves.append(exception_scenario("url-invalid-port", "from urllib3.util import parse_url\ntry: parse_url('http://example.com:abc')\nexcept Exception as e: result={'kind':'exception','type':type(e).__module__+'.'+type(e).__qualname__,'message':str(e)}", "LocationParseError"))
    leaves.append(scenario("headers-case-insensitive", "from urllib3._collections import HTTPHeaderDict\nh=HTTPHeaderDict({'Content-Type':'text/plain'})\nresult=[h['content-type'],h.get('CONTENT-TYPE'),len(h),list(h.items())]", ["text/plain", "text/plain", 1, [["Content-Type", "text/plain"]]]))
    leaves.append(scenario("headers-repeat-order", "from urllib3._collections import HTTPHeaderDict\nh=HTTPHeaderDict(); h.add('X-Test','one'); h.add('x-test','two')\nresult=[h.getlist('X-TEST'),list(h.iteritems())]", [["one", "two"], [["X-Test", "one"], ["X-Test", "two"]]]))
    leaves.append(scenario("headers-combine", "from urllib3._collections import HTTPHeaderDict\nh=HTTPHeaderDict(); h.add('Accept','a'); h.add('accept','b',combine=True)\nresult=[h.get('ACCEPT'),list(h.items())]", ["a, b", [["Accept", "a, b"]]]))
    leaves.append(scenario("headers-copy", "from urllib3._collections import HTTPHeaderDict\nh=HTTPHeaderDict({'A':'1'}); c=h.copy(); c.add('B','2')\nresult=[list(h.items()),list(c.items()),h is c]", [[["A", "1"]], [["A", "1"], ["B", "2"]], False]))
    leaves.append(scenario("make-headers", "from urllib3.util import make_headers\nresult=make_headers(keep_alive=True,accept_encoding=['gzip','br'],user_agent='ua',disable_cache=True)", {"connection":"keep-alive","accept-encoding":"gzip,br","user-agent":"ua","cache-control":"no-cache"}))
    leaves.append(scenario("basic-auth", "from urllib3.util import make_headers\nresult=make_headers(basic_auth='u:p')", {"authorization":"Basic dTpw"}))
    leaves.append(scenario("content-type-guess", "from urllib3.fields import guess_content_type\nresult=[guess_content_type('a.json'),guess_content_type('a.txt'),guess_content_type('a.unknown'),guess_content_type(None)]", ["application/json","text/plain","application/octet-stream","application/octet-stream"]))
    leaves.append(scenario("request-field", "from urllib3.fields import RequestField\nf=RequestField('name','value',filename='a.txt'); f.make_multipart(content_type='text/plain')\nresult=f.render_headers()", "Content-Disposition: form-data; name=\"name\"; filename=\"a.txt\"\r\nContent-Type: text/plain\r\n\r\n"))
    leaves.append(scenario("multipart-fixed-boundary", "from urllib3.filepost import encode_multipart_formdata\nbody,ct=encode_multipart_formdata([('a','b'),('f',('x.txt',b'hi'))],boundary='BOUND')\nresult=[body.decode('latin1'),ct]", ["--BOUND\r\nContent-Disposition: form-data; name=\"a\"\r\n\r\nb\r\n--BOUND\r\nContent-Disposition: form-data; name=\"f\"; filename=\"x.txt\"\r\nContent-Type: text/plain\r\n\r\nhi\r\n--BOUND--\r\n", "multipart/form-data; boundary=BOUND"]))
    leaves.append(scenario("timeout-from-float", "from urllib3.util import Timeout\nt=Timeout.from_float(2.5)\nresult=[t.connect_timeout,t.read_timeout,t.total]", [2.5,2.5,None]))
    leaves.append(scenario("timeout-clone", "from urllib3.util import Timeout\nt=Timeout(total=5,connect=1,read=3); c=t.clone(); result=[c is t,c.total,c.connect_timeout,c.read_timeout]", [False,5,1,3]))
    leaves.append(exception_scenario("timeout-invalid", "from urllib3.util import Timeout\ntry: Timeout(connect=-1)\nexcept Exception as e: result={'kind':'exception','type':type(e).__module__+'.'+type(e).__qualname__,'message':str(e)}", "ValueError"))
    leaves.append(scenario("retry-from-int", "from urllib3.util import Retry\nr=Retry.from_int(3)\nresult=[r.total,r.redirect,r.raise_on_redirect,r.history]", [3,None,True,[]]))
    leaves.append(scenario("retry-is-retry", "from urllib3.util import Retry\nr=Retry(total=2,status_forcelist=[500],allowed_methods=['GET'])\nresult=[r.is_retry('GET',500),r.is_retry('POST',500),r.is_retry('GET',200)]", [True,False,False]))
    leaves.append(scenario("retry-backoff", "from urllib3.util import Retry\nr=Retry(total=2,backoff_factor=0.5)\nresult=[r.get_backoff_time(),r.increment(method='GET',url='/').get_backoff_time()]", [0,0]))
    leaves.append(scenario("retry-history", "from urllib3.util import Retry\nr=Retry(total=2); n=r.increment(method='GET',url='/')\nresult=[len(n.history),n.history[0].method,n.history[0].url,n.total]", [1,"GET","/",1]))
    leaves.append(exception_scenario("retry-exhausted", "from urllib3.util import Retry\nr=Retry(total=0)\ntry: r.increment(method='GET',url='/')\nexcept Exception as e: result={'kind':'exception','type':type(e).__module__+'.'+type(e).__qualname__,'message':str(e)}", "MaxRetryError"))
    leaves.append(scenario("response-read", "import io\nfrom urllib3.response import HTTPResponse\nr=HTTPResponse(body=io.BytesIO(b'abc'),preload_content=False)\nresult=[r.read(2),r.read(),r.read()]", ["b'ab'","b'c'","b''"]))
    leaves.append(scenario("response-stream", "import io\nfrom urllib3.response import HTTPResponse\nr=HTTPResponse(body=io.BytesIO(b'abcdef'),preload_content=False)\nresult=list(r.stream(2))", ["b'ab'","b'cd'","b'ef'"]))
    leaves.append(scenario("response-headers", "import io\nfrom urllib3.response import HTTPResponse\nr=HTTPResponse(body=io.BytesIO(b'x'),headers={'Content-Type':'text/plain','X-Test':'yes'},preload_content=False)\nresult=[r.getheader('content-type'),r.getheaders()['X-Test'],r.headers.get('x-test')]", ["text/plain","yes","yes"]))
    leaves.append(scenario("response-json", "import io\nfrom urllib3.response import HTTPResponse\nr=HTTPResponse(body=io.BytesIO(b'{\"a\":1}'),preload_content=False)\nresult=r.json()", {"a":1}))
    leaves.append(scenario("response-decode-disabled", "import io\nfrom urllib3.response import HTTPResponse\nr=HTTPResponse(body=io.BytesIO(b'plain'),headers={'Content-Encoding':'gzip'},preload_content=False,decode_content=False)\nresult=r.read()", "b'plain'"))
    leaves.append(scenario("exceptions-inheritance", "from urllib3.exceptions import HTTPError,ProtocolError,MaxRetryError,LocationParseError\nresult=[issubclass(ProtocolError,HTTPError),issubclass(MaxRetryError,HTTPError),issubclass(LocationParseError,HTTPError)]", [True,True,True]))
    leaves.append(scenario("root-exports", "import urllib3\nresult=sorted(urllib3.__all__)", sorted(["HTTPConnectionPool","HTTPHeaderDict","HTTPSConnectionPool","PoolManager","ProxyManager","HTTPResponse","Retry","Timeout","add_stderr_logger","connection_from_url","disable_warnings","encode_multipart_formdata","make_headers","proxy_from_url","request","BaseHTTPResponse"])))
    leaves.append(scenario("deterministic-repetition", "from urllib3.util import parse_url\nfrom urllib3.filepost import encode_multipart_formdata\nu=parse_url('http://example.com/a?x=1'); a=encode_multipart_formdata([('a','b')],boundary='B'); b=encode_multipart_formdata([('a','b')],boundary='B')\nresult=[u.url,a==b]", ["http://example.com/a?x=1",True]))
    leaves.append(scenario("no-network-contract", "from urllib3 import PoolManager\np=PoolManager()\nresult=[type(p.pools).__name__,p.headers is not None,p.headers=={}]", ["RecentlyUsedContainer",True,True]))
    print(json.dumps({"schema_version":"1.0","leaves":leaves}, ensure_ascii=False, separators=(",",":"), sort_keys=True, default=lambda value: repr(value)))


if __name__ == "__main__":
    main()
