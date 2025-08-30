from zzz.config import zzz_config

from .script import ZzzScript
from .context import ZzzScriptContext
from .precompiler import ZzzPreCompiler

from zzz.utils.console import AdvConsole

class ExecContext:
  def __init__(self, options, console: AdvConsole, script: ZzzScript):
    self.script = script
    self.options = options
    self.console = console

    self.zzz = ZzzScriptContext(self.console, self.script.args)
    # globals for script
    self.export = {
      "zzz": self.zzz,
      "scr": self.zzz.scr
    }


class ZzzScriptExecutor:
  def __init__(self, script: ZzzScript, console: AdvConsole = zzz_config.console) -> None:
    self.script = script
    self.console = console
    
    # Pre compiler
    self.precompiler = ZzzPreCompiler(self.script)
    self.code = self.precompiler.compile()
    
    # Available in script
    self.execute_context = ExecContext(self.precompiler.options, self.console, self.script)

  def execute(self):
    # execute user code
    return exec(self.code, self.execute_context.export)

