from __future__ import annotations

import base64
import json
import sys

from nl2repobench.verification.candidate_client import call, execute_script


def script(source: str) -> bool:
    result = execute_script(source, timeout_sec=20)
    if not result.ok:
        print(f"script failure: {result.exception_type}: {result.exception_message}", file=sys.stderr)
    return result.ok and result.value is True


def call_value(module: str, name: str, *args, **kwargs):
    result = call(module, name, *args, **kwargs)
    if not result.ok:
        print(f"call failure {module}.{name}: {result.exception_type}: {result.exception_message}", file=sys.stderr)
    return result.value if result.ok else None


def exception(module: str, name: str, *args, suffix: str = "ValueError", **kwargs) -> bool:
    result = call(module, name, *args, **kwargs)
    if result.ok:
        print(f"expected exception missing {module}.{name}", file=sys.stderr)
    elif not result.exception_type.endswith(suffix):
        print(f"unexpected exception {module}.{name}: {result.exception_type}: {result.exception_message}", file=sys.stderr)
    return not result.ok and result.exception_type.endswith(suffix)


def main() -> None:
    cases = [
        ("version", lambda: script("""
import msal
result = msal.__version__ == '1.38.0'
""")),
        ("exports", lambda: script("""
import msal
names = ['ClientApplication','PublicClientApplication','ConfidentialClientApplication','TokenCache','SerializableTokenCache','PopAuthScheme','AutoRefresher','Prompt']
result = all(hasattr(msal, n) for n in names) and msal.__version__ == '1.38.0'
""")),
        ("canonicalize", lambda: script("""
from msal.authority import canonicalize
parsed, host, tenant = canonicalize('https://LOGIN.example.com/tenant/path')
result = host == 'login.example.com' and tenant == 'tenant' and parsed.scheme == 'https'
""")),
        ("canonicalize-invalid", lambda: exception("msal.authority", "canonicalize", "http://login.example.com/t")),
        ("ciam-canonicalize", lambda: _ciam()),
        ("authority-builder", lambda: script("""
from msal.authority import AuthorityBuilder
result = str(AuthorityBuilder('login.example.com/', '/tenant/')) == 'https://login.example.com/tenant'
""")),
        ("decode-part", lambda: call_value("msal.oauth2cli.oidc", "decode_part", base64.urlsafe_b64encode(b'{\"x\":1}').decode().rstrip('=')) == '{"x":1}'),
        ("decode-bytes", lambda: script("""
from msal.oauth2cli.oidc import decode_part
result = decode_part('AP8', encoding=None) == bytes([0, 255])
""")),
        ("base64decode-alias", lambda: script("""
from msal.oauth2cli.oidc import base64decode, decode_part
result = base64decode('c2Fs') == decode_part('c2Fs') == 'sal'
""")),
        ("decode-id-token", lambda: script("""
import base64, json
from msal.oauth2cli.oidc import decode_id_token
p={'iss':'https://issuer','sub':'s','aud':'client','iat':100,'exp':1000,'nonce':'n'}
enc=lambda x: base64.urlsafe_b64encode(json.dumps(x).encode()).decode().rstrip('=')
result = decode_id_token(enc({})+'.'+enc(p)+'.s', client_id='client', issuer='https://issuer', nonce='n', now=200) == p
""")),
        ("decode-id-token-invalid-audience", lambda: script("""
import base64, json
from msal.oauth2cli.oidc import decode_id_token
enc=lambda x: base64.urlsafe_b64encode(json.dumps(x).encode()).decode().rstrip('=')
try: decode_id_token(enc({})+'.'+enc({'iss':'i','aud':'other','iat':1,'exp':999})+'.s', client_id='client', now=2)
except Exception as e: result = type(e).__name__ == 'IdTokenAudienceError'
else: result = False
""")),
        ("prompt-constants", lambda: script("""
from msal.oauth2cli.oidc import Prompt
result=[Prompt.NONE,Prompt.LOGIN,Prompt.CONSENT,Prompt.SELECT_ACCOUNT,Prompt.CREATE]==['none','login','consent','select_account','create']
""")),
        ("oauth-build-uri", lambda: script("""
from msal.oauth2cli.oauth2 import Client
c=Client({'authorization_endpoint':'https://login.example/authorize'},'client')
u=c.build_auth_request_uri('code',redirect_uri='https://app/cb',scope=['b','a'],state='state',prompt='login')
result=all(x in u for x in ['response_type=code','redirect_uri=https%3A%2F%2Fapp%2Fcb','scope=a+b','state=state','prompt=login'])
""")),
        ("oauth-existing-query", lambda: script("""
from msal.oauth2cli.oauth2 import Client
u=Client({'authorization_endpoint':'https://login.example/authorize?fixed=1'},'c').build_auth_request_uri('code',state='s')
result=u.startswith('https://login.example/authorize?fixed=1&') and 'state=s' in u
""")),
        ("auth-code-flow-shape", lambda: script("""
from msal.oauth2cli.oidc import Client
f=Client({'authorization_endpoint':'https://login.example/authorize'},'c').initiate_auth_code_flow(scope=['user.read'],redirect_uri='https://app/cb')
result=set(['auth_uri','state','nonce','code_verifier'])<=set(f) and 'openid' in f['auth_uri'] and len(f['code_verifier'])==43 and 'code_challenge=' in f['auth_uri']
""")),
        ("pkce-relationship", lambda: script("""
import base64,hashlib
from msal.oauth2cli.oidc import Client
f=Client({'authorization_endpoint':'https://login.example/authorize'},'c').initiate_auth_code_flow()
from urllib.parse import parse_qs, urlparse
challenge=parse_qs(urlparse(f['auth_uri']).query)['code_challenge'][0]
result=challenge==base64.urlsafe_b64encode(hashlib.sha256(f['code_verifier'].encode()).digest()).decode().rstrip('=')
""")),
        ("ext-key-empty", lambda: call_value("msal.token_cache","_compute_ext_cache_key",{'client_id':'x','scope':['a'],'claims':'x'}) == ''),
        ("ext-key-order", lambda: script("""
from msal.token_cache import _compute_ext_cache_key
result=_compute_ext_cache_key({'fmi_path':'p','x':'y'})==_compute_ext_cache_key({'x':'y','fmi_path':'p'})
""")),
        ("ext-key-different", lambda: script("""
from msal.token_cache import _compute_ext_cache_key
result=_compute_ext_cache_key({'fmi_path':'a'})!=_compute_ext_cache_key({'fmi_path':'b'})
""")),
        ("parse-claims", lambda: call_value("msal.token_cache","_parse_claims_or_raise",'{"a":{"b":1}}') == {'a':{'b':1}}),
        ("parse-claims-invalid", lambda: _claims_invalid()),
        ("merge-claims", lambda: _merge()),
        ("cache-access-token", lambda: script("""
from msal import TokenCache
c=TokenCache(); c.add({'client_id':'client','scope':['s2','s1'],'token_endpoint':'https://login.example/t/v2.0/token','response':{'access_token':'at','expires_in':3600}},now=100)
x=c.find(c.CredentialType.ACCESS_TOKEN,target=['s1'],query={'client_id':'client'},now=100)
result=len(x)==1 and x[0]['secret']=='at' and x[0]['target']=='s1 s2'
""")),
        ("cache-user-entries", lambda: script("""
import base64,json
from msal import TokenCache
idtoken='h.'+base64.b64encode(json.dumps({'sub':'s','oid':'o','preferred_username':'u'}).encode()).decode()+'.s'
c=TokenCache(); c.add({'client_id':'c','scope':['s'],'token_endpoint':'https://login.example/t/v2.0/token','response':{'access_token':'a','refresh_token':'r','id_token':idtoken,'expires_in':10,'client_info':base64.b64encode(b'{"uid":"u","utid":"t"}').decode()}},now=100)
result=all(len(list(c.search(t)))==1 for t in [c.CredentialType.REFRESH_TOKEN,c.CredentialType.ACCOUNT,c.CredentialType.ID_TOKEN])
""")),
        ("cache-serialize", lambda: script("""
from msal import SerializableTokenCache
c=SerializableTokenCache(); c.add({'client_id':'c','scope':['s'],'token_endpoint':'https://login.example/t/v2.0/token','response':{'access_token':'a','expires_in':10}},now=10)
s=c.serialize(); d=SerializableTokenCache(); d.deserialize(s)
result=not c.has_state_changed and not d.has_state_changed and s==d.serialize()
""")),
        ("cache-state-change", lambda: script("""
from msal import SerializableTokenCache
c=SerializableTokenCache(); c.add({'client_id':'c','scope':['s'],'token_endpoint':'https://login.example/t/v2.0/token','response':{'access_token':'a','expires_in':10}},now=10)
result=c.has_state_changed is True
""")),
        ("cache-expiry", lambda: script("""
from msal import TokenCache
c=TokenCache(); c.add({'client_id':'c','scope':['s'],'token_endpoint':'https://login.example/t/v2.0/token','response':{'access_token':'a','expires_in':10}},now=10)
result=c.find(c.CredentialType.ACCESS_TOKEN,now=21)==[]
""")),
        ("cache-remove", lambda: script("""
from msal import TokenCache
c=TokenCache(); c.add({'client_id':'c','scope':['s'],'token_endpoint':'https://login.example/t/v2.0/token','response':{'access_token':'a','expires_in':10}},now=10)
x=c.find(c.CredentialType.ACCESS_TOKEN,now=10)[0]; c.remove_at(x); result=c.find(c.CredentialType.ACCESS_TOKEN,now=10)==[]
""")),
        ("retry-429", lambda: script("""
from msal.throttled_http_client import RetryAfterParser
class R: status_code=429; headers={}
result=RetryAfterParser(default_value=7).parse(result=R())==7
""")),
        ("retry-header-cap", lambda: script("""
from msal.throttled_http_client import RetryAfterParser
class R: status_code=200; headers={'rEtRy-AfTeR':'99999'}
result=RetryAfterParser(default_value=7).parse(result=R())==3600
""")),
        ("normalized-response", lambda: script("""
from msal.throttled_http_client import NormalizedResponse
class R: status_code=201; text='body'; headers={'X-Test':'yes'}
r=NormalizedResponse(R()); result=r.status_code==201 and r.text=='body' and r.headers=={'x-test':'yes'}
""")),
        ("normalized-error", lambda: script("""
from msal.throttled_http_client import NormalizedResponse
class R: status_code=401; text='no'; headers={}
try: NormalizedResponse(R()).raise_for_status()
except Exception as e: result=type(e).__name__=='MsalServiceError'
else: result=False
""")),
        ("pop-valid", lambda: script("""
from msal import PopAuthScheme
p=PopAuthScheme('GET','https://api.example/resource','nonce'); result=p._http_method=='GET' and p._url.hostname=='api.example' and p._nonce=='nonce'
""")),
        ("pop-invalid", lambda: exception("msal","PopAuthScheme","get","https://api.example","n")),
        ("escape-xml", lambda: call_value("msal.wstrust_request","escape_xml",'a&<b>"\'') == 'a&amp;&lt;b&gt;&quot;&apos;'),
        ("wsu-time", lambda: script("""
from datetime import datetime,timezone
from msal.wstrust_request import wsu_time_format
result=wsu_time_format(datetime(2020,1,2,3,4,5,tzinfo=timezone.utc))=='2020-01-02T03:04:05Z'
""")),
    ]
    leaves=[]
    for name, test in cases:
        try: passed=bool(test()); message='' if passed else 'behavior mismatch'
        except Exception as exc: passed=False; message=f'{type(exc).__name__}: {exc}'[:500]
        leaves.append({'id':f'msal-contract::{name}','status':'passed' if passed else 'failed','message':message})
    print(json.dumps({'schema_version':'1.0','leaves':leaves},sort_keys=True))


def _ciam():
    return script("""
from msal.authority import canonicalize
_, host, tenant = canonicalize('https://contoso.ciamlogin.com')
result = host == 'contoso.ciamlogin.com' and tenant == 'contoso.onmicrosoft.com'
""")


def _claims_invalid():
    result=call('msal.token_cache','_parse_claims_or_raise','[sensitive]')
    return not result.ok and result.exception_type.endswith('ValueError') and 'sensitive' not in (result.exception_message or '')


def _merge():
    result=call_value('msal.token_cache','_merge_claims','{"a":{"x":1},"z":0}','{"a":{"y":2},"z":3}')
    return json.loads(result)=={'a':{'x':1,'y':2},'z':3}


if __name__ == '__main__':
    main()
