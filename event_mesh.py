"""
Pattern 5: Ambient Event Mesh

Agents listen on event streams and react continuously in the background.
When a new specialist is registered, the mesh self-organizes around it.

This example simulates:
  - A Pub/Sub event stream (simulated with asyncio queues)
  - A router agent that classifies and routes events
  - Specialist agents that handle specific event types
  - Dynamic registration of new agents into the mesh

In production this would use:
  - Google Cloud Pub/Sub for event streams
  - BigQuery for data event triggers
  - Agent Observability for tracing every interaction
"""

import asyncio
import random
from datetime import datetime
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import tool
from google.adk.a2a.client import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()


# ─────────────────────────────────────────────────────────────
# EVENT STREAM SIMULATION
# In production: Google Cloud Pub/Sub or BigQuery triggers
# ─────────────────────────────────────────────────────────────

EVENT_TYPES = [
    "new_support_ticket",
    "payment_received",
    "vip_customer_action",
    "content_uploaded",
    "data_quality_issue",
]


def generate_event() -> dict:
    """Simulate an incoming event from Pub/Sub."""
    event_type = random.choice(EVENT_TYPES)
    return {
        "event_id": f"EVT-{random.randint(10000, 99999)}",
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "payload": {
            "customer_id": f"CUST-{random.randint(1000, 9999)}",
            "amount": round(random.uniform(10, 5000), 2),
            "priority": random.choice(["low", "normal", "high", "urgent"]),
            "content_id": f"CONT-{random.randint(100, 999)}",
        }
    }


# ─────────────────────────────────────────────────────────────
# SPECIALIST AGENTS
# Each handles a specific event type
# ─────────────────────────────────────────────────────────────

@tool
def process_billing_event(customer_id: str, amount: float, event_id: str) -> dict:
    """Process a billing or payment event."""
    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "amount_processed": amount,
        "transaction_id": f"TXN-{random.randint(100000, 999999)}",
        "status": "processed",
        "handler": "billing_agent"
    }


billing_agent = Agent(
    name="billing_agent",
    model="gemini-2.0-flash",
    description="Handles billing and payment events from the event mesh.",
    instruction="Process billing events. Always confirm the transaction ID and amount.",
    tools=[process_billing_event],
)


@tool
def handle_support_event(customer_id: str, priority: str, event_id: str) -> dict:
    """Handle an incoming support ticket event."""
    ticket_id = f"TKT-{random.randint(10000, 99999)}"
    return {
        "event_id": event_id,
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "priority": priority,
        "assigned_team": "support_team_a" if priority in ["high", "urgent"] else "support_team_b",
        "status": "created",
        "handler": "technical_support_agent"
    }


support_agent = Agent(
    name="technical_support_agent",
    model="gemini-2.0-flash",
    description="Handles support ticket events from the event mesh.",
    instruction="Process support events. Route urgent tickets to Team A, others to Team B.",
    tools=[handle_support_event],
)


@tool
def handle_vip_event(customer_id: str, event_id: str, event_type: str) -> dict:
    """Handle a VIP customer action — highest priority routing."""
    return {
        "event_id": event_id,
        "customer_id": customer_id,
        "vip_status": "confirmed",
        "action_taken": "escalated_to_account_manager",
        "notification_sent": True,
        "handler": "vip_priority_agent"
    }


vip_agent = Agent(
    name="vip_priority_agent",
    model="gemini-2.0-flash",
    description="Handles VIP customer events with highest priority routing.",
    instruction="Process VIP customer events. Always escalate to account manager and send notification.",
    tools=[handle_vip_event],
)


# ─────────────────────────────────────────────────────────────
# ROUTER AGENT
# The mesh's brain — classifies and routes every incoming event
# ─────────────────────────────────────────────────────────────

