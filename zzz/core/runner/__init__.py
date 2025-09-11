import sys
from .cli import ZScriptRunnerCli
from .interactive import ZScriptRunner

# ------ Run types
def run_script_it(script):
  return ZScriptRunner(script).cmdloop()

def run_script_cli(script):
  return ZScriptRunnerCli(script).run()

def run_script(script):
  return run_script_cli(script) if len(sys.argv) > 1 else run_script_it(script)
