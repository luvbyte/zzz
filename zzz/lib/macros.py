

class ZzzScriptMacro:
  def __init__(self, func, *args, **kwargs) -> None:
    self.func = func

# Decorator
def macro(*args, **kwargs) -> ZzzScriptMacro:
  def wrapper(func):
    return ZzzScriptMacro(func, *args, **kwargs)
  
  return wrapper
