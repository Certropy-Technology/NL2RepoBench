# termcolor Task Authoring Status

## Task Information
- **Task ID**: termcolor
- **Version**: 1.0.0
- **Language**: Python
- **Difficulty**: easy
- **Category**: utility-library

## Source Freeze
- **Upstream URL**: https://github.com/termcolor/termcolor
- **Revision**: 0980eb52aa867fc32f70859a61c0609501b73a99
- **Version**: 3.3.0
- **License**: MIT (SPDX-License-Identifier: MIT)
- **Source Digest**: sha256:c43f9ad2ed38f168bb84666a70ac8c645b648eac1cab10b79438971af48f2290
- **Source Archive**: /data/NL2RepoBench-integration-20260827/.nl2repo/authoring-work/python-wave2/termcolor/source-0980eb52aa867fc32f70859a61c0609501b73a99.tar.gz

## Collection
- **Test Framework**: pytest
- **Frozen Total**: 85 tests
- **Collection Command**: `python3 -m pytest tests/ --collect-only -q`
- **Collection Status**: Successfully collected 85 tests from frozen source

## Instruction
- **Location**: catalog/sources/termcolor/instruction.md
- **Length**: 396 lines
- **Sections**:
  - Project Description
  - Natural Language Instruction
  - Environment Configuration
  - Project Directory Structure
  - API Usage Guide (complete with all functions, constants, and parameters)
  - Implementation Notes
  - Examples
  - Error Handling and Boundary Conditions
  - Security

## Dependencies
- **Runtime Dependencies**: None (standard library only)
- **Build Dependencies**: hatch-vcs, hatchling
- **Lock Artifact**: sha256:aea4b055fb9579955bcec242e5bbd7f0a3abc3813d8f274c3e6850ac1a764fea (135 bytes)

## Environment
- **Python Version**: 3.12
- **Base Image**: python:3.12-slim
- **Base Image Digest**: sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea
- **Build Command**: `SETUPTOOLS_SCM_PRETEND_VERSION=3.3.0 pip install --no-cache-dir .`
- **Network Mode**: no-network (offline dependencies preinstalled-image)

## Verifier
- **Protocol**: custom-json-v1
- **Type**: separate verifier
- **Entrypoint**: run.py
- **Test Count**: 85 hidden tests covering:
  - Public exports validation
  - Constants (COLORS, HIGHLIGHTS, ATTRIBUTES, RESET)
  - colored() function with all color/background/attribute combinations
  - RGB tuple support for foreground and background
  - Environment variable handling (NO_COLOR, FORCE_COLOR, ANSI_COLORS_DISABLED)
  - can_colorize() function with override parameters
  - cprint() function
  - Type conversion and edge cases
- **Verifier Bundle**: sha256:6fe90b5b96407d36f8e5d03d9b69d90af02069e4d8a3a32fc263865b15a23d9a (9183 bytes)

## Oracle Solution
- **Type**: Frozen source extraction
- **Bundle**: sha256:248549500fbaaeb0e9aa391dfb2c805a6e8229f3c141ef4d133c998248dd42b4 (15709 bytes)
- **Source Verification**: SHA-256 checked against expected digest
- **Installation**: Uses SETUPTOOLS_SCM_PRETEND_VERSION=3.3.0 for version
- **Oracle Bundle Contents**:
  - solve.sh (88 lines)
  - source-0980eb52aa867fc32f70859a61c0609501b73a99.tar.gz (frozen source archive)

## Control Scripts
All control scripts created and validated with `bash -n`:

1. **empty.sh**: Empty workspace control
2. **stub.sh**: Minimal installable package with empty implementations
3. **forgery.sh**: Attempts to forge grading results (verifier must ignore)
4. **install-failure.sh**: Candidate that cannot be installed
5. **panic.sh**: Candidate that crashes on import
6. **hang.sh**: Candidate that hangs on function calls
7. **oversized-output.sh**: Candidate that produces excessive output
8. **background-process.sh**: Candidate that spawns background processes
9. **offline.sh**: Verifies verifier works without network

## Compilation
- **Command**: `uv run nl2repo harbor compile catalog/sources/termcolor --output catalog/tasks --toolchain toolchain.lock.toml --artifact-root .nl2repo/artifacts --allow-private`
- **Status**: ✅ SUCCESS
- **Output**: catalog/tasks/termcolor/
- **Bundle Manifest**: catalog/tasks/termcolor/bundle.manifest.json
- **Canonical Manifest Digest**: sha256:55abbd053775e99d3c69d25161f97abacf7aec01e7bd8742f24ae0d422fb357d

## Validation Gates
- ✅ Source validation: `uv run nl2repo task validate-source catalog/sources/termcolor`
- ✅ Network policy lint: No errors found
- ✅ Python syntax check: `python3 -m py_compile catalog/sources/termcolor/harbor/verifier/run.py`
- ✅ Shell script validation: `bash -n` on all control scripts and solution
- ✅ Harbor compilation: Successfully generated runtime bundle

## Artifacts Registry
All artifacts registered in `.nl2repo/artifacts/private/sha256/`:

1. **requirements.lock.txt**
   - Digest: sha256:aea4b055fb9579955bcec242e5bbd7f0a3abc3813d8f274c3e6850ac1a764fea
   - Size: 135 bytes
   - Location: .nl2repo/artifacts/private/sha256/ae/aea4b055fb9579955bcec242e5bbd7f0a3abc3813d8f274c3e6850ac1a764fea

