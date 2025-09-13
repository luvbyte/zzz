import inspect

from cmd2 import Cmd2ArgumentParser


class Arg:
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs

class ScriptCommand:
  def __init__(self, name, func, short=None, desc=None):
    self.name = name
    self.func = func # callable
    # Short description
    self.short = short
    
    self.argparser = Cmd2ArgumentParser(prog=self.name)
    # parse args from function
    self._parse_func_args()

    # if desc or get from func desc
    self.desc = desc or self.func.__doc__

  def has(self, name):
    return name in self._registers
  
  def get(self, name, default=None):
    return self._registers.get(name, default)

  def help_text(self, line):
    return self.desc or self.argparser.format_help()

  # Building argparse
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
  
  # args will be cmd2 Namespace()
  def run(self, args):
    import inspect

    # Convert argparse Namespace to dict
    if not isinstance(args, dict):
      arg_dict = vars(args)
    else:
      arg_dict = args

    sig = inspect.signature(self.func)
    positional = []
    keywords = {}
    varargs = []
    extra_kwargs = {}

    for name, param in sig.parameters.items():
      if param.kind == inspect.Parameter.VAR_POSITIONAL:
        # collect *args
        varargs = arg_dict.get(name, [])
      elif param.kind == inspect.Parameter.VAR_KEYWORD:
        # collect remaining kwargs not already matched
        for k, v in arg_dict.items():
          if k not in sig.parameters:
            extra_kwargs[k] = v
      else:
        # normal positional or keyword parameters
        if name in arg_dict:
          if param.default is inspect._empty:
            # no default → positional
            positional.append(arg_dict[name])
          else:
            # has default → keyword
            keywords[name] = arg_dict[name]

    # Call the function
    return self.func(*positional, *varargs, **keywords, **extra_kwargs)

  def run_cli(self, args):
    return self.run(self.argparser.parse_args(args))

class ScriptCommands:
  def __init__(self):
    self._registers = {}
  
  def items(self):
    return self._registers.items()
  
  def get(self, name, default=None):
    return self._registers.get(name, default)

  def add(self, name, func, *args, **kwargs):
    self._registers[name] = ScriptCommand(name, func, *args, **kwargs)
