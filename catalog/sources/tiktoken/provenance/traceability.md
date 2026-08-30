# Hidden contract traceability

| Leaf | Public contract section | Behavior |
| --- | --- | --- |
| exports, encoding_repr, explicit_vocab | Encoding | exports, representation, constructor validation |
| bpe_merge, single_token, decode_errors | Encoding | ranked merge, token lookup, decode errors |
| special_guard, surrogate_replace | Encoding | special-token policy and Unicode replacement |
| offsets, batch_order, pickle | Encoding | offsets, ordered batch methods, state serialization |
| registry_names, unknown_encoding | Registry | built-in names and unknown-name failure |
| model_exact, model_prefix, model_unknown | Model helpers | exact/prefix/unknown model mapping |
| load_bpe, load_hash_mismatch, dump_bpe, data_gym_local | Load helpers | local parsing, integrity, deterministic output |
| educational_bpe, educational_train, educational_wrapper | Educational API | BPE algorithm, training, wrapper behavior |
| no_remote_loader | Offline boundary | no URL/network operation in scored loader |

Every frozen leaf is exercised through `tiktoken` public import paths in a
child-side adapter. The verifier owns collection, JUnit, grading, and reward.
