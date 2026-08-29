from __future__ import annotations

import argparse
import datetime as dt
import importlib
import itertools
import json
import sys
from pathlib import Path


def error_type(fn):
    try:
        fn()
    except Exception as exc:
        return type(exc).__name__
    return None


def pkg(_site):
    import google.api_core as core

    origin = Path(core.__file__).resolve()
    return {
        "version": core.__version__,
        "origin_under_site": str(origin).startswith(str(Path(_site).resolve())),
        "typed": origin.with_name("py.typed").is_file(),
        "modules": all(importlib.util.find_spec(f"google.api_core.{name}") for name in (
            "client_info", "client_options", "datetime_helpers", "exceptions", "page_iterator",
            "path_template", "protobuf_helpers", "rest_helpers", "retry", "timeout", "universe",
        )),
    }


def client_info(_site):
    from google.api_core.client_info import ClientInfo

    info = ClientInfo("3.12.0", "grpc/1", "2.35.0", "gapic/1", "client/2", "tool/3", "rest/4", "pb/5")
    return info.to_user_agent()


def options(_site):
    from google.api_core.client_options import ClientOptions, from_dict

    value = from_dict({"api_endpoint": "api.example", "scopes": ["a", "b"], "api_key": "key"})
    return {"attrs": [value.api_endpoint, value.scopes, value.api_key], "repr": repr(ClientOptions(api_endpoint="x"))}


def option_errors(_site):
    from google.api_core.client_options import ClientOptions, from_dict

    return [
        error_type(lambda: ClientOptions(client_cert_source=lambda: (), client_encrypted_cert_source=lambda: ())),
        error_type(lambda: ClientOptions(credentials_file="a", api_key="b")),
        error_type(lambda: from_dict({"not_an_option": 1})),
    ]


def datetime_values(_site):
    from google.api_core import datetime_helpers as h

    value = dt.datetime(2024, 1, 2, 3, 4, 5, 123456, tzinfo=dt.timezone.utc)
    return {
        "milliseconds": h.to_milliseconds(value),
        "microseconds": h.to_microseconds(value),
        "roundtrip": h.from_microseconds(h.to_microseconds(value)).isoformat(),
    }


def rfc3339(_site):
    from google.api_core import datetime_helpers as h

    parsed = h.from_rfc3339("2020-01-02T03:04:05.123456Z")
    return {"iso": parsed.isoformat(), "formatted": h.to_rfc3339(parsed), "date": h.from_iso8601_date("2020-01-02").isoformat()}


def nanoseconds(_site):
    from google.api_core.datetime_helpers import DatetimeWithNanoseconds

    value = DatetimeWithNanoseconds(2020, 1, 2, 3, 4, 5, nanosecond=123456789)
    return {"nanosecond": value.nanosecond, "rfc3339": value.rfc3339()}


def path_values(_site):
    from google.api_core import path_template as p

    return {
        "expanded": p.expand("v1/{name=projects/*/locations/*}", name="projects/p1/locations/l1"),
        "positional": p.expand("books/*/chapters/**", "book 1", "a/b"),
        "encoded": p.get_field({"resource": {"name": "a/b c"}}, "resource.name", encode=True),
        "valid": p.validate("projects/*/locations/**", "projects/p/locations/a/b"),
        "invalid": p.validate("projects/*/locations/**", "projects/p/locations"),
    }


def path_mutation(_site):
    from google.api_core import path_template as p

    request = {"a": {"b": "value", "keep": 4}}
    p.delete_field(request, "a.b")
    return {"request": request, "missing": error_type(lambda: p.expand("v1/{name}"))}


def rest_flatten(_site):
    from google.api_core.rest_helpers import flatten_query_params

    return {
        "strict": flatten_query_params({"a": {"b": ["x", "y"]}, "flag": True, "none": None}, strict=True),
        "loose": flatten_query_params({"n": 3, "flag": False}, strict=False),
        "bad": error_type(lambda: flatten_query_params("not-a-map")),
    }


def exceptions(_site):
    from google.api_core import exceptions as e

    not_found = e.from_http_status(404, "missing")
    unavailable = e.from_grpc_status("UNAVAILABLE", "down")
    return {
        "http_class": type(not_found).__name__,
        "http_message": str(not_found),
        "grpc_class": type(unavailable).__name__,
        "status_class": e.exception_class_for_http_status(429).__name__,
        "unknown": e.exception_class_for_http_status(499).__name__,
    }


def universe(_site):
    from google.api_core import universe as u

    return {
        "chosen": u.get_universe_domain(None, " custom.example ", default_universe=u.DEFAULT_UNIVERSE),
        "determined": u.determine_domain(None, "alt.example"),
        "mtls": u.get_default_mtls_endpoint("https://foo.googleapis.com:443"),
        "endpoint": u.get_api_endpoint(None, "alt.example", u.DEFAULT_UNIVERSE, None, "api.{UNIVERSE_DOMAIN}", False),
        "empty": error_type(lambda: u.get_universe_domain("", default_universe="")),
    }


