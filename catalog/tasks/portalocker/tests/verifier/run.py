from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from nl2repobench.verification.process_cleanup import terminate_uid_processes

PREFIX = "PORTALOCKER_RESULT="
SCENARIOS: dict[str, Any] = {
    "exports-version-flags": {"version":"4.3.0","exclusive":2,"shared":1,"nonblocking":4,"unblock":8,"flags":["EXCLUSIVE","SHARED","NON_BLOCKING","UNBLOCK"]},
    "package-metadata": {"distribution":"4.3.0","description":"Wraps the portalocker recipe for easy usage"},
    "lock-context-persistence": {"before":False,"inside":[True,True,True],"after":True},
    "lock-write-read": "payload",
    "nonblocking-contention": {"acquired":False,"type":"portalocker.exceptions.AlreadyLocked","waited":False},
    "timeout-contention": {"acquired":False,"type":"portalocker.exceptions.AlreadyLocked","waited":True},
    "blocking-contention": {"acquired":2,"exits":[0,0]},
    "lock-release": True,
    "lock-exception": {"type":"LockException","strerror":None},
    "rlock-reentry": {"same":[False,False],"count":2,"mid":1},
    "temporary-file-lock": {"inside":True,"after":True},
    "pid-file-lock": {"positive":True,"same":True,"removed":True},
    "pid-file-read-missing": True,
    "semaphore-slots": {"first":True,"second":"portalocker.exceptions.AlreadyLocked","files":1},
    "named-semaphore": {"name":"named","count":2},
    "open-atomic-binary": True,
    "open-atomic-text": True,
    "open-atomic-existing": "old",
    "open-atomic-cleanup": {"published":True,"temp_gone":True},
    "flags-validation": [True,True],
    "shared-lock": True,
    "low-level-lock": True,
    "lock-file-open-kwargs": True,
    "lock-timeout-defaults": {"timeout":5,"interval":0.25,"fail":False},
    "rlock-overrelease": "LockException",
    "pidfile-cleanup": True,
    "semaphore-invalid": "wrong",
    "semaphore-filename": ["demo.00.lock","demo.01.lock"],
    "module-exports": {"all":["AlreadyLocked","BoundedSemaphore","LOCK_EX","LOCK_NB","LOCK_SH","LOCK_UN","Lock","LockException","LockFlags","LockLostError","NamedBoundedSemaphore","PidFileLock","RLock","RedisLock","TemporaryFileLock","lock","open_atomic","unlock"],"modules":["portalocker.constants","portalocker.exceptions","portalocker.portalocker","portalocker.types","portalocker.utils"]},
    "deterministic-repeated": [True,True],
    "candidate-isolation": {"uid":10001,"site":"/tmp/candidate-site"},
    "network-false": True,
}


def invoke(scenario: str) -> dict[str, Any]:
    command = ["python","-I","-B",str(Path(__file__).with_name("adapter.py")),"--candidate-site","/tmp/candidate-site","--scenario",scenario]
    environment = {"HOME":"/tmp/candidate-build/home","TMPDIR":"/tmp/candidate-build/tmp","PORTALOCKER_CANDIDATE_SITE":"/tmp/candidate-site","PATH":"/usr/local/bin:/usr/bin:/bin","PYTHONDONTWRITEBYTECODE":"1"}
    with tempfile.TemporaryDirectory(prefix="portalocker-verifier-"):
        proc = subprocess.Popen(command, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True, preexec_fn=_drop_candidate_privileges)
        try:
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL); proc.wait()
            return {"ok":False,"type":"CandidateTimeout","message":scenario}
        finally:
            terminate_uid_processes(10001)
    lines = [line for line in stdout.splitlines() if line.startswith(PREFIX)]
    if proc.returncode != 0 or len(lines) != 1: return {"ok":False,"type":"CandidateProcessError","message":stderr[-2000:]}
    try: value = json.loads(lines[0][len(PREFIX):])
    except json.JSONDecodeError as exc: return {"ok":False,"type":"CandidateProtocolError","message":str(exc)}
    return value if isinstance(value, dict) else {"ok":False,"type":"CandidateProtocolError"}


def _drop_candidate_privileges() -> None:
    os.setgroups([])
    os.setgid(10001)
    os.setuid(10001)


def main() -> int:
    leaves = []
    for name, expected in SCENARIOS.items():
        result = invoke(name)
        actual = result.get("value") if result.get("ok") is True else result.get("type")
        if name == "pid-file-lock" and isinstance(actual, dict):
            passed = actual.get("positive") is True and actual.get("same") is True and actual.get("removed") is True
        elif name == "candidate-isolation" and isinstance(actual, dict):
            passed = actual.get("uid") == 10001 and actual.get("site") == "/tmp/candidate-site"
        else:
            passed = actual == expected
        leaves.append({"id":f"portalocker/{name}","status":"passed" if passed else "failed","message":"" if passed else json.dumps({"actual":actual,"expected":expected},sort_keys=True,default=str)[:2000]})
    print(json.dumps({"schema_version":"1.0","leaves":leaves},sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
