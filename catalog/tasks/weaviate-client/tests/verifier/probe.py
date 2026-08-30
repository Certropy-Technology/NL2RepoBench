from __future__ import annotations

import dataclasses
import datetime
import importlib.metadata
import json
import os
import sys
import uuid
import warnings
from enum import Enum
from pathlib import Path
from typing import Any


candidate_site = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
dependency_site = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
sys.path.insert(0, candidate_site)
if dependency_site:
    sys.path.insert(1, dependency_site)


def _normalize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Path):
        return str(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            "type": type(value).__name__,
            "fields": {
                field.name: _normalize(getattr(value, field.name))
                for field in dataclasses.fields(value)
            },
        }
    if hasattr(value, "model_dump"):
        return {
            "type": type(value).__name__,
            "fields": _normalize(value.model_dump(by_alias=True, exclude_none=True)),
        }
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if hasattr(value, "__dict__"):
        return {
            "type": type(value).__name__,
            "fields": {
                key: _normalize(item)
                for key, item in sorted(vars(value).items())
                if not key.startswith("__")
            },
        }
    return value


def _capture(function: Any) -> Any:
    try:
        return _normalize(function())
    except BaseException as error:
        return {"error": type(error).__name__, "message": str(error)}


def _auth(request: dict[str, Any]) -> Any:
    from weaviate.classes.init import Auth

    kind = request["kind"]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        if kind == "api-key":
            value = Auth.api_key(request["api_key"])
        elif kind == "client-credentials":
            value = Auth.client_credentials(request["secret"], request.get("scope"))
        elif kind == "client-password":
            value = Auth.client_password(
                request["username"], request["password"], request.get("scope")
            )
        elif kind == "bearer":
            value = Auth.bearer_token(
                request["access_token"],
                request.get("expires_in", 60),
                request.get("refresh_token"),
            )
        else:
            raise KeyError(kind)
    return {
        "value": _normalize(value),
        "warnings": [
            {"category": item.category.__name__, "message": str(item.message)}
            for item in caught
        ],
    }


def _connection(request: dict[str, Any]) -> Any:
    from weaviate.config import AdditionalConfig, Proxies, Timeout
    from weaviate.connect.base import ConnectionParams, ProtocolParams, _get_proxies

    kind = request["kind"]
    if kind == "protocol":
        value = ProtocolParams(**request["params"])
        return {"model": _normalize(value), "is_gcp": value.is_gcp()}
    if kind == "from-url":
        value = ConnectionParams.from_url(
            request["url"], request["grpc_port"], request.get("grpc_secure", False)
        )
        return {
            "model": _normalize(value),
            "http_url": value._http_url,
            "grpc_target": value._grpc_target,
            "gcp_on_wcd": value.is_gcp_on_wcd(),
        }
    if kind == "from-params":
        value = ConnectionParams.from_params(**request["params"])
        return {
            "model": _normalize(value),
            "http_url": value._http_url,
            "grpc_target": value._grpc_target,
        }
    if kind == "additional-default":
        value = AdditionalConfig()
        return {"model": _normalize(value), "timeout": _normalize(value.timeout)}
    if kind == "additional-tuple":
        value = AdditionalConfig(timeout=tuple(request["timeout"]), trust_env=request["trust_env"])
        return {"model": _normalize(value), "timeout": _normalize(value.timeout)}
    if kind == "proxies":
        source = request["value"]
        if isinstance(source, dict) and request.get("as_model"):
            source = Proxies(**source)
        return _get_proxies(source, request.get("trust_env", False))
    if kind == "timeout":
        return _normalize(Timeout(**request["params"]))
    raise KeyError(kind)


