# Project Description

Create an installable Python project named `schedule`: a lightweight,
in-process scheduler for periodically calling Python callables. It should offer
a human-readable builder API such as `every(10).minutes.do(func)`. The library
only decides when work is due and invokes it when the application calls
`run_pending()` or `run_all()`; it does not create a daemon, event loop, worker
thread, or persistent job store.

The implementation must preserve scheduler state across calls, support
independent `Scheduler` instances and a module-level default scheduler, and
handle ordinary intervals, randomized ranges, fixed wall-clock times, weekdays,
deadlines, tags, cancellation, and timezone-aware wall-clock scheduling.

# Supports

- Python 3.7 or newer. Evaluation uses CPython 3.12.14 on Debian 12 Linux.
- A `pyproject.toml` that lets the `schedule` distribution be installed with
  standard Python packaging tools. Use distribution version `1.2.2`.
- An importable `schedule` package. A root package layout or a `src/` layout is
  acceptable. Include `schedule/py.typed`.
- No required third-party dependency for timezone-free scheduling. Timezone
  arguments require `pytz`; expose it as an optional `timezone` dependency.
  Evaluation preinstalls `pytz` 2025.2 and runs the suite with `pytest` 8.4.1.
- Naive `datetime` values for the public `last_run`, `next_run`, and
  `cancel_after` state. Timezone-aware calculations are internal and are
  converted back to naive local-system time for compatibility.
- The public API is available directly from `schedule`. `from schedule import
  *` must expose the core scheduler functions, classes, and exceptions listed
  below.

# API Usage Guide

## Exceptions and cancellation marker

Provide this hierarchy:

```python
class ScheduleError(Exception): ...
class ScheduleValueError(ScheduleError): ...
class IntervalError(ScheduleValueError): ...
class CancelJob: ...
```

`CancelJob` is a marker. If a job function returns either the `CancelJob` class
or an instance of it, the scheduler that ran the job removes that job.

## `Scheduler`

```python
class Scheduler:
    def __init__(self) -> None: ...
    def every(self, interval: int = 1) -> "Job": ...
    def run_pending(self) -> None: ...
    def run_all(self, delay_seconds: int = 0) -> None: ...
    def get_jobs(self, tag: Hashable | None = None) -> list["Job"]: ...
    def clear(self, tag: Hashable | None = None) -> None: ...
    def cancel_job(self, job: "Job") -> None: ...
    def get_next_run(self, tag: Hashable | None = None) -> datetime.datetime | None: ...

    next_run: datetime.datetime | None
    idle_seconds: float | None
```

Each instance owns a mutable `jobs` list. `every()` returns an unregistered
`Job` associated with that scheduler. Registration happens only after a valid
call to `Job.do()`; abandoned or partly configured builders must not affect the
scheduler.

`run_pending()` selects jobs whose `should_run` property is true, orders them
by ascending `next_run`, and executes each selected job once. It intentionally
does not replay missed intervals. For example, a minutely job checked after an
hour is called once, not sixty times. An exception from a job callable
propagates and does not get converted into cancellation.

`run_all()` runs a snapshot of all registered jobs regardless of due time, in
list order. It calls `time.sleep(delay_seconds)` after each attempted job so
load can be spread out. Cancellation during this traversal must not corrupt
iteration.

`get_jobs()` returns a shallow copy of all jobs when no tag is given. With a
tag it returns jobs containing that tag, preserving scheduler list order.
`clear()` removes every job, or only jobs carrying a supplied tag. Clearing
must mutate the existing jobs list in place. `cancel_job()` removes one job;
passing an object that is not currently scheduled is a no-op.

`get_next_run()` returns the minimum `next_run` among all jobs or among jobs
with the requested tag. It returns `None` if that selection is empty.
`next_run` is the corresponding property. `idle_seconds` is the signed number
of seconds between local `datetime.datetime.now()` and `next_run`, or `None`
when no job is scheduled.

## `Job`

```python
class Job:
    def __init__(self, interval: int, scheduler: Scheduler | None = None): ...
    def tag(self, *tags: Hashable) -> "Job": ...
    def at(self, time_str: str, tz: str | pytz.BaseTzInfo | None = None) -> "Job": ...
    def to(self, latest: int) -> "Job": ...
    def until(
        self,
        until_time: datetime.datetime | datetime.timedelta | datetime.time | str,
    ) -> "Job": ...
    def do(self, job_func: Callable, *args, **kwargs) -> "Job": ...
    def run(self): ...

    should_run: bool
```

A new job exposes these state attributes:

