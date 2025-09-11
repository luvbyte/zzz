import sys
import types

from cmd2 import Cmd
from datetime import datetime

from rich.text import Text
from rich.table import Table

from .script import ZScript
from .command import ScriptCommand

from zzz.core import __version__
from zzz.modules.process import sh


BANNER = r"""
[blue]███████╗███████╗███████╗[/]
╚══███╔╝╚══███╔╝╚══███╔╝
[red]  ███╔╝   ███╔╝   ███╔╝ [/]
 ███╔╝   ███╔╝   ███╔╝  
[yellow]███████╗███████╗███████╗[/]
╚══════╝╚══════╝╚══════╝
"""


class ZUtils:
  def __init__(self):
    self.default_help_text = self.help_table()
  
  def help_table(self, rows=[]):
    table = Table(
      title="[bold magenta]Available Commands[/bold magenta]",
      header_style="bold cyan",
      border_style="blue",
      expand=True
    )
    # Create table
    table.add_column("Command", style="green")
    table.add_column("Description", style="yellow")
    
    # Add rows (example descriptions)
    table.add_row("alias", "Create command shortcuts")
    table.add_row("edit", "Edit a script or configuration")
    table.add_row("help", "Show help (use 'help -v' for verbose)")
    table.add_row("history", "Show command history")
    table.add_row("macro", "Record or play macros")
    table.add_row("quit", "Exit the program")
    table.add_row("run_pyscript", "Run a Python script")
    table.add_row("run_script", "Run a script")
    table.add_row("set", "Set configuration options")
    table.add_row("shell", "Run shell commands")
    table.add_row("shortcuts", "List available keyboard shortcuts")
    table.add_row("options", "Display ZOptions")
    table.add_row("zset", "Set ZOption")
    for name in rows:
      table.add_row(*name)

    return table

