# Frozenlist revalidation

- Expected migrated catalog digest: `sha256:915ce630c146b9f4fb5ef9d86eaafd89871b0b5817b69f31bfca9434d3710880`.
- Two final `Harbor 0.21.0` production compiles were byte-identical: 61 files, raw manifest `sha256:916bd7a9a63b8af9debe58635d3b28a794c872f377dc57194c64398b7fd01464`, canonical manifest `sha256:370c9bd01768cecc1ebacc3c8379ad0e3f55b8050e4adc1bb4ce473d932abf2e`.
- Oracle passed 21/21 with reward `1.0`; empty, stub, forgery, and offline checks are recorded in the adjacent summaries. All network probes were false.
- `empty.sh` was added as a standalone source control; the compiler's Python `prepare-control` registry synthesizes the equivalent empty control bundle.
- Existing lifecycle and historical `production-evidence.json` were not changed. Parent integration must refresh the generated projection and canonical production evidence against this final bundle.
