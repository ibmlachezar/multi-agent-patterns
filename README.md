# ♟ Multi-Agent Patterns with A2A and Google ADK

5 production patterns for building multi-agent systems.
Real code. Real Google ADK. Learning in public.

Built while studying the patterns from Google Cloud Next '26.

---

## The 5 patterns

| # | Pattern | What it demonstrates |
|---|---------|---------------------|
| 1 | Agent Card Discovery | Agents discover each other via published Agent Cards |
| 2 | Delegated Specialization | Coordinator delegates to specialist agents across teams |
| 3 | Tool Bridge with MCP | Agents access external tools via Model Context Protocol |
| 4 | Cross-Org Federation | Agents collaborate across organizational boundaries |
| 5 | Ambient Event Mesh | Agents react to event streams continuously |

---

## Quick start — Pattern 1 (5 minutes)

Requirements: Python 3.12+, Google AI Studio API key — free at aistudio.google.com/apikey

1. Clone and install

git clone https://github.com/ibmlachezar/multi-agent-patterns
cd multi-agent-patterns
python -m venv venv
venv\Scripts\activate
pip install google-adk

2. Set your API key

Windows: set GOOGLE_API_KEY=your_key_here
Mac/Linux: export GOOGLE_API_KEY=your_key_here

3. Run the agents

adk web pattern_01_agent_card_discovery\specialist_agents

4. Open http://127.0.0.1:8000 — select an agent and start chatting

---

## What you will see

financial_agent — try: "What is the stock price for GOOGL and generate me a report?"

support_agent — try: "I have an urgent billing issue. My customer ID is C-12345."

Watch the agents call their tools in real time — all powered by Google ADK and Gemini.

---

## Pattern 1: Agent Card Discovery

Every A2A agent publishes a JSON Agent Card at /.well-known/agent.json.
Coordinators discover specialists by fetching their cards — like OpenAPI specs but for agents.

pattern_01_agent_card_discovery/
├── specialist_agents/
│   ├── financial_agent/agent.py   ← stock lookups + financial reports
│   └── support_agent/agent.py     ← ticket creation + status
└── coordinator/agent.py           ← discovers and delegates to both

Key insight: The coordinator never needs to know how specialists work internally.

---

## Pattern 2: Delegated Specialization

Coordinator delegates a multi-step onboarding flow to 5 specialists — different teams, different languages.

Key insight: A2A is language-agnostic. Python, Go, Java — doesn't matter.

---

## Pattern 3: Tool Bridge with MCP

MCP (Model Context Protocol) gives agents access to external tools through one protocol layer.

Key insight: One integration for GitHub, Notion, Stripe, 30+ databases, and more.

---

## Pattern 4: Cross-Org Federation

Two organizations collaborate via A2A while each maintains its own governance and data boundaries.

Key insight: Your gateway controls what you share. Their agents control their side.

---

## Pattern 5: Ambient Event Mesh

Agents listen on event streams and react continuously. Register a new specialist and the mesh self-organizes.

Key insight: Events arrive → router classifies → specialist handles. Fully automatic.

---

## How ADK + A2A works

1. Build an ADK agent with a root_agent variable
2. Run: adk web <folder>
3. ADK serves it and generates an Agent Card at /.well-known/agent.json
4. Other agents connect via RemoteA2aAgent(url="...")
5. Coordinator delegates tasks without knowing internals

---

## What is next

Still learning — updating as I go.

- Pattern 1: Add real live stock API
- Pattern 3: Connect to GitHub MCP server
- Pattern 5: Connect to Google Cloud Pub/Sub
- All patterns: Add observability tracing

---

## Built by

Lachezar Atanasov
Head of AI Product · AI startup founder · Advisor to multiple AI companies
Learning A2A and multi-agent systems in public

lachezaratanasov.com
linkedin.com/in/lachezar-atanasov198

Other open source tools:
github.com/ibmlachezar/ai-product-toolkit
github.com/ibmlachezar/career-ops
github.com/ibmlachezar/ai-interview-coach

---

## References

Google ADK Docs: https://google.github.io/adk-docs/
A2A Protocol: https://google.github.io/adk-docs/a2a/
MCP Tools: https://google.github.io/adk-docs/tools-custom/mcp-tools/

## License

MIT