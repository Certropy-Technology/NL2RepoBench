FROM --platform=linux/amd64 nl2repobench/openhands-sdk-fork:930e9b1da AS python-runtime
FROM --platform=linux/amd64 nl2repobench/java-runtime:21.0.12-maven3.9.11-20260902-r2 AS java-runtime
FROM python-runtime
COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk
COPY --from=java-runtime /opt/maven /opt/maven
ENV JAVA_HOME=/opt/java/openjdk MAVEN_HOME=/opt/maven PATH=/opt/java/openjdk/bin:/opt/maven/bin:$PATH
COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
COPY requirements.lock.txt /tmp/requirements.lock.txt
RUN python -m pip install --no-cache-dir --require-hashes --index-url https://pypi.org/simple -r /tmp/requirements.lock.txt
COPY --chmod=0555 test.sh /tests/test.sh
COPY --chmod=0500 private /tests/private
COPY --from=java-runtime /opt/maven /opt/maven
COPY dependencies/maven-repository /opt/maven/repository
RUN useradd --uid 10001 --create-home candidate \
  && chmod -R 0555 /usr/local/lib/python3.12/site-packages/nl2repobench
WORKDIR /tests
