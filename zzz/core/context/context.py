import click
from importlib import import_module

from zzz.utils.process import sh
from zzz.lib.module import ZzzModule

from typing import Any, Union

class OptionRef:
  def __init__(self, value=None, type_=str) -> None:
    self._value = value
    self._type = self.__resolve_type(type_)
  
  def __resolve_type(self, value: str) -> Union[str, int, float]:
    if not isinstance(value, str):
      return value
    return {
      "str": str, "int": int, "float": float
    }[value]

  @property
  def value(self) -> Any:
    return self._value

  def ask(self, desc) -> Any:
    self._value = click.prompt(desc, type=self._type, default=self._value)
    return self._value
  
  def __str__(self) -> str:
    return str(self.value)

class ZzzOptions:
  def create(self, value, type_=str) -> OptionRef:
    return OptionRef(value, type_)

class ZzzArgs:
  def __init__(self, args: tuple) -> None:
    self._raw_args = args
    self.count = len(self._raw_args)

  def exists(self) -> bool:
    return len(self._raw_args) > 0

  def __str__(self) -> str:
    return " ".join(self._raw_args).strip()

class ZzzModules:
  def __init__(self, zzz) -> None:
    self.zzz = zzz
    self.__modules_path = "zzz.ext.modules"
  
  def _import_module(self, name: str):
    module = import_module(f"{self.__modules_path}.{name.replace('/', '.')}").Module(self.zzz)
    if not isinstance(module, ZzzModule):
      raise Exception("Error loading module: Module should be ZzzModule type")
    return module

  def get(self, *names):
    return [self._import_module(name) for name in names]

class ZzzScriptContext:
  def __init__(self, scr, args: tuple):
    self.sh = sh
    self.scr = scr
    self.op = ZzzOptions()
    self.args = ZzzArgs(args)
    self.modules = ZzzModules(self)

  def ref(self, *args, **kwargs):
    return self.op.create(*args, **kwargs)

  def include(self, *names):
    return self.modules.get(*names)

  def run(self, *args, use_args: bool = False):
    if use_args:
      args = args + self.args._raw_args
    return sh(" ".join(dict.fromkeys(args))).run()

  def echo(self, *args, **kwargs):
    return click.echo(*args, **kwargs)

  def prompt(self, *args, **kwargs):
    try:
      return click.prompt(*args, **kwargs)
    except click.Abort:
      raise KeyboardInterrupt("Exiting")

  def confirm(self, *args, **kwargs):
    return click.confirm(*args, **kwargs)

  def __call__(self, cmd: str):
    return self.sh(cmd).run()

