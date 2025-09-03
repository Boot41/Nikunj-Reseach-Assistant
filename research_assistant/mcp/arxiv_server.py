import asyncio
import json
import os, sys
import arxiv
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
log_file = os.path.join(log_dir, "mcp_server.log")

logging.basicConfig(
    level=logging.INFO,                    # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),     # Log to file
        # logging.StreamHandler()          # Remove StreamHandler to avoid terminal output
    ]
)

logger = logging.getLogger(__name__)

server = Server('Arxiv_server')

# Global flag to handle graceful shutdown
shutdown_event = asyncio.Event()

# --- Tool: Search ArXiv ---
async def search_tool(query: str, max_results: int = 10):
    logger.info(f"Searching arXiv with query: '{query}', max_results: {max_results}")
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for r in search.results():
            results.append({
                "title": r.title,
                "authors": [a.name for a in r.authors],
                "summary": r.summary,
                "published": r.published.isoformat(),
                "arxiv_id": r.get_short_id(),
                "pdf_url": r.pdf_url,
            })
        logger.info(f"Found {len(results)} papers.")
        return {"papers": results}
    except Exception as e:
        logger.error(f"Error in search_tool: {e}")
        return {"error": str(e), "papers": []}

# --- Tool: Get Abstract ---
async def read_abstract_tool(arxiv_id: str):
    logger.info(f"Reading abstract for arXiv ID: {arxiv_id}")
    try:
        paper = arxiv.Search(id_list=[arxiv_id]).results()
        result = next(paper)
        logger.info(f"Found paper: '{result.title}'")
        return {
            "id": result.entry_id,
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "summary": result.summary,
            "published": result.published.isoformat()
        }
    except StopIteration:
        logger.warning(f"Paper with arXiv ID '{arxiv_id}' not found.")
        return {"error": "Paper not found"}
    except Exception as e:
        logger.error(f"Error in read_abstract_tool: {e}")
        return {"error": str(e)}

# --- Tool: Download PDF ---
async def download_pdf_tool(arxiv_id: str):
    logger.info(f"Downloading PDF for arXiv ID: {arxiv_id}")
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(search.results())
        pdf_path = f"{arxiv_id.replace('/', '_')}.pdf"
        result.download_pdf(filename=pdf_path)
        logger.info(f"Successfully downloaded PDF to '{pdf_path}'")
        return {"pdf_path": pdf_path}
    except StopIteration:
        logger.warning(f"Paper with arXiv ID '{arxiv_id}' not found for download.")
        return {"error": "Paper not found"}
    except Exception as e:
        logger.error(f"Error in download_pdf_tool: {e}")
        return {"error": str(e)}

# --- Tool: List Recent Papers ---
async def list_recent_tool(category: str, max_results: int = 10):
    logger.info(f"Listing recent papers for category: '{category}', max_results: {max_results}")
    try:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        papers = []
        for result in search.results():
            papers.append({
                "id": result.entry_id,
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "summary": result.summary,
                "pdf_url": result.pdf_url,
                "published": result.published.isoformat()
            })
        logger.info(f"Found {len(papers)} recent papers.")
        return {"papers": papers}
    except Exception as e:
        logger.error(f"Error in list_recent_tool: {e}")
        return {"error": str(e), "papers": []}


arxiv_tools ={
        "search_tool": FunctionTool(search_tool),
        "read_abstract_tool": FunctionTool(read_abstract_tool),
        "download_pdf_tool": FunctionTool(download_pdf_tool),
        "list_recent_tool": FunctionTool(list_recent_tool),
}

@server.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """Lists all available tools provided by this MCP server."""
    logger.info("Listing available tools.")
    mcp_tools = []
    for tool_name, fnc_name in arxiv_tools.items():
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
    if tool_name not in arxiv_tools:
        logger.error(f"Tool '{tool_name}' not found.")
        return [mcp_types.TextContent(type="text", text="Tool not found")]
    tool = arxiv_tools[tool_name]
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