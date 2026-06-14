#!/bin/bash

# stop.sh - Terminate Ollama, FastAPI gateway, and the lightweight web server

# Color codes for clean output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Stopping GemmaJnana Stack ===${NC}\n"

# 1. Stop Python lightweight HTTP server
echo -e "${YELLOW}Stopping lightweight HTTP Web Server (port 8080)...${NC}"
pkill -f "http.server 8080" && echo -e "${GREEN}Web server stopped.${NC}" || echo -e "Web server was not running."

# 2. Stop FastAPI API Gateway
echo -e "${YELLOW}Stopping FastAPI Gateway (port 8435)...${NC}"
pkill -f "app.py" && echo -e "${GREEN}FastAPI Gateway stopped.${NC}" || echo -e "FastAPI Gateway was not running."

# 3. Stop Ollama
echo -e "${YELLOW}Stopping Ollama application and background daemon...${NC}"
pkill -f "Ollama.app" || true
pkill -x "ollama" || true
echo -e "${GREEN}Ollama processes stopped.${NC}"

echo -e "\n${GREEN}=== All Services Stopped Successfully ===${NC}"
