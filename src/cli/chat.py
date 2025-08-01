"""Chat interface commands for conversation management."""

import json
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from src.cli.client import AgentClient
from src.schemas import MessageCreate
from src.storage.conversation import ConversationStorage
from src.storage.database import init_database

console = Console()
storage = ConversationStorage()


def init_chat_database():
    """Initialize the database for chat functionality."""
    try:
        init_database()
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        raise typer.Exit(1)


def get_agent_client() -> AgentClient:
    """Get the agent client with error handling."""
    try:
        return AgentClient()
    except Exception as e:
        console.print(f"[red]Error initializing agent client: {e}[/red]")
        raise typer.Exit(1)


def start(
    title: Optional[str] = typer.Option(
        None, "--title", "-t", help="Title for new conversation"
    )
):
    """Start a new conversation."""
    init_chat_database()

    # Create new conversation
    conversation = storage.create_conversation(title)
    console.print(f"[green]Started new conversation:[/green] {conversation.title}")
    console.print(f"[dim]Conversation ID: {conversation.id[:8]}...[/dim]")

    # Start the chat loop
    run_chat_loop(conversation)


def resume(
    session_id: Optional[str] = typer.Option(
        None, "--session", "-s", help="Specific conversation ID to resume"
    ),
):
    """Resume an existing conversation."""
    init_chat_database()

    conversation = None

    if session_id:
        # Resume specific conversation
        conversation = storage.get_conversation(session_id)
        if not conversation:
            console.print(f"[red]Conversation {session_id} not found[/red]")
            raise typer.Exit(1)
    else:
        # Show conversation selection menu
        conversations = storage.list_conversations(limit=10)

        if not conversations:
            console.print(
                "[yellow]No conversations found. Use 'perplexity-cli chat start' to begin a new conversation.[/yellow]"
            )
            raise typer.Exit(0)

        console.print("[green]Recent conversations:[/green]")

        # Create a numbered list for selection
        for i, conv in enumerate(conversations, 1):
            console.print(f"[cyan]{i:2d}.[/cyan] [white]{conv.title}[/white]")
            console.print(
                f"    [dim]ID: {conv.id[:8]}... | Last: {conv.last_accessed.strftime('%Y-%m-%d %H:%M')}[/dim]"
            )

        console.print()

        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    f"Select conversation (1-{len(conversations)}) or 'q' to quit",
                    default="q",
                )

                if choice.lower() == "q":
                    console.print("[yellow]Goodbye![/yellow]")
                    raise typer.Exit(0)

                choice_num = int(choice)
                if 1 <= choice_num <= len(conversations):
                    conversation = conversations[choice_num - 1]
                    # Get full conversation details
                    conversation = storage.get_conversation(conversation.id)
                    break
                else:
                    console.print(
                        f"[red]Please enter a number between 1 and {len(conversations)}[/red]"
                    )

            except ValueError:
                console.print("[red]Please enter a valid number or 'q' to quit[/red]")

    console.print(f"[green]Resuming conversation:[/green] {conversation.title}")

    run_chat_loop(conversation)


