FROM --platform=linux/amd64 ghcr.io/multimodal-art-projection/nl2repobench/pysondb-v2@sha256:d54c22d710aaf1dbb3aee8894536e2fc3ca26b685c10a427f9b175b4d81e3c96

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1

RUN python -c "import platform, sys; assert platform.machine() == 'x86_64'; assert sys.version_info[:2] == (3, 10)"
RUN python -c "import prettytable, pytest, pytest_mock"

# Copy the immutable test tree into a verifier-only location, then clear the
# image workspace so hidden tests are not part of the candidate artifact.
RUN mkdir -p /tests/fixture \
    && cp -a /workspace/tests /tests/fixture/tests \
    && printf '%s  %s\n' \
      'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' '/tests/fixture/tests/__init__.py' \
      '75ea65d9135cdf66d915d53ce80c01445a3e99c2bc3706d280c30571cde69313' '/tests/fixture/tests/test_cli.py' \
      'c4f4a53810c109513265bd1a61d8367c87aa3cf5e5b24e30093bc3fcf9152e21' '/tests/fixture/tests/test_cli_merge.py' \
      '0d9763c91c2e55ebe1e46b7e7f516870f26553a91da47b666be8853fa1b6a371' '/tests/fixture/tests/test_cli_purge.py' \
      '4eb58e502f5aa2f61055967db8ac2a4f55b6b84bcb66cbe5152dd73089994aa9' '/tests/fixture/tests/test_cli_show.py' \
      '809e8ee69e65f2a9205efa9a5e8b16fe1e335c85ff128f869a9837952c2484e1' '/tests/fixture/tests/test_cli_tocsv.py' \
      '193db462773db284027ee4c9038bd02d26fa90ccc0069780e1ab12e0889ee280' '/tests/fixture/tests/test_db_add.py' \
      '5c9c2a1d8da14a5f2ebdb65e46891fb816bfc631c8bab2b235b0e552e1e3d77c' '/tests/fixture/tests/test_db_add_many.py' \
      '79eef036d0228a6b09856b6260ebb2a1e6cae239b12aebe321f121a09fbe4e38' '/tests/fixture/tests/test_db_add_new_key.py' \
      '0838a8461fb9af1abc7307e6e2c9dd639125b3c1306e4fad7e7ba891526c3448' '/tests/fixture/tests/test_db_autoupdate.py' \
      'c5987f61ce3d1fc3af5e3f70357744ffbebe96e5720b610f939a2813a0e24f06' '/tests/fixture/tests/test_db_delete_by_query.py' \
      '9f2099d0386e51d491285147fffa0b343b3dfa93a62f5979bfb3827e5f5cfa6f' '/tests/fixture/tests/test_db_get_all.py' \
      'dffe48db19e3dc72831ac1079dde59232237d416d6f79fc0ff05947ce402146a' '/tests/fixture/tests/test_db_get_all_select_keys.py' \
      'fc0c56b5ef341ee3dee323e0d455419bd90d302edb6dbd1ea9c442126d6966bb' '/tests/fixture/tests/test_db_get_by_id.py' \
      'cecae1974e2e6618e99899e1947a6b5627ff98d833c99fabb3b1540c6f0a1971' '/tests/fixture/tests/test_db_get_by_query.py' \
      '168f5e71ec2c5acd367e87bd848791a4d67c9731ce94ebe003fd5ebbc2b43f8a' '/tests/fixture/tests/test_db_purge.py' \
      '891f1085ba4a0426add67800a9c3830543f5b5f3bc018ffb00c5c9abe57de305' '/tests/fixture/tests/test_db_update_by_id.py' \
      'dafff32aaed3c359901d15d16560d5bde3cf12fc32e6f114b14a98541d38dce1' '/tests/fixture/tests/test_db_update_by_query.py' \
      'c46b133e234290e61b8ed1ab3e675708e6560bf3d1b8bc33721f1e931961a973' '/tests/fixture/tests/test_db_utils_methods.py' \
      'a698207e0cf1351893c251afa4e3546b02a27b812298bfdf49fbdda516c3169a' '/tests/fixture/tests/test_delete_by_id.py' \
      '68a4b2671ce0935ffb985d215906a35e3858fc61f0921360a225abe95dba9897' '/tests/fixture/tests/test_id_generator.py' \
      'c61f75b942b3d25be0bc5c08905040e93153201dbfa18c2faab714c6ec1cda95' '/tests/fixture/tests/test_something.py' \
      'b974d8c989f928acd0ea3458ddfdb7eba4b3f185ac84e106cce8263a7725ca3a' '/tests/fixture/tests/test_utils_migrate/new_data.json' \
      '8bae5fa018a8518577422bf48657f151e68ac43978990480ebfa4fb51cfab465' '/tests/fixture/tests/test_utils_migrate/old_db.json' \
      'e338e5345cfe272c25334ea7e38ce66617e4740d5ebcba07a203c69c0e06a483' '/tests/fixture/tests/test_utils_migrate.py' \
    | sha256sum -c - \
    && chmod -R a-w /tests/fixture/tests \
    && rm -rf /workspace \
    && mkdir -p /workspace

COPY test.sh /tests/test.sh
COPY grade.py /tests/grade.py

RUN useradd --uid 10001 --create-home candidate 2>/dev/null || true \
    && chmod 0555 /tests/test.sh \
    && chmod 0444 /tests/grade.py
