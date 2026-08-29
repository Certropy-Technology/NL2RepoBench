# jaraco-classes traceability

| Contract area | Scenarios |
| --- | --- |
| MRO helpers | `ancestry-mro`, `ancestry-mro-diamond` |
| Depth-first unique subclass traversal | `subclass-order`, `subclass-diamond`, `subclass-type-root` |
| Non-data descriptor getter and shadowing | `nondata-basic`, `nondata-class-access`, `nondata-assertions` |
| Metaclass-backed class property | `classproperty-meta`, `classproperty-method-kinds`, `classproperty-subclass`, `classproperty-setter-identity` |
| Missing classproperty setter and legacy behavior | `classproperty-read-only`, `classproperty-legacy` |
| Leaf registry | `leaf-registry`, `leaf-independent` |
| Tag registry | `tag-registry`, `tag-duplicate`, `tag-independent`, `tag-no-tag` |
| Package closure and marker | `package-imports`, `package-marker`, `package-metadata` |
| Deterministic public behavior | all 23 scenarios and repeated Oracle invocation |
