import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from research_assistant.core.agent import root_agent

# --- ADK imports ---
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types

app = typer.Typer()
console = Console()

APP_NAME = "weather_cli"
USER_ID = "cli_user"

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


async def create_session():
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    return session.id


async def repl(session_id: str):
    """Interactive REPL loop with persistent session_id."""
    console.print(Panel("[bold yellow]Type 'exit' or 'quit' to leave the session.[/bold yellow]"))

    while True:
        try:
            user_input = await asyncio.to_thread(Prompt.ask, "[bold green]You[/bold green]")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Wrap input in Content
            content = genai_types.Content(
                role="user", parts=[genai_types.Part(text=user_input)]
            )

            # Reuse the SAME session_id every time
            events = runner.run(
                user_id=USER_ID,
                session_id=session_id,
                new_message=content
            )

            response_text = None
            for event in events:
                if event.is_final_response():
                    if event.content.parts:
                        response_text = event.content.parts[0].text
                    break

            if response_text:
                console.print(Panel(f"[bold blue]Assistant:[/bold blue] {response_text}"))
            else:
                console.print(Panel("[red]No response from agent.[/red]"))

        except (KeyboardInterrupt, EOFError):
            break


@app.command()
def chat():
    """Start a chat session with the weather agent."""
    try:
        session_id = asyncio.run(create_session())
        asyncio.run(repl(session_id))
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        console.print(Panel("[bold yellow]Chat session ended.[/bold yellow]"))


if __name__ == "__main__":
    app()
