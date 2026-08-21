# Blocked Pilot Tasks

## boltons

The candidate source currently reaches 407/423 against the frozen legacy
tests. Sixteen failures are concentrated in `funcutils` and traceback parsing,
which indicates that the selected source revision does not match the frozen
test image. It remains outside the active pilot until the original source
revision is recovered or a new dataset version is frozen.

## humanize

The candidate source currently reaches 573/607 against the frozen legacy
tests. Thirty-four assertions differ in time and number formatting, indicating
source/test version drift. It remains outside the active pilot until the
matching source revision is recovered.

## tenacity

The candidate source currently reaches 120/124 against the frozen legacy
tests. Four assertions fail in logging format and decorator metadata behavior,
indicating source/test version drift. It remains outside the active pilot
until the matching source revision is recovered or a new dataset version is
frozen.

## pytz

The legacy verifier image stores `pytz` as an egg and its source build requires
generated timezone data. The current catalog task is retained for provenance,
but is excluded from the active pilot dataset until an offline source-freeze
stage produces the required zoneinfo artifact. This is an environment/task
packaging blocker, not a model result.

## cookiecutter

Oracle reaches 362/377 effective tests. The remaining failures are source/test
version drift, so the task is excluded from the active pilot.

## pyjwt

Oracle reaches 293/299 effective tests. The failing crypto, option and issuer
validation cases indicate source/test version drift.

## python-dotenv

Oracle reaches 181/209 tests. The CLI behavior in the frozen tests does not
match the selected source revision; it remains blocked as version drift.

## pathlib2

The source requires the `six` runtime dependency and still produces platform
specific collection errors after that dependency is supplied. It remains
blocked pending an environment-specific source freeze.

## dictdatabase

The 594-test suite is sensitive to concurrent filesystem timing: one Oracle
run passed 594/594 and another reached 593/594. It remains blocked until the
stress-test environment is made deterministic.

## pytest-cov

Coverage and xdist subprocess tests fail in the current verifier image. The
task remains blocked pending a verifier environment lock.

## deslib

The selected source revision reaches 509/532 tests. The remaining failures
indicate source/test revision drift.

## python-fsutil

Three hidden tests require external `raw.githubusercontent.com` access. The
task is blocked under the offline verifier contract.

## databases

The async database suite exceeds the current verifier timeout. It remains
blocked until database-driver setup and timeout isolation are made explicit.
