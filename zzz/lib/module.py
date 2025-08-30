
class ZzzModule:
  def __init__(self, zzz, *args, **kwargs) -> None:
    self.zzz = zzz
    self._init_(*args, **kwargs)

  def _init_(self, *args, **kwargs) -> None:
    pass

  @property
  def scr(self) -> None:
    return self.zzz.scr