@tool
def classify_event(event_type: str, payload: dict) -> dict:
    """
    Classify an incoming event and determine routing.

    Args:
        event_type: The type of event from the stream
        payload: The event payload

    Returns:
        dict with routing decision and priority
    """
    routing_map = {
        "payment_received": {"agent": "billing_agent", "priority": "normal"},
        "new_support_ticket": {"agent": "technical_support_agent",
                               "priority": payload.get("priority", "normal")},
        "vip_customer_action": {"agent": "vip_priority_agent", "priority": "urgent"},
        "content_uploaded": {"agent": "content_moderation_agent", "priority": "low"},
        "data_quality_issue": {"agent": "data_engineering_agent", "priority": "high"},
    }

    routing = routing_map.get(event_type, {"agent": "default_agent", "priority": "low"})
    return {
        "event_type": event_type,
        "routed_to": routing["agent"],
        "priority": routing["priority"],
        "routing_reason": f"Event type '{event_type}' matches routing rule"
    }


# Connect to specialist agents via A2A
# When new specialists are registered, the mesh self-organizes
remote_billing = RemoteA2aAgent(url="http://localhost:8051")
remote_support = RemoteA2aAgent(url="http://localhost:8052")
remote_vip = RemoteA2aAgent(url="http://localhost:8053")

router_agent = Agent(
    name="event_router_agent",
    model="gemini-2.0-flash",
    description="Routes events from the ambient event mesh to specialist agents.",
    instruction=(
        "You are the Event Router for the Ambient Event Mesh. "
        "When you receive an event:\n"
        "1. Use classify_event to determine routing\n"
        "2. Delegate to the appropriate specialist agent\n"
        "3. Report the event_id, routing decision, and outcome\n\n"
        "Routing rules:\n"
        "- payment_received → billing_agent\n"
        "- new_support_ticket → technical_support_agent\n"
        "- vip_customer_action → vip_priority_agent\n"
    ),
    tools=[classify_event],
    agents=[remote_billing, remote_support, remote_vip],
)


# ─────────────────────────────────────────────────────────────
# EVENT MESH RUNNER
# Simulates continuous event processing
# ─────────────────────────────────────────────────────────────

async def process_event(runner: Runner, session_id: str, event: dict):
    """Process a single event through the mesh."""
    event_message = (
        f"New event received:\n"
        f"Event ID: {event['event_id']}\n"
        f"Type: {event['event_type']}\n"
        f"Customer: {event['payload']['customer_id']}\n"
        f"Priority: {event['payload']['priority']}\n"
        f"Amount: ${event['payload']['amount']}\n"
        f"Timestamp: {event['timestamp']}\n\n"
        f"Please classify and route this event to the appropriate specialist."
    )

    async for mesh_event in runner.run_async(
        user_id="mesh_processor",
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=event_message)]
        )
    ):
        if mesh_event.is_final_response():
            print(f"\n[{event['event_id']}] {mesh_event.content.parts[0].text[:200]}...")


async def run_demo(num_events: int = 5):
    """
    Simulate the ambient event mesh processing events continuously.

    Args:
        num_events: Number of events to process in the demo
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="pattern_05_demo",
        user_id="mesh_processor"
    )

    runner = Runner(
        agent=router_agent,
        app_name="pattern_05_demo",
        session_service=session_service,
    )

    print(f"\nAmbient Event Mesh — Processing {num_events} events\n")
    print("=" * 60)

    for i in range(num_events):
        event = generate_event()
        print(f"\n[Event {i+1}/{num_events}] Incoming: {event['event_type']} | {event['event_id']}")
        await process_event(runner, session.id, event)

        # Simulate events arriving at intervals
        if i < num_events - 1:
            await asyncio.sleep(1)

    print("\n" + "=" * 60)
    print("Event mesh processing complete.")


if __name__ == "__main__":
    print("Pattern 5: Ambient Event Mesh")
    print("Start specialist agent servers first:")
    print("  python agents/servers.py")
    print()
    asyncio.run(run_demo(num_events=5))
