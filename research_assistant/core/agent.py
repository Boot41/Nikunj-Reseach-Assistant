# agent.py
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
import subprocess
import sys
import atexit

load_dotenv('/home/nikunjagrwl/Documents/Research-assistant/.env')
api_key = os.getenv("GOOGLE_API_KEY")

mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params={
            "command": "python",
            "args": ["/home/nikunjagrwl/Documents/Research-assistant/research_assistant/mcp/server.py"],
        }
    ),
    tool_filter=["get_weather"]
)

root_agent = LlmAgent( 
    name="weather_agent",
    model="gemini-1.5-flash",
    description="An agent that provides weather info using an external MCP server.",
    instruction=(
        "You are a helpful assistant. When the user asks about weather, "
        "use the `get_weather` tool with a city name."
    ),
    tools=[mcp_toolset],
)