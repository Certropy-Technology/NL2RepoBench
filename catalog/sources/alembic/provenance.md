# Alembic Provenance

- Upstream: `https://github.com/sqlalchemy/alembic`
- Frozen revision: `c116cbc0f39d9df2b4ce5f1871043a622ca8774f`
- Git archive SHA-256: `d152069190bef5403affcb73bd9b25cdeb34b4662a9bc8b70f9fe65968b72e72`
- License: MIT; `LICENSE` SHA-256: `6e68d94a03a0e3e327ddf3e86d1ebedc14eece3922022618fc246a36296fd0cc`
- Build backend: `setuptools.build_meta`, with upstream `setuptools>=77.0.3`.
- Runtime closure: private hash-locked pip requirements artifact `sha256:2977f99ef38095162afc88a4cfc62a4e54ade5c9db4d12c8266a366b5c808114`, including `setuptools==84.0.0` for Alembic's no-build-isolation build backend contract.

The source probe used CPython 3.12.11 with Alembic 1.19.2, SQLAlchemy 2.0.36, Mako 1.4.1, and pytest 8.3.5. The upstream `test_config.py` and `test_offline_environment.py` collection completed `89 passed`.
