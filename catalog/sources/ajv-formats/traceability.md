# ajv-formats traceability

| Public contract | Frozen upstream evidence | Private leaves |
| --- | --- | ---: |
| Package metadata, CommonJS root export, plugin identity | `package.json`, `src/index.ts`, upstream `tests/index.spec.ts` | 2 |
| Full format table and selective registration | `src/formats.ts`, `tests/index.spec.ts` | 4 |
| Full date/time/date-time and leap-year semantics | `src/formats.ts`, `tests/issues/617_full_format_leap_year.spec.ts` | 5 |
| URI, email, hostname, IPv4/IPv6, regex, UUID | `src/formats.ts`, upstream JSON Schema format suites | 8 |
| JSON pointers, byte, int32/int64, float/double, permissive formats | `src/formats.ts`, upstream JSON Schema and extras suites | 4 |
| Four format comparison keywords and compare behavior | `src/limit.ts`, `tests/formatLimit.spec.ts` | 4 |

Every private leaf maps to behavior explicitly stated in `instruction.md`. The adapter excludes callbacks, custom formats, `$data` references, direct Ajv object transport, and upstream development-tooling details because those cannot be represented by the bounded JSON contract. No hidden test depends on a private helper name or an unmentioned implementation detail.