2. **verifier.tar.gz**
   - Digest: sha256:6fe90b5b96407d36f8e5d03d9b69d90af02069e4d8a3a32fc263865b15a23d9a
   - Size: 9183 bytes
   - Location: .nl2repo/artifacts/private/sha256/6f/6fe90b5b96407d36f8e5d03d9b69d90af02069e4d8a3a32fc263865b15a23d9a

3. **oracle.tar.gz**
   - Digest: sha256:248549500fbaaeb0e9aa391dfb2c805a6e8229f3c141ef4d133c998248dd42b4
   - Size: 15709 bytes
   - Location: .nl2repo/artifacts/private/sha256/24/248549500fbaaeb0e9aa391dfb2c805a6e8229f3c141ef4d133c998248dd42b4

## Lifecycle Status
- **Current Status**: packaged
- **Ready for**: Oracle and controls execution
- **Blocked by**: None - all artifacts prepared and compilation successful

## Next Steps
1. Run Oracle once: `uv run --frozen --project harbor-runner harbor run -p catalog/tasks/termcolor -a oracle --job-name termcolor-oracle-001 -o .nl2repo/runs/termcolor-oracle --n-concurrent 1 --yes`
2. Verify Oracle results: valid=true, collected=85, reward>=0.80
3. Run control matrix (empty, stub, forgery, install-failure, panic, hang, oversized-output, background-process, offline)
4. Save evidence to catalog/sources/termcolor/evidence/
5. Update lifecycle status to controls-passed if all gates pass

## Commands Run
```bash
# Source verification
sha256sum /data/NL2RepoBench-integration-20260827/.nl2repo/authoring-work/python-wave2/termcolor/source-0980eb52aa867fc32f70859a61c0609501b73a99.tar.gz
# Output: c43f9ad2ed38f168bb84666a70ac8c645b648eac1cab10b79438971af48f2290

# Test collection
cd .nl2repo/authoring-work/termcolor/source-extracted/termcolor-0980eb52aa867fc32f70859a61c0609501b73a99
SETUPTOOLS_SCM_PRETEND_VERSION=3.3.0 pip install -e .
python3 -m pytest tests/ --collect-only -q
# Output: 85 tests collected

# Test execution
python3 -m pytest tests/ -v
# Output: 85 passed in 0.24s

# Validation
python3 -m py_compile catalog/sources/termcolor/harbor/verifier/run.py
bash -n catalog/sources/termcolor/harbor/solution/solve.sh
bash -n catalog/sources/termcolor/harbor/controls/*.sh
uv run nl2repo task validate-source catalog/sources/termcolor
uv run nl2repo task lint-network
uv run nl2repo harbor compile catalog/sources/termcolor --output catalog/tasks --toolchain toolchain.lock.toml --artifact-root .nl2repo/artifacts --allow-private
```

## Tool Versions
- Python: 3.14.0a3
- Docker: Available
- uv: (via uv run)
- nl2repo: Current checkout
- harbor-runner: pinned (via --frozen)

## Risk Assessment
- **Source Authority**: KNOWN - exact commit SHA verified
- **License**: CLEAR - MIT license confirmed
- **Dependencies**: MINIMAL - no runtime dependencies
- **Environment**: STABLE - fixed Python version and image digest
- **Network**: COMPLIANT - no-network mode, offline dependencies
- **Verifier Isolation**: PROPER - separate verifier with subprocess boundary
- **Controls Coverage**: COMPLETE - all required controls implemented

## Traceability
- All 85 tests in the verifier are traceable to public API behaviors documented in instruction.md
- No upstream test assertions copied
- No implementation internals exposed
- No network/TTY/filesystem dependencies in hidden tests (all use force_color=True override)
- Fixed collection denominator of 85 tests

## Changed Files
```
catalog/sources/termcolor/task.toml
catalog/sources/termcolor/instruction.md
catalog/sources/termcolor/harbor/verifier/run.py
catalog/sources/termcolor/harbor/solution/solve.sh
catalog/sources/termcolor/harbor/controls/empty.sh
catalog/sources/termcolor/harbor/controls/stub.sh
catalog/sources/termcolor/harbor/controls/forgery.sh
catalog/sources/termcolor/harbor/controls/install-failure.sh
catalog/sources/termcolor/harbor/controls/panic.sh
catalog/sources/termcolor/harbor/controls/hang.sh
catalog/sources/termcolor/harbor/controls/oversized-output.sh
catalog/sources/termcolor/harbor/controls/background-process.sh
catalog/sources/termcolor/harbor/controls/offline.sh
catalog/sources/termcolor/evidence/source-freeze.txt
catalog/sources/termcolor/evidence/authoring-status.md
```

## Artifact Inventory
```
.nl2repo/authoring-work/termcolor/source-extracted/
.nl2repo/authoring-work/termcolor/artifacts/requirements.lock.txt
.nl2repo/authoring-work/termcolor/artifacts/verifier.tar.gz
.nl2repo/authoring-work/termcolor/artifacts/oracle.tar.gz
.nl2repo/artifacts/private/sha256/ae/aea4b055fb9579955bcec242e5bbd7f0a3abc3813d8f274c3e6850ac1a764fea
.nl2repo/artifacts/private/sha256/6f/6fe90b5b96407d36f8e5d03d9b69d90af02069e4d8a3a32fc263865b15a23d9a
.nl2repo/artifacts/private/sha256/24/248549500fbaaeb0e9aa391dfb2c805a6e8229f3c141ef4d133c998248dd42b4
```
