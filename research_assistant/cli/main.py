import asyncio
import typer
import dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from research_assistant.research_agent.agent import root_agent

dotenv.load_dotenv('/home/nikunjagrwl/Documents/Research-assistant/research_assistant/research_agent/.env')

# --- ADK imports ---
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types

app = typer.Typer()
console = Console()

APP_NAME = "research_assistant"
USER_ID = "cli_user"

def start_chat_session():
    """Initializes the agent and runs an interactive chat session."""
    # console.print("[yellow]Initializing agent...[/yellow]")
    agent = root_agent
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    # console.print("[green]✓ Agent initialized successfully[/green]")

    # The session service calls are async, so we need to run them in an event loop.
    session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID))
    session_id = session.id

    console.print(Panel("[bold yellow]Type 'exit' or 'quit' to leave the session.[/bold yellow]"))

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if user_input.lower() in ["exit", "quit"]:
                break

            content = genai_types.Content(
                role="user", parts=[genai_types.Part(text=user_input)]
            )

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
            break  # Exit the loop on Ctrl+C or Ctrl+D
        except Exception as e:
            console.print(Panel(f"[red]Error: {str(e)}[/red]"))  # Print error and continue loop


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Start a chat session with the research agent."""
    if ctx.invoked_subcommand is None:
        try:
            start_chat_session()
        finally:
            # This will run when the loop in start_chat_session is broken
            console.print(Panel("[bold yellow]Chat session ended.[/bold yellow]"))


if __name__ == "__main__":
    app()
