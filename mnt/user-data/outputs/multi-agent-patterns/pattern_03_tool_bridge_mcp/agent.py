"""
Pattern 3: Tool Bridge with MCP (Model Context Protocol)

MCP turns external tools — GitHub, databases, APIs — into
agent-accessible tools through a single protocol layer.

This agent demonstrates:
1. Connecting to an MCP server (filesystem in this example)
2. Using MCP tools transparently alongside native ADK tools
3. How ADK's MCP integration works

In production you'd swap the filesystem MCP for:
  - GitHub MCP: github.com/github/github-mcp-server
  - Notion MCP: notion.so/mcp
  - Stripe MCP: stripe.com/mcp
  - 30+ database connections via MCP Toolbox
"""

import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


def create_filesystem_agent():
    """
    Create an agent with MCP filesystem tools.

    MCPToolset connects to any MCP-compatible server.
    The agent gets access to all tools the MCP server exposes.
    """

    # Connect to the filesystem MCP server (built into @modelcontextprotocol/server-filesystem)
    # This gives the agent read/write access to a local directory
    mcp_tools = MCPToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",                                   # auto-install if not present
                "@modelcontextprotocol/server-filesystem",
                "./mcp_workspace"                       # directory the agent can access
            ],
        )
    )

    agent = Agent(
        name="mcp_tool_bridge_agent",
        model="gemini-2.0-flash",
        description=(
            "Agent demonstrating MCP Tool Bridge pattern. "
            "Accesses filesystem tools via MCP protocol."
        ),
        instruction=(
            "You are a file management agent with access to a workspace directory. "
            "Use MCP filesystem tools to read, write, and manage files. "
            "Always confirm actions before making changes."
        ),
        tools=[mcp_tools],
    )

    return agent


async def run_demo():
    """Demonstrate MCP Tool Bridge in action."""
    import os
    os.makedirs("./mcp_workspace", exist_ok=True)

    # Create a sample file for the demo
    with open("./mcp_workspace/sample_data.txt", "w") as f:
        f.write("Q1 Revenue: $2.4M\nQ2 Revenue: $3.1M\nQ3 Revenue: $2.9M\nQ4 Revenue: $3.8M\n")

    agent = create_filesystem_agent()

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="pattern_03_demo",
        user_id="demo_user"
    )

    runner = Runner(
        agent=agent,
        app_name="pattern_03_demo",
        session_service=session_service,
    )

    queries = [
        "List all files in the workspace directory.",
        "Read the sample_data.txt file and calculate the total annual revenue.",
        "Create a new file called 'summary.txt' with a brief revenue summary.",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"USER: {query}")
        print(f"{'='*60}")

        async for event in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
        ):
            if event.is_final_response():
                print(f"AGENT: {event.content.parts[0].text}")


if __name__ == "__main__":
    print("Pattern 3: Tool Bridge with MCP")
    print("Prerequisite: Node.js must be installed (for npx)")
    print()
    asyncio.run(run_demo())
