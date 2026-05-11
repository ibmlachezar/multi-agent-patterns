"""
Pattern 4: Cross-Organization Federation

Two organizations communicate via A2A while each maintains
its own governance, security model, and data boundaries.

Org A: Your organization — has a coordinator and gateway
Org B: Partner organization — has specialist agents

The key: Org B's agents never expose their internals.
Org A's gateway controls what can be shared.
Org B's agents control their own side.
"""

import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import tool
from google.adk.a2a.client import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


# ─────────────────────────────────────────────────────────────
# ORG B: Partner Organization Agents
# Each runs with its own governance and security model
# ─────────────────────────────────────────────────────────────

@tool
def process_salesforce_crm(customer_id: str, action: str) -> dict:
    """
    Process a CRM action in Salesforce.
    Governed by Salesforce Security policies.
    """
    return {
        "customer_id": customer_id,
        "action": action,
        "status": "completed",
        "crm_record_id": f"SF-{customer_id}-001",
        "governed_by": "Salesforce Security",
        "data_boundary": "org_b_salesforce"
    }


salesforce_agent = Agent(
    name="salesforce_agent",
    model="gemini-2.0-flash",
    description="Salesforce CRM agent. Governed by Salesforce Security. Org B partner agent.",
    instruction=(
        "You are a Salesforce CRM specialist operating under Salesforce Security policies. "
        "Process CRM actions while maintaining data boundary compliance."
    ),
    tools=[process_salesforce_crm],
)


@tool
def create_servicenow_ticket(title: str, description: str, priority: str) -> dict:
    """
    Create a ServiceNow ticket.
    Governed by ServiceNow Security policies.
    """
    import random
    return {
        "ticket_id": f"SN-{random.randint(100000, 999999)}",
        "title": title,
        "priority": priority,
        "status": "new",
        "governed_by": "ServiceNow Security",
        "data_boundary": "org_b_servicenow"
    }


servicenow_agent = Agent(
    name="servicenow_agent",
    model="gemini-2.0-flash",
    description="ServiceNow ticketing agent. Governed by ServiceNow Security. Org B partner agent.",
    instruction=(
        "You are a ServiceNow specialist operating under ServiceNow Security policies. "
        "Create and manage tickets while maintaining data boundary compliance."
    ),
    tools=[create_servicenow_ticket],
)


# ─────────────────────────────────────────────────────────────
# ORG A: Your Organization
# Gateway controls what your agents can share with Org B
# ─────────────────────────────────────────────────────────────

@tool
def validate_federation_request(request_type: str, data_fields: list) -> dict:
    """
    Org A Gateway: Validate what data can be shared with partner organizations.
    Enforces Org A's governance policies before any cross-org communication.

    Args:
        request_type: Type of request being federated
        data_fields: List of data fields to be shared

    Returns:
        dict with approval status and any redacted fields
    """
    # Org A's governance rules
    sensitive_fields = ["ssn", "password", "internal_cost", "margin"]
    redacted = [f for f in data_fields if f.lower() in sensitive_fields]
    approved = [f for f in data_fields if f.lower() not in sensitive_fields]

    return {
        "approved": len(redacted) == 0,
        "approved_fields": approved,
        "redacted_fields": redacted,
        "governance_policy": "Org A Data Sharing Policy v2.1",
        "audit_id": f"AUDIT-{hash(str(data_fields)) % 99999}"
    }


# Remote connections to Org B's partner agents
# In production these would be validated by Google Cloud Security
org_b_salesforce = RemoteA2aAgent(url="http://localhost:8041")
org_b_servicenow = RemoteA2aAgent(url="http://localhost:8042")

org_a_coordinator = Agent(
    name="org_a_coordinator",
    model="gemini-2.0-flash",
    description="Org A coordinator. Federates with Org B partner agents via A2A.",
    instruction=(
        "You are Org A's coordination agent. "
        "When working with partner organizations:\n"
        "1. First validate the request through validate_federation_request\n"
        "2. Only share approved data fields\n"
        "3. Delegate to the appropriate partner agent (Salesforce or ServiceNow)\n"
        "4. Always report which data boundaries were maintained"
    ),
    tools=[validate_federation_request],
    agents=[org_b_salesforce, org_b_servicenow],
)


async def run_demo():
    """Demonstrate Cross-Organization Federation."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="pattern_04_demo",
        user_id="demo_user"
    )

    runner = Runner(
        agent=org_a_coordinator,
        app_name="pattern_04_demo",
        session_service=session_service,
    )

    request = """
    We need to update our partner systems for customer CUST-789:
    1. Update their record in Salesforce CRM with action: 'upgrade_to_premium'
    2. Create a ServiceNow ticket: 'Premium Upgrade - CUST-789' with high priority

    Share customer_id, account_type, and upgrade_date.
    Do NOT share: internal_cost, margin, or SSN.
    """

    print(f"\n{'='*60}")
    print("Cross-Organization Federation Demo")
    print(f"{'='*60}")
    print(request)

    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=request)]
        )
    ):
        if event.is_final_response():
            print(f"\nResult:\n{event.content.parts[0].text}")


if __name__ == "__main__":
    print("Pattern 4: Cross-Organization Federation")
    print("Start Org B agents first:")
    print("  The org_b servers are defined at the bottom of this file")
    print("  In production, Org B runs their own infrastructure")
    print()
    asyncio.run(run_demo())
