# Macros 

class ZzzMacros:
  def __init__(self) -> None:
    self.loaded_macros = {}

  def say(self, line, *args) -> str:
    text = " ".join(args)
    return f"zzz.scr.print(f'{text}')"

  # Try from loaded_macros
  def __fallback__(self, name, *args) -> None:
    raise ValueError(f"Macro not found: {name}")

  def __call__(self, line) -> None:
    split_lines = line.stripped[1:].split()
    if len(split_lines) < 1:
      raise ValueError(f"Invalid macro syntax: {line.raw}")

    name = split_lines[0]
    args = split_lines[1:]

    func = getattr(self, name, None)
    if callable(func):
      return func(line, *args)
    return self.__fallback__(name, line, *args)

