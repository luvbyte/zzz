import sys
import types
import argparse

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from datetime import datetime

from rich.text import Text
from rich.table import Table

from zzz.core.context import ZScript, ScriptCommand

from zzz.modules.process import sh

from .base import BANNER, RunnerUtils



def make_script_parser():
  # script argparser
  script_argparse = Cmd2ArgumentParser()
  script_argparse.add_argument(
    'subcommand',
    choices=['commands', 'commands-full', 'options', 'options-required'],
    help='Choose subcommand'
  )
  return script_argparse

# cmd2 - interactive
class ZScriptRunner(Cmd):
  def __init__(self, script: ZScript):
    # bypassing cmd2 default argparse :)
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0]]
    # init of Cmd
    super().__init__()
    # restoring argv
    sys.argv = original_argv

    self.script = script

    self.utils = RunnerUtils(self.script)
    self._register_commands()
    
    # emit init event
    self.script.events.emit("init")

  # arg parser
  def __register_commands(self):
    for name, command in self.script.commands.items():
      # Build methods directly
      @with_argparser(command.argparser)
      def do_func(self, args, cmd=command):
        try:
          cmd.run(args)
        except Exception as e:
          self.exception(e.args[0])
      
      do_func.argparser.prog = name
  
      setattr(self, f"do_{name}", types.MethodType(do_func, self))
  
  def _register_commands(self):
    for name, command in self.script.commands.items():
      desired_prog = command.argparser.prog or name

      @with_argparser(command.argparser)
      def do_func(inner_self, args, cmd=command):
        try:
          cmd.run(args)
        except Exception as e:
          inner_self.exception(e.args[0])

      # cmd2's decorator changes both the argparser.prog and the function name
      # Fix them back:
      do_func.argparser.prog = desired_prog    # fixes Usage: text
      do_func.__name__ = f"do_{name}"  # fixes command name in help
      do_func.__qualname__ = f"do_{name}"  # also for introspection

      # finally bind the method to your instance
      setattr(self, f"do_{name}", types.MethodType(do_func, self))
  
  @property
  def scr(self):
    return self.utils.scr

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
  @with_argparser(make_script_parser())
  def do_script(self, args):
    if args.subcommand == "commands":
      self.utils._print_commands(False)
    elif args.subcommand == "commands-full":
      self.utils.print_commands_cmd2()
    elif args.subcommand == "options":
      self.utils.print_options(False)
    elif args.subcommand == "options-required":
      self.utils.print_options(True)

  # ----------
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
    
    self.scr.print_panel("[red]Usage[/red]: command [ARGS] [-h]", padding=False)
    self.utils.print_commands_cmd2()

  def default(self, line):
    event = self.script.events.get("default")
    if event:
      return event.emit(line)
    self.scr.print(f"[blue]zzz[/blue]: Unknown command: [red]{line.command}[/red]")
  
  def run(self, clear: bool = False, intro: bool = True):
    if clear:
      self.scr.clear()

    if intro:
      self.utils.print_intro()
    
    self.cmdloop()

  def exception(self, text):
    self.utils.exception(text)