def _util(request: dict[str, Any]) -> Any:
    from weaviate import util

    kind = request["kind"]
    if kind == "uuid":
        value: Any = request["value"]
        if request.get("as_uuid"):
            value = uuid.UUID(value)
        return util.get_valid_uuid(value)
    if kind == "beacon-valid":
        return util.is_weaviate_object_url(request["value"])
    if kind == "object-url-valid":
        return util.is_object_url(request["value"])
    if kind == "version":
        return _normalize(util.parse_version_string(request["value"]))
    if kind == "server-version":
        value = util._ServerVersion.from_string(request["value"])
        result = {"parsed": str(value)}
        if "minimum" in request:
            result["at_least"] = value.is_at_least(*request["minimum"])
        if "minimums" in request:
            result["at_least_any"] = value.is_at_least_any(
                *(tuple(item) for item in request["minimums"])
            )
        return result
    if kind == "uuid5":
        return util.generate_uuid5(request["identifier"], request.get("namespace", ""))
    if kind == "sanitize":
        return util._sanitize_str(request["value"])
    if kind == "beacons":
        return util._to_beacons(request["values"], request.get("to_class", ""))
    if kind == "timeout-config":
        value = request.get("value")
        if isinstance(value, list):
            value = tuple(value)
        return _normalize(util._get_valid_timeout_config(value))
    if kind == "datetime-encode":
        value = datetime.datetime.fromisoformat(request["value"])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            encoded = util._datetime_to_string(value)
        return {"value": encoded, "warnings": len(caught)}
    if kind == "datetime-decode":
        return _normalize(util._datetime_from_weaviate_str(request["value"]))
    if kind == "vector":
        return _normalize(util.get_vector(request["value"]))
    if kind == "domain":
        return util.get_domain_from_weaviate_url(request["value"])
    if kind == "weaviate-domain":
        return util.is_weaviate_domain(request["value"])
    raise KeyError(kind)


def _filter(request: dict[str, Any]) -> Any:
    import weaviate.classes as wvc

    kind = request["kind"]
    if kind == "property":
        builder = wvc.query.Filter.by_property(request["name"], request.get("length", False))
        return _normalize(getattr(builder, request["operator"])(request["value"]))
    if kind == "id":
        builder = wvc.query.Filter.by_id()
        return _normalize(getattr(builder, request["operator"])(request["value"]))
    if kind == "ref-property":
        builder = wvc.query.Filter.by_ref_multi_target(
            request["link_on"], request["target_collection"]
        ).by_property(request["name"])
        return _normalize(getattr(builder, request["operator"])(request["value"]))
    if kind == "ref-count":
        builder = wvc.query.Filter.by_ref_count(request["link_on"])
        return _normalize(getattr(builder, request["operator"])(request["value"]))
    if kind == "time":
        builder = getattr(wvc.query.Filter, request["factory"])()
        value = datetime.datetime.fromisoformat(request["value"])
        return _normalize(getattr(builder, request["operator"])(value))
    if kind == "geo":
        point = wvc.query.GeoCoordinate(
            latitude=request["latitude"], longitude=request["longitude"]
        )
        return _normalize(
            wvc.query.Filter.by_property(request["name"]).within_geo_range(
                point, request["distance"]
            )
        )
    if kind == "combine":
        first = wvc.query.Filter.by_property("age").greater_or_equal(18)
        second = wvc.query.Filter.by_property("active").equal(True)
        if request["operator"] == "and":
            value = first & second
        elif request["operator"] == "or":
            value = first | second
        elif request["operator"] == "not":
            value = ~first
        else:
            raise KeyError(request["operator"])
        return _normalize(value)
    if kind == "empty-combine":
        return _normalize(getattr(wvc.query.Filter, request["method"])([]))
    if kind == "direct":
        return _normalize(wvc.query.Filter())
    raise KeyError(kind)


