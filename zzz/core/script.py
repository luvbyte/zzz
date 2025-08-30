import os

from zzz.config import zzz_config
from zzz.utils.cli import read_from_stdin


class BasePath:
  def __init__(self, path: str) -> None:
    self.path = path

class Url(BasePath):
  @property
  def name(self) -> str:
    return self.path.split("/")[-1]
  
  def get_code(self) -> str:
    import requests

    response = requests.get(self.path)
    response.raise_for_status()
    return response.text

class File(BasePath):
  def __init__(self, path: str) -> None:
    self.path = zzz_config.get_script_path(path)

  @property
  def name(self) -> str:
    return os.path.basename(self.path)

  def get_code(self) -> str:
    with open(self.path, "r", encoding="utf-8") as f:
      return f.read()

class ZzzScript:
  def __init__(self, path: str, args: tuple) -> None:
    self.args = args
    self.path: BasePath = self._resolve_path(path)

    self.name = self.path.name
    self.code: list[str] = self.path.get_code().splitlines()

  def _resolve_path(self, path: str) -> BasePath:
    if path.startswith("http"):
      return Url(path)
    
    return File(path)
