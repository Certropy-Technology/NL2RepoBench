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
