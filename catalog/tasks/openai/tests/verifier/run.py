from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Callable

from nl2repobench.verification.candidate_client import call, execute_script, get


def run_script(source: str) -> bool:
    result = execute_script(source)
    return result.ok and result.value is True


def simple(name: str, source: str) -> tuple[str, Callable[[], bool]]:
    return name, lambda: run_script(source)


def headers(payload: str, timestamp: str = "1750000000", secret: str = "secret") -> dict[str, str]:
    signed = f"evt.{timestamp}.{payload}".encode()
    digest = base64.b64encode(hmac.new(secret.encode(), signed, hashlib.sha256).digest()).decode()
    return {"Webhook-Id": "evt", "Webhook-Timestamp": timestamp, "Webhook-Signature": f"v1,{digest}"}


def version() -> bool:
    result = get("openai", "__version__")
    return result.ok and result.value == "3.3.1"


TESTS: list[tuple[str, Callable[[], bool]]] = [
    ("version", version),
    simple("exports", "import openai\nresult = all(hasattr(openai, n) for n in ['OpenAI','AsyncOpenAI','BaseModel','NOT_GIVEN','not_given','Omit','omit','OpenAIError','InvalidWebhookSignatureError'])"),
    simple("sentinel", "from openai import NOT_GIVEN, not_given, omit\nresult = not bool(NOT_GIVEN) and not bool(not_given) and not bool(omit) and repr(NOT_GIVEN) == 'NOT_GIVEN' and NOT_GIVEN is not not_given"),
    simple("model_repr", "from openai import BaseModel\nclass M(BaseModel):\n    name: str\nm=M(name='Ada')\nresult = str(m) == \"M(name='Ada')\" and repr(m) == \"M(name='Ada')\""),
    simple("model_dict_alias", "from openai import BaseModel\nfrom pydantic import Field\nclass M(BaseModel):\n    first_name: str = Field(alias='firstName')\nm=M(firstName='Ada', extra=3)\nresult = m.to_dict() == {'firstName':'Ada','extra':3} and m.to_dict(use_api_names=False) == {'first_name':'Ada','extra':3}"),
    simple("model_json", "from datetime import datetime, timezone\nfrom openai import BaseModel\nclass M(BaseModel):\n    when: datetime\nm=M(when=datetime(2025,1,2,tzinfo=timezone.utc))\nresult = isinstance(m.to_dict(mode='json')['when'], str) and '2025-01-02' in m.to_json(indent=None)"),
    simple("model_construct", "from openai import BaseModel\nclass C(BaseModel):\n    value: int\nclass P(BaseModel):\n    child: C\nP.model_rebuild(_types_namespace={'C':C})\nm=P.construct(child={'value':4})\nresult = isinstance(m.child,C) and m.child.value == 4"),
    simple("model_extra", "from openai import BaseModel\nclass M(BaseModel):\n    value: int\nm=M.construct(value=1, unknown={'x':True})\nresult = m.unknown == {'x':True} and m.to_dict()['unknown'] == {'x':True}"),
    simple("model_validation", "from openai import BaseModel\nfrom pydantic import ValidationError\nclass M(BaseModel):\n    value: int\ntry:\n    M(value='wrong')\nexcept ValidationError:\n    result=True\nelse:\n    result=False"),
    simple("qs_empty_basic", "from openai._qs import stringify\nresult = stringify({}) == '' and stringify({'a':1,'b':True,'c':None}) == 'a=1&b=true'"),
    simple("qs_nested_brackets", "from urllib.parse import unquote\nfrom openai._qs import stringify\nresult = unquote(stringify({'a':{'b':'c','d':'e'}})) == 'a[b]=c&a[d]=e'"),
    simple("qs_nested_dots", "from urllib.parse import unquote\nfrom openai._qs import stringify, Querystring\nresult = unquote(stringify({'a':{'b':{'c':'d'}}}, nested_format='dots')) == 'a.b.c=d' and Querystring(nested_format='dots').stringify({'a':{'b':1}}) == 'a.b=1'"),
    simple("qs_array_repeat", "from urllib.parse import unquote\nfrom openai._qs import stringify\nresult = unquote(stringify({'in':['foo','bar',None]})) == 'in=foo&in=bar'"),
    simple("qs_array_comma", "from urllib.parse import unquote\nfrom openai._qs import stringify\nresult = unquote(stringify({'in':['foo','bar',None]}, array_format='comma')) == 'in=foo,bar'"),
    simple("qs_array_brackets", "from urllib.parse import unquote\nfrom openai._qs import stringify\nresult = unquote(stringify({'in':['foo','bar']}, array_format='brackets')) == 'in[]=foo&in[]=bar'"),
    simple("qs_parse", "from openai._qs import Querystring\nresult = Querystring().parse('a=1&a=2')['a'] == ['1','2']"),
    simple("sse_sync", "from openai._streaming import SSEDecoder\ne=list(SSEDecoder().iter_bytes(iter([b'data:{\"x\":1}\\n\\n',b'data:[DONE]\\n\\n'])))\nresult = len(e)==2 and e[0].json()=={'x':1} and e[1].data=='[DONE]'"),
    simple("sse_multiline", "from openai._streaming import SSEDecoder\ne=list(SSEDecoder().iter_bytes(iter([b'data:first\\ndata:second\\n\\n'])))\nresult = e[0].data == 'first\\nsecond'"),
    simple("sse_id_retry", "from openai._streaming import SSEDecoder\ne=list(SSEDecoder().iter_bytes(iter([b'id:abc\\nretry:25\\ndata:x\\n\\n',b'data:y\\n\\n'])))\nresult = [(x.data,x.id,x.retry) for x in e] == [('x','abc',25),('y','abc',None)]"),
    simple("sse_fragmented", "from openai._streaming import SSEDecoder\ne=list(SSEDecoder().iter_bytes(iter([b'data:o',b'k\\r',b'\\n',b'\\r',b'\\n'])))\nresult = [x.data for x in e] == ['ok']"),
    simple("sse_comments", "from openai._streaming import SSEDecoder\ne=list(SSEDecoder().iter_bytes(iter([b':ignored\\nunknown:value\\ndata:ok\\n\\n'])))\nresult = [x.data for x in e] == ['ok']"),
    simple("sse_async", "import asyncio\nfrom openai._streaming import SSEDecoder\nasync def chunks():\n    yield b'data:one\\n\\n'\n    yield b'data:two\\n\\n'\nasync def main():\n    return [e.data async for e in SSEDecoder().aiter_bytes(chunks())]\nresult = asyncio.run(main()) == ['one','two']"),
    simple("webhook_raw", "from unittest.mock import patch\nfrom openai.lib._webhooks import webhook_signature_matches\nwith patch('time.time', return_value=1750000000):\n    result=webhook_signature_matches('{payload}', {headers}, secret='secret', tolerance=300)".format(payload='{"ok":true}', headers=repr(headers('{"ok":true}')))),
    simple("webhook_prefixed_multiple", "from unittest.mock import patch\nfrom openai.lib._webhooks import webhook_signature_matches\nh={h!r}\nh['Webhook-Signature']='v1,bad v1,'+h['Webhook-Signature'][3:]\nwith patch('time.time', return_value=1750000000):\n    result=webhook_signature_matches('body', h, secret='whsec_{s}', tolerance=300)".format(h=headers('body'), s=base64.b64encode(b'secret').decode())),
    simple("webhook_bytes", "from unittest.mock import patch\nfrom openai.lib._webhooks import webhook_signature_matches\nwith patch('time.time', return_value=1750000000):\n    result=webhook_signature_matches('café'.encode(), {h!r}, secret='secret', tolerance=300)".format(h=headers('café'))),
    simple("webhook_replay", "from unittest.mock import patch\nfrom openai.lib._webhooks import webhook_signature_matches\nfrom openai import InvalidWebhookSignatureError\ntry:\n    with patch('time.time', return_value=1750000000):\n        webhook_signature_matches('body', {h!r}, secret='secret', tolerance=300)\nexcept InvalidWebhookSignatureError:\n    result=True\nelse:\n    result=False".format(h=headers('body', timestamp='1749999699'))),
    simple("webhook_missing_header", "from openai.lib._webhooks import webhook_signature_matches\ntry:\n    webhook_signature_matches('body', {}, secret='secret', tolerance=300)\nexcept ValueError as e:\n    result='webhook-signature' in str(e)\nelse:\n    result=False"),
    simple("webhook_mismatch", "from unittest.mock import patch\nfrom openai.lib._webhooks import webhook_signature_matches\nh={h!r}; h['Webhook-Signature']='v1,invalid'\nwith patch('time.time', return_value=1750000000):\n    result=not webhook_signature_matches('body', h, secret='secret', tolerance=300)".format(h=headers('body'))),
    simple("webhook_unwrap", "from unittest.mock import patch\nfrom openai import OpenAI, BaseModel\nc=OpenAI(api_key='key', webhook_secret='secret')\nwith patch('time.time', return_value=1750000000):\n    event=c.webhooks.unwrap('{p}', {h!r})\nresult=isinstance(event, BaseModel) and event.type == 'demo' and event.to_dict()['n'] == 2\nc.close()".format(p='{"type":"demo","n":2}', h=headers('{"type":"demo","n":2}'))),
    simple("webhook_async", "from unittest.mock import patch\nfrom openai import AsyncOpenAI\nc=AsyncOpenAI(api_key='key', webhook_secret='secret')\nwith patch('time.time', return_value=1750000000):\n    c.webhooks.verify_signature('body', {h!r})\nresult=True".format(h=headers('body'))),
    simple("client_properties", "from openai import OpenAI\nc=OpenAI(api_key='key',base_url='https://example.test/v1',organization='org',project='proj',default_headers={'X-Test':'yes'},default_query={'a':'b'})\nresult=str(c.base_url)=='https://example.test/v1/' and c.organization=='org' and c.project=='proj' and c.auth_headers=={'Authorization':'Bearer key'} and c.default_headers['X-Test']=='yes' and c.default_query=={'a':'b'}\nc.close()"),
    simple("client_copy", "from openai import OpenAI\nc=OpenAI(api_key='one',default_headers={'A':'1'},default_query={'x':'1'})\nd=c.copy(api_key='two',default_headers={'B':'2'},default_query={'y':'2'})\nresult=d is not c and d.api_key=='two' and d.default_headers['A']=='1' and d.default_headers['B']=='2' and d.default_query=={'x':'1','y':'2'}\nc.close();d.close()"),
    simple("client_auth_headers", "from openai import OpenAI\ntry:\n    OpenAI(api_key='key').copy(default_headers={},set_default_headers={})\nexcept ValueError:\n    result=True\nelse:\n    result=False"),
    simple("client_get_transport", "import httpx2\nfrom openai import OpenAI\ndef handler(r):\n    return httpx2.Response(200,json={'ok':str(r.url)=='https://example.test/v1/items?a=1&b=2' and r.headers['authorization']=='Bearer key' and r.headers['x-extra']=='yes'})\nc=OpenAI(api_key='key',base_url='https://example.test/v1',default_query={'a':'1'},http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))\nresult=c.get('/items',cast_to=httpx2.Response,options={'params':{'b':'2'},'headers':{'X-Extra':'yes'}}).json()['ok']\nc.close()"),
    simple("client_async_get", "import asyncio\nimport httpx2\nfrom openai import AsyncOpenAI\nasync def main():\n    def handler(r): return httpx2.Response(200,json={'path':str(r.url),'auth':r.headers['authorization']})\n    async with AsyncOpenAI(api_key='key',base_url='https://example.test/v1',http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))) as c:\n        return (await c.get('/health',cast_to=httpx2.Response)).json()=={'path':'https://example.test/v1/health','auth':'Bearer key'}\nresult=asyncio.run(main())"),
    simple("client_context_close", "from openai import OpenAI\nwith OpenAI(api_key='key') as c:\n    before=c.is_closed()\nafter=c.is_closed()\nresult=before is False and after is True"),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for name, test in TESTS:
        try:
            passed = bool(test())
            leaves.append({"id": name, "status": "passed" if passed else "failed", "message": "" if passed else "contract assertion failed"})
        except BaseException as exc:
            leaves.append({"id": name, "status": "failed", "message": f"{type(exc).__name__}: {exc}"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":")))


if __name__ == "__main__":
    main()
