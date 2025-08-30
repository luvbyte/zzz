import sys
import shutil
import platform

from click import confirm

from zzz.config import zzz_config
from zzz.utils.process import sh

class PkgInstaller:
  def __init__(self) -> None:
    self.os_name = platform.system()
    self.linux_pkg_managers = [
      "apt", "apt-get", "pkg", "yum", "dnf"
    ]

  def check(self, name: str, tp=None) -> bool:
    if tp == "py":
      try:
        __import__(name)
      except ImportError:
        return False
      return True
    return True if shutil.which(name) else False

  def install(self, pkgs: list, tp=None) -> bool:
    if len(pkgs) <= 0:
      return True
      
    if tp == "py":
      zzz_config.console.print_panel(f'[green]{" ".join(pkgs)}[/]', title="Required Python Modules")
    else:
      zzz_config.console.print_panel(f'[red]{" ".join(pkgs)}[/]', title="Script Required Packages")
    if not confirm("Install?", default=True):
      sys.exit()

    if tp == "py":
      if sh(" ".join([sys.executable, "-m", "pip", "install"] + pkgs)).run().returncode != 0:
        raise Exception("Error installing py modules")
      return True
    # Linux
    if self.os_name == "Linux":
      for name in self.linux_pkg_managers:
        if shutil.which(name):
          if sh(" ".join(["sudo", name, "install", "-y"] + pkgs)).run().returncode != 0:
            raise Exception("Error installing packages")
          return True
      raise EnvironmentError("No supported package manager found on Linux.")
    # macOS *
    # Windows *
    else:
      raise EnvironmentError(f"Automatic install not supported on {platform.system()}.")
    
    return True

class Checker:
  def __init__(self) -> None:
    self.pkg_installer = PkgInstaller()

  def require(self, args_list) -> None:
    pkgs = [name for name in args_list if not name.startswith("!") and not self.pkg_installer.check(name)]
    py_pkgs = [name[1:] for name in args_list if name.startswith("!") and not self.pkg_installer.check(name[1:], "py")]

    # install
    self.pkg_installer.install(pkgs)
    self.pkg_installer.install(py_pkgs, "py")

  def check_platform(self, names: list) -> None:
    if len(names) <= 0:
      return None
    if platform.system().lower() not in names:
      raise Exception("Cant run script in this os!")
