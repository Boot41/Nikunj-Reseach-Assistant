import os
import sys
import io
import contextlib
import warnings
import logging
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


# -------------------------
# Silence MCP banners/logs/tracebacks
# -------------------------

def asyncgen_finalizer(agen):
    try:
        agen.aclose()
    except (RuntimeError, GeneratorExit):
        pass  # Known AnyIO/MCP bug
    except Exception as e:
        raise e

sys.set_asyncgen_hooks(finalizer=asyncgen_finalizer)

# Suppress FastMCP banners
os.environ["FASTMCP_NO_BANNER"] = "1"

# Hide warnings + set noisy loggers to CRITICAL
warnings.filterwarnings("ignore", category=UserWarning)
for noisy in ["fastmcp", "google", "mcp", "anyio"]:
    logging.getLogger(noisy).setLevel(logging.CRITICAL)


def silence_asyncio_exceptions(loop, context):
    msg = str(context.get("exception", context.get("message", "")))
    if "generator didn't stop" in msg or "Attempted to exit cancel scope" in msg:
        return  # ignore noisy MCP shutdown errors
    loop.default_exception_handler(context)

asyncio.get_event_loop().set_exception_handler(silence_asyncio_exceptions)


@contextlib.contextmanager
def suppress_stdout_stderr():
    """Hide stdout/stderr temporarily (for MCP startup banners)."""
    new_stdout, new_stderr = io.StringIO(), io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_stdout, new_stderr
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


# -------------------------
# Setup Typer CLI
# -------------------------
app = typer.Typer()
console = Console()

APP_NAME = "weather_cli"
USER_ID = "cli_user"

# Global session state
session_service = InMemorySessionService()
with suppress_stdout_stderr():
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


async def create_session():
    """Initialize a new session with the agent."""
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    return session.id


async def repl(session_id: str):
    """Interactive REPL loop with the weather agent."""
    console.print(
        Panel("[bold yellow]Type 'exit' or 'quit' to leave the session.[/bold yellow]")
    )

    while True:
        try:
            user_input = await asyncio.to_thread(Prompt.ask, "[bold green]You[/bold green]")
            if user_input.lower() in ["exit", "quit"]:
                break

            content = genai_types.Content(
                role="user", parts=[genai_types.Part(text=user_input)]
            )

            events = runner.run(user_id=USER_ID, session_id=session_id, new_message=content)

            response_text = None
            for event in events:
                if event.is_final_response() and event.content.parts:
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
    except (RuntimeError, GeneratorExit) as e:
        if "Attempted to exit cancel scope" not in str(e):
            raise
    finally:
        try:
            if hasattr(runner, "close") and callable(runner.close):
                runner.close()
            elif hasattr(runner, "aclose"):
                asyncio.run(runner.aclose())
        except Exception as e:
            if "Attempted to exit cancel scope" in str(e) or isinstance(e, GeneratorExit):
                pass  # ignore MCP shutdown noise
            else:
                raise


if __name__ == "__main__":
    app()
