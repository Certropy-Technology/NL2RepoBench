from __future__ import annotations

import asyncio
from enum import Enum
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Annotated


def scenario(name: str):
    def register(func):
        SCENARIOS[name] = func
        return func
    return register


SCENARIOS = {}


@scenario('exports')
def exports(tmp: Path):
    import pydantic_settings as ps
    names = ['BaseSettings', 'SettingsConfigDict', 'SettingsError', 'NoDecode', 'ForceDecode', 'CliApp',
             'CliPositionalArg', 'CliSubCommand']
    return {'available': {name: hasattr(ps, name) for name in names}, 'version_is_str': isinstance(ps.__version__, str)}


@scenario('defaults')
def defaults(tmp: Path):
    from pydantic import ValidationError
    from pydantic_settings import BaseSettings
    class Settings(BaseSettings):
        host: str = 'localhost'
        port: int
    value = Settings(port='8080').model_dump()
    try:
        Settings()
    except ValidationError as exc:
        error = exc.errors(include_url=False)[0]['type']
    else:
        error = None
    return {'value': value, 'missing_error': error}


@scenario('environment')
def environment(tmp: Path):
    from pydantic_settings import BaseSettings
    os.environ['APPLE'] = 'honeycrisp'
    class Settings(BaseSettings):
        apple: str
    return Settings().model_dump()


