import os
import sys
import json
import ollama
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv
from contextlib import AsyncExitStack

load_dotenv()

# Ensure local connection works reliably on macOS (avoiding IPv6 resolution issues)
os.environ.setdefault("OLLAMA_HOST", os.getenv("OLLAMA_HOST", "127.0.0.1"))

from logger import log_info, log_error, get_session_log_file

async def get_system_prompt(domain: str = "travel") -> str:
    """
    Load dynamic skills dynamically by connecting to active MCP servers
    and querying the `skills://list` resource.
    """
    skills_list = []
    
    # Resolve target MCP server URLs based on domain parameter
    urls = []
    if domain in ("all", "unified"):
        for key, val in os.environ.items():
            if key.endswith("_MCP_URL") and val:
                urls.append((key.replace("_MCP_URL", "").lower(), val))
    else:
        target_key = f"{domain.upper()}_MCP_URL"
        val = os.getenv(target_key)
        if val:
            urls.append((domain.lower(), val))
            
    # Connect and read resource
    for name, mcp_url in urls:
        try:
            async with sse_client(mcp_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    res = await session.read_resource("skills://list")
                    if res and res.contents:
                        for content in res.contents:
                            if hasattr(content, "text") and content.text:
                                loaded_skills = json.loads(content.text)
                                if isinstance(loaded_skills, list):
                                    skills_list.extend(loaded_skills)
        except Exception:
            # Silently fail or fallback if server is offline
            pass

    skills_instruction = ""
    if skills_list:
        skills_instruction = "Available Skills (Predefined tool sequences):\n"
        for skill in skills_list:
            skills_instruction += (
                f"- **{skill['name']}** (ID: {skill['id']}):\n"
                f"  Description: {skill['description']}\n"
                f"  Strict Sequence: {' -> '.join(skill['sequence'])}\n"
                f"  Instructions: {skill['instructions']}\n\n"
            )
    else:
        skills_instruction = "No skills loaded."

    system_prompt = (
        "You are an expert Unified AI Assistant that orchestrates planning workflows across multiple domains (Vacation Travel and Birthday Party planning) using local tools.\n"
        "Depending on the user's request, dynamically select the appropriate tools and follow any matching predefined skill sequences.\n\n"
        "You have access to 14 tools:\n\n"
        "--- Travel Planning Tools ---\n"
        "1. `search_flights(origin, destination, date)`: Searches flight options and pricing.\n"
        "2. `book_flight(flight_id)`: Reserves a flight ticket and returns a confirmation code.\n"
        "3. `search_hotels(city, budget)`: Finds nearby hotel options and ratings.\n"
        "4. `book_hotel(hotel_name, nights)`: Reserves hotel rooms.\n"
        "5. `rent_car(city, car_type)`: Books a rental car (SUV, sedan, etc.).\n"
        "6. `book_attraction(city, activity)`: Reserves tickets for local tours or attractions.\n"
        "7. `generate_travel_itinerary(bookings)`: Compiles a list of bookings into a formatted itinerary document.\n\n"
        "--- Birthday Party Planning Tools ---\n"
        "8. `invite_guests(guest_names)`: Sends invitations and returns RSVP count.\n"
        "9. `budget_expenses(rsvp_count)`: Estimates venue, food, and decoration costs.\n"
        "10. `book_venue(venue_name, guest_count)`: Reserves the party venue space.\n"
        "11. `order_cake(flavor, size, inscription)`: Orders a custom birthday cake.\n"
        "12. `hire_entertainment(type)`: Books Magician/DJ/Photobooth entertainment.\n"
        "13. `buy_decorations(theme)`: Purchases themed decorations (streamers, balloons).\n"
        "14. `send_reminders(guest_emails, location)`: Sends final reminder messages to guests.\n\n"
        f"{skills_instruction}"
        "CRITICAL EXECUTION RULES:\n"
        "1. When the user requests a pipeline/skill (e.g. Core Event Planning, Invitation & Budget, Flight Booking, Accommodation & Ground, or Full Vacation), you MUST execute the tools in the EXACT sequence specified. Do NOT skip any steps, and do NOT call tools out of order.\n"
        "2. Feed the outputs from previous steps as inputs to subsequent steps (e.g., pass the 'rsvp_count' returned by invite_guests to budget_expenses; pass the flight booking object to generate_travel_itinerary).\n"
        "3. Execute only ONE tool at a time. Wait for the tool result before initiating the next call.\n"
        "4. Once the sequence is finished, write a final summary detailing the success of each tool step and reporting the final travel or event plan."
    )
    return system_prompt

async def get_mcp_tools(domain: str = "travel", session_name: str = "health") -> list:
    """
    Connects to the network MCP server temporarily to retrieve list of active tools.
    Dynamically finds environment variables ending with _MCP_URL.
    """
    urls = []
    if domain in ("all", "unified"):
        for key, val in os.environ.items():
            if key.endswith("_MCP_URL") and val:
                urls.append(val)
    else:
        # Match key like TRAVEL_MCP_URL for domain "travel"
        target_key = f"{domain.upper()}_MCP_URL"
        val = os.getenv(target_key)
        if val:
            urls.append(val)
        
    all_tools = []
    for mcp_url in urls:
        try:
            async with sse_client(mcp_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools_res = await session.list_tools()
                    for t in mcp_tools_res.tools:
                        all_tools.append({
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.inputSchema
                        })
        except Exception as e:
            log_error(session_name, f"Error in get_mcp_tools for URL {mcp_url}: {e}")
            
    return all_tools

async def check_and_run_tools(messages: list, model_name: str, domain: str = "travel", session_name: str = "default"):
    """
    Checks if the model requests any tool calls in a loop (up to 8 steps) to support sequential/multi-step reasoning.
    Dynamically connects to all active servers found in .env matching *_MCP_URL using AsyncExitStack.
    Yields trace events during execution, ending with the final compiled tool result state.
    """
    tool_messages = []
    tool_results = {}
    llm_calls = 0
    current_messages = list(messages)
    
    # Retrieve all active MCP URLs dynamically from environment variables
    urls = []
    for key, val in os.environ.items():
        if key.endswith("_MCP_URL") and val:
            urls.append((key.replace("_MCP_URL", "").lower(), val))
            
    if not urls:
        log_error(session_name, "Error: No MCP URLs configured in environment.")
        yield {"type": "status", "status": "error", "message": "No MCP URLs configured."}
        return
    
    try:
        log_info(session_name, f"Connecting to {len(urls)} active MCP server(s)...")
        yield {"type": "status", "status": "connecting", "message": f"Connecting to {len(urls)} active MCP server(s)..."}
        
        async with AsyncExitStack() as stack:
            sessions = []
            for name, url in urls:
                try:
                    read, write = await stack.enter_async_context(sse_client(url))
                    session = await stack.enter_async_context(ClientSession(read, write))
                    await session.initialize()
                    sessions.append((name, session))
                except Exception as e:
                    log_error(session_name, f"Failed to connect to {name} MCP server at {url}: {e}")
                    
            if not sessions:
                raise ConnectionError("Failed to connect to any of the active MCP servers.")
                
            log_info(session_name, "Initializing dynamic MCP tool discovery...")
            yield {"type": "status", "status": "initializing", "message": "Initializing MCP Client Sessions..."}
            
            # Fetch tools via JSON-RPC list_tools from all servers
            yield {"type": "rpc", "direction": "request", "method": "tools/list", "params": {}}
            
            tool_to_session = {}
            mcp_tools = []
            for name, session in sessions:
                try:
                    tools_res = await session.list_tools()
                    for t in tools_res.tools:
                        tool_to_session[t.name] = session
                        mcp_tools.append(t)
                except Exception as e:
                    log_error(session_name, f"Failed to list tools for {name} MCP: {e}")
            
            tools_list = [
                {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                for t in mcp_tools
            ]
            yield {"type": "rpc", "direction": "response", "method": "tools/list", "result": {"tools": tools_list}}
            yield {"type": "status", "status": "discovered", "tools": tools_list, "message": f"Discovered {len(tools_list)} tool(s) dynamically."}
            
            # Map MCP tools to Ollama tool schema format
            ollama_tools = []
            for tool in mcp_tools:
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            log_info(session_name, f"Discovered {len(ollama_tools)} tool(s) from MCP servers: {[t['function']['name'] for t in ollama_tools]}")
            
            # ReAct Multi-step reasoning loop (up to 8 iterations to support longer sequences)
            for iteration in range(8):
                log_info(session_name, f"[LLM Call] Checking if the model requests any tool calls (iteration {iteration + 1})...")
                llm_calls += 1
                
                # Yield reasoning thought start
                yield {
                    "type": "react_step",
                    "iteration": iteration + 1,
                    "step": "llm",
                    "step_type": "thought",
                    "message": f"LLM Turn {iteration + 1}: Checking model tool requests..."
                }
                
                # Call async ollama chat
                client = ollama.AsyncClient()
                
                yield {
                    "type": "rpc",
                    "direction": "request",
                    "method": "ollama/chat",
                    "params": {
                        "model": model_name,
                        "messages": current_messages + tool_messages,
                        "tools_count": len(ollama_tools)
                    }
                }
                
                response = await client.chat(
                    model=model_name,
                    messages=current_messages + tool_messages,
                    tools=ollama_tools,
                    options={"temperature": 0.0}
                )
                
                tool_calls = getattr(response.message, "tool_calls", None)
                
                # Yield Ollama chat RPC response
                yield {
                    "type": "rpc",
                    "direction": "response",
                    "method": "ollama/chat",
                    "result": {
                        "content": response.message.content or "",
                        "tool_calls": [
                            {"name": c.function.name, "arguments": c.function.arguments}
                            for c in tool_calls
                        ] if tool_calls else []
                    }
                }
                
                if not tool_calls:
                    log_info(session_name, f"No more tool calls requested by the model at iteration {iteration + 1}.")
                    yield {
                        "type": "react_step",
                        "iteration": iteration + 1,
                        "step": "llm",
                        "step_type": "completed",
                        "message": "Model finalized reasoning. Generating final answer..."
                    }
                    break
                    
                log_info(session_name, f"Model requested {len(tool_calls)} tool call(s) at iteration {iteration + 1}: {[c.function.name for c in tool_calls]}")
                
                # Build assistant's tool-calling response structure
                assistant_tool_msg = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments
                            }
                        } for call in tool_calls
                    ]
                }
                tool_messages.append(assistant_tool_msg)
                
                # Execute tool calls via MCP client
                for call in tool_calls:
                    func_name = call.function.name
                    args = call.function.arguments or {}
                    
                    log_info(session_name, f"Executing tool '{func_name}' via MCP with args: {args}")
                    yield {
                        "type": "react_step",
                        "iteration": iteration + 1,
                        "step": "tool",
                        "step_type": "tool_call",
                        "tool_name": func_name,
                        "arguments": args,
                        "message": f"Calling tool '{func_name}'..."
                    }
                    
                    # RPC tool call request
                    yield {
                        "type": "rpc",
                        "direction": "request",
                        "method": "tools/call",
                        "params": {
                            "name": func_name,
                            "arguments": args
                        }
                    }
                    
                    # Route tool call to correct session
                    target_session = tool_to_session.get(func_name)
                    if not target_session:
                        raise ValueError(f"Tool {func_name} not found in active MCP registries.")
                    
                    # Call MCP tool
                    result_block = await target_session.call_tool(func_name, arguments=args)
                    
                    # Extract string response
                    raw_output = ""
                    if result_block.content and len(result_block.content) > 0:
                        raw_output = result_block.content[0].text
                        
                    # Parse JSON results if returned, else store raw string
                    try:
                        result = json.loads(raw_output)
                    except Exception:
                        result = {"content": raw_output}
                        
                    tool_results[func_name] = result
                    
                    # RPC tool call response
                    yield {
                        "type": "rpc",
                        "direction": "response",
                        "method": "tools/call",
                        "result": result
                    }
                    
                    # Yield tool execution result
                    yield {
                        "type": "react_step",
                        "iteration": iteration + 1,
                        "step": "tool",
                        "step_type": "tool_result",
                        "tool_name": func_name,
                        "result": result,
                        "message": f"Tool '{func_name}' finished executing."
                    }
                    
                    # Extract pre-formatted context or fallback to json string
                    if isinstance(result, dict) and "content" in result:
                        content = result["content"]
                    else:
                        content = json.dumps(result)
                        
                    tool_response_msg = {
                        "role": "tool",
                        "name": func_name,
                        "content": content
                    }
                    tool_messages.append(tool_response_msg)
                    log_info(session_name, f"Tool '{func_name}' execution completed successfully.")
                    
    except Exception as e:
        log_error(session_name, f"Error in check_and_run_tools: {e}")
        yield {"type": "status", "status": "error", "message": f"Error: {e}"}
        
    # Yield final results
    yield {
        "type": "result",
        "tool_messages": tool_messages,
        "tool_results": tool_results,
        "llm_calls": llm_calls
    }
