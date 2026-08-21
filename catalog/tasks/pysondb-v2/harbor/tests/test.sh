#!/usr/bin/env bash
set -uo pipefail

readonly EXPECTED=96
readonly EXPECTED_COLLECTED=96
readonly CANDIDATE_UID=10001

mkdir -p /logs/verifier
chmod 0700 /logs/verifier
rm -f /logs/verifier/*
rm -rf /tmp/candidate /tmp/candidate-venv /tmp/candidate-results

if ! cp -a /workspace /tmp/candidate \
    > /logs/verifier/copy-stdout.txt \
    2> /logs/verifier/copy-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --reason artifact-copy-failed
    exit 0
fi

# Keep untrusted setup code inside a candidate-owned virtual environment.
if ! python -m venv --system-site-packages /tmp/candidate-venv \
    > /logs/verifier/venv-stdout.txt \
    2> /logs/verifier/venv-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --reason verifier-environment-failed
    exit 0
fi

mkdir -p /tmp/candidate-results
chown -R "$CANDIDATE_UID:$CANDIDATE_UID" \
    /tmp/candidate /tmp/candidate-venv /tmp/candidate-results

timeout --signal=TERM --kill-after=5s 90s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        PIP_DISABLE_PIP_VERSION_CHECK=1 \
        PIP_NO_INDEX=1 \
        /tmp/candidate-venv/bin/python -m pip install \
            --no-build-isolation \
            --no-deps \
            --no-index \
            -e /tmp/candidate \
    > /logs/verifier/install-stdout.txt \
    2> /logs/verifier/install-stderr.txt
install_exit_code=$?
if [[ "$install_exit_code" -ne 0 ]]; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --reason candidate-installation-failed
    exit 0
fi

# Candidate-authored tests never participate in grading. Replace them with
# the immutable fixture copied from the pinned verifier image.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate/tests
cp -a /tests/fixture/tests/. /tmp/candidate/tests/

if ! printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/tmp/candidate/tests/__init__.py' \
      '75ea65d9135cdf66d915d53ce80c01445a3e99c2bc3706d280c30571cde69313' '/tmp/candidate/tests/test_cli.py' \
      'c4f4a53810c109513265bd1a61d8367c87aa3cf5e5b24e30093bc3fcf9152e21' '/tmp/candidate/tests/test_cli_merge.py' \
      '0d9763c91c2e55ebe1e46b7e7f516870f26553a91da47b666be8853fa1b6a371' '/tmp/candidate/tests/test_cli_purge.py' \
      '4eb58e502f5aa2f61055967db8ac2a4f55b6b84bcb66cbe5152dd73089994aa9' '/tmp/candidate/tests/test_cli_show.py' \
      '809e8ee69e65f2a9205efa9a5e8b16fe1e335c85ff128f869a9837952c2484e1' '/tmp/candidate/tests/test_cli_tocsv.py' \
      '193db462773db284027ee4c9038bd02d26fa90ccc0069780e1ab12e0889ee280' '/tmp/candidate/tests/test_db_add.py' \
      '5c9c2a1d8da14a5f2ebdb65e46891fb816bfc631c8bab2b235b0e552e1e3d77c' '/tmp/candidate/tests/test_db_add_many.py' \
      '79eef036d0228a6b09856b6260ebb2a1e6cae239b12aebe321f121a09fbe4e38' '/tmp/candidate/tests/test_db_add_new_key.py' \
      '0838a8461fb9af1abc7307e6e2c9dd639125b3c1306e4fad7e7ba891526c3448' '/tmp/candidate/tests/test_db_autoupdate.py' \
      'c5987f61ce3d1fc3af5e3f70357744ffbebe96e5720b610f939a2813a0e24f06' '/tmp/candidate/tests/test_db_delete_by_query.py' \
      '9f2099d0386e51d491285147fffa0b343b3dfa93a62f5979bfb3827e5f5cfa6f' '/tmp/candidate/tests/test_db_get_all.py' \
      'dffe48db19e3dc72831ac1079dde59232237d416d6f79fc0ff05947ce402146a' '/tmp/candidate/tests/test_db_get_all_select_keys.py' \
      'fc0c56b5ef341ee3dee323e0d455419bd90d302edb6dbd1ea9c442126d6966bb' '/tmp/candidate/tests/test_db_get_by_id.py' \
      'cecae1974e2e6618e99899e1947a6b5627ff98d833c99fabb3b1540c6f0a1971' '/tmp/candidate/tests/test_db_get_by_query.py' \
      '168f5e71ec2c5acd367e87bd848791a4d67c9731ce94ebe003fd5ebbc2b43f8a' '/tmp/candidate/tests/test_db_purge.py' \
      '891f1085ba4a0426add67800a9c3830543f5b5f3bc018ffb00c5c9abe57de305' '/tmp/candidate/tests/test_db_update_by_id.py' \
      'dafff32aaed3c359901d15d16560d5bde3cf12fc32e6f114b14a98541d38dce1' '/tmp/candidate/tests/test_db_update_by_query.py' \
      'c46b133e234290e61b8ed1ab3e675708e6560bf3d1b8bc33721f1e931961a973' '/tmp/candidate/tests/test_db_utils_methods.py' \
      'a698207e0cf1351893c251afa4e3546b02a27b812298bfdf49fbdda516c3169a' '/tmp/candidate/tests/test_delete_by_id.py' \
      '68a4b2671ce0935ffb985d215906a35e3858fc61f0921360a225abe95dba9897' '/tmp/candidate/tests/test_id_generator.py' \
      'c61f75b942b3d25be0bc5c08905040e93153201dbfa18c2faab714c6ec1cda95' '/tmp/candidate/tests/test_something.py' \
      'b974d8c989f928acd0ea3458ddfdb7eba4b3f185ac84e106cce8263a7725ca3a' '/tmp/candidate/tests/test_utils_migrate/new_data.json' \
      '8bae5fa018a8518577422bf48657f151e68ac43978990480ebfa4fb51cfab465' '/tmp/candidate/tests/test_utils_migrate/old_db.json' \
      'e338e5345cfe272c25334ea7e38ce66617e4740d5ebcba07a203c69c0e06a483' '/tmp/candidate/tests/test_utils_migrate.py' \
    | sha256sum -c - \
    > /logs/verifier/test-integrity-stdout.txt \
    2> /logs/verifier/test-integrity-stderr.txt; then
    python /tests/grade.py --expected "$EXPECTED" --expected-collected "$EXPECTED_COLLECTED" \
        --reason frozen-test-integrity-failed
    exit 0
fi

chown -R root:root /tmp/candidate-venv
chmod -R a-w /tmp/candidate-venv

# Candidate-authored tests never participate in grading. Replace them with
# the immutable fixture copied from the pinned verifier image.
rm -rf /tmp/candidate/tests
mkdir -p /tmp/candidate/tests
cp -a /tests/fixture/tests/. /tmp/candidate/tests/

# Freeze the hidden test tree before collection. The candidate may modify its
# implementation, but cannot replace the verifier-owned test bytes.
chown -R root:root /tmp/candidate/tests
chmod -R a-w /tmp/candidate/tests
mkdir -p /tmp/candidate-results

timeout --signal=TERM --kill-after=5s 300s \
    runuser -u candidate -- env \
        HOME=/home/candidate \
        PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
        sh -c 'cd /tmp/candidate && /tmp/candidate-venv/bin/python -I -B -m pytest \
            -p pytest_mock --continue-on-collection-errors tests \
            --junitxml=/tmp/candidate-results/junit.xml --tb=short' \
    > /logs/verifier/pytest-stdout.txt \
    2> /logs/verifier/pytest-stderr.txt
pytest_exit_code=$?

if [[ -f /tmp/candidate-results/junit.xml && ! -L /tmp/candidate-results/junit.xml ]]; then
    cp /tmp/candidate-results/junit.xml /logs/verifier/junit.xml
fi

python /tests/grade.py \
    --expected "$EXPECTED" \
    --expected-collected "$EXPECTED_COLLECTED" \
    --junit /logs/verifier/junit.xml \
    --pytest-exit-code "$pytest_exit_code"
