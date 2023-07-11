from functools import partial

import click
import pytest
from hbutils.testing import simulate_entry

from gchar.config.meta import __VERSION__


@pytest.fixture(scope='module')
def sample_cli():
    from gchar.utils import GLOBAL_CONTEXT_SETTINGS
    from gchar.utils import print_version as _origin_print_version

    print_version = partial(_origin_print_version, 'zoo')

    @click.group(context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Sample of CLI.')
    @click.option('-v', '--version', is_flag=True,
                  callback=print_version, expose_value=False, is_eager=True)
    def cli():
        pass  # pragma: no cover

    @cli.command('plus', context_settings={**GLOBAL_CONTEXT_SETTINGS}, help='Just A + B Problem.')
    @click.option('-a', 'a', type=int, required=True, help='A Number')
    @click.option('-b', 'b', type=int, required=True, help='B Number')
    def plus(a, b):
        print(f'{a} + {b} = {a + b}')

    return cli


@pytest.mark.unittest
class TestUtilsCLI:
    def test_cli_help(self, sample_cli):
        result = simulate_entry(sample_cli, ['cli', '-h'])
        result.assert_okay()
        assert 'Sample of CLI.' in result.stdout

    def test_cli_version(self, sample_cli):
        result = simulate_entry(sample_cli, ['cli', '-v'])
        result.assert_okay()
        assert __VERSION__.upper() in result.stdout.upper()
        assert 'zoo'.upper() in result.stdout.upper()

    def test_cli_plus(self, sample_cli):
        result = simulate_entry(sample_cli, ['cli', 'plus', '-a', '233', '-b', '347'])
        result.assert_okay()
        assert '233 + 347 = 580' in result.stdout
