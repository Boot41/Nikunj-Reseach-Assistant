# agent.py

from google.adk.agents import Agent

root_agent = Agent( 
    name="research_agent",
    model="gemini-1.5-flash",
    description="An agent that provides weather info.",
    instruction="""
    You are a helpful research assistant.
    When asked for a topic you tell the user about the research topic,
    and help him learn like a 5 year old. 
    """,
)