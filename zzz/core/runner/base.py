from rich.table import Table


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
  
  # Default help table # can extend with rows
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