- `interval`: the base interval passed to the constructor;
- `latest`: initially `None`, otherwise the inclusive upper randomized bound;
- `unit`: initially `None`, then one of `seconds`, `minutes`, `hours`, `days`,
  or `weeks`;
- `at_time` and `at_time_zone`: initially `None`;
- `last_run` and `next_run`: initially `None`;
- `start_day`: initially `None`, otherwise a lowercase weekday;
- `cancel_after`: initially `None`;
- `tags`: an initially empty set;
- `scheduler`: the associated scheduler or `None`.

### Units and weekdays

The chainable plural properties `seconds`, `minutes`, `hours`, `days`, and
`weeks` set `unit` and return the same job. Singular aliases `second`,
`minute`, `hour`, `day`, and `week` do the same only when `interval == 1`.
For any other interval, a singular property raises `IntervalError` with
`Use <plural> instead of <singular>`.

The chainable weekday properties `monday` through `sunday` select a weekly
job whose `start_day` is that weekday. Weekday selection is supported only for
an interval of one. For a larger interval, raise `IntervalError` using this
message template, substituting the weekday twice:

```text
Scheduling .<weekday>() jobs is only allowed for weekly jobs. Using
.<weekday>() on a job scheduled to run every 2 or more weeks is not supported.
```

An unknown unit, a start day on a non-weekly job, or an unknown weekday must
raise `ScheduleValueError` when the next run is calculated.

### Fixed times and timezones

`at()` records a wall-clock component and returns the job. It is valid for
daily jobs, weekday jobs, hourly jobs, and minutely jobs:

- daily or weekday: zero-padded `HH:MM` or `HH:MM:SS`, with hour 00-23;
- hourly: `:MM` for minute with zero seconds, or `MM:SS`;
- minutely: `:SS`.

Minutes and seconds are 00-59. Whitespace, omitted zero padding, fractional
seconds, extra components, impossible values, and formats belonging to a
different unit raise `ScheduleValueError`. A non-string `time_str` raises
`TypeError`. Calling `at()` for an unsupported or unset unit raises
`ScheduleValueError`.

The optional `tz` is either a name accepted by `pytz.timezone()` or a
`pytz.BaseTzInfo` instance. Store the resolved timezone in `at_time_zone`.
Propagate `pytz.UnknownTimeZoneError` for an unknown name. Other timezone
types raise `ScheduleValueError`. Without `tz`, interpret the wall-clock time
in the process's local timezone.

### Random ranges, deadlines, and tags

`to(latest)` sets an irregular interval range and returns the job. Each next
run independently chooses an integer interval from `interval` through
`latest`, inclusive. Validate while scheduling that `latest >= interval`;
otherwise raise `ScheduleError`.

`until()` sets the latest permitted execution moment and returns the job. It
accepts:

- a `datetime`, used directly;
- a `timedelta`, added to the current local datetime;
- a `time`, combined with today's local date;
- a string in `YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DD HH:MM`, `YYYY-MM-DD`,
  `HH:MM:SS`, or `HH:MM` form. A time-only string uses today's date.

Unsupported types raise `TypeError`; invalid strings and moments strictly in
the past raise `ScheduleValueError`. A job is cancelled without being called
if execution starts after its deadline. If a successful call computes a
`next_run` after the deadline, that call is retained as the last run and the
job is then cancelled. A moment equal to the deadline is still permitted.

`tag(*tags)` requires every supplied tag to be hashable. It adds tags to the
set, naturally discards duplicates, and returns the job. If any argument is
unhashable, raise `TypeError` without partially adding the batch.

### Binding and running callables

`do(job_func, *args, **kwargs)` binds the callable and arguments, preserves
callable metadata where possible, computes the first `next_run`, appends the
job to its scheduler, and returns the job. A job with no valid unit cannot be
registered. A directly constructed job with no associated scheduler raises
`ScheduleError` rather than being silently registered elsewhere.

`should_run` is true when local `datetime.datetime.now()` is greater than or
equal to `next_run`. Access before scheduling may assert that `next_run` is
present.

`run()` checks the deadline, invokes the bound callable, records `last_run` as
the current time after a successful return, and computes a new `next_run`
relative to that completion time. This means a long-running job does not
backfill periods or schedule from a stale planned time. If the callable raises,
the exception propagates and the successful-run state is not updated. Return
the callable's value unless deadline handling requires the `CancelJob` marker.

### Ordering and representations

Jobs compare by `next_run`; this defines pending-job execution order.

`str(job)` uses this stable diagnostic shape:

