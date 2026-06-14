# GemmaJnana

![GemmaJnana Banner](./images/linkedin_banner_v5.png)

A local development stack to download, serve, and interact with Google's **Gemma 4 (Effective 4B)** model using **Ollama** and an asynchronous **FastAPI** gateway. The package includes a multi-domain Model Context Protocol (MCP) server structure and a beautiful, fully animated chat playground UI.

---

## Project Architecture Flow

Below is the visual flow of the GemmaJnana local multi-domain architecture.

![Architecture Flow](./images/architecture_flow_v5.png)

### Data Flow Diagram

```mermaid
graph TD
    Client[Browser UI: index.html / Port 8080] -->|1. POST Request with Domain| Backend[FastAPI Gateway: app.py / Port 8435]
    Backend -->|2. Invoke check_and_run_tools| Agent[Agent Dispatcher: agent.py]
    Agent -->|3. Spawn MCP Server Process| MCPServer[MCP Server: mcp_servers/<domain>/mcp_server_<domain>.py / stdio]
    Agent -->|4. Discover Tools via list_tools| MCPServer
    Agent -->|5. Tool-calling Query| Ollama[Ollama Server / Port 11434]
    Ollama -->|6. Requested Tool Calls| Agent
    Agent -->|7a. Execute Tools via call_tool| MCPServer
    MCPServer -->|7b. Execute Domain Handlers| Tools[Domain Tools Submodule]
    Tools -->|7c. Return Result JSON| MCPServer
    MCPServer -->|7d. Tool Output JSON| Agent
    Agent -->|7e. Yield Live Trace Events| Backend
    Backend -->|7f. Stream Live Status Cards & Tracer JSON| Client
    Agent -->|8a. Return Aggregated Tool Results| Backend
    Agent -->|8b. Clean Up MCP Server Subprocess| MCPServer
    Backend -->|9. Final Inference Query| Ollama
    Ollama -->|10. Response Stream| Backend
    Backend -->|11. Stream SSE Chat Chunks| Client
    Ollama -.->|Load Model| Model[(Google Gemma 4 Model: gemma4:e4b)]
```

### Dynamic Agentic Pipeline Flow

```mermaid
sequenceDiagram
    autonumber
    participant Client as "Browser Client"
    participant App as "app.py"
    participant Agent as "agent.py"
    participant Ollama as "Ollama Service"
    participant MCPServer as "MCP Server (mcp_servers/<domain>/mcp_server_*.py)"

    Client->>App: POST /chat/stream with history & domain
    App->>Agent: check_and_run_tools(messages, model, domain)
    Note over Agent: Spawns domain-specific MCP Server Subprocess
    Agent->>MCPServer: list_tools()
    MCPServer-->>Agent: Returns active domain tools
    
    loop ReAct Multi-Step Loop (up to 8 turns)
        Agent->>Ollama: [LLM Call] ollama.chat with history + tool context
        Ollama-->>Agent: Returns tool_calls (or empty if finished)
        break If no more tool calls
            Note over Agent: Exit Loop
        end
        Agent-->>App: Yield status event (Spawning/Reasoning/Thought)
        App-->>Client: Stream SSE trace update (UI Pulsing/Thought card)
        Agent->>MCPServer: call_tool(name, arguments)
        MCPServer-->>Agent: Returns tool results (JSON string)
        Agent-->>App: Yield status event (Tool execution result)
        App-->>Client: Stream SSE trace update (UI tool result card)
        Note over Agent: Append tool results to message context
    end
    
    Agent-->>App: Returns aggregated tool messages, results, and LLM call counts
    Note over Agent: Cleans up MCP Server Subprocess
    App->>Ollama: [LLM Call] Stream final chat response (with complete tool context)
    Ollama-->>App: Stream response chunks
    App-->>Client: Stream SSE chat chunks
```

---

## Domain Architecture Overview

GemmaJnana is structured as a multi-domain agentic framework supporting two fully featured planning assistant types. You can toggle between domains dynamically via the UI settings bar:

### 1. Vacation Travel Planner (`mcp_servers/travel/`)
Equips the agent with 7 tools to search flight/hotel inventory, make bookings, rent vehicles, schedule tourist attractions, and compile final formatted itinerary documents:
*   `search_flights(origin, destination, date)`
*   `book_flight(flight_id)`
*   `search_hotels(city, budget)`
*   `book_hotel(hotel_name, nights)`
*   `rent_car(city, car_type)`
*   `book_attraction(city, activity)`
*   `generate_travel_itinerary(bookings)`

