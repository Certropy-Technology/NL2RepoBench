"""Private deterministic scenarios for the requests-cache task."""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {"status": "passed" if actual == expected else "failed", "actual": actual}


CASES: list[tuple[str, str, object]] = [
    (
        "exports",
        "import requests_cache\nresult=[requests_cache.CachedSession.__name__, callable(requests_cache.create_key), hasattr(requests_cache,'CachedResponse'), hasattr(requests_cache,'install_cache')]",
        {"ok": True, "value": ["CachedSession", True, True, True]},
    ),
    (
        "normalize-params",
        "from requests_cache.cache_keys import normalize_params\nresult=normalize_params('b=2&a=1&a=3&flag',['a'])",
        {"ok": True, "value": "a=REDACTED&a=REDACTED&b=2&flag"},
    ),
    (
        "normalize-url",
        "from requests_cache.cache_keys import normalize_url\nresult=normalize_url('https://example.com?b=2&a=1',None)",
        {"ok": True, "value": "https://example.com/?a=1&b=2"},
    ),
    (
        "normalize-headers",
        "from requests_cache.cache_keys import normalize_headers\nresult=dict(normalize_headers({'X-Test':' b, A, a ','Bytes':b'ok'}))",
        {"ok": True, "value": {"X-Test": "a, a, b", "Bytes": "ok"}},
    ),
    (
        "normalize-json-body",
        "from requests_cache.cache_keys import normalize_json_body\nresult=normalize_json_body('{\"z\": 2, \"secret\": \"x\", \"a\": 1}',['secret'])",
        {"ok": True, "value": '{"a": 1, "secret": "REDACTED", "z": 2}'},
    ),
    (
        "normalize-request-copy",
        "from requests import Request\nfrom requests_cache.cache_keys import normalize_request\nr=Request('get','https://example.com?b=2&a=1',json={'z':2,'a':1})\nn=normalize_request(r)\nresult=[r.url,n.url,n.body.decode(),r.method,n.method]",
        {"ok": True, "value": ["https://example.com?b=2&a=1", "https://example.com/?a=1&b=2", '{"a": 1, "z": 2}', "get", "GET"]},
    ),
    (
        "cache-key-equivalence",
        "from requests import Request\nfrom requests_cache.cache_keys import create_key\na=create_key(Request('GET','https://example.com?b=2&a=1'),ignored_parameters=['token'])\nb=create_key(Request('get','https://example.com?a=1&b=2'),ignored_parameters=['token'])\nresult=a==b",
        {"ok": True, "value": True},
    ),
    (
        "cache-key-distinguishes-method",
        "from requests import Request\nfrom requests_cache.cache_keys import create_key\nresult=create_key(Request('GET','https://example.com')) != create_key(Request('POST','https://example.com'))",
        {"ok": True, "value": True},
    ),
    (
        "expiration-relative",
        "from datetime import datetime,timezone,timedelta\nfrom requests_cache.policy.expiration import get_expiration_datetime\ns=datetime(2020,1,1,tzinfo=timezone.utc)\nresult=[get_expiration_datetime(60,s).isoformat(),get_expiration_datetime(timedelta(seconds=5),s).isoformat(),get_expiration_datetime(-1,s) is None]",
        {"ok": True, "value": ["2020-01-01T00:01:00+00:00", "2020-01-01T00:00:05+00:00", True]},
    ),
    (
        "expiration-httpdate",
        "from requests_cache.policy.expiration import get_expiration_datetime\ntry:\n get_expiration_datetime('not a date')\nexcept ValueError as e:\n result=[get_expiration_datetime('Wed, 21 Oct 2015 07:28:00 GMT').isoformat(),type(e).__name__]",
        {"ok": True, "value": ["2015-10-21T07:28:00+00:00", "ValueError"]},
    ),
    (
        "url-expiration",
        "from requests_cache.policy.expiration import get_url_expiration\nresult=[get_url_expiration('https://example.com/api/1',{'example.com/api':60,'example.com/**':99}),get_url_expiration('https://other.test/x',{'example.com/**':99})]",
        {"ok": True, "value": [60, None]},
    ),
    (
        "request-directives",
        "from requests_cache.policy.directives import set_request_headers\nresult=dict(set_request_headers({'Cache-Control':'max-age=60'},60,True,True,True))",
        {"ok": True, "value": {"Cache-Control": "max-age=60,must-revalidate,no-cache,only-if-cached"}},
    ),
    (
        "settings-defaults",
        "from requests_cache.policy import CacheSettings\ns=CacheSettings()\nresult=[s.expire_after==-1,s.cache_control is False,'GET' in s.allowable_methods,'POST' in s.allowable_methods,s.read_only is False,s.stale_if_error is False]",
        {"ok": True, "value": [False, True, True, False, True, True]},
    ),
    (
        "dict-storage",
        "from requests_cache.backends.base import DictStorage\nd=DictStorage();d['a']=1;d.update({'b':2})\nresult=[d['a'],list(d.keys()),d.serialize('x'),d.deserialize('a','x')]",
        {"ok": True, "value": [1, ["a", "b"], "x", "x"]},
    ),
    (
        "base-cache-filter",
        "from requests import Response,Request\nfrom urllib3.response import HTTPResponse\nfrom io import BytesIO\nfrom requests_cache.backends.base import BaseCache\nc=BaseCache();r=Response();r.status_code=200;r.url='mock://cache/item';r.request=Request('GET',r.url).prepare();r._content=b'ok';r.raw=HTTPResponse(body=BytesIO(b'ok'),status=200,request_url=r.url);c.save_response(r)\nresult=[c.contains(url=r.url),c.urls(),len(list(c.filter())),c.get_response(next(iter(c.responses))).from_cache]",
        {"ok": True, "value": [True, ["mock://cache/item"], 1, True]},
    ),
    (
        "cached-response-model",
        "from requests import Response,Request\nfrom urllib3.response import HTTPResponse\nfrom io import BytesIO\nfrom requests_cache.models.response import CachedResponse\nr=Response();r.status_code=201;r.url='mock://response';r.request=Request('GET',r.url).prepare();r._content=b'hello';r.raw=HTTPResponse(body=BytesIO(b'hello'),status=201,request_url=r.url);c=CachedResponse.from_response(r)\nresult=[c.status_code,c.url,c.from_cache,c.text,c.request.method]",
        {"ok": True, "value": [201, "mock://response", True, "hello", "GET"]},
    ),
    (
        "response-formatting",
        "from requests_cache.models.response import format_file_size,format_datetime\nresult=[format_file_size(0),format_file_size(3072),format_datetime(None)]",
        {"ok": True, "value": ["0 bytes", "3.00 KiB", "N/A"]},
    ),
    (
        "json-serializer",
        "import json\nfrom requests_cache.serializers import init_serializer,Stage\ns=init_serializer(Stage(json),False)\nresult=[s.dumps({'a':1}),s.loads('{\"a\": 1}')]",
        {"ok": True, "value": ['{"a": 1}', {"a": 1}]},
    ),
    (
        "serializer-copy",
        "import json\nfrom requests_cache.serializers import init_serializer,Stage\na=init_serializer(Stage(json),False);b=a.copy()\nresult=[a is b,len(a.stages),len(b.stages),a.dumps({'a':1})==b.dumps({'a':1})]",
        {"ok": True, "value": [False, 1, 1, True]},
    ),
    (
        "cached-session-hit",
        "from io import BytesIO\nfrom urllib3.response import HTTPResponse\nfrom requests import Response\nfrom requests.adapters import BaseAdapter\nfrom requests_cache import CachedSession\nclass A(BaseAdapter):\n def __init__(self): self.n=0\n def send(self,request,**kwargs):\n  self.n+=1;r=Response();r.status_code=200;r.url=request.url;r.request=request;r._content=f'v{self.n}'.encode();r.raw=HTTPResponse(body=BytesIO(r._content),status=200,request_url=request.url);return r\n def close(self): pass\na=A();s=CachedSession(backend='memory');s.mount('mock://',a);x=s.get('mock://x');y=s.get('mock://x')\nresult=[x.text,y.text,x.from_cache,y.from_cache,a.n,len(s.cache.responses)]",
        {"ok": True, "value": ["v1", "v1", False, True, 1, 1]},
    ),
    (
        "only-if-cached-miss",
        "from requests_cache import CachedSession\ns=CachedSession(backend='memory')\nr=s.get('mock://missing',only_if_cached=True)\nresult=[r.status_code,r.reason,r.from_cache]",
        {"ok": True, "value": [504, "Not Cached", True]},
    ),
    (
        "cache-disabled",
        "from io import BytesIO\nfrom urllib3.response import HTTPResponse\nfrom requests import Response\nfrom requests.adapters import BaseAdapter\nfrom requests_cache import CachedSession\nclass A(BaseAdapter):\n def __init__(self): self.n=0\n def send(self,request,**kwargs):\n  self.n+=1;r=Response();r.status_code=200;r.url=request.url;r.request=request;r._content=f'v{self.n}'.encode();r.raw=HTTPResponse(body=BytesIO(r._content),status=200,request_url=request.url);return r\n def close(self): pass\na=A();s=CachedSession(backend='memory');s.mount('mock://',a);x=s.get('mock://x')\nwith s.cache_disabled(): y=s.get('mock://x')\nresult=[x.from_cache,y.from_cache,a.n]",
        {"ok": True, "value": [False, False, 2]},
    ),
    (
        "patcher-install",
        "import requests,requests_cache\noriginal=requests.Session\nrequests_cache.install_cache(backend='memory')\ninside=[requests_cache.is_installed(),isinstance(requests_cache.get_cache(),object)]\nrequests_cache.uninstall_cache()\nresult=inside+[requests.Session is original]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "patcher-context",
        "import requests_cache\nwith requests_cache.enabled(backend='memory'):\n a=requests_cache.is_installed()\n with requests_cache.disabled():\n  b=requests_cache.is_installed()\n c=requests_cache.is_installed()\nd=requests_cache.is_installed()\nresult=[a,b,c,d]",
        {"ok": True, "value": [True, False, True, False]},
    ),
    (
        "session-methods",
        "from io import BytesIO\nfrom urllib3.response import HTTPResponse\nfrom requests import Response\nfrom requests.adapters import BaseAdapter\nfrom requests_cache import CachedSession\nclass A(BaseAdapter):\n def send(self,request,**kwargs):\n  r=Response();r.status_code=200;r.url=request.url;r.request=request;r._content=b'ok';r.raw=HTTPResponse(body=BytesIO(b'ok'),status=200,request_url=request.url);return r\n def close(self): pass\ns=CachedSession(backend='memory',allowable_methods=['GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS']);s.mount('mock://',A());result=[s.get('mock://g').status_code,s.post('mock://p').status_code,s.put('mock://u').status_code,s.patch('mock://a').status_code,s.delete('mock://d').status_code,s.head('mock://h').status_code,s.options('mock://o').status_code]",
        {"ok": True, "value": [200, 200, 200, 200, 200, 200, 200]},
    ),
    (
        "response-history",
        "from requests import Response,Request\nfrom urllib3.response import HTTPResponse\nfrom io import BytesIO\nfrom requests_cache.models.response import CachedResponse\nr=Response();r.status_code=200;r.url='mock://history';r.request=Request('GET',r.url).prepare();r._content=b'x';r.raw=HTTPResponse(body=BytesIO(b'x'),status=200,request_url=r.url);c=CachedResponse.from_response(r)\nresult=[c.history==[],c.request.url,c.raw is not None]",
        {"ok": True, "value": [True, "mock://history", True]},
    ),
    (
        "request-model",
        "from requests import Request\nfrom requests_cache.models.request import CachedRequest\nr=Request('POST','https://example.com/a',params={'b':2,'a':1},data='x').prepare();c=CachedRequest.from_request(r)\nresult=[c.method,c.url,c.body.decode(),c.headers['Content-Length']]",
        {"ok": True, "value": ["POST", "https://example.com/a?b=2&a=1", "x", "1"]},
    ),
    (
        "utility-encoding",
        "from requests_cache._utils import encode,decode,try_int,is_json_content_type\nresult=[encode('caf\u00e9').decode(),decode(encode('caf\u00e9')),try_int('3'),try_int('x'),is_json_content_type('application/vnd.api+json')]",
        {"ok": True, "value": ["caf\u00e9", "caf\u00e9", 3, None, True]},
    ),
    (
        "optional-backend-placeholder",
        "from requests_cache.backends import MongoCache\ntry:\n MongoCache('x')\n result=False\nexcept ImportError:\n result=True",
        {"ok": True, "value": True},
    ),
    (
        "deterministic-repeat",
        "from requests import Request\nfrom requests_cache.cache_keys import create_key,normalize_params\nr=Request('GET','https://example.com?b=2&a=1')\nk1=create_key(r);k2=create_key(r);p1=normalize_params('z=3&a=1');p2=normalize_params('z=3&a=1')\nresult=[k1==k2,len(k1)==16,p1==p2]",
        {"ok": True, "value": [True, True, True]},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        outcome = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": outcome["status"]}
        if outcome["status"] == "failed":
            leaf["message"] = json.dumps(outcome["actual"], ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