def _query(request: dict[str, Any]) -> Any:
    import weaviate.classes as wvc

    kind = request["kind"]
    if kind == "metadata":
        method = request.get("method")
        value = getattr(wvc.query.MetadataQuery, method)() if method else wvc.query.MetadataQuery()
        return _normalize(value)
    if kind == "sort":
        value = wvc.query.Sort.by_property(request["name"], request.get("ascending", True))
        if request.get("then_id"):
            value.by_id(request.get("id_ascending", True))
        return _normalize(value)
    if kind == "group":
        return _normalize(wvc.query.GroupBy(**request["params"]))
    if kind == "rerank":
        return _normalize(wvc.query.Rerank(**request["params"]))
    if kind == "move":
        return _normalize(
            wvc.query.Move(
                request["force"], request.get("objects"), request.get("concepts")
            )._to_gql_payload()
        )
    if kind == "diversity":
        return _normalize(wvc.query.Diversity.mmr(**request["params"]))
    if kind == "bm25":
        if request["operator"] == "or":
            value = wvc.query.BM25Operator.or_(request["minimum_match"])
        elif request["operator"] == "and":
            value = wvc.query.BM25Operator.and_()
        elif request["operator"] == "and-cross":
            value = wvc.query.BM25Operator.and_cross()
        else:
            raise KeyError(request["operator"])
        result = _normalize(value)
        result["operator"] = int(value.operator)
        return result
    if kind == "boost-time":
        value = wvc.query.Boost.time_decay(
            request["property"],
            origin=datetime.datetime.fromisoformat(request["origin"]),
            scale=datetime.timedelta(seconds=request["scale_seconds"]),
            offset=datetime.timedelta(seconds=request["offset_seconds"]),
            curve=wvc.query.Boost.Curve.GAUSSIAN,
            decay=request["decay"],
            weight=request["weight"],
            depth=request["depth"],
        )
        return _normalize(value)
    if kind == "boost-numeric":
        return _normalize(
            wvc.query.Boost.numeric_decay(
                request["property"],
                origin=request["origin"],
                scale=request["scale"],
                offset=request.get("offset"),
                curve=wvc.query.Boost.Curve.LINEAR,
                decay=request.get("decay"),
            )
        )
    if kind == "boost-property":
        return _normalize(
            wvc.query.Boost.numeric_property(
                request["name"],
                modifier=wvc.query.Boost.Modifier.LOG1P,
                weight=request.get("weight"),
            )
        )
    if kind == "boost-blend":
        first = wvc.query.Boost.filter(
            wvc.query.Filter.by_property("featured").equal(True), weight=2.0
        )
        second = wvc.query.Boost.numeric_property("rating", weight=1.0)
        return _normalize(
            wvc.query.Boost.blend([first, second], weight=0.4, depth=150)
        )
    if kind == "direct-sort":
        return _normalize(wvc.query.Sort())
    raise KeyError(kind)


