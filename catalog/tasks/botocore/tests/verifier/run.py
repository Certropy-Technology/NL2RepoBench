from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


CASES = {
    "import_version": "import botocore; assert botocore.__version__ == '1.43.80'",
    "service_model": "from botocore.session import get_session; m=get_session().get_service_model('s3'); assert m.service_name == 's3'; assert m.metadata['protocol'] == 'rest-xml'",
    "operation_names": "from botocore.session import get_session; ops=get_session().get_service_model('s3').operation_names; assert 'ListObjectsV2' in ops and 'PutObject' in ops",
    "paginator_model": "from botocore.session import get_session; p=get_session().get_paginator_model('s3'); assert 'ListObjectsV2' in p._paginator_config and p._paginator_config['ListObjectsV2']['input_token'] == 'ContinuationToken'",
    "available_services": "from botocore.session import get_session; assert 's3' in get_session().get_available_services() and 'dynamodb' in get_session().get_available_services()",
    "available_regions": "from botocore.session import get_session; regions=get_session().get_available_regions('s3'); assert 'us-east-1' in regions and get_session().get_available_regions('not-a-service') == []",
    "config_merge": "from botocore.config import Config; a=Config(region_name='us-east-1',retries={'max_attempts':3}); b=a.merge(Config(user_agent_extra='bench')); assert b.region_name == 'us-east-1' and b.user_agent_extra == 'bench' and a.user_agent_extra is None",
    "credentials": "from botocore.session import get_session; s=get_session(); s.set_credentials('AKID','SECRET','TOKEN'); c=s.get_credentials(); assert (c.access_key,c.secret_key,c.token)==('AKID','SECRET','TOKEN')",
    "session_precedence": "import os; from botocore.session import get_session; os.environ['AWS_DEFAULT_REGION']='eu-west-1'; s=get_session(); s.set_config_variable('region','us-east-1'); assert s.get_config_variable('region') == 'us-east-1'",
    "request_prepare": "from botocore.awsrequest import AWSRequest; r=AWSRequest(method='POST',url='https://example.test/path',data=b'abc',headers={'X-Test':'yes'}); p=r.prepare(); assert p.method == 'POST' and p.body == b'abc' and p.headers['X-Test'] == 'yes'",
    "unsigned_request": "import botocore; from botocore.awsrequest import AWSRequest; from botocore.auth import UNSIGNED_PAYLOAD; r=AWSRequest(method='GET',url='https://example.test/'); assert r.method == 'GET' and UNSIGNED_PAYLOAD",
    "sigv4": "from botocore.awsrequest import AWSRequest; from botocore.auth import SigV4Auth; from botocore.credentials import Credentials; r=AWSRequest(method='GET',url='https://example.test/'); r.context['timestamp']='20200101T000000Z'; SigV4Auth(Credentials('AKID','SECRET'),'execute-api','us-east-1').add_auth(r); assert 'Authorization' in r.headers and r.headers['Authorization'].startswith('AWS4-HMAC-SHA256') and 'X-Amz-Date' in r.headers",
    "client_metadata": "from botocore.session import get_session; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1',endpoint_url='https://s3.us-east-1.amazonaws.com'); assert c.meta.service_model.service_name == 's3' and c.meta.region_name == 'us-east-1'",
    "client_mapping": "from botocore.session import get_session; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1'); assert c.meta.method_to_api_mapping['list_objects_v2'] == 'ListObjectsV2'",
    "stub_response": "from botocore.session import get_session; from botocore.stub import Stubber; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1'); x=Stubber(c); x.add_response('list_buckets',{'Buckets':[]}); x.activate(); assert c.list_buckets() == {'Buckets':[]}",
    "stub_context": "from botocore.session import get_session\nfrom botocore.stub import Stubber\ns=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1')\nx=Stubber(c); x.add_response('list_buckets',{'Buckets':[]})\nwith x:\n    assert c.list_buckets() == {'Buckets':[]}",
    "stub_unexpected": "from botocore.session import get_session; from botocore.stub import Stubber; from botocore.exceptions import UnStubbedResponseError; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1'); x=Stubber(c); x.activate();\ntry: c.list_buckets(); raise AssertionError\nexcept UnStubbedResponseError: pass",
    "stub_exhausted": "from botocore.session import get_session; from botocore.stub import Stubber; from botocore.exceptions import UnStubbedResponseError; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1'); x=Stubber(c); x.add_response('list_buckets',{}); x.activate(); c.list_buckets();\ntry: c.list_buckets(); raise AssertionError\nexcept UnStubbedResponseError: pass",
    "client_error": "from botocore.session import get_session; from botocore.stub import Stubber; from botocore.exceptions import ClientError; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1'); x=Stubber(c); x.add_client_error('list_buckets','AccessDenied','no'); x.activate();\ntry: c.list_buckets(); raise AssertionError\nexcept ClientError as e: assert e.response['Error']['Code'] == 'AccessDenied'",
    "param_validation": "from botocore.session import get_session; from botocore.stub import Stubber; from botocore.exceptions import ParamValidationError; s=get_session(); s.set_credentials('AKID','SECRET'); c=s.create_client('s3',region_name='us-east-1'); x=Stubber(c); x.add_response('get_object',{}); x.activate();\ntry: c.get_object(); raise AssertionError\nexcept ParamValidationError: pass",
    "retry_config": "from botocore.translate import build_retry_config; x=build_retry_config('s3', {'__default__': {'max_attempts': 3}}, {'__default__': {'__type': 'standard', 'max_attempts': 3}}); assert isinstance(x, dict) and x['__default__']['max_attempts'] == 3",
    "endpoint_partition": "from botocore.session import get_session; s=get_session(); assert s.get_partition_for_region('us-east-1') == 'aws'",
    "waiter_model": "from botocore.session import get_session; w=get_session().get_waiter_model('s3'); assert 'BucketExists' in w.waiter_names and w.get_waiter('BucketExists').operation == 'HeadBucket' and w.get_waiter('BucketExists').max_attempts > 0",
    "model_repeatability": "from botocore.session import get_session; s=get_session(); a=s.get_service_model('s3').operation_model('ListObjectsV2').input_shape.name; b=s.get_service_model('s3').operation_model('ListObjectsV2').input_shape.name; assert a == b == 'ListObjectsV2Request'",
}


def main() -> int:
    worker = "import sys\n" + "code = " + repr(CASES) + "\n" + "sys.path[:0] = ['/tmp/candidate-site', '/opt/candidate-dependencies/site']\n" + "case=sys.argv[1]; exec(code[case], {'__name__':'__main__'})\n"
    fd, worker_name = tempfile.mkstemp(prefix="botocore-worker-", suffix=".py", dir="/tmp")
    os.close(fd)
    worker_path = Path(worker_name)
    try:
        worker_path.write_text(worker, encoding="utf-8")
        os.chown(worker_path, 10001, 10001)
        os.chmod(worker_path, 0o500)
        leaves = []
        for case in CASES:
            completed = subprocess.run(
                ["runuser", "-u", "candidate", "--", sys.executable, "-I", str(worker_path), case],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                env={**os.environ, "AWS_EC2_METADATA_DISABLED": "true"},
            )
            leaves.append({"id": case, "status": "passed" if completed.returncode == 0 else "failed", "message": completed.stderr[-1000:]})
        print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
        return 0
    finally:
        worker_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
