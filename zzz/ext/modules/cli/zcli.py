from zzz.lib.module import ZzzModule

class Group:
  def __init__(self, name, title, itext=None):
    self.name = name
    self.title = title or "Options"
    self.itext = itext or "Select"
    self._options = []
  
  @property
  def options(self):
    return [option[0] for option in self._options]

  def map(self, name, func):
    self._options.append((name, func))

  def run(self, index, *args, **kwargs):
    for i, (name, func) in enumerate(self._options, start=1):
      if i == index:
        return func(name, index, *args, **kwargs) if callable(func) else func

  def on(self, name):
    def wrapper(func):
      self.map(name, func)
    return wrapper

class Module(ZzzModule):
  def init(self, title=None, itext=None):
    self._groups = {
      "__main__": Group("__main__", title, itext)
    }
    self.groups_stack = [self.group("__main__")]
    
    self._stop = False
  
  @property
  def active_group(self):
    return self.groups_stack[-1]
  
  def stop(self):
    self._stop = True

  def group(self, name, title=None, itext=None):
    if name not in self._groups:
      self._groups[name] = Group(name, title or name.capitalize(), itext)
    return self._groups[name]
  
  def map(self, name, func):
    self._groups["__main__"].map(name, func)

  def on(self, name):
    def wrapper(func):
      self.map(name, func)
    return wrapper
  
  def input_int(self, text, length):
    while True:
      try:
        i = int(input(f"{text}: "))
        if 0 <= i <= length:
          return i  # Valid input, return it
        else:
          print(f"Please enter a number between 1 - {length}.")
      except ValueError:
        print("Invalid input. Please enter an integer.")

  def start(self):
    self._stop = False
    while True:
      if self._stop:
        break
      self.scr.print_list(self.active_group.options, title=self.active_group.title, multi=True if len(self.active_group.options) > 10 else False)
      value = self.input_int(self.active_group.itext, len(self.active_group.options))
      if value == 0:
        if len(self.groups_stack) <= 1:
          break
        self.groups_stack.pop()
      else:
        result = self.active_group.run(value)
        if isinstance(result, Group):
          self.groups_stack.append(result)
        elif isinstance(result, bool) and result:
          break
      self.scr.br()

  def __call__(self):
    self.start()

