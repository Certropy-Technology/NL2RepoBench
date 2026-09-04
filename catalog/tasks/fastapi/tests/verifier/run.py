from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


CASES = [
    (
        "exports-version",
        "import fastapi; from fastapi import FastAPI, APIRouter, Depends, Query, Path, Header, Cookie, Body; "
        "assert fastapi.__version__ == '0.141.1'; assert all(callable(x) for x in [FastAPI,APIRouter,Depends,Query,Path,Header,Cookie,Body]); result=True",
    ),
    (
        "jsonable-primitives",
        "from fastapi.encoders import jsonable_encoder; from datetime import date,datetime,time,timedelta; from decimal import Decimal; from enum import Enum; "
        "exec(\"class Color(str,Enum):\\n red='red'\"); value={'d':date(2024,1,2),'dt':datetime(2024,1,2,3,4,5),'t':time(3,4,5),'delta':timedelta(seconds=2.5),'dec':Decimal('3.5'),'enum':Color.red,'bytes':b'hi'}; "
        "assert jsonable_encoder(value)=={'d':'2024-01-02','dt':'2024-01-02T03:04:05','t':'03:04:05','delta':2.5,'dec':3.5,'enum':'red','bytes':'hi'}; result=True",
    ),
    (
        "jsonable-custom-encoder",
        "from fastapi.encoders import jsonable_encoder; from dataclasses import dataclass; "
        "exec(\"@dataclass\\nclass Item:\\n name:str\\n count:int\")\n"
        "v=Item('x',2); assert jsonable_encoder(v)=={'name':'x','count':2}; assert jsonable_encoder(v,custom_encoder={Item:lambda x:x.name.upper()})=='X'; result=True",
    ),
    (
        "jsonable-include-exclude",
        "from fastapi.encoders import jsonable_encoder; value={'name':'Ada','secret':'x','nested':{'a':1,'b':2}}; "
        "assert jsonable_encoder(value,exclude={'secret':True})=={'name':'Ada','nested':{'a':1,'b':2}}; result=True",
    ),
    (
        "params-query",
        "from fastapi import Query; q=Query('default',alias='q',title='Search',description='term',min_length=2,max_length=8,deprecated=True,include_in_schema=False); "
        "assert q.default=='default' and q.alias=='q' and q.title=='Search' and q.description=='term' and q.deprecated is True and q.include_in_schema is False; result=True",
    ),
    (
        "params-path",
        "from fastapi import Path; p=Path(title='Identifier',ge=1,le=10); assert p.default.__class__.__name__=='PydanticUndefinedType' and p.title=='Identifier'; assert p.in_.value=='path'; result=True",
    ),
    (
        "params-body-form-file",
        "from fastapi import Body,Form,File; b=Body(None,embed=True,media_type='application/custom'); f=Form('x'); u=File(None); "
        "assert b.embed is True and b.media_type=='application/custom'; assert f.media_type=='application/x-www-form-urlencoded'; assert u.media_type=='multipart/form-data'; result=True",
    ),
    (
        "depends-security-marker",
        "from fastapi import Depends,Security; fn=lambda:1; d=Depends(fn,use_cache=False,scope='function'); s=Security(fn,scopes=['read'],use_cache=True); "
        "assert d.dependency is fn and d.use_cache is False and d.scope=='function'; assert s.dependency is fn and s.scopes==['read']; result=True",
    ),
    (
        "default-placeholder",
        "from fastapi.datastructures import Default,DefaultPlaceholder; x=Default(dict); assert isinstance(x,DefaultPlaceholder) and x.value is dict and bool(x) is True; assert x==Default(dict) and x!=Default(list); result=True",
    ),
    (
        "exceptions",
        "from fastapi import HTTPException; from fastapi.exceptions import RequestValidationError,ResponseValidationError,WebSocketRequestValidationError; "
        "h=HTTPException(404,'missing',{'x':'y'}); assert h.status_code==404 and h.detail=='missing' and h.headers=={'x':'y'}; "
        "errors=[{'type':'missing','loc':('query','q'),'msg':'required','input':None}]; r=RequestValidationError(errors,body={'x':1}); w=WebSocketRequestValidationError(errors); o=ResponseValidationError(errors,body='bad'); "
        "assert r.errors()==errors and r.body=={'x':1} and w.errors()==errors and o.body=='bad'; result=True",
    ),
    (
        "security-header",
        "import asyncio; from fastapi.security import APIKeyHeader; from starlette.requests import Request; "
        "exec(\"async def main():\"+chr(10)+\" s=APIKeyHeader(name='x-key',scheme_name='Key',description='desc')\"+chr(10)+\" r=Request({'type':'http','method':'GET','path':'/','headers':[(b'x-key',b'abc')],'query_string':b''})\"+chr(10)+\" assert await s(r)=='abc' and s.scheme_name=='Key' and s.model.in_.value=='header'\"); asyncio.run(main()); result=True",
    ),
    (
        "security-header-missing",
        "import asyncio; from fastapi.security import APIKeyHeader; from starlette.exceptions import HTTPException; from starlette.requests import Request; "
        "exec(\"async def main():\"+chr(10)+\" s=APIKeyHeader(name='x-key')\"+chr(10)+\" r=Request({'type':'http','method':'GET','path':'/','headers':[],'query_string':b''})\"+chr(10)+\" try: await s(r)\"+chr(10)+\" except HTTPException as e: assert e.status_code==401 and e.detail=='Not authenticated'\"+chr(10)+\" else: raise AssertionError('missing auth accepted')\"); asyncio.run(main()); result=True",
    ),
    (
        "security-http-basic",
        "import asyncio,base64; from fastapi.security import HTTPBasic; from starlette.requests import Request; "
        "exec(\"async def main():\"+chr(10)+\" token=base64.b64encode(b'user:pass').decode()\"+chr(10)+\" r=Request({'type':'http','method':'GET','path':'/','headers':[(b'authorization',('Basic '+token).encode())],'query_string':b''})\"+chr(10)+\" c=await HTTPBasic()(r); assert c.username=='user' and c.password=='pass'\"); asyncio.run(main()); result=True",
    ),
    (
        "security-bearer",
        "import asyncio; from fastapi.security import HTTPBearer; from starlette.requests import Request; "
        "exec(\"async def main():\"+chr(10)+\" r=Request({'type':'http','method':'GET','path':'/','headers':[(b'authorization',b'Bearer token')],'query_string':b''})\"+chr(10)+\" c=await HTTPBearer()(r); assert c.scheme=='Bearer' and c.credentials=='token'\"); asyncio.run(main()); result=True",
    ),
    (
        "security-oauth-form",
        "from fastapi.security import OAuth2PasswordRequestForm,SecurityScopes; f=OAuth2PasswordRequestForm(username='ada',password='pw',scope='read write',grant_type='password',client_id='c',client_secret='s'); "
        "assert f.scopes==['read','write'] and f.username=='ada' and f.client_id=='c'; x=SecurityScopes(['read','write']); assert x.scope_str=='read write'; result=True",
    ),
    (
        "app-registration",
        "from fastapi import FastAPI; app=FastAPI(title='Demo',version='1.2.3',description='desc',docs_url=None,redoc_url=None); "
        "exec(\"@app.get('/items/{item_id}',tags=['items'],summary='Read item')\\nasync def read(item_id:int): return {'item_id':item_id}\")\n"
        "assert app.title=='Demo' and app.version=='1.2.3'; route=app.routes[-1]; assert route.path=='/items/{item_id}' and route.methods=={'GET'} and route.summary=='Read item'; result=True",
    ),
    (
        "router-prefix",
        "from fastapi import APIRouter,FastAPI; router=APIRouter(prefix='/api',tags=['api']); "
        "exec(\"@router.post('/items',status_code=201)\\ndef create(): return {'ok':True}\")\n"
        "app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None); app.include_router(router); schema=app.openapi(); op=schema['paths']['/api/items']['post']; assert op['responses']['201']['description']=='Successful Response'; result=True",
    ),
    (
        "openapi-basic",
        "from fastapi import FastAPI,Query; app=FastAPI(title='Demo',version='1.0',docs_url=None,redoc_url=None); "
        "exec(\"@app.get('/items/{item_id}',response_model=dict[str,int])\\ndef read(item_id:int,q:str=Query('x',min_length=1)): return {'value':item_id}\")\n"
        "schema=app.openapi(); assert schema['openapi'].startswith('3.1.') and schema['info']['title']=='Demo'; op=schema['paths']['/items/{item_id}']['get']; assert op['operationId'].startswith('read_items__item_id__get'); assert [p['name'] for p in op['parameters']]==['item_id','q']; result=True",
    ),
    (
        "openapi-cache",
        "from fastapi import FastAPI; app=FastAPI(title='X',docs_url=None,redoc_url=None); first=app.openapi(); second=app.openapi(); assert first is second and app.openapi_schema is first; result=True",
    ),
    (
        "openapi-tags-servers",
        "from fastapi import FastAPI; app=FastAPI(title='X',openapi_tags=[{'name':'users','description':'Users'}],servers=[{'url':'https://example.test'}],docs_url=None,redoc_url=None); s=app.openapi(); assert s['tags'][0]['name']=='users' and s['servers']==[{'url':'https://example.test'}]; result=True",
    ),
    (
        "url-for",
        "from fastapi import FastAPI; app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None); "
        "exec(\"@app.get('/users/{user_id}',name='user')\\ndef user(user_id:str): return user_id\")\n"
        "assert str(app.url_path_for('user',user_id='ada'))=='/users/ada'; result=True",
    ),
    (
        "operation-id",
        "from fastapi import FastAPI; app=FastAPI(docs_url=None,redoc_url=None); "
        "exec(\"@app.get('/a-b/{x}')\\ndef read_value(x:str): return x\")\n"
        "op=app.openapi()['paths']['/a-b/{x}']['get']['operationId']; assert op=='read_value_a_b__x__get'; result=True",
    ),
    (
        "body-status-utils",
        "from fastapi.utils import is_body_allowed_for_status_code,get_path_param_names,deep_dict_update,get_value_or_default; from fastapi.datastructures import Default; "
        "assert is_body_allowed_for_status_code(200) and not is_body_allowed_for_status_code(204) and not is_body_allowed_for_status_code(304); assert get_path_param_names('/x/{a}/{b:int}')=={'a','b:int'}; "
        "d={'a':{'x':1},'l':[1]}; deep_dict_update(d,{'a':{'y':2},'l':[2],'z':3}); assert d=={'a':{'x':1,'y':2},'l':[1,2],'z':3}; assert get_value_or_default(Default('x'),'y')=='y'; result=True",
    ),
    (
        "authorization-parse",
        "from fastapi.security.utils import get_authorization_scheme_param; assert get_authorization_scheme_param('Bearer abc')==('Bearer','abc'); assert get_authorization_scheme_param('Basic')==('Basic',''); assert get_authorization_scheme_param(None)==('',''); result=True",
    ),
    (
        "sse-format",
        "from fastapi.sse import ServerSentEvent,format_sse_event,KEEPALIVE_COMMENT; e=ServerSentEvent(data='one\\ntwo',event='message',id='7',retry=1000); text=format_sse_event(data_str=e.data,event=e.event,id=e.id,retry=e.retry).decode(); assert text=='event: message\\ndata: one\\ndata: two\\nid: 7\\nretry: 1000\\n\\n'; assert KEEPALIVE_COMMENT.startswith(b':'); result=True",
    ),
    (
        "sse-validation",
        "from fastapi.sse import ServerSentEvent; from pydantic import ValidationError; "
        "exec(\"try:\\n ServerSentEvent(data='x',event='bad\\\\nname')\\nexcept ValidationError:\\n pass\\nelse:\\n raise AssertionError('newline event accepted')\"); result=True",
    ),
    (
        "response-aliases",
        "from fastapi.responses import JSONResponse,HTMLResponse,PlainTextResponse,RedirectResponse,StreamingResponse,FileResponse; from starlette.responses import JSONResponse as S; assert JSONResponse is S and all(x is not None for x in [HTMLResponse,PlainTextResponse,RedirectResponse,StreamingResponse,FileResponse]); assert JSONResponse({'ok':True}).body==b'{\"ok\":true}'; result=True",
    ),
    (
        "middleware-aliases",
        "from fastapi.middleware.cors import CORSMiddleware; from fastapi.middleware.gzip import GZipMiddleware; from fastapi.middleware.trustedhost import TrustedHostMiddleware; from starlette.middleware.cors import CORSMiddleware as S; assert CORSMiddleware is S and GZipMiddleware.__name__=='GZipMiddleware' and TrustedHostMiddleware.__name__=='TrustedHostMiddleware'; result=True",
    ),
    (
        "background-order",
        "import asyncio; from fastapi import BackgroundTasks; events=[]; "
        "exec(\"def add(x): events.append(x)\"+chr(10)+\"async def adda(x): events.append(x)\"+chr(10)+\"async def main():\"+chr(10)+\" b=BackgroundTasks(); b.add_task(add,1); b.add_task(adda,2); await b()\"); asyncio.run(main()); assert events==[1,2]; result=True",
    ),
    (
        "determinism",
        "import json; from fastapi import FastAPI; app=FastAPI(title='D',docs_url=None,redoc_url=None); "
        "exec(\"@app.get('/x/{value}')\\ndef get_x(value:int): return {'value':value}\")\n"
        "a=json.dumps(app.openapi(),sort_keys=True,separators=(',',':')); b=json.dumps(app.openapi(),sort_keys=True,separators=(',',':')); assert a==b; result=True",
    ),
]


def main() -> None:
    leaves = []
    for case_id, source in CASES:
        result = execute_script(source, timeout_sec=20.0)
        if result.ok and result.value is True:
            leaves.append({"id": f"fastapi/{case_id}", "status": "passed"})
        else:
            message = result.exception_message or result.exception_type or "false result"
            leaves.append(
                {"id": f"fastapi/{case_id}", "status": "failed", "message": message[-1000:]}
            )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