```text
Job(interval=<interval>, unit=<unit>, do=<callable-name>, args=<args>, kwargs=<kwargs>)
```

`repr(job)` begins with `Every <interval>`, includes `to <latest>` for random
ranges, singularizes the unit when the interval is one, includes `at
HH:MM:SS` when configured, shows the callable invocation, and ends with:

```text
(last run: <timestamp-or-[never]>, next run: <timestamp-or-[never]>)
```

Render timestamps as `YYYY-MM-DD HH:MM:SS`. A partially configured job must be
representable and use `[None]` for its missing callable and `[never]` for
missing run times. Lambda functions and `functools.partial` callables must not
break either representation; partial representations retain their bound and
keyword argument information.

## Module-level scheduler API

Create one `default_scheduler = Scheduler()` and expose `jobs` as the exact
same mutable list object as `default_scheduler.jobs`. Provide these delegating
functions:

```python
def every(interval: int = 1) -> Job: ...
def run_pending() -> None: ...
def run_all(delay_seconds: int = 0) -> None: ...
def get_jobs(tag: Hashable | None = None) -> list[Job]: ...
def clear(tag: Hashable | None = None) -> None: ...
def cancel_job(job: Job) -> None: ...
def next_run(tag: Hashable | None = None) -> datetime.datetime | None: ...
def idle_seconds() -> float | None: ...
```

The decorator helper has this contract:

```python
def repeat(job: Job, *args, **kwargs): ...
```

It registers the decorated function on `job` with the supplied arguments and
returns the original function, so normal direct calls still work.

## Date and timezone calculation contract

All ordinary intervals are calendar calculations from the current local
datetime. A job without `at_time` gets its first run one complete chosen period
in the future. A fixed daily time later today may run today; a fixed time that
has passed advances by the configured period. For intervals larger than one,
the first fixed-time run is one full multi-unit period ahead. Weekly weekday
selection moves to the nearest requested weekday on or after the candidate
date; when the resulting moment is not in the future, advance one week.

After each successful run, recompute from the then-current time. Preserve exact
seconds for fixed-time jobs, reset microseconds to zero, and support boundaries
across hours, days, months, years, and leap days.

For timezone-qualified `at()` jobs:

1. Determine now and the candidate run in the requested timezone.
2. Apply the interval and requested wall-clock components there.
3. Normalize UTC offsets whenever the interval crosses an offset transition.
4. Convert the final instant to the process local timezone and remove its
   `tzinfo` before storing `next_run`.

Preserve the requested wall-clock hour/minute/second whenever that local time
exists. During a spring-forward gap, move the nonexistent time forward by the
size of the offset change. During an overlap, choose a valid occurrence without
accidentally scheduling a second same-period run; subsequent runs return to the
requested wall-clock time. These rules apply to daily and weekly jobs as well
as hourly/minutely jobs with fixed components, including zones with half-hour
or quarter-hour offsets and transitions in a different hemisphere from the
system timezone.

The following compatibility helpers are part of the required module behavior:

```python
def _move_to_next_weekday(
    moment: datetime.datetime,
    weekday: str,
) -> datetime.datetime: ...

def _weekday_index(day: str) -> int: ...
```

`_move_to_next_weekday()` retains the time components and returns the same day
when it already has the requested weekday, otherwise the next occurrence no
more than six days ahead. `_weekday_index()` accepts lowercase weekday names
from Monday through Sunday and raises `ScheduleValueError` otherwise.

`Job._schedule_next_run()` implements the validation and next-run state change
described above. `Job._correct_utc_offset(moment, fixate_time)` returns `moment`
unchanged for jobs without an `at_time_zone`. With a timezone, normalize it. If
the offset changed and `fixate_time` is false, preserve the instant selected by
normalization. If `fixate_time` is true, first try to retain the original wall
clock components; if those components are in a DST gap, use the first valid
time displaced forward by that gap.

# Implementation Notes

- Keep scheduler instances independent. Module shortcuts operate only on
  `default_scheduler`; jobs created by another `Scheduler` stay there.
- `datetime.datetime.now()` is the clock source. Do not cache real time or read
  it at import time; callers may patch it to test deterministic state changes.
- Use `time.sleep()` only for the explicit `run_all(delay_seconds=...)` delay.
- Keep the project self-contained. Do not include copied upstream tests or rely
  on network access during normal package use.
- A representative usage sequence is:

```python
import schedule

runs = []
job = schedule.every(3).minutes.do(runs.append, "done").tag("worker")
assert job in schedule.get_jobs("worker")
schedule.run_all()
assert runs == ["done"]
schedule.cancel_job(job)
```