#### Predefined Travel Skills (JSON pipelines under `skills/`):
*   **Full Vacation Planner Pipeline:** `search_flights` ➔ `book_flight` ➔ `search_hotels` ➔ `book_hotel` ➔ `generate_travel_itinerary`
*   **Quick Flight Booking Pipeline:** `search_flights` ➔ `book_flight` ➔ `generate_travel_itinerary`
*   **Accommodation & Ground Services Pipeline:** `search_hotels` ➔ `book_hotel` ➔ `rent_car` ➔ `book_attraction`

---

### 2. Birthday Party Planner (`mcp_servers/party/`)
Equips the AI assistant to manage invitations, budget estimations, venue scheduling, cake ordering, entertainment hiring, theme decorations, and reminders:
*   `invite_guests(guest_names)`
*   `budget_expenses(rsvp_count)`
*   `book_venue(venue_name, guest_count)`
*   `order_cake(flavor, size, inscription)`
*   `hire_entertainment(type)`
*   `buy_decorations(theme)`
*   `send_reminders(guest_emails, location)`

#### Predefined Party Skills (JSON pipelines under `skills/`):
*   **Core Event Planning Sequence:** `invite_guests` ➔ `budget_expenses` ➔ `book_venue` ➔ `order_cake` ➔ `send_reminders`
*   **Invitation & Budget Setup:** `invite_guests` ➔ `budget_expenses` ➔ `send_reminders`
*   **Logistics & Theme Purchasing:** `book_venue` ➔ `order_cake` ➔ `hire_entertainment` ➔ `buy_decorations`

---

## File Structure

```text
ollama-gemma-agents-mcp-skills/
├── mcp_servers/                 <-- Multi-domain MCP Servers
│   ├── travel/                  <-- Vacation Travel Planner Domain
│   │   ├── skills/              (JSON Skill pipelines)
│   │   ├── tools/               (Tool implementations & schemas)
│   │   └── mcp_server_travel.py (FastMCP Server process)
│   └── party/                   <-- Birthday Party Planner Domain
│       ├── skills/              (JSON Skill pipelines)
│       ├── tools/               (Tool implementations & schemas)
│       └── mcp_server_party.py  (FastMCP Server process)
├── tests/                       <-- Complete Unit Test Suite
│   ├── test_handlers.py         (Validates all 14 tool handlers)
│   ├── test_mcp.py              (Verifies tool registrations)
│   └── test_skills.py           (Validates JSON sequence formats)
├── agent.py                     (Asynchronous agent orchestrator & ReAct runner)
├── app.py                       (FastAPI Gateway & SSE event streams)
├── index.html                   (Beautiful dark-mode chat playground client)
├── logger.py                    (Global session logger)
├── start.sh                     (Automation installer & launcher)
└── stop.sh                      (Automation teardown script)
```

---

## Prerequisites

To run this application, make sure you have:
1.  **macOS** (the automated installer `start.sh` assumes Mac context).
2.  **Python 3.x** with dependencies listed in `requirements.txt`:
    ```bash
    pip install fastapi uvicorn ollama mcp fastmcp python-dotenv
    ```

---

## How to Run

1.  **Start the entire service stack**:
    ```bash
    ./start.sh
    ```
    This script automatically updates Ollama, pulls the `gemma4:e4b` model, installs required dependencies, runs the backend API Gateway (port `8435`), and spins up a local web server (port `8080`).

2.  **Open the Web Playground**:
    Navigate to [**`http://localhost:8080`**](http://localhost:8080) in your browser. Toggle between **Vacation Travel Planner** and **Birthday Party Planner** domains dynamically using the selector in the upper right.

3.  **Shut down servers gracefully**:
    Press `Ctrl+C` in your terminal, or to guarantee all background processes (FastAPI, Ollama) exit cleanly, run:
    ```bash
    ./stop.sh
    ```

---

## Running Unit Tests

We maintain a rigorous test suite validating the registry, schemas, and execution responses of all tool handlers:
```bash
python3 -m unittest discover -s tests
```

---

## API Reference

The backend FastAPI gateway runs at `http://127.0.0.1:8435`:
*   `GET /health`: Diagnoses model presence and connection status.
*   `GET /tools?domain=...`: Lists active tools dynamically registered by FastMCP for the specified domain.
*   `GET /skills?domain=...`: Retrieves predefined JSON skill pipelines for the specified domain.
*   `POST /chat`: Simple non-streaming message response endpoint.
*   `POST /chat/stream`: Initiates an SSE text stream event channel, sending live tracer cards for active tools.