def _config(request: dict[str, Any]) -> Any:
    import weaviate.classes as wvc

    kind = request["kind"]
    if kind == "property":
        value = wvc.config.Property(
            name=request["name"],
            data_type=getattr(wvc.config.DataType, request["data_type"]),
            description=request.get("description"),
            index_filterable=request.get("index_filterable"),
            index_searchable=request.get("index_searchable"),
            index_range_filters=request.get("index_range_filters"),
            skip_vectorization=request.get("skip_vectorization", False),
            tokenization=(
                getattr(wvc.config.Tokenization, request["tokenization"])
                if request.get("tokenization")
                else None
            ),
        )
        return value._to_dict()
    if kind == "nested-property":
        child = wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT)
        value = wvc.config.Property(
            name="details",
            data_type=wvc.config.DataType.OBJECT,
            nested_properties=[child],
        )
        return value._to_dict()
    if kind == "reference":
        value = wvc.config.ReferenceProperty(
            name=request["name"],
            target_collection=request["target_collection"],
            description=request.get("description"),
        )
        return value._to_dict()
    if kind == "reference-multi":
        value = wvc.config.ReferenceProperty.MultiTarget(
            name=request["name"], target_collections=request["target_collections"]
        )
        return value._to_dict()
    if kind == "text-analyzer":
        return wvc.config.Configure.text_analyzer(**request["params"])._to_dict()
    if kind == "inverted":
        return wvc.config.Configure.inverted_index(**request["params"])._to_dict()
    if kind == "multi-tenancy":
        return wvc.config.Configure.multi_tenancy(**request["params"])._to_dict()
    if kind == "replication":
        return wvc.config.Configure.replication(**request["params"])._to_dict()
    if kind == "hnsw-pq":
        quantizer = wvc.config.Configure.VectorIndex.Quantizer.pq(**request["quantizer"])
        value = wvc.config.Configure.VectorIndex.hnsw(
            distance_metric=wvc.config.VectorDistances.COSINE,
            ef_construction=request["ef_construction"],
            max_connections=request["max_connections"],
            quantizer=quantizer,
        )
        return value._to_dict()
    if kind == "flat-bq":
        quantizer = wvc.config.Configure.VectorIndex.Quantizer.bq(**request["quantizer"])
        return wvc.config.Configure.VectorIndex.flat(quantizer=quantizer)._to_dict()
    if kind == "hfresh-rq":
        quantizer = wvc.config.Configure.VectorIndex.Quantizer.rq(**request["quantizer"])
        value = wvc.config.Configure.VectorIndex.hfresh(
            distance_metric=wvc.config.VectorDistances.DOT,
            max_posting_size_kb=request["max_posting_size_kb"],
            replicas=request["replicas"],
            search_probe=request["search_probe"],
            quantizer=quantizer,
        )
        return value._to_dict()
    if kind == "dynamic":
        value = wvc.config.Configure.VectorIndex.dynamic(
            distance_metric=wvc.config.VectorDistances.L2_SQUARED,
            threshold=request["threshold"],
            hnsw=wvc.config.Configure.VectorIndex.hnsw(ef=100),
            flat=wvc.config.Configure.VectorIndex.flat(),
        )
        return value._to_dict()
    if kind == "reconfigure-hfresh":
        quantizer = wvc.config.Reconfigure.VectorIndex.Quantizer.rq(**request["quantizer"])
        value = wvc.config.Reconfigure.VectorIndex.hfresh(
            max_posting_size_kb=request.get("max_posting_size_kb"),
            search_probe=request.get("search_probe"),
            quantizer=quantizer,
        )
        return value.model_dump(by_alias=True, exclude_none=True)
    if kind == "hfresh-merge":
        from weaviate.collections.classes.config import _CollectionConfigUpdate

        schema = {
            "class": "HFreshRQ",
            "vectorConfig": {
                "boi": {
                    "vectorizer": {"text2vec-weaviate": {}},
                    "vectorIndexType": "hfresh",
                    "vectorIndexConfig": {
                        "distance": "cosine",
                        "maxPostingSizeKB": 1024,
                        "searchProbe": 8,
                        "rq": {"enabled": True, "bits": 1, "rescoreLimit": 20},
                    },
                }
            },
        }
        update = _CollectionConfigUpdate(
            vector_config=wvc.config.Reconfigure.Vectors.update(
                name="boi",
                vector_index_config=wvc.config.Reconfigure.VectorIndex.hfresh(
                    quantizer=wvc.config.Reconfigure.VectorIndex.Quantizer.rq(
                        rescore_limit=request["rescore_limit"]
                    )
                ),
            )
        )
        merged = update.merge_with_existing(schema)
        return merged["vectorConfig"]["boi"]["vectorIndexConfig"]
    raise KeyError(kind)


def _main(request: dict[str, Any]) -> Any:
    operation = request["operation"]
    if operation == "exports":
        import weaviate
        import weaviate.classes as wvc

        names = request["names"]
        return {
            "version": weaviate.__version__,
            "root_exports": {name: hasattr(weaviate, name) for name in names},
            "class_namespaces": {
                name: hasattr(wvc, name) for name in ["config", "init", "query"]
            },
        }
    if operation == "metadata":
        metadata = importlib.metadata.metadata("weaviate-client")
        return {
            "name": metadata["Name"],
            "version": importlib.metadata.version("weaviate-client"),
            "requires_python": metadata["Requires-Python"],
            "requires": sorted(importlib.metadata.requires("weaviate-client") or []),
        }
    dispatch = {
        "auth": _auth,
        "connection": _connection,
        "util": _util,
        "filter": _filter,
        "query": _query,
        "config": _config,
    }
    if operation not in dispatch:
        raise KeyError(operation)
    return _capture(lambda: dispatch[operation](request))


request = json.loads(sys.stdin.read())
try:
    if isinstance(request, dict) and isinstance(request.get("batch"), list):
        value = [_capture(lambda item=item: _main(item)) for item in request["batch"]]
    else:
        value = _main(request)
    response = {"ok": True, "value": _normalize(value)}
except BaseException as error:
    response = {"ok": False, "error": f"{type(error).__name__}: {error}"}
print(json.dumps(response, sort_keys=True, separators=(",", ":")))
