FROM --platform=linux/amd64 nl2repobench/java-runtime:21.0.12-maven3.9.11-20260902-r2 AS java-runtime

FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork:930e9b1da

LABEL org.nl2repobench.agent-runtime-image="nl2repobench/openhands-sdk-fork@sha256:21f0ba5b3649db3ccc91b1128e5c8c6ffb915d4a8a04faaa11162793099dfac8" \
  org.nl2repobench.agent-runtime-image-id="sha256:21f0ba5b3649db3ccc91b1128e5c8c6ffb915d4a8a04faaa11162793099dfac8" \
  org.nl2repobench.agent-dependency-build="maven-offline-v1"

COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk
COPY --from=java-runtime /opt/maven /opt/maven
ENV JAVA_HOME=/opt/java/openjdk \
    MAVEN_HOME=/opt/maven \
    PATH=/opt/java/openjdk/bin:/opt/maven/bin:$PATH
RUN test "$(java -version 2>&1 | awk -F'\"' '/version/{print $2}')" = "21.0.12" \
  && test "$(mvn -version 2>&1 | awk '/^Apache Maven/{print $3}')" = "3.9.11"
WORKDIR /workspace
