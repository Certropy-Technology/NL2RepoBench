# Test Traceability

| Contract group | Public specification | Frozen behavior evidence |
| --- | --- | --- |
| metadata and imports | Root and compatibility modules; Supports | `test_metadata`, `test_availability_flags`, `test_module_surface`, `test_reserved_attributes`, `test_package_available` |
| field selection | `JsonFormatter` formats, defaults, static fields, renaming | `test_default_message` through `test_static_fields`, plus `test_merge_record_extra` |
| record fields | mapping messages, extras, prefix, timestamp, unknown fields | `test_dictionary_message`, `test_dictionary_not_mutated`, `test_extra_fields`, `test_prefix`, `test_timestamp`, `test_unknown_format_field` |
| exceptions and hooks | exception/stack arrays, process hook, abstract base | `test_no_exception_field`, `test_exception_string`, `test_exception_array`, `test_stack_array`, `test_process_hook`, `test_base_jsonify_abstract` |
| JSON encoding | Unicode, bytes, dates, UUID, exception, dataclass, enum, type, unknown object | `test_unicode_*`, `test_*_encoding`, `test_custom_default`, `test_json_indent`, `test_serializer_call_contract` |
| compatibility and errors | invalid styles, optional package errors, deprecated paths | `test_invalid_style`, `test_missing_package*`, `test_legacy_module_warning`, `test_reserved_attrs_warning` |

Every production leaf is a deterministic child-side scenario assertion. The verifier accepts only the declared 50 unique IDs and computes reward from its own normalized report.
