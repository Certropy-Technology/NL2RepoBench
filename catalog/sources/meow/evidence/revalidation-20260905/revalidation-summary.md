# meow revalidation (2026-09-05 queue; executed 2026-09-07)

The queue source digest and `validate-source` result matched the current source.
All four declared private artifacts were found in the parent CAS and verified by
exact size and SHA-256. The Oracle bundle was inspected before execution: it
contains the frozen built runtime and a `solve.sh` that only copies bundled
files, with no runtime source fetch or network command.

The production bundle compiled twice with the locked Node/npm toolchain and
`--allow-private`, without `--allow-incomplete`. Both manifests were byte
identical (15,737 bytes; raw SHA-256
`sha256:fb577ef93c36be08e0c62a3289ae0f90049034316036d12a4aac8a4eb3b38417`).

## Fresh NoNetwork matrix

| run | valid | collected | passed | failed | reward | failure classification |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Oracle | true | 37 | 37 | 0 | 1.0 | none |
| call-hang | true | 0 | 0 | 0 | 0.0 | model / candidate-call-failed |
| forgery | true | 37 | 2 | 35 | 0.05405405405405406 | model |
| hang | true | 37 | 3 | 34 | 0.08108108108108109 | model |
| install-script | true | 0 | 0 | 0 | 0.0 | model / candidate-installation-failed |
| loader-hook | true | 37 | 2 | 35 | 0.05405405405405406 | model |
| offline | true | 37 | 2 | 35 | 0.05405405405405406 | model |
| stub | true | 37 | 0 | 37 | 0.0 | model |

Every fresh verifier network receipt reported `public_network_available=false`
and both external probes false. The forgery receipt ignored workspace-written
grading/reward and remained verifier-owned. All receipts are fresh and remain
in ignored task-local run roots; this source evidence records only their stable
metrics and SHA-256 digests.

## Receipt digests

`oracle`: grading `22957ec06a26da659f2f7e3e85f28b4472dae782c12197548fb6f8ace8ba2c75`, network `85cd9737a7f5f99e5fc9675f97d10edcedfc7552e39ebef745b1855d3d28332c`.
`call-hang`: grading `4561b31885da75c3142c0bef2a3287f384fe87a3a75bb2202a39dc9fa37d4648`, network `f71248a809b68bd459fe27f58f684b76d50441c7860e00d12a552449098586d8`.
`forgery`: grading `cc62d93315e7e68fe152b8cb248b5bf8b0691661d52aa193aef69c61ec38567c`, network `953e1e2f3662d4a7090125aefeafed7896a95691a447299429a219d21d89f`.
`hang`: grading `b7b7fc4b86f81747443e20b35536c091d25e81f7e70d318142c2c381ff950270`, network `63b5d7be15da0346b32cee748b1ce9e3e794a5bc09bf42922ae51fe2815c6b0a`.
`install-script`: grading `b752cf7527d84c8b6b37f325a157dbce6a455ec08be133c54104c70406ca2e19`, network `c28a77f2f768772764a3f0140d837179a3189d24ac638f1103ec477313a616d4`.
`loader-hook`: grading `cc62d93315e7e68fe152b8cb248b5bf8b0691661d52aa193aef69c61ec38567c`, network `bd3f6f4c9c962c7c0968ef514945af94a91c4d2b747feadd1715106f8b25a5cb`.
`offline`: grading `cc62d93315e7e68fe152b8cb248b5bf8b0691661d52aa193aef69c61ec38567c`, network `1034b4dcf7c2e3a098e95f63bc320bbcdca8b20ea6e9802e5198ff312c424f32`.
`stub`: grading `748ce2427a080fbe9bdafa67cf7366eb82713bf34b1e6cc16ecdadfc5cd7edae`, network `13cec582eb5e674b55ab96902f96ad7f3b59243cb8d77a70510d1aa6766ecff4`.

No lifecycle, task metadata, generated projection, shared CAS, or historical
production evidence was changed.
