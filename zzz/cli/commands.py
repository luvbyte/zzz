import click

from zzz.config import zzz_config
from zzz.core.script import ZzzScript
from zzz.core.runner import run_script


@click.command()
@click.argument("PATH", nargs=1)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.option("--skip-intro", default=None, is_flag=True, help="Don't print zzz intro")
@click.option("--no-cls", default=None, is_flag=True, help="Clear screen before running script")
def main(path, args, skip_intro, no_cls):
  run_script(
    ZzzScript(path, args),
    intro=False if skip_intro else zzz_config.cli.intro,
    clear=False if no_cls else zzz_config.cli.clear
  )
