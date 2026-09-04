FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork@sha256:21f0ba5b3649db3ccc91b1128e5c8c6ffb915d4a8a04faaa11162793099dfac8 AS python-runtime
FROM --platform=linux/amd64 nl2repobench/java-runtime@sha256:d5e429fd4c57040b5fe23cc92196828dc9f1e3b13ac47539183431b223ea84f3 AS java-runtime
FROM python-runtime
COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk
COPY --from=java-runtime /opt/maven /opt/maven
ENV JAVA_HOME=/opt/java/openjdk MAVEN_HOME=/opt/maven PATH=/opt/java/openjdk/bin:/opt/maven/bin:$PATH
COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes --index-url https://pypi.org/simple -r /tmp/requirements.lock.txt
COPY --chmod=0555 test.sh /tests/test.sh
COPY private-artifact-refs.json /tests/private-artifact-refs.json

RUN useradd --uid 10001 --create-home candidate \
  && chmod -R 0555 /usr/local/lib/python3.12/site-packages/nl2repobench
WORKDIR /tests
