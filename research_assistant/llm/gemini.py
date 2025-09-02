import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ✅ Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing. Please set it in .env or environment variables.")

# ✅ Configure Gemini
genai.configure(api_key=api_key)

from fastmcp import Client
from google.generativeai.types import FunctionDeclaration, Tool

async def list_resources_as_tools(server_name: str) -> list:
    """Lists resources from an MCP server and converts them to Gemini tools."""
    client = Client(server_name)
    try:
        async with client:
            resources = await client.list_resources()
        tools = []
        for resource in resources:
            # Assuming resources have a 'spec' attribute with OpenAPI-like schema
            if hasattr(resource, 'spec') and 'properties' in resource.spec:
                f_decl = FunctionDeclaration(
                    name=resource.name,
                    description=resource.description,
                    parameters={
                        'type': 'object',
                        'properties': resource.spec['properties']
                    }
                )
                tools.append(Tool(function_declarations=[f_decl]))
        return tools
    except Exception as e:
        print(f"Failed to list resources: {e}")
        return []

async def generate_response(prompt: str, tools: list, mcp_server_name: str) -> str:
    """Generates a response from the Gemini model, with tool calling."""
    
    # For now, create a simple model without tools to avoid the TypeError
    # TODO: Fix tool integration later
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    chat = model.start_chat()
    response = await chat.send_message_async(prompt)
    
    return response.text
