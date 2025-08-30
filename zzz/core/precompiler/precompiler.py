import ast

from .agent import Checker
from .macros import ZzzMacros

from zzz.core.script import ZzzScript
from zzz.core.models import ZzzScriptOptionsModel


class PreCodeLine:
  def __init__(self, line: str):
    self.raw = line.rstrip("\n")
    self.stripped = self.raw.strip()
    self.tokens = self.stripped.split()

  @property
  def token(self) -> None:
    return self.tokens[0] if self.tokens else None

class ZzzPreCompiler:
  def __init__(self, script: ZzzScript) -> None:
    self.script = script
    self.checker = Checker()
    self.macros = ZzzMacros()
    self.options = ZzzScriptOptionsModel(**{})

  def transform(self, line: PreCodeLine) -> str:
    # comments // → #
    if line.stripped.startswith("//"):
      return line.raw.replace("//", "#", 1)
  
    indent = len(line.raw) - len(line.raw.lstrip(" "))
  
    # Dispatch map for + variants
    print_handlers = {
      "< ":  lambda c: f'scr.print("{c}")',   # plain string
      "<< ": lambda c: f'scr.print(f"{c}")',  # f-string
      "<<< ": lambda c: f"scr.print({c})",     # raw args
    }

    for prefix, handler in print_handlers.items():
      if line.stripped.startswith(prefix):
        content = line.stripped[len(prefix):].strip()
        return " " * indent + handler(content)

    # >> → assignment shorthand
    if line.stripped.startswith(">> "):
      content = line.stripped[2:].strip()
      try:
        target, value = content.split(" ", 1)
      except ValueError:
        raise ValueError(f"Invalid assignment syntax: {line.raw}")
      return " " * indent + f"{target} = {value}"
    # fn → def shorthand
    if line.stripped.startswith("fn "):
      signature = line.stripped[3:].strip()
  
      if "->" in signature:  # one-liner return
        sig, expr = signature.split("->", 1)
        return " " * indent + f"def {sig.strip()}: return {expr.strip()}"
      else:  # normal block function
        return " " * indent + "def " + signature
    # conditionals with ?
    if line.stripped.startswith("?"):
      if line.stripped.startswith("?! "):  # elif
        content = line.stripped[3:].strip()
        return " " * indent + f"elif {content}:"
      elif line.stripped.startswith("?:"):  # else
        return " " * indent + "else:"
      else:  # plain if
        content = line.stripped[2:].strip()
        return " " * indent + f"if {content}"
    # for loops
    if line.stripped.startswith("for "):
      content = line.stripped[4:].strip()
    
      # range sugar: for i in 1..X:
      if ".." in content:
        try:
          var, rng = content.split("in", 1)
          var = var.strip()
          rng = rng.strip().rstrip(":")
          start, end = [x.strip() for x in rng.split("..", 1)]
          return " " * indent + f"for {var} in range({start}, {end} + 1):"
        except Exception:
          raise ValueError(f"Invalid range loop syntax: {line.raw}")
    
      # fallback: normal Python for
      return " " * indent + "for " + content
    # while loop
    if line.stripped.startswith("loop:"):
      return " " * indent + "while True:" + content
    # shell commands
    if line.stripped.startswith("$"):
      content = line.stripped[1:].strip()
      return " " * indent + f'zzz(f"{content}")'
    # macros : ...
    if line.stripped.startswith(":"):
      return " " * indent + self.macros(line)

    return line.raw

  def compile_line(self, line: str, lang: str) -> str:
    if not line.strip():
      return ""  # skip empty lines

    # For python code
    if lang == "py":
      return line

    pre_line = PreCodeLine(line)
    if lang == "zzz":
      return self.transform(pre_line)

    raise Exception(f"LangNotFound: '{lang}' not found")

  # Parse zzz script options
  def parse_config_string(self, config_str: str) -> ZzzScriptOptionsModel:
    # Remove leading "#!" if present
    config_str = config_str.lstrip("#!").strip()
    
    # Split into key-value pairs by `;`
    parts = [p.strip() for p in config_str.split(";") if p.strip()]
    
    parsed = {}
    for part in parts:
      if "=" in part:
        key, value = map(str.strip, part.split("=", 1))
        try:
          # Try evaluating Python literal safely
          value = ast.literal_eval(value)
        except Exception:
          # Leave as string if not evaluable
          value = value
        parsed[key] = value
    
    return ZzzScriptOptionsModel(**parsed)

  def _compile(self, lines: list[str], has_options: bool = False):
    lang = "zzz"
    compiled = []

    start = 1 if has_options else 0
    for line in lines[start:]:
      stripped = line.rstrip("\n")
      
      # if it finds
      if line.startswith("/-/"):
        lang = stripped[3:].strip()
        compiled.append(f"# LANG START [{lang}]")
      else:
        compiled.append(self.compile_line(stripped, lang))
    return "\n".join(compiled)

  def compile(self) -> str:  # 50 MB default
    lines = self.script.code

    if not lines:
      return ""

    first_line = lines[0]
    if first_line.startswith("#!"):
      self.options = self.parse_config_string(first_line)
      if not self.options.precompile:
        return "\n".join(lines)
      # Install script requirements
      self.checker.require(self.options.require)
      self.checker.check_platform(self.options.platform)
      return self._compile(lines, has_options=True)
  
    return self._compile(lines)
