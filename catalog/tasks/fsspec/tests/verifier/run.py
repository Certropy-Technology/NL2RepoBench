from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


SCENARIOS = {
    "memory-basic": "from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/a',b'abc'); assert fs.cat_file('/a')==b'abc'; result=True",
    "memory-tree": "from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/d/a',b'a'); fs.pipe_file('/d/s/b',b'b'); assert fs.find('/',detail=False)==['/d/a','/d/s/b']; result=True",
    "memory-copy-move-rm": "from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/a',b'x'); fs.copy('/a','/b'); fs.mv('/b','/c'); assert fs.cat_file('/c')==b'x'; fs.rm('/c'); assert not fs.exists('/c'); result=True",
    "fsmap-basic": "from fsspec.implementations.memory import MemoryFileSystem; from fsspec.mapping import FSMap; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.mkdir('/kv'); m=FSMap('/kv',fs); m['one']=b'1'; assert m['one']==b'1' and list(m)==['one']; del m['one']; result=True",
    "mapper-factory": "import fsspec; from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/kv/a',b'A'); assert fsspec.get_mapper('memory:///kv')['a']==b'A'; result=True",
    "registry-and-url": "import fsspec; from fsspec.core import url_to_fs,split_protocol,strip_protocol; fs,p=url_to_fs('memory:///x'); assert fs.protocol=='memory' and p=='/x' and split_protocol('plain')==(None,'plain') and strip_protocol('memory:///x')=='/x'; result=True",
    "open-memory-text": "exec(\"import fsspec\\nfrom fsspec.implementations.memory import MemoryFileSystem\\nfs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/x',b'alpha')\\nwith fsspec.open('memory:///x','rt') as h: assert h.read()=='alpha'\") ; result=True",
    "open-gzip": "exec(\"import fsspec,gzip\\nfrom fsspec.core import get_compression\\nfrom fsspec.implementations.memory import MemoryFileSystem\\nfs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/x.gz',gzip.compress(b'text'))\\nwith fsspec.open('memory:///x.gz','rt',compression='gzip') as h: assert h.read()=='text'\\nassert get_compression('x.gz','infer')=='gzip'\") ; result=True",
    "open-files": "exec(\"import fsspec\\nfrom fsspec.implementations.memory import MemoryFileSystem\\nfs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear()\\nwith fsspec.open_files(['memory:///a','memory:///b'],'wt') as hs: hs[0].write('a'); hs[1].write('b')\\nassert fs.cat_file('/a')==b'a'\") ; result=True",
    "filesystem-helpers": "from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.pipe_file('/d/a',b'abc'); assert fs.head('/d/a',2)==b'ab' and fs.tail('/d/a',2)==b'bc'; result=True",
    "filesystem-json": "from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); assert MemoryFileSystem.from_json(fs.to_json()).protocol=='memory'; result=True",
    "storage-options": "from fsspec.utils import infer_storage_options,update_storage_options; o=infer_storage_options('hdfs://u:p@n:8020/x'); assert o['host']=='n' and o['port']==8020 and o['username']=='u' and o['password']=='p'; update_storage_options(o,{'x':1}); result=True",
    "path-utilities": "from fsspec.utils import build_name_function,common_prefix,other_paths,get_protocol,get_file_extension,merge_offset_ranges,tokenize; assert [build_name_function(12)(i) for i in range(3)]==['00','01','02']; assert common_prefix(['/a/b','/a/c'])=='/a' and get_protocol('memory:///x')=='memory' and get_file_extension('x.TXT')=='TXT' and other_paths(['/a/x','/a/y'],'/o')==['/o/x','/o/y'] and len(tokenize('x'))==32; result=True",
    "read-block": "from io import BytesIO; from fsspec.utils import read_block,isfilelike; f=BytesIO(b'aa\\nbb\\ncc'); assert read_block(f,0,5,delimiter=b'\\n')==b'aa\\nbb\\n' and isfilelike(f); result=True",
    "all-bytes-cache": "from fsspec.caching import AllBytes; calls=[]; fetch=lambda s,e:(calls.append((s,e)) or b'abcdefghij'[s:e]); c=AllBytes(4,fetch,10); assert c._fetch(0,5)==b'abcde' and c._fetch(5,8)==b'fgh' and len(calls)==1; result=True",
    "read-ahead-cache": "from fsspec.caching import ReadAheadCache; calls=[]; fetch=lambda s,e:(calls.append((s,e)) or b'abcdefghij'[s:e]); c=ReadAheadCache(4,fetch,10); assert c._fetch(0,5)==b'abcde' and c._fetch(2,4)==b'cd'; result=True",
    "block-cache": "from fsspec.caching import BlockCache; calls=[]; fetch=lambda s,e:(calls.append((s,e)) or b'abcdefghij'[s:e]); c=BlockCache(4,fetch,10); assert c._fetch(0,4)==b'abcd' and c._fetch(4,8)==b'efgh' and c._fetch(0,2)==b'ab'; result=True",
    "error-contracts": "import fsspec; from fsspec.core import get_compression; from fsspec.implementations.memory import MemoryFileSystem; fs=MemoryFileSystem(skip_instance_cache=True); fs.store.clear(); fs.mkdir('/d');\ntry: fs.open('/d','rb')\nexcept IsADirectoryError: pass\nelse: raise AssertionError\ntry: get_compression('x','unknown')\nexcept ValueError: pass\nelse: raise AssertionError\nresult=True",
}


def main() -> None:
    leaves = []
    for leaf_id, source in SCENARIOS.items():
        observed = execute_script(source, timeout_sec=12.0)
        if observed.ok and observed.value is True:
            leaves.append({"id": leaf_id, "status": "passed"})
        else:
            message = observed.exception_type or observed.exception_message or "scenario failed"
            leaves.append({"id": leaf_id, "status": "failed", "message": message})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