def timeout_values(_site):
    from google.api_core.timeout import ConstantTimeout, ExponentialTimeout

    seen = []

    def target(*, timeout=None):
        seen.append(timeout)
        return "ok"

    ConstantTimeout(7)(target)()
    decorated = ExponentialTimeout(initial=1, maximum=4, multiplier=2)(target)
    decorated()
    decorated()
    decorated()
    return {"seen": seen, "constant": str(ConstantTimeout(7)), "sequence": list(itertools.islice(iter([1, 2, 4]), 3))}


def deadline_timeout(_site):
    from google.api_core.timeout import TimeToDeadlineTimeout

    class Clock:
        values = iter([dt.datetime(2030, 1, 1), dt.datetime(2030, 1, 1, 0, 0, 1)])

        def __call__(self):
            return next(self.values)

    seen = []

    def target(*, timeout=None):
        seen.append(timeout)

    TimeToDeadlineTimeout(5, clock=Clock())(target)()
    return seen


def retry_values(_site):
    from google.api_core import exceptions, retry
    import random

    random.seed(0)

    predicate = retry.if_exception_type(ValueError, exceptions.ServiceUnavailable)
    return {
        "predicate": [predicate(ValueError()), predicate(TypeError()), predicate(exceptions.ServiceUnavailable("x"))],
        "sleep": list(itertools.islice(retry.exponential_sleep_generator(1, 5, multiplier=2), 5)),
        "transient": [retry.if_transient_error(exceptions.ServiceUnavailable("x")), retry.if_transient_error(ValueError())],
    }


def retry_call(_site):
    from google.api_core import exceptions, retry

    attempts = []

    def target():
        attempts.append(len(attempts))
        if len(attempts) == 1:
            raise exceptions.ServiceUnavailable("retry")
        return "done"

    wrapped = retry.Retry(predicate=retry.if_exception_type(exceptions.ServiceUnavailable), initial=0, maximum=0, multiplier=1, timeout=10)(target)
    return {"result": wrapped(), "attempts": len(attempts)}


def protobuf_values(_site):
    from google.api_core import protobuf_helpers as h
    from google.protobuf import duration_pb2

    value = duration_pb2.Duration(seconds=1)
    before = h.get(value, "seconds")
    h.set(value, "seconds", 4)
    h.setdefault(value, "nanos", 7)
    return {"before": before, "after": h.get(value, "seconds"), "count": h.get(value, "nanos"), "messages": len(h.get_messages(duration_pb2))}


def field_mask(_site):
    from google.api_core import protobuf_helpers as h
    from google.protobuf import duration_pb2

    left = duration_pb2.Duration(seconds=1)
    right = duration_pb2.Duration(seconds=2, nanos=3)
    mask = h.field_mask(left, right)
    return list(mask.paths)


def page_values(_site):
    from google.api_core.page_iterator import Page

    page = Page(None, [1, 2, 3], lambda _parent, item: item * 10, raw_page={"token": "x"})
    first = next(page)
    return {"first": first, "remaining": page.remaining, "count": page.num_items, "rest": list(page), "raw": page.raw_page}


def version_header(_site):
    from google.api_core.version_header import API_VERSION_METADATA_KEY, to_api_version_header

    return {"key": API_VERSION_METADATA_KEY, "header": list(to_api_version_header("v1"))}


def optional_boundary(_site):
    try:
        import google.api_core.grpc_helpers as grpc_helpers
    except ImportError:
        return {"module": "google.api_core.grpc_helpers", "missing": "ImportError"}
    return {"module": grpc_helpers.__name__, "missing": error_type(lambda: grpc_helpers.create_channel("example.invalid"))}


OPERATIONS = {
    "pkg": pkg,
    "client_info": client_info,
    "options": options,
    "option_errors": option_errors,
    "datetime": datetime_values,
    "rfc3339": rfc3339,
    "nanoseconds": nanoseconds,
    "path": path_values,
    "path_mutation": path_mutation,
    "rest_flatten": rest_flatten,
    "exceptions": exceptions,
    "universe": universe,
    "timeout": timeout_values,
    "deadline_timeout": deadline_timeout,
    "retry": retry_values,
    "retry_call": retry_call,
    "protobuf": protobuf_values,
    "field_mask": field_mask,
    "page": page_values,
    "version_header": version_header,
    "optional_boundary": optional_boundary,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--operation", required=True, choices=sorted(OPERATIONS))
    parser.add_argument("--nonce", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    sys.path.insert(1, args.dependency_site)
    try:
        value = OPERATIONS[args.operation](args.candidate_site)
        payload = {"nonce": args.nonce, "ok": True, "value": value}
    except Exception as exc:
        payload = {"nonce": args.nonce, "ok": False, "exception": type(exc).__name__, "message": str(exc)}
    print("NL2REPO_REPORT=" + json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