@scenario('env-prefix')
def env_prefix(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    os.environ['APP_PORT'] = '9000'
    class Settings(BaseSettings):
        port: int
        model_config = SettingsConfigDict(env_prefix='app_')
    return Settings().model_dump()


@scenario('ignore-empty')
def ignore_empty(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    os.environ['VALUE'] = ''
    class Settings(BaseSettings):
        value: str = 'default'
        model_config = SettingsConfigDict(env_ignore_empty=True)
    return Settings().model_dump()


@scenario('complex-json')
def complex_json(tmp: Path):
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings
    class Child(BaseModel):
        enabled: bool
    class Settings(BaseSettings):
        items: list[str]
        numbers: set[int]
        mapping: dict[str, int | None]
        child: Child
    os.environ.update(ITEMS='["a", "b"]', NUMBERS='[3, 1, 3]', MAPPING='{"x": 1, "y": null}', CHILD='{"enabled": true}')
    result = Settings().model_dump(mode='json')
    result['numbers'].sort()
    return result


@scenario('invalid-json')
def invalid_json(tmp: Path):
    from pydantic_settings import BaseSettings
    os.environ['ITEMS'] = '[1,]'
    class Settings(BaseSettings):
        items: list[int]
    try:
        Settings()
    except Exception as exc:
        return {'type': type(exc).__name__, 'mentions_field': 'items' in str(exc), 'mentions_source': 'EnvSettingsSource' in str(exc)}
    return {'type': None}


@scenario('nested-delimiter')
def nested_delimiter(tmp: Path):
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Db(BaseModel):
        host: str
        port: int
    class Settings(BaseSettings):
        db: Db
        model_config = SettingsConfigDict(env_prefix='app_', env_nested_delimiter='__')
    os.environ['APP_DB'] = '{"host": "json", "port": 1}'
    os.environ['APP_DB__PORT'] = '5432'
    return Settings().model_dump()


@scenario('nested-max-split')
def nested_max_split(tmp: Path):
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Service(BaseModel):
        api_key: str
    class Settings(BaseSettings):
        service: Service
        model_config = SettingsConfigDict(env_nested_delimiter='_', env_nested_max_split=1)
    os.environ['SERVICE_API_KEY'] = 'secret'
    return Settings().model_dump()


@scenario('aliases')
def aliases(tmp: Path):
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Settings(BaseSettings):
        apple: str = Field(validation_alias='pomo')
        model_config = SettingsConfigDict(populate_by_name=True)
    os.environ.update(APPLE='field-name', POMO='alias-name')
    return Settings().model_dump()


def precedence_files(tmp: Path):
    env_file = tmp / '.env'
    env_file.write_text('FOO=from-dotenv\n')
    secrets = tmp / 'secrets'
    secrets.mkdir()
    (secrets / 'FOO').write_text('from-secrets\n')
    return env_file, secrets


@scenario('init-over-env')
def init_over_env(tmp: Path):
    from pydantic_settings import BaseSettings
    os.environ['FOO'] = 'from-env'
    class Settings(BaseSettings):
        foo: str
    return Settings(foo='from-init').model_dump()


@scenario('env-over-dotenv')
def env_over_dotenv(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    env_file, _ = precedence_files(tmp)
    os.environ['FOO'] = 'from-env'
    class Settings(BaseSettings):
        foo: str
        model_config = SettingsConfigDict(env_file=env_file)
    return Settings().model_dump()


@scenario('dotenv-over-secrets')
def dotenv_over_secrets(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    env_file, secrets = precedence_files(tmp)
    class Settings(BaseSettings):
        foo: str
        model_config = SettingsConfigDict(env_file=env_file, secrets_dir=secrets)
    return Settings().model_dump()


@scenario('secrets-over-default')
def secrets_over_default(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _, secrets = precedence_files(tmp)
    class Settings(BaseSettings):
        foo: str = 'default'
        model_config = SettingsConfigDict(secrets_dir=secrets)
    return Settings().model_dump()


@scenario('merge-sources')
def merge_sources(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    env_file, _ = precedence_files(tmp)
    env_file.write_text('NESTED={"x": 1}\n')
    os.environ['NESTED__y'] = '3'
    class Settings(BaseSettings):
        marker: int = 10
        nested: dict[str, int]
        model_config = SettingsConfigDict(env_file=env_file, env_nested_delimiter='__')
    return Settings(nested={'w': 4}).model_dump()


@scenario('custom-source-order')
def custom_source_order(tmp: Path):
    from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
    os.environ['VALUE'] = 'from-env'
    class Settings(BaseSettings):
        value: str
        @classmethod
        def settings_customise_sources(cls, settings_cls: type[BaseSettings], init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource, dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource):
            return env_settings, init_settings, dotenv_settings, file_secret_settings
    return Settings(value='from-init').model_dump()


@scenario('parse-none-enum')
def parse_none_enum(tmp: Path):
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Color(Enum):
        RED = 'red-value'
    class Settings(BaseSettings):
        optional: str | None = 'fallback'
        color: Color
        model_config = SettingsConfigDict(env_parse_none_str='NULL', env_parse_enums=True)
    os.environ.update(OPTIONAL='NULL', COLOR='RED')
    return Settings().model_dump(mode='json')


@scenario('no-force-decode')
def no_force_decode(tmp: Path):
    from pydantic import field_validator
    from pydantic_settings import BaseSettings, ForceDecode, NoDecode, SettingsConfigDict
    class Settings(BaseSettings):
        raw: Annotated[list[str], NoDecode]
        forced: Annotated[list[int], ForceDecode]
        model_config = SettingsConfigDict(enable_decoding=False)
        @field_validator('raw', mode='before')
        @classmethod
        def split_raw(cls, value):
            return value.split(',') if isinstance(value, str) else value
    os.environ.update(RAW='a,b', FORCED='[1, 2]')
    return Settings().model_dump()


@scenario('cli-run')
def cli_run(tmp: Path):
    from pydantic import BaseModel
    from pydantic_settings import CliApp
    class SyncCommand(BaseModel):
        count: int
        called: bool = False
        def cli_cmd(self):
            self.called = True
    class AsyncCommand(BaseModel):
        name: str
        called: bool = False
        async def cli_cmd(self):
            self.called = True
    sync = CliApp.run(SyncCommand, cli_args=['--count', '7'])
    async def invoke():
        return CliApp.run(AsyncCommand, cli_args=['--name', 'job'])
    asynchronous = asyncio.run(invoke())
    return {'sync': sync.model_dump(), 'async': asynchronous.model_dump()}


@scenario('cli-serialize')
def cli_serialize(tmp: Path):
    from pydantic import BaseModel
    from pydantic_settings import CliApp
    class Config(BaseModel):
        values: list[int]
        mapping: dict[str, int]
    value = Config(values=[1, 2], mapping={'a': 1, 'b': 2})
    lazy = CliApp.serialize(value, list_style='lazy')
    repeated = CliApp.serialize(value, list_style='argparse', dict_style='env')
    return {'lazy': lazy, 'repeated': repeated,
            'lazy_roundtrip': CliApp.run(Config, cli_args=lazy).model_dump(),
            'repeated_roundtrip': CliApp.run(Config, cli_args=repeated).model_dump()}


def main():
    request = json.loads(sys.stdin.read())
    name = request['scenario']
    os.environ.clear()
    with tempfile.TemporaryDirectory(prefix='pydantic-settings-case-') as directory:
        try:
            result = SCENARIOS[name](Path(directory))
            response = {'ok': True, 'result': result}
        except BaseException as exc:
            response = {'ok': False, 'error': {'type': type(exc).__name__, 'message': str(exc)}}
    sys.stdout.write(json.dumps(response, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
