FROM docker.io/library/maven@sha256:463a1849665463254b2dd56e3a5b316f1596bc93d0571065c06ea05bb48ab8f4 AS maven-runtime

FROM docker.io/library/eclipse-temurin@sha256:a16bfc04b28f66c1d27218ffeefc8ae6a2621de423e01597156ba813ca5fa668

COPY --from=maven-runtime /usr/share/maven /opt/maven
ENV MAVEN_HOME=/opt/maven
ENV PATH=/opt/maven/bin:${PATH}

RUN set -eu \
  && test "$(mvn -version 2>&1 | awk '/^Apache Maven/{print $3}')" = "3.9.11" \
  && test "$(java -version 2>&1 | awk -F'\"' '/version/{print $2}')" = "21.0.12"
