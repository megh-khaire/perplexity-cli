import typer
from dotenv import load_dotenv
from rich.console import Console

from src.cli import chat

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="perplexity-cli",
    help="A CLI replica of Perplexity AI",
    add_completion=False,
)
console = Console()

chat_app = typer.Typer(help="Conversation management commands")
app.add_typer(chat_app, name="chat")

chat_app.command("start", help="Start a new conversation")(chat.start)
chat_app.command("resume", help="Resume an existing conversation")(chat.resume)
chat_app.command("history", help="List conversation history")(chat.history)
chat_app.command("show", help="Show a specific conversation")(chat.show)
chat_app.command("clear", help="Clear conversation history")(chat.clear)
chat_app.command("export", help="Export a conversation to JSON")(chat.export)

if __name__ == "__main__":
    app()