def run_chat_loop(conversation):
    """Run the main chat interaction loop."""
    # Initialize agent client
    agent_client = get_agent_client()

    console.print(
        "\n[yellow]Type 'exit' to end the conversation, 'history' to see full history[/yellow]"
    )
    console.print("[yellow]Type '/help' for more commands[/yellow]\n")

    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold green]You")

            if not user_input.strip():
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if user_input.lower() == "history":
                show_conversation_history(conversation.id)
                continue

            if user_input.startswith("/"):
                handle_chat_command(user_input, conversation.id)
                continue

            # Add user message to conversation first
            storage.add_message(
                MessageCreate(
                    conversation_id=conversation.id, role="user", content=user_input
                )
            )

            # If this is the first user message, update conversation title if it's still default
            messages = storage.get_conversation_messages(conversation.id)
            if len(messages) == 1:
                current_conversation = storage.get_conversation(conversation.id)
                if current_conversation and current_conversation.title.startswith("Conversation "):
                    title = user_input[:255] if len(user_input) > 255 else user_input
                    storage.update_conversation_title(conversation.id, title)

            # Get conversation history for context (including the message we just added)
            history = storage.get_conversation_history(conversation.id)

            # Generate response with conversation context and streaming
            console.print("\n[cyan]Assistant:[/cyan] ", end="")

            try:
                # Show search/thinking loader while waiting for first token
                status_msg = "[cyan]Thinking...[/cyan]"
                with console.status(status_msg):
                    response_stream = agent_client.chat(history, stream=True)
                    if response_stream is None:
                        raise Exception("No response stream received from agent")

                    # Get the first chunk to stop the thinking loader
                    try:
                        first_chunk = next(response_stream, None)
                    except StopIteration:
                        first_chunk = None

                # Start streaming output
                full_response = ""
                if first_chunk is not None:
                    print(first_chunk, end="", flush=True)
                    full_response += str(first_chunk)

                    # Continue with remaining chunks
                    try:
                        for chunk in response_stream:
                            if chunk is not None:
                                print(chunk, end="", flush=True)
                                full_response += str(chunk)
                    except Exception as chunk_error:
                        console.print(f"\n[red]Streaming error: {chunk_error}[/red]")
                else:
                    # Fallback if no chunks received
                    console.print("[dim]No response received from API[/dim]")

                response = full_response if full_response else "No response generated."
                console.print()  # New line after streaming

            except Exception as e:
                response = f"I apologize, but I encountered an error: {str(e)}"
                console.print(f"\n{response}")

            # Add assistant response to conversation
            storage.add_message(
                MessageCreate(
                    conversation_id=conversation.id, role="assistant", content=response
                )
            )

        except KeyboardInterrupt:
            console.print("\n[yellow]Conversation interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


def handle_chat_command(command: str, conversation_id: str):
    """Handle special chat commands."""
    cmd = command.lower().strip()

    if cmd == "/help":
        console.print(
            Panel.fit(
                "[bold]Chat Commands:[/bold]\n\n"
                "[cyan]/help[/cyan] - Show this help message\n"
                "[cyan]/title <new_title>[/cyan] - Change conversation title\n"
                "[cyan]/export[/cyan] - Export conversation to JSON\n"
                "[cyan]/clear[/cyan] - Clear current conversation\n"
                "[cyan]history[/cyan] - Show conversation history\n"
                "[cyan]exit[/cyan] - End conversation",
                title="Help",
            )
        )
    elif cmd == "/export":
        export_conversation(conversation_id)
    elif cmd == "/clear":
        if Confirm.ask("Are you sure you want to clear this conversation?"):
            if storage.delete_conversation(conversation_id):
                console.print("[green]Conversation cleared[/green]")
            else:
                console.print("[red]Failed to clear conversation[/red]")
    else:
        console.print(f"[red]Unknown command: {command}[/red]")


def show_conversation_history(conversation_id: str):
    """Display the full conversation history."""
    messages = storage.get_conversation_messages(conversation_id)

    if not messages:
        console.print("[yellow]No messages in this conversation yet[/yellow]")
        return

    console.print(
        Panel.fit(f"[bold]Conversation History ({len(messages)} messages)[/bold]")
    )

    for msg in messages:
        role_color = "green" if msg.role == "user" else "cyan"
        timestamp = msg.timestamp.strftime("%H:%M:%S")

        console.print(
            f"\n[dim]{timestamp}[/dim] [{role_color}]{msg.role.upper()}:[/{role_color}]"
        )
        console.print(msg.content)


def export_conversation(conversation_id: str, filename: Optional[str] = None):
    """Export conversation to JSON file."""
    try:
        export_data = storage.export_conversation(conversation_id)
        if not export_data:
            console.print("[red]Conversation not found[/red]")
            return

        # Create filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{export_data.session.id[:8]}_{timestamp}.json"

        # Export to JSON
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data.dict(), f, indent=2, default=str)

        console.print(f"[green]Conversation exported to:[/green] {filename}")

    except Exception as e:
        console.print(f"[red]Export failed: {e}[/red]")


def history(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of conversations to show"
    ),
    search: Optional[str] = typer.Option(
        None, "--search", "-s", help="Search conversations"
    ),
):
    """List conversation history."""
    init_chat_database()

    if search:
        conversations = storage.search_conversations(search, limit)
        console.print(f"[green]Search results for '{search}':[/green]")
    else:
        conversations = storage.list_conversations(limit)
        console.print("[green]Recent conversations:[/green]")

    if not conversations:
        console.print("[yellow]No conversations found[/yellow]")
        return

    table = Table()
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Title", style="white")
    table.add_column("Last Access", style="green")

    for conv in conversations:
        table.add_row(
            conv.id[:8] + "...",
            conv.title,
            conv.last_accessed.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


def show(
    session_id: str = typer.Argument(..., help="Conversation ID to show"),
):
    """Show a specific conversation."""
    init_chat_database()

    conversation = storage.get_conversation(session_id)
    if not conversation:
        console.print(f"[red]Conversation {session_id} not found[/red]")
        raise typer.Exit(1)

    console.print(
        Panel.fit(
            f"[bold]Title:[/bold] {conversation.title}\n"
            f"[bold]Created:[/bold] {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Last Access:[/bold] {conversation.last_accessed.strftime('%Y-%m-%d %H:%M:%S')}\n",
            title="Conversation Info",
        )
    )

    show_conversation_history(session_id)


def clear(
    all: bool = typer.Option(False, "--all", help="Clear all conversations"),
    session_id: Optional[str] = typer.Option(
        None, "--session", "-s", help="Specific conversation ID to clear"
    ),
):
    """Clear conversation history."""
    init_chat_database()

    if all:
        if Confirm.ask(
            "Are you sure you want to clear ALL conversations? This cannot be undone."
        ):
            count = storage.clear_all_conversations()
            console.print(f"[green]Cleared {count} conversations[/green]")
    elif session_id:
        if Confirm.ask(f"Are you sure you want to clear conversation {session_id}?"):
            if storage.delete_conversation(session_id):
                console.print("[green]Conversation cleared[/green]")
            else:
                console.print("[red]Conversation not found or failed to clear[/red]")
    else:
        console.print("[red]Please specify --all or --session <id>[/red]")


def export(
    session_id: str = typer.Argument(..., help="Conversation ID to export"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
):
    """Export a conversation to JSON."""
    init_chat_database()
    export_conversation(session_id, output)
