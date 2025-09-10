import os
import sys
import cmd2
import inspect

from zzz.utils.console import AdvConsole
from zzz.utils.process import sh

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
  
  def __str__(self):
    return " ".join(self._raw_args)

# ----

class ScriptEvent:
  def __init__(self, name, func, *args, **kwargs):
    self.name = name
    self.func = func
  
  def emit(self, *args, **kwargs):
    return self.func(*args, **kwargs)

class ScriptEvents:
  def __init__(self):
    self._registers = {}

  def add(self, name, func, *args, **kwargs):
    self._registers[name] = ScriptEvent(name, func, *args, **kwargs)
  
  def has(self, name):
    return name in self._registers
  
  def get(self, name, default=None):
    return self._registers.get(name, default)

  def emit(self, name, *args, **kwargs):
    event = self._registers.get(name, None)
    if event:
      return event.emit(*args, **kwargs)

# ----
class Arg:
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs

class ScriptCommand:
  def __init__(self, name, func, short=None, desc=None):
    self.name = name
    self.func = func # callable
    self.short = short
    
    self.argparser = cmd2.Cmd2ArgumentParser(prog=self.name)
    self._parse_func_args()
    
    self.desc = desc or self.func.__doc__
  
  def has(self, name):
    return name in self._registers
  
  def get(self, name, default=None):
    return self._registers.get(name, default)

  def help_text(self, line):
    return self.desc or self.argparser.format_help()

  def _parse_func_args(self):
    sig = inspect.signature(self.func)
  
    for param_name, param in sig.parameters.items():
      # Handle *args and **kwargs
      if param.kind == inspect.Parameter.VAR_POSITIONAL:
        # treat as multiple args
        self._add_argument(param_name, nargs='*', help=f"Extra positional args for {param_name}")
        continue
      elif param.kind == inspect.Parameter.VAR_KEYWORD:
        # skip automatic parsing of **kwargs
        continue

      # If annotation is Arg instance, use it directly
      if isinstance(param.annotation, Arg):
        arg = param.annotation
        self._add_argument(*arg.args, **arg.kwargs)
        continue

      # Fallback: normal type+default detection
      arg_type = param.annotation if param.annotation != inspect._empty else str
      default = param.default if param.default != inspect._empty else None

      if default is None:
        # positional argument
        self._add_argument(param_name, type=arg_type)
      else:
        # optional argument
        self._add_argument(f"--{param_name}", type=arg_type, default=default)

  def _add_argument(self, *args, **kwargs):
    self.argparser.add_argument(*args, **kwargs)

  def emit_func(self, *args, **kwargs):
    return self.func(*args, **kwargs) if callable(self.func) else self.func

  def run(self, argv):
    try:
      parsed = self.argparser.parse_args(argv.arg_list)
    except SystemExit:
      return

    data = vars(parsed).copy()
    sig = inspect.signature(self.func)

    pos_args = []    # real positional arguments in order
    var_args = []    # for *args
    kwargs = {}      # for keywords
    has_var_kw = False

    for name, param in sig.parameters.items():
      if param.kind == inspect.Parameter.VAR_POSITIONAL:
        items = data.pop(name, [])
        if not isinstance(items, (list, tuple)):
          items = [items]
        var_args.extend(items)
      elif param.kind == inspect.Parameter.VAR_KEYWORD:
        has_var_kw = True
      else:
        # this is a normal positional-or-keyword param
        if name in data:
          pos_args.append(data.pop(name))
        else:
          # leave default handling — optional param with default
          # will be satisfied automatically
          pass

    if has_var_kw:
      kwargs.update(data)

    return self.func(*pos_args, *var_args, **kwargs)

  def complete(self, shell, text, line, begidx, endidx):
    completions = []

    # Complete option flags
    for action in self.argparser._actions:
        if action.option_strings:
            for opt in action.option_strings:
                if opt.startswith(text):
                    completions.append(opt)

    # Complete positional arguments
    positional_args = [a for a in self.argparser._actions if not a.option_strings]
    if positional_args:
        # First positional argument
        arg = positional_args[0]
        if arg.choices:
            completions += [c for c in arg.choices if c.startswith(text)]
        else:
            # default to path completion if no choices
            completions += shell.path_complete(text, line, begidx, endidx)

    return completions

class ScriptCommands:
  def __init__(self):
    self._registers = {}

  def add(self, name, func, *args, **kwargs):
    if name.startswith("zzz:"):
      self._registers[name] = ScriptEvent(name, func, *args, **kwargs)
    else:
      self._registers[name] = ScriptCommand(name, func, *args, **kwargs)

# ----

class ScriptConsole(AdvConsole):
  pass

class ZScript:
  prompt = "| "
  banner = None
  def __init__(self, intro=True, config={}):
    self.args = ScriptArgs()
    self.scr = ScriptConsole()
    self.config = ScriptConfig(ScriptConfigModel(**config))
    
    self.events = ScriptEvents()
    self.commands = ScriptCommands()

    self.name = os.path.basename(sys.argv[0])
    self.intro = intro
    self.version = None
    self.author = None
    
    self.sh = sh

  def arg(self, *args, **kwargs):
    return Arg(*args, **kwargs)

  def on(self, name, *args, **kwargs):
    def wrapper(func):
      if name.startswith("zzz:"):
        self.events.add(name[4:], func, *args, **kwargs)
      else:
        self.commands.add(name, func, *args, **kwargs)
    return wrapper

  def on_event(self, name, *args, **kwargs):
    def wrapper(func):
      self.events.add(name, func, *args, **kwargs)
    return wrapper
