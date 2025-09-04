import asyncio
import re
import typer
import dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.rule import Rule
from rich import box

from research_assistant.research_agent.agent import root_agent

# Load env for your agent
dotenv.load_dotenv('/home/nikunjagrwl/Documents/Research-assistant/research_assistant/research_agent/.env')

# --- ADK imports ---
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types

app = typer.Typer()
console = Console()

APP_NAME = "research_assistant"
USER_ID = "cli_user"
BRAND = "RE-AST"  # Research Exploration Assistant Tool


# ---------- Helpers ----------
def big_banner():
    ascii_art = r"""
██████╗ ███████╗         █████╗ ███████╗████████╗
██╔══██╗██╔════╝        ██╔══██╗██╔════╝╚══██╔══╝
██████╔╝█████╗   ████╗  ███████║███████╗   ██║   
██ ██╔╝ ██╔══╝   ╚═══╝  ██╔══██║╚════██║   ██║   
██╔╝███╗███████╗        ██║  ██║███████║   ██║   
╚═╝ ╚══╝╚══════╝        ╚═╝  ╚═╝╚══════╝   ╚═╝   
"""
    console.print(ascii_art, style="bold cyan")
    console.print(
        Panel.fit(
            f"[bold cyan]{BRAND}[/bold cyan]\n"
            "[bold white]Research Assistant CLI Tool[/bold white]\n\n"
            "[bold yellow]Type 'exit' or 'quit' to leave the session.[/bold yellow]",
            box=box.DOUBLE,
            border_style="bold blue",
            style="bold white",
        )
    )


def format_lists(text: str) -> str:
    """
    Normalize common list patterns so Rich Markdown renders them cleanly.
    - ensures '- ' bullets are consistent
    - converts '1) ' -> '1. ' for ordered lists
    """
    text = re.sub(r"^\s*[-*]\s+", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*(\d+)[\.\)]\s+", r"\1. ", text, flags=re.MULTILINE)
    return text


def italics_to_bold_safe(text: str) -> str:
    """
    Convert *italic* and _italic_ to **bold** outside of fenced code blocks.
    Avoids touching **bold**, lists, and code fences.
    """
    lines = text.splitlines()
    in_code_fence = False
    out = []

    single_star = re.compile(r'(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)')
    single_underscore = re.compile(r'(?<!_)_(?!_)([^_\n]+?)(?<!_)_(?!_)')

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            out.append(line)
            continue
        if in_code_fence:
            out.append(line)
            continue

        converted = single_star.sub(r'**\1**', line)
        converted = single_underscore.sub(r'**\1**', converted)
        out.append(converted)

    return "\n".join(out)


def clean_response(text: str) -> str:
    text = italics_to_bold_safe(text)
    text = format_lists(text)
    return text


# ---------- Core Loop ----------
def start_chat_session():
    """Initializes the agent and runs an interactive chat session."""
    agent = root_agent
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

    session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID))
    session_id = session.id

    big_banner()

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green] 💬")
            if user_input.lower() in ["exit", "quit"]:
                break

            content = genai_types.Content(role="user", parts=[genai_types.Part(text=user_input)])
            events = runner.run(user_id=USER_ID, session_id=session_id, new_message=content)

            response_text = None
            for event in events:
                if event.is_final_response():
                    parts = getattr(event.content, "parts", None) if event.content else None
                    if parts:
                        texts = []
                        for p in parts:
                            t = getattr(p, "text", None)
                            if t:
                                texts.append(t)
                        response_text = "\n\n".join(texts) if texts else None
                    break

            console.print(Rule(style="dim cyan"))

            if response_text:
                cleaned = clean_response(response_text)
                console.print(
                    Panel(
                        Markdown(cleaned),
                        title=f"[bold cyan]{BRAND}[/bold cyan]",
                        title_align="left",
                        border_style="bold blue",
                        box=box.ROUNDED,
                        style="bold white",
                        padding=(1, 2),
                    )
                )
            else:
                console.print(
                    Panel("[bold red]⚠️ No response from agent.[/bold red]", box=box.ROUNDED)
                )

            console.print(Rule(style="dim cyan"))

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(
                Panel(f"[bold red]❌ Error: {str(e)}[/bold red]", border_style="red", box=box.ROUNDED)
            )

    console.print(
        Panel.fit(
            "👋 [bold yellow]Chat session ended.[/bold yellow]",
            box=box.DOUBLE,
            border_style="bold red",
            style="bold white",
        )
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Start a chat session with the research agent."""
    if ctx.invoked_subcommand is None:
        try:
            start_chat_session()
        finally:
            pass


if __name__ == "__main__":
    app()
