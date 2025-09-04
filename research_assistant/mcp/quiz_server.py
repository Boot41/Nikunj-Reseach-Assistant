import asyncio
import json
import os, sys
import arxiv
from dotenv import load_dotenv
import logging
import signal
from typing import List, Dict
import json
import os

from exceptiongroup import BaseExceptionGroup
from mcp import types as mcp_types # Use alias to avoid conflict
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio # For running as a stdio server

# ADK Tool Imports
from google.adk.tools.function_tool import FunctionTool
# ADK <-> MCP Conversion Utility
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

load_dotenv('/home/nikunjagrwl/Documents/Research-assistant/research_agent')
QUIZ_FILE = "/home/nikunjagrwl/Documents/Research-assistant/quizzes.json"

log_dir = '/home/nikunjagrwl/Documents/Research-assistant/.logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "mcp_server_quiz.log")
logging.basicConfig(
    level=logging.INFO,                    # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),     # Log to file
        # logging.StreamHandler()          # Remove StreamHandler to avoid terminal output
    ]
)
logger = logging.getLogger(__name__)

def load_quizzes() -> Dict:
    if not os.path.exists(QUIZ_FILE):
        with open(QUIZ_FILE, "w") as f:
            f.write("{}")
    if os.path.exists(QUIZ_FILE):
        try:
            with open(QUIZ_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}  # Empty file → return empty dict
                return json.loads(content)
        except json.JSONDecodeError:
            # Corrupt file → log and return empty dict
            logging.warning(f"Quizzes JSON file is invalid. Starting with empty quizzes.")
            return {}
    return {}

def save_quizzes(data: Dict):
    os.makedirs(os.path.dirname(QUIZ_FILE), exist_ok=True)
    with open(QUIZ_FILE, "w") as f:
        json.dump(data, f, indent=2)

def reload_quizzes():
    manager.quizzes = load_quizzes()

class QuizManager:
    def __init__(self):
        self.quizzes = load_quizzes()

    def create_quiz(self, title: str):
        if title in self.quizzes:
            logger.info(f"Quiz '{title}' already exists.")
        self.quizzes[title] = {"questions": []}
        save_quizzes(self.quizzes)
        logger.info(f"Quizzes after update: {json.dumps(manager.quizzes, indent=2)}")
        return f"Quiz '{title}' created."

    def add_question(self, title: str, question: str, options: List[str], answer: int):
        if title not in self.quizzes:
            logger.info(f"Quiz '{title}' not found.")
            return f"Quiz '{title}' does not exist."
        self.quizzes[title]["questions"].append({
            "question": question,
            "options": options,
            "answer": answer
        })
        save_quizzes(self.quizzes)
        return f"Question added to quiz '{title}'."
    
server = Server('quiz_server')
manager = QuizManager()

# Global flag to handle graceful shutdown
shutdown_event = asyncio.Event()

async def create_quiz_in_file(title: str):
    logger.info(f"creating quiz: '{title}'")
    #msg = manager.create_quiz(title)
    return {"message": 'Quiz created'}

async def add_question_to_quiz(quiz_title: str, question: str, options: list[str], answer: int):
    logger.info(f"Adding question to quiz: '{quiz_title}'")
    reload_quizzes()
    if quiz_title not in manager.quizzes:
        # Create quiz first
        manager.create_quiz(quiz_title)
        logger.info(f"Quiz '{quiz_title}' auto-created.")
    
    msg = manager.add_question(quiz_title, question, options, answer)
    logger.info(f"Quiz saved. Current quizzes: {json.dumps(manager.quizzes, indent=2)}")
    return {"message": msg}


quiz_tools ={
        "create_quiz_in_file": FunctionTool(create_quiz_in_file),
        "add_question_to_quiz": FunctionTool(add_question_to_quiz),
}

@server.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """Lists all available tools provided by this MCP server."""
    logger.info("Listing available tools.")
    mcp_tools = []
    for tool_name, fnc_name in quiz_tools.items():
        if not fnc_name.name:
            fnc_name.name = tool_name

        mcp_tool = adk_to_mcp_tool_type(fnc_name)
        mcp_tools.append(mcp_tool)
    logger.info(f"Found {len(mcp_tools)} tools.")
    return mcp_tools

@server.call_tool()
async def call_tool(tool_name: str, args: dict) -> list[mcp_types.TextContent]:
    """Invokes a specified tool with given arguments."""
    logger.info(f"Calling tool: '{tool_name}' with args: {args}")
    if tool_name not in quiz_tools:
        logger.error(f"Tool '{tool_name}' not found.")
        return [mcp_types.TextContent(type="text", text="Tool not found")]
    tool = quiz_tools[tool_name]
    try:
        result = await tool.run_async(args=args, tool_context=None) # type: ignore
        response = json.dumps(result, indent=2)  # Ensure the result is JSON serializable
        logger.info(f"Tool '{tool_name}' executed successfully.")
        return [mcp_types.TextContent(type="text", text=response)]
    except Exception as e:
        logger.error(f"Error calling tool '{tool_name}': {e}", exc_info=True)
        return [mcp_types.TextContent(type="text", text="Error: " + str(e))]

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    shutdown_event.set()

async def run_mcp_stdio_server():
    """Runs the MCP server, listening for connections over standard input/output."""
    logger.info("MCP Stdio Server: Starting...")
    
    try:
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Use the stdio_server context manager from the mcp.server.stdio library
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("MCP Stdio Server: Starting handshake with client...")
            
            # Create a task for the server run
            server_task = asyncio.create_task(
                server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=server.name,
                        server_version="0.1.0",
                        capabilities=server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
            )
            
            # # Wait for either the server task to complete or shutdown signal
            done, pending = await asyncio.wait(
                [server_task, asyncio.create_task(shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            logger.info("MCP Stdio Server: Shutdown completed.")
            
    except Exception as e:
        logger.error(f"Error in run_mcp_stdio_server: {e}", exc_info=True)
    finally:
        logger.info("MCP Stdio Server: Cleanup completed.")

if __name__ == "__main__":
    logger.info("Launching MCP Server to expose ADK tools via stdio...")
    try:
        # Use asyncio.run with proper exception handling
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        logger.info("\nMCP Server (stdio) stopped by user.")
    except Exception as e:
        logger.error(f"MCP Server (stdio) encountered an error: {e}", exc_info=True)
    finally:
        logger.info("MCP Server (stdio) process exiting.")