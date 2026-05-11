"""
Pattern 2: Delegated Specialization
Customer Onboarding Coordinator

The coordinator handles a multi-step onboarding flow by delegating
to specialist agents — each owned by a different team, in a different language.

The coordinator doesn't know their internals.
It just delegates goals via A2A and waits for results.

Flow: Identity → Credit → Account Provisioning → Compliance → Communication
"""

import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.client import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Each specialist runs as its own A2A server
# Different teams own each one — different deploy cycles, different languages
identity_agent = RemoteA2aAgent(url="http://localhost:8011")      # Security Team
credit_agent = RemoteA2aAgent(url="http://localhost:8012")        # Risk Team
account_agent = RemoteA2aAgent(url="http://localhost:8013")       # Platform Team
compliance_agent = RemoteA2aAgent(url="http://localhost:8014")    # Legal Team
communication_agent = RemoteA2aAgent(url="http://localhost:8015") # Marketing Team

onboarding_coordinator = Agent(
    name="customer_onboarding_coordinator",
    model="gemini-2.0-flash",
    description="Coordinates the full customer onboarding flow across 5 specialist agents",
    instruction="""
You are the Customer Onboarding Coordinator.
When asked to onboard a new customer, execute these steps in order:

1. IDENTITY VERIFICATION (identity_verification_agent)
   → Verify the customer's identity documents

2. CREDIT ASSESSMENT (credit_assessment_agent)
   → Assess creditworthiness based on customer data

3. ACCOUNT PROVISIONING (account_provisioning_agent)
   → Create the customer account in the system

4. COMPLIANCE REVIEW (compliance_doc_agent)
   → Generate required compliance documentation

5. COMMUNICATION (communication_agent)
   → Send welcome message and onboarding materials

Each step must complete before the next begins.
Report the status after each step.
If any step fails, stop and report the failure clearly.
""",
    agents=[
        identity_agent,
        credit_agent,
        account_agent,
        compliance_agent,
        communication_agent,
    ],
)


async def run_demo():
    """Demonstrate a full customer onboarding flow."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="pattern_02_demo",
        user_id="demo_user"
    )

    runner = Runner(
        agent=onboarding_coordinator,
        app_name="pattern_02_demo",
        session_service=session_service,
    )

    customer_request = """
    Please onboard the following new customer:
    - Name: Jane Smith
    - Email: jane.smith@example.com
    - Date of Birth: 1985-03-15
    - SSN Last 4: 4321
    - Annual Income: $95,000
    - Account Type: Premium Business
    """

    print(f"\n{'='*60}")
    print("Starting Customer Onboarding Flow")
    print(f"{'='*60}")
    print(customer_request)
    print(f"{'='*60}\n")

    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=customer_request)]
        )
    ):
        if event.is_final_response():
            print(f"COORDINATOR RESULT:\n{event.content.parts[0].text}")


if __name__ == "__main__":
    print("Pattern 2: Delegated Specialization")
    print("Start all 5 specialist agents first:")
    print("  python specialists/identity_agent/server.py   (port 8011)")
    print("  python specialists/credit_agent/server.py     (port 8012)")
    print("  python specialists/account_agent/server.py    (port 8013)")
    print("  python specialists/compliance_agent/server.py (port 8014)")
    print("  python specialists/comm_agent/server.py       (port 8015)")
    print()
    asyncio.run(run_demo())
