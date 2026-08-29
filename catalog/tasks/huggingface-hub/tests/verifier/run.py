from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _call(source: str) -> tuple[int, str, str]:
    candidate = os.environ.get("HF_HUB_CANDIDATE_PATH", "/tmp/candidate-site")
    dependency = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "")
    prelude = (
        "import sys; "
        f"sys.path.insert(0, {candidate!r}); "
        f"sys.path.insert(1, {dependency!r}) if {bool(dependency)!r} else None\n"
    )
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", prelude + source],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 70, "", str(exc)
    return completed.returncode, completed.stdout, completed.stderr


def _scenario(source: str) -> bool:
    code, stdout, _ = _call(source)
    return code == 0 and stdout.strip().endswith("OK")


SCENARIOS: list[tuple[str, str]] = [
    ("version", "from huggingface_hub import __version__; assert __version__ == '1.29.0.dev0'; print('OK')"),
    ("root_exports", "import huggingface_hub as h; names = ['HfApi','ModelInfo','DatasetInfo','SpaceInfo','RepoUrl','HfFileMetadata','CommitOperationAdd','CommitOperationDelete','HfFileSystem','hf_hub_url']; assert all(hasattr(h, n) for n in names); print('OK')"),
    ("url_model", "from huggingface_hub import hf_hub_url; assert hf_hub_url('org/model','config.json') == 'https://huggingface.co/org/model/resolve/main/config.json'; print('OK')"),
    ("url_dataset", "from huggingface_hub import hf_hub_url; assert hf_hub_url('org/data','train.csv', repo_type='dataset') == 'https://huggingface.co/datasets/org/data/resolve/main/train.csv'; print('OK')"),
    ("url_space", "from huggingface_hub import hf_hub_url; assert hf_hub_url('org/demo','app.py', repo_type='space', revision='v1') == 'https://huggingface.co/spaces/org/demo/resolve/v1/app.py'; print('OK')"),
    ("url_subfolder_endpoint", "from huggingface_hub import hf_hub_url; assert hf_hub_url('org/model','weights.bin', subfolder='nested/dir', revision='abc', endpoint='https://example.test/') == 'https://example.test//org/model/resolve/abc/nested/dir/weights.bin'; print('OK')"),
    ("valid_repo_ids", "from huggingface_hub.utils import validate_repo_id; [validate_repo_id(x) for x in [None,'model','org/model','_hidden/model','a.b-c_d']]; print('OK')"),
    ("invalid_repo_space", "from huggingface_hub.utils import validate_repo_id, HFValidationError;\ntry: validate_repo_id('bad id')\nexcept HFValidationError: print('OK')\nelse: raise AssertionError"),
    ("invalid_repo_slashes", "from huggingface_hub.utils import validate_repo_id, HFValidationError;\ntry: validate_repo_id('a/b/c')\nexcept HFValidationError: print('OK')\nelse: raise AssertionError"),
    ("invalid_repo_punctuation", "from huggingface_hub.utils import validate_repo_id, HFValidationError;\ntry: validate_repo_id('org/name..bad')\nexcept HFValidationError: print('OK')\nelse: raise AssertionError"),
    ("headers_token", "from huggingface_hub.utils import build_hf_headers; h=build_hf_headers(token='secret', library_name='demo', library_version='2'); assert h['authorization']=='Bearer secret'; assert h['user-agent'].startswith('demo/2; hf_hub/1.29.0.dev0'); print('OK')"),
    ("headers_false", "from huggingface_hub.utils import build_hf_headers; h=build_hf_headers(token=False); assert 'authorization' not in h; assert 'hf_hub/1.29.0.dev0' in h['user-agent']; print('OK')"),
    ("headers_precedence", "from huggingface_hub.utils import build_hf_headers; raw={'authorization':'Custom','x-test':'yes'}; h=build_hf_headers(token='secret', user_agent='client/1', headers=raw); assert h['authorization']=='Custom' and h['x-test']=='yes' and raw == {'authorization':'Custom','x-test':'yes'}; print('OK')"),
    ("headers_mapping", "from huggingface_hub.utils import build_hf_headers; h=build_hf_headers(token=False, user_agent={'z':'last','a':'first'}); assert h['user-agent'].endswith('; z/last; a/first'); print('OK')"),
    ("datetime_z", "from huggingface_hub.utils import parse_datetime; d=parse_datetime('2024-01-02T03:04:05Z'); assert d.year==2024 and d.tzinfo is not None and d.utcoffset().total_seconds()==0; print('OK')"),
    ("datetime_fraction", "from huggingface_hub.utils import parse_datetime; d=parse_datetime('2024-01-02T03:04:05.123456Z'); assert d.microsecond==123456; print('OK')"),
    ("datetime_invalid", "from huggingface_hub.utils import parse_datetime;\ntry: parse_datetime('invalid')\nexcept ValueError: print('OK')\nelse: raise AssertionError"),
    ("filter_all", "from huggingface_hub.utils import filter_repo_objects; xs=['a.txt','b.py','sub/c.txt']; assert list(filter_repo_objects(xs))==xs; print('OK')"),
    ("filter_allow", "from huggingface_hub.utils import filter_repo_objects; xs=['a.txt','b.py','sub/c.txt']; assert list(filter_repo_objects(xs, allow_patterns='*.txt'))==['a.txt','sub/c.txt']; print('OK')"),
    ("filter_ignore", "from huggingface_hub.utils import filter_repo_objects; xs=['a.txt','b.py','sub/c.txt']; assert list(filter_repo_objects(xs, allow_patterns=['*.txt','*.py'], ignore_patterns='sub/*'))==['a.txt','b.py']; print('OK')"),
    ("filter_key", "from huggingface_hub.utils import filter_repo_objects; xs=[{'path':'a.txt'},{'path':'b.py'}]; assert list(filter_repo_objects(xs, allow_patterns='*.txt', key=lambda x:x['path']))==[xs[0]]; print('OK')"),
    ("uri_bare", "from huggingface_hub.hf_api import repo_type_and_id_from_hf_id; assert repo_type_and_id_from_hf_id('org/model') == (None,'org','model'); print('OK')"),
    ("uri_hf_dataset", "from huggingface_hub.hf_api import repo_type_and_id_from_hf_id; assert repo_type_and_id_from_hf_id('hf://datasets/org/data') == ('dataset','org','data'); print('OK')"),
    ("uri_https_space", "from huggingface_hub.hf_api import repo_type_and_id_from_hf_id; assert repo_type_and_id_from_hf_id('https://huggingface.co/spaces/org/demo') == ('space','org','demo'); print('OK')"),
    ("uri_foreign_host", "from huggingface_hub.hf_api import repo_type_and_id_from_hf_id;\ntry: repo_type_and_id_from_hf_id('https://example.test/org/model')\nexcept ValueError: print('OK')\nelse: raise AssertionError"),
    ("folder_model", "from huggingface_hub.file_download import repo_folder_name; assert repo_folder_name(repo_id='org/model', repo_type='model') == 'models--org--model'; print('OK')"),
    ("folder_dataset", "from huggingface_hub.file_download import repo_folder_name; assert repo_folder_name(repo_id='org/data', repo_type='dataset') == 'datasets--org--data'; print('OK')"),
    ("folder_space", "from huggingface_hub.file_download import repo_folder_name; assert repo_folder_name(repo_id='org/demo', repo_type='space') == 'spaces--org--demo'; print('OK')"),
    ("file_metadata", "from huggingface_hub import HfFileMetadata; x=HfFileMetadata('abc','etag','https://example.test/file',12,None); assert x.commit_hash=='abc' and x.etag=='etag' and x.size==12 and x.xet_file_data is None; print('OK')"),
    ("model_info", "from huggingface_hub import ModelInfo; x=ModelInfo(id='org/model', sha='deadbeef', pipeline_tag='text-classification'); assert x.id=='org/model' and x.sha=='deadbeef' and x.pipeline_tag=='text-classification'; assert 'ModelInfo' in repr(x); print('OK')"),
    ("dataset_info", "from huggingface_hub import DatasetInfo; x=DatasetInfo(id='org/data', sha='abc', downloads=4); assert x.id=='org/data' and x.downloads==4 and x.sha=='abc'; print('OK')"),
    ("space_info", "from huggingface_hub import SpaceInfo; x=SpaceInfo(id='org/demo', sdk='gradio', private=True); assert x.id=='org/demo' and x.sdk=='gradio' and x.private is True; print('OK')"),
    ("card_data", "from huggingface_hub import DatasetCardData; x=DatasetCardData(language='en', license='mit'); assert x.language=='en' and x.license=='mit'; print('OK')"),
    ("eval_result", "from huggingface_hub import EvalResult; x=EvalResult(task_type='text-classification', dataset_type='demo', dataset_name='Demo', metric_type='accuracy', metric_value=.9); assert x.metric_value==.9 and x.task_type=='text-classification'; print('OK')"),
    ("commit_add", "from huggingface_hub import CommitOperationAdd; x=CommitOperationAdd('a.txt', b'abc'); assert x.path_in_repo=='a.txt' and x.path_or_fileobj==b'abc' and x.upload_info.size==3 and x.upload_info.sha256.hex()=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'; print('OK')"),
    ("commit_delete_auto", "from huggingface_hub import CommitOperationDelete; assert CommitOperationDelete('folder/').is_folder is True and CommitOperationDelete('file').is_folder is False; print('OK')"),
    ("commit_delete_explicit", "from huggingface_hub import CommitOperationDelete; assert CommitOperationDelete('x', True).is_folder is True and CommitOperationDelete('x', False).is_folder is False; print('OK')"),
    ("api_config", "from huggingface_hub import HfApi; x=HfApi(endpoint='https://example.test/', token='abc', library_name='demo', library_version='1'); assert x.endpoint=='https://example.test/' and x.token=='abc' and x.library_name=='demo' and x.library_version=='1' and x.headers is None; print('OK')"),
    ("api_headers_copy", "from huggingface_hub import HfApi; raw={'x':'y'}; x=HfApi(endpoint='https://example.test', headers=raw); assert x.headers == raw and x.headers is raw; print('OK')"),
    ("filesystem", "from huggingface_hub import HfFileSystem; x=HfFileSystem(token='abc'); assert x.protocol=='hf' and x.token=='abc'; print('OK')"),
]


def main() -> int:
    leaves = []
    for identifier, source in SCENARIOS:
        try:
            passed = _scenario(source)
        except Exception:
            passed = False
        leaves.append({"id": identifier, "status": "passed" if passed else "failed"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
