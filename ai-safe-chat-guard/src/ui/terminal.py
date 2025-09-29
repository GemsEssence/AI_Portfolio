from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

def print_event(message, outputs):
    table = Table(show_header=True, header_style="bold")
    table.add_column("Model")
    table.add_column("Result")
    table.add_column("Details")
    for k, v in outputs.items():
        table.add_row(k, str(v.get("label")), v.get("details","-"))
    console.print(f"[bold]User:[/bold] {message}")
    console.print(table)
