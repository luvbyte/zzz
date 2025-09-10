from pathlib import Path

from zzz.utils import ensure_dir
from zzz.utils.console import AdvConsole
from zzz.utils.parser import parse_config
from zzz.core.models import ZzzConfigModel, ZzzCliModel

ZZZ_PATH = ensure_dir(Path.home() / ".zzz")
SCRIPTS_PATH = ensure_dir(ZZZ_PATH / "scripts")
ZZZ_DATA_PATH = ensure_dir(ZZZ_PATH / "data")
ZZZ_CONFIG_PATH = ZZZ_PATH / "config.json"


class ZzzConfig:
  def __init__(self) -> None:
    self.console = AdvConsole()

    try:
      self._config = parse_config(ZZZ_CONFIG_PATH, ZzzConfigModel)
    except FileNotFoundError:
      self._config = ZzzConfigModel()

  @property
  def config(self) -> ZzzConfigModel:
    return self._config
  
  @property
  def cli(self) -> ZzzCliModel:
    return self.config.cli

  def get_script_path(self, path: str) -> Path:
    if path.startswith("@"):
      return SCRIPTS_PATH / f"{path[1:]}.zzz"

    return Path(path).resolve()

zzz_config = ZzzConfig()

