from datetime import datetime

from .script import ZzzScript
from .executor import ZzzScriptExecutor

from zzz.cli import __version__
from zzz.config import zzz_config



BANNER = r"""
[blue]███████╗███████╗███████╗[/]
╚══███╔╝╚══███╔╝╚══███╔╝
[red]  ███╔╝   ███╔╝   ███╔╝ [/]
 ███╔╝   ███╔╝   ███╔╝  
[yellow]███████╗███████╗███████╗[/]
╚══════╝╚══════╝╚══════╝
"""



def run_script(script: ZzzScript, intro: bool, clear: bool) -> None:
  console = zzz_config.console
  if clear:
    console.clear()

  started_at = datetime.now()
  if intro:
    zzz_config.console.print_center(BANNER)
    zzz_config.console.print_center(f"zzz: [blue]luvbyte[/] | version: [red]{__version__}[/]")

    console.print_panel(f"Running [red]{script.name}[/red]", padding=False)
  try:
    ZzzScriptExecutor(script).execute()
  except Exception as e:
    raise e
    # console.print_panel(str(e), title="ERROR")
  finally:
    # ended timestamp
    if intro:
      ended_at = datetime.now()
      duration = ended_at - started_at
      seconds = duration.total_seconds()

      console.print_panel(f"Finished in [yellow]{seconds:.2f}[/] seconds", padding=False)
  
