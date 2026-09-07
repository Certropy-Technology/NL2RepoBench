# Commons Configuration Provenance

- upstream URL: https://github.com/apache/commons-configuration
- frozen revision: `8660301dda712033e27adacae418c23f722ac3ff`
- source archive: `.nl2repo/authoring-inputs/java-maven-wave1/java-commons-configuration/source.tar`
- source archive SHA-256: `ed7899204ba28dcfc7efc3f4c01d12c087b3cc5b137944c6aee6a1638c93e254`
- license: Apache-2.0, `LICENSE.txt` SHA-256 `b1d2870f1a00e4d7f56576e5f087cba109e041f8af66866cf5b499478e654e7`
- runtime: Temurin JDK 21.0.12+8, Maven 3.9.11, Linux amd64
- contract scope: `org.apache.commons.configuration2.ex.ConfigurationException`
- dependency closure: empty for the bounded candidate contract

The full upstream project has optional integrations and a large Maven test
closure. This task intentionally contracts only the standalone public
exception type; no upstream test source is copied into the verifier.
