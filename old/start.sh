#!/bin/bash

# start.sh - Download and serve gemma2:2b using Ollama

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== GemmaJnana Setup ===${NC}\n"

FORCE_RESTART=false

# 1. Check if Ollama CLI is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Error: Ollama is not installed.${NC}"
    echo -e "Please install Ollama first as a prerequisite: https://ollama.com"
    exit 1
fi

# 2. Check and start Ollama server if not running
if ! curl -m 2 -s http://localhost:11434 > /dev/null; then
    echo -e "${YELLOW}Ollama server is not running. Starting Ollama...${NC}"
    if [ -d "/Applications/Ollama.app" ]; then
        open -a Ollama
    else
        ollama serve > /dev/null 2>&1 &
    fi

    echo -n "Waiting for Ollama server to respond"
    for i in {1..15}; do
        if curl -m 2 -s http://localhost:11434 > /dev/null; then
            echo -e "${GREEN} Connected!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
    echo ""
    
    if ! curl -m 2 -s http://localhost:11434 > /dev/null; then
        echo -e "${RED}Failed to start Ollama server. Please start the Ollama application manually.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Ollama server is already running.${NC}"
fi

# 3. Pull the gemma2:2b model
echo -e "\n${YELLOW}Checking if gemma2:2b is available locally...${NC}"
if ! ollama list | grep -q "gemma2:2b"; then
    echo -e "${YELLOW}gemma2:2b not found. Downloading model...${NC}"
    ollama pull gemma2:2b || { echo -e "${RED}Failed to pull model.${NC}"; exit 1; }
    echo -e "${GREEN}Model gemma2:2b downloaded successfully!${NC}"
else
    echo -e "${GREEN}gemma2:2b is already downloaded.${NC}"
fi

# 4. Start the FastAPI Gateway and MCP Servers in the background
if [ -f "app.py" ]; then
    cleanup() {
        echo -e "\n${YELLOW}Shutting down Gateway and MCP Servers...${NC}"
        [ ! -z "$TRAVEL_PID" ] && kill "$TRAVEL_PID" 2>/dev/null
        [ ! -z "$PARTY_PID" ] && kill "$PARTY_PID" 2>/dev/null
        [ ! -z "$FASTAPI_PID" ] && kill "$FASTAPI_PID" 2>/dev/null
        exit 0
    }
    trap cleanup SIGINT SIGTERM EXIT

    # Install Python dependencies if not present
    echo -e "${YELLOW}Checking python dependencies...${NC}"
    python3 -c "import fastapi, uvicorn, ollama, dotenv, mcp, fastmcp" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Installing missing python dependencies from requirements.txt...${NC}"
        python3 -m pip install -r requirements.txt
    else
        echo -e "${GREEN}Python dependencies are up-to-date.${NC}"
    fi

    # Start Travel MCP Server
    echo -e "\n${YELLOW}Starting Travel MCP SSE Server (port 8001)...${NC}"
    python3 mcp_servers/travel/mcp_server_travel.py > /dev/null 2>&1 &
    TRAVEL_PID=$!

    # Start Party MCP Server
    echo -e "\n${YELLOW}Starting Party MCP SSE Server (port 8002)...${NC}"
    python3 mcp_servers/party/mcp_server_party.py > /dev/null 2>&1 &
    PARTY_PID=$!

    echo -e "\n${YELLOW}Starting FastAPI Gateway Server (port 8435)...${NC}"
    python3 app.py > /dev/null 2>&1 &
    FASTAPI_PID=$!
    
    sleep 2
    if ! ps -p $TRAVEL_PID > /dev/null; then
        echo -e "${RED}Error: Travel MCP Server failed to start.${NC}"
    fi
    if ! ps -p $PARTY_PID > /dev/null; then
        echo -e "${RED}Error: Party MCP Server failed to start.${NC}"
    fi
    if ! ps -p $FASTAPI_PID > /dev/null; then
        echo -e "${RED}Error: FastAPI Gateway failed to start.${NC}"
    else
        echo -e "${GREEN}Services are running (Gateway PID: $FASTAPI_PID, Travel PID: $TRAVEL_PID, Party PID: $PARTY_PID).${NC}"
    fi
fi

# 5. Start the lightweight Web Server in the foreground
echo -e "\n${GREEN}=== Setup Complete ===${NC}"
echo -e "Access the Chat Playground at: ${BLUE}http://localhost:8080${NC}"
echo -e "Press Ctrl+C to shut down all servers.\n"

python3 -m http.server 8080
