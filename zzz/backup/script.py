import os
import sys

from zzz.utils.process import sh

from zzz.utils.console import AdvConsole
from .models import ScriptConfigModel


class ScriptConfig:
  def __init__(self, config: ScriptConfigModel):
    self._config = config

class ScriptArgs:
  def __init__(self):
    self._raw_args = sys.argv[1:]
  
  def get(self, index, default=None):
    try:
      return self._raw_args[index]
    except ValueError:
      return default

class Arg:
  def __init__(self, name, type_=str, default=None, help_=None):
    self.name = name
    self.type = type_
    self.default = default
    self.help = help_

  def __repr__(self):
    return f"Arg(name={self.name}, type={self.type.__name__}, default={self.default})"

class ScriptCommandBack:
  def __init__(self, name, func, short=None):
    self.name = name
    self.func = func
    
    self.short = short

  def emit(self, *args, **kwargs):
    return self.func(*args, **kwargs) if callable(self.func) else self.func
  
  def __call__(self, *args, **kwargs):
    return self.emit(*args, **kwargs)

class ScriptCommands:
  def __init__(self):
    self._registers = {}

  def add(self, name, func, *args, **kwargs):
    self._registers[name] = ScriptCommand(name, func, *args, **kwargs)

  def _get(self, name, *args, **kwargs):
    func = self._registers.get(name)
    if not func:
      raise Exception("Command not found")
    return func

class ScriptConsole(AdvConsole):
  pass


class ZScript:
  prompt = "| "
  banner = None

  def __init__(self, config={}):
    self.args = ScriptArgs()
    self.scr = ScriptConsole()
    self.commands = ScriptCommands()
    self.config = ScriptConfig(ScriptConfigModel(**config))

    self.name = os.path.basename(sys.argv[0])
    self.version = None
    self.author = None
    
    self.sh = sh

  def on(self, name, *args, **kwargs):
    def wrapper(func):
      self.commands.add(name, func, *args, **kwargs)
    return wrapper

