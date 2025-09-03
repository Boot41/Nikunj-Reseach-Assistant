import os
import sys
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import dotenv
dotenv.load_dotenv('/home/nikunjagrwl/Documents/Research-assistant/research_assistant/research_agent/.env')  # Load environment variables from .env file
import warnings
import logging

# Configure logging

log_dir = '/home/nikunjagrwl/Documents/Research-assistant/.logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "agent.log")

logging.basicConfig(
    level=logging.INFO,                    # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),     # Log to file
        # logging.StreamHandler()          # Remove StreamHandler to avoid terminal output
    ]
)

logger = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore",
    message=r"\[EXPERIMENTAL\] BaseAuthenticatedTool.*",
    category=UserWarning
)

# Get absolute paths to avoid path issues
BASE_DIR = "/home/nikunjagrwl/Documents/Research-assistant"
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python3")
SERVER_SCRIPT = os.path.join(BASE_DIR, "research_assistant", "mcp", "arxiv_server.py")
PARSER_SCRIPT = os.path.join(BASE_DIR, "research_assistant", "mcp", "pdf_parser.py")

# Verify paths exist
if not os.path.exists(VENV_PYTHON):
    logger.error(f"Python executable not found at: {VENV_PYTHON}")
    sys.exit(1)

if not os.path.exists(SERVER_SCRIPT):
    logger.error(f"Server script not found at: {SERVER_SCRIPT}")
    sys.exit(1)

logger.info(f"Using Python: {VENV_PYTHON}")
logger.info(f"Using server script: {SERVER_SCRIPT}")

try:
    root_agent = Agent( 
        name="research_agent",
        model="gemini-2.5-flash-lite",
        description="An agent that provides research info from arXiv.",
        instruction="""
        You are a helpful research assistant that can search arXiv for academic papers.
        When asked about a research topic, you can:
        1. Search for relevant papers using search_tool
        2. Read abstracts using read_abstract_tool  
        3. List recent papers in specific categories using list_recent_tool
        4. Download papers using download_pdf_tool

        When you are asked to perform a task follow this flow:
        1. If asked for searching, search and list down the papers you searched, alsongside the abstract.
        2. you are supposed to give options to the user, so that he can choose the next step.
        3. You can offer choices like search for more papers, read abstracts, find summaries, or download PDFs.
        4. Always wait for the user's input before taking the next action.
        5. Keep your responses concise and to the point.
        6. If the user asks for a summary, provide a brief overview of the topic
        7. If the user asks for a detailed explanation, provide an in-depth explanation of the topic.
        8. If the user asks for examples, provide relevant examples to illustrate the topic.
        9. If the user asks for applications, provide real-world applications of the topic.
        10. If the user asks for historical context, provide a brief history of the topic
        11. If the user asks for related topics, provide a list of related topics.
        12. If the user asks for further reading, provide a list of books, articles, or websites for further reading.
        13. If the user asks for clarification, provide a clear and concise explanation of the topic.
        14. If the user asks for a simple explanation, provide a simplified explanation of the topic.
        15. Always aim to enhance the user's understanding of the topic.
        16. Use simple language and avoid jargon.   
        
        Explain complex topics simply, as if teaching a 5-year-old, but provide accurate academic information.
        """,
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command=VENV_PYTHON,
                        args=[SERVER_SCRIPT],
                    )
                ),
                # Optional: specify which tools to load
                # tool_filter=['search_tool', 'read_abstract_tool', 'list_recent_tool', 'download_pdf_tool']
            ),
            # McpToolset(
            #     connection_params=StdioConnectionParams(
            #         server_params = StdioServerParameters(
            #             command=VENV_PYTHON,
            #             args=[PARSER_SCRIPT],
            #         )
            #     ),
            #     # Optional: specify which tools to load
            # ),
        ],
    )
    
    logger.info("Agent created successfully")
    
except Exception as e:
    logger.error(f"Error creating agent: {e}")
    raise