#!/bin/bash

# start.sh - Download and serve gemma4:e4b using Ollama

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== GemmaJnana Setup ===${NC}\n"

FORCE_RESTART=false

# 1. Check if Ollama CLI is installed and update if out-of-date
if command -v ollama &> /dev/null; then
    LOCAL_VERSION=$(ollama --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)
else
    LOCAL_VERSION="0.0.0"
fi

echo -e "${YELLOW}Checking Ollama version...${NC}"
LATEST_VERSION=$(curl -m 10 -s https://api.github.com/repos/ollama/ollama/releases/latest | grep '"tag_name":' | cut -d '"' -f 4 | sed 's/^v//' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)

if [ -z "$LATEST_VERSION" ]; then
    echo -e "${RED}Warning: Could not fetch latest version from GitHub. Continuing with local...${NC}"
    [ "$LOCAL_VERSION" = "0.0.0" ] && { echo -e "${RED}Error: Ollama not installed.${NC}"; exit 1; }
else
    python3 -c "import sys, re; p=lambda v: [int(x) for x in re.findall(r'\d+', v)]; sys.exit(0 if p(sys.argv[1]) >= p(sys.argv[2]) else 2)" "$LOCAL_VERSION" "$LATEST_VERSION"
    COMPARE_RESULT=$?
    
    if [ "$LOCAL_VERSION" = "0.0.0" ]; then
        echo -e "${YELLOW}Ollama not installed. Installing version $LATEST_VERSION...${NC}"
    elif [ $COMPARE_RESULT -eq 2 ]; then
        echo -e "${YELLOW}Newer version available (Local: $LOCAL_VERSION, Latest: $LATEST_VERSION). Skipping automatic update to avoid network delays.${NC}"
    else
        echo -e "${GREEN}Ollama is up-to-date (Version: $LOCAL_VERSION).${NC}"
    fi

    if [ "$LOCAL_VERSION" = "0.0.0" ]; then
        TEMP_DIR="./temp_ollama"
        mkdir -p "$TEMP_DIR"
        
        echo -e "${YELLOW}Downloading latest Ollama for macOS...${NC}"
        curl --connect-timeout 10 -L -o "$TEMP_DIR/Ollama-darwin.zip" "https://ollama.com/download/Ollama-darwin.zip"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to download Ollama. Skipping update.${NC}"
            rm -rf "$TEMP_DIR"
            [ "$LOCAL_VERSION" = "0.0.0" ] && exit 1
        else
            echo -e "${YELLOW}Stopping running Ollama instances...${NC}"
            pkill -f "Ollama.app" || true
            pkill -x "ollama" || true
            
            if [ -d "/Applications/Ollama.app" ] && [ ! -w "/Applications/Ollama.app" ]; then
                echo -e "${RED}Error: No write permission to /Applications/Ollama.app.${NC}"
                rm -rf "$TEMP_DIR"
                exit 1
            fi
            
            rm -rf "/Applications/Ollama.app"
            unzip -o -q "$TEMP_DIR/Ollama-darwin.zip" -d "$TEMP_DIR"
            mv "$TEMP_DIR/Ollama.app" "/Applications/Ollama.app"
            rm -rf "$TEMP_DIR"
            
            echo -e "${GREEN}Ollama updated successfully!${NC}"
            FORCE_RESTART=true
        fi
    fi
fi

# 2. Check and start Ollama server
if [ "$FORCE_RESTART" = true ] || ! curl -m 2 -s http://localhost:11434 > /dev/null; then
    if [ "$FORCE_RESTART" = true ]; then
        echo -e "${YELLOW}Restarting Ollama server to apply updates...${NC}"
    else
        echo -e "${YELLOW}Ollama server is not running. Starting server...${NC}"
    fi

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

# 3. Pull the gemma4:e4b model
echo -e "\n${YELLOW}Checking if gemma4:e4b is available locally...${NC}"
if ! ollama list | grep -q "gemma4:e4b"; then
    echo -e "${YELLOW}gemma4:e4b not found. Downloading model...${NC}"
    ollama pull gemma4:e4b || { echo -e "${RED}Failed to pull model.${NC}"; exit 1; }
    echo -e "${GREEN}Model gemma4:e4b downloaded successfully!${NC}"
else
    echo -e "${GREEN}gemma4:e4b is already downloaded.${NC}"
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
    python3 -c "import fastapi, uvicorn, ollama, ddgs, dotenv, mcp, fastmcp" > /dev/null 2>&1
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
