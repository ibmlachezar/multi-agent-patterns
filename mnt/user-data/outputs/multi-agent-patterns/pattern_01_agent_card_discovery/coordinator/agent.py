"""
Pattern 1: Agent Card Discovery
Coordinator Agent

Discovers specialist agents by fetching their Agent Cards,
then delegates tasks to the right specialist via A2A.

This is the key insight of Pattern 1:
  The coordinator doesn't need to know how each specialist works internally.
  It just needs the URL. A2A handles the rest.
"""

import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.client import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# The coordinator discovers each agent by fetching its Agent Card
# Agent Cards are auto-generated at /.well-known/agent.json by to_a2a()
# This is like an OpenAPI spec — but for agent-to-agent communication
financial_specialist = RemoteA2aAgent(
    url="http://localhost:8001",
    # ADK fetches the agent card from http://localhost:8001/.well-known/agent.json
    # and understands the agent's capabilities, auth requirements, and rate limits
)

support_specialist = RemoteA2aAgent(
    url="http://localhost:8002",
)

# The coordinator knows about both specialists via their discovered Agent Cards
coordinator = Agent(
    name="coordinator_agent",
    model="gemini-2.0-flash",
    description="Coordinator that routes requests to specialist agents via Agent Card Discovery",
    instruction=(
        "You are a coordinator agent. "
        "Route requests to the appropriate specialist:\n"
        "- Financial questions, stock data, reports → financial_analysis_agent\n"
        "- Support tickets, live chat, customer issues → customer_support_agent\n"
        "Always delegate to the right specialist and summarize their response."
    ),
    agents=[financial_specialist, support_specialist],
)


async def run_demo():
    """Demonstrate Agent Card Discovery in action."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="pattern_01_demo",
        user_id="demo_user"
    )

    runner = Runner(
        agent=coordinator,
        app_name="pattern_01_demo",
        session_service=session_service,
    )

    queries = [
        "What's the current stock price and a report for GOOGL over the last month?",
        "I'm customer C-12345 and I have an urgent billing issue. Can you create a support ticket?",
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
                print(f"COORDINATOR: {event.content.parts[0].text}")


if __name__ == "__main__":
    print("Pattern 1: Agent Card Discovery")
    print("Make sure both specialist agents are running first:")
    print("  Terminal 1: cd specialist_agents/financial_agent && python server.py")
    print("  Terminal 2: cd specialist_agents/support_agent && python server.py")
    print()
    asyncio.run(run_demo())