# cmd2
class ZScriptRunner(Cmd):
  def __init__(self, script: ZScript, clear: bool = False):
    super().__init__()
    self.script = script

    if clear:
      self.scr.clear()

    if self.script.intro:
      # Script banner or default (zzz)
      if self.script.banner is not False:
        self.scr.print_center(self.script.banner or BANNER)
        # script headers
        self._print_zzz_header()
      self._print_script_header()

    self._utils = ZUtils()
    self.commands = {name: command for name, command in self.script.commands._registers.items() if isinstance(command, ScriptCommand)}
    self._register_commands()
    
    self.script.events.emit("init")

  def _register_commands(self):
    for name, command in self.commands.items():
      # Build methods directly
      def do_func(self, line, cmd=command):
        try:
          cmd.run(line)
        except Exception as e:
          self.exception(e.args[0])

      def complete_func(self, text, line, begidx, endidx, cmd=command):
        return cmd.complete(self, text, line, begidx, endidx)

      def help_func(self, cmd=command):
        self.poutput(cmd.help_text(self))

      setattr(self, f"do_{name}", types.MethodType(do_func, self))
      setattr(self, f"complete_{name}", types.MethodType(complete_func, self))
      setattr(self, f"help_{name}", types.MethodType(help_func, self))

  def _print_zzz_header(self):
    self.scr.print_center(f"zzz: [blue]luvbyte[/blue] | version: [red]{__version__}[/red]")

  def _print_script_header(self):
    # Script header
    version = f" [red]v{self.script.version}[/red]" if self.script.version else ""
    author = self.script.author if self.script.author else "Someone [red]ᥫ᭡[/red]"
    self.scr.print_panel(f"✨ [blue]{self.script.name.capitalize()}[/blue]{version} by [green]{author}[/green]", padding=False)

  @property
  def scr(self):
    return self.script.scr

  @property
  def prompt(self):
    prompt = self.script.events.emit("prompt") or self.script.prompt
    return prompt() if callable(prompt) else prompt
  
  # --- commands
  def do_clear(self, _):
    self.scr.clear()

  def do_ls(self, line):
    sh(f"ls --color {line}").run()

  def do_pwd(self, line):
    sh(f"pwd {line}").run()

  def do_exit(self, line):
    return True
  
  #--- setting option
  def do_options(self, line):
    options = self.script.options._options
    if len(options) <= 0:
      return self.scr.print_center("\nScript has no options\n")

    table = Table(title="Script Options", expand=True)
    
    # Define columns
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Required", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Choices", style="blue")

    for name, opt in options.items():
      # value might raise if required but missing
      try:
        val = opt.value
      except ValueError as e:
        val = f"[red]{e}[/red]"  # show error in red
      
      table.add_row(
        name,
        str(val),
        "Yes" if opt.require else "No",
        opt._type.__name__,
        ", ".join(map(str, opt.choices)) or "-"
      )
    self.scr.print(table)

  def help_zset(self):
    self.scr.print("[red]Usage[/red]: zset <name> <value>\n\nSET ZOption\n")

  def complete_zset(self, text, line, begidx, endidx):
    tokens = line.split()

    # Suggest option names when typing the option name
    if len(tokens) <= 1 or (begidx <= len(tokens[0]) + 1):
      return [name for name in self.script.options._options if name.startswith(text)]

    opt_name = tokens[1]

    # If typing the value
    if opt_name in self.script.options._options:
      opt = self.script.options._options[opt_name]

      # If the option has choices, show choices matching text
      if opt.choices:
        return [str(c) for c in opt.choices if str(c).startswith(text)]

      # Otherwise, use cmd2 built-in path completer
      return self.path_complete(text, line, begidx, endidx)

    return []

  def do_zset(self, line):
    if not line:
      self.scr.print("[red]Usage[/red]: zset <name> <value>\n")

    elif len(line.arg_list) < 2:
      self.scr.print("[red]Missing[/red]: <value>\n")
    else:
      try:
        # set
        name = line.arg_list[0]
        value = " ".join(line.arg_list[1:])
        
        self.script.options.set(name, value)
        self.scr.print(f"[red]Updated[/red]: {name}={value}\n")
      except Exception as e:
        self.exception(e.args[0])
  # ---

  def complete_help(self, text, line, begidx, endidx):
    # Collect all commands (remove 'do_' prefix)
    commands = [name[3:] for name in dir(self) if name.startswith('do_')]
    # If no text typed yet, return all commands
    if not text:
      return commands
    # Filter commands by what the user has typed so far
    return [cmd for cmd in commands if cmd.startswith(text)]

  def do_help(self, line):
    if line:
      return super().do_help(line)
    # commands with no short helps
    no_short_commands = [name for name, command in self.commands.items() if command.short is None]
    short_commands = [(f"[red]{name}[/red]", command.short) for name, command in self.commands.items() if command.short]

    if len(short_commands) > 0:
      self.scr.print(self._utils.help_table(short_commands))
    else:
      self.scr.print(self._utils.default_help_text)

    if len(no_short_commands) > 0:
      self.scr.print_panel(f"[blue]{' '.join(no_short_commands)}[/blue]", padding=False)
  
  # cli
  def _run_cli(self, args: tuple=sys.argv[1:]):
    return super().onecmd_plus_hooks(' '.join(args))
  
  def default(self, line):
    event = self.script.events.get("default")
    if event:
      return event.emit(line)
    self.scr.print(f"[blue]zzz[/blue]: Unknown command: [red]{line.command}[/red]")
  
  def exception(self, text):
    self.scr.print(f"[red]Error:[/red] zzz: [blue]{text}[/blue]")

# ------ Run types
def run_script_it(script: ZScript):
  return ZScriptRunner(script).cmdloop()

def run_script_cli(script: ZScript):
  return ZScriptRunner(script, clear=False)._run_cli()

def run_script(script: ZScript):
  return run_script_cli(script) if len(sys.argv) > 1 else run_script_it(script)
