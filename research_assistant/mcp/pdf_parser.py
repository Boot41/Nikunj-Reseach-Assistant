import pdfplumber
# from markdownify import markdownify as md_convert
import os
import asyncio
import json
from dotenv import load_dotenv
import logging
import signal

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

log_dir = '/home/nikunjagrwl/Documents/Research-assistant/.logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "mcp_server_pdf.log")

logging.basicConfig(
    level=logging.INFO,                    # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),     # Log to file
        # logging.StreamHandler()          # Remove StreamHandler to avoid terminal output
    ]
)

logger = logging.getLogger(__name__)

server = Server('pdf_par_server')

# Global flag to handle graceful shutdown
shutdown_event = asyncio.Event()

import os
import fitz  # PyMuPDF
import mistune

output_dir = "/home/nikunjagrwl/Documents/Research-assistant/markdown"

async def pdf_to_markdown(pdf_path: str):
    """
    Parse a PDF into Markdown, including headings, paragraphs, images, and simple tables.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_dir = os.path.join(output_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    

pdf_tools ={
        "pdf_to_markdown": FunctionTool(pdf_to_markdown),
}

@server.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """Lists all available tools provided by this MCP server."""
    logger.info("Listing available tools.")
    mcp_tools = []
    for tool_name, fnc_name in pdf_tools.items():
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
    if tool_name not in pdf_tools:
        logger.error(f"Tool '{tool_name}' not found.")
        return [mcp_types.TextContent(type="text", text="Tool not found")]
    tool = pdf_tools[tool_name]
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
