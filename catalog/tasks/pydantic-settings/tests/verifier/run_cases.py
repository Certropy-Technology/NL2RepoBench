from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

EXPECTED = {
    'exports': {'available': {name: True for name in ['BaseSettings', 'SettingsConfigDict', 'SettingsError', 'NoDecode', 'ForceDecode', 'CliApp', 'CliPositionalArg', 'CliSubCommand']}, 'version_is_str': True},
    'defaults': {'value': {'host': 'localhost', 'port': 8080}, 'missing_error': 'missing'},
    'environment': {'apple': 'honeycrisp'},
    'env-prefix': {'port': 9000},
    'ignore-empty': {'value': 'default'},
    'complex-json': {'items': ['a', 'b'], 'numbers': [1, 3], 'mapping': {'x': 1, 'y': None}, 'child': {'enabled': True}},
    'invalid-json': {'type': 'SettingsError', 'mentions_field': True, 'mentions_source': True},
    'nested-delimiter': {'db': {'host': 'json', 'port': 5432}},
    'nested-max-split': {'service': {'api_key': 'secret'}},
    'aliases': {'apple': 'alias-name'},
    'init-over-env': {'foo': 'from-init'},
    'env-over-dotenv': {'foo': 'from-env'},
    'dotenv-over-secrets': {'foo': 'from-dotenv'},
    'secrets-over-default': {'foo': 'from-secrets'},
    'merge-sources': {'marker': 10, 'nested': {'w': 4, 'x': 1, 'y': 3}},
    'custom-source-order': {'value': 'from-env'},
    'parse-none-enum': {'optional': None, 'color': 'red-value'},
    'no-force-decode': {'raw': ['a', 'b'], 'forced': [1, 2]},
    'cli-run': {'sync': {'count': 7, 'called': True}, 'async': {'name': 'job', 'called': True}},
    'cli-serialize': {
        'lazy': ['--values', '1,2', '--mapping', '{"a": 1, "b": 2}'],
        'repeated': ['--values', '1', '--values', '2', '--mapping', 'a=1', '--mapping', 'b=2'],
        'lazy_roundtrip': {'values': [1, 2], 'mapping': {'a': 1, 'b': 2}},
        'repeated_roundtrip': {'values': [1, 2], 'mapping': {'a': 1, 'b': 2}},
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python', required=True)
    parser.add_argument('--client', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    records = []
    for name, expected in EXPECTED.items():
        try:
            completed = subprocess.run(
                [args.python, str(args.client)], input=json.dumps({'scenario': name}), text=True,
                capture_output=True, timeout=1, env={'PYTHONNOUSERSITE': '1'},
            )
            response = json.loads(completed.stdout)
            actual = response.get('result') if response.get('ok') else response
            passed = completed.returncode == 0 and response.get('ok') is True and actual == expected
            detail = None if passed else {'returncode': completed.returncode, 'expected': expected, 'actual': actual,
                                           'stderr': completed.stderr[-2000:]}
        except Exception as exc:
            passed = False
            detail = {'controller_error': f'{type(exc).__name__}: {exc}'}
        records.append({'name': name, 'passed': passed, 'detail': detail})
        print(f'{"PASS" if passed else "FAIL"} {name}')
    args.output.write_text(json.dumps(records, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
