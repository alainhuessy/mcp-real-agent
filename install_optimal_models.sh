#!/bin/bash

echo "======================================================================"
echo "🚀 Installing Optimal Models for Agent OS v2.1"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if model exists
model_exists() {
    ollama list 2>/dev/null | awk '{print $1}' | grep -q "^$1$"
    return $?
}

# Function to install model
install_model() {
    local model=$1
    local description=$2
    
    if model_exists "$model"; then
        echo -e "${GREEN}✅${NC} Already installed: $model"
        echo "   $description"
    else
        echo -e "${BLUE}⏳${NC} Installing: $model"
        echo "   $description"
        ollama pull "$model"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅${NC} Successfully installed: $model"
        else
            echo -e "${YELLOW}⚠️${NC} Failed to install: $model"
        fi
    fi
    echo ""
}

# Install models in priority order

echo -e "${BLUE}TIER 1: TOOL-USE SPECIALISTS${NC}"
echo "=================================="
install_model "llama3-groq-tool-use:8b" "PRIMARY - Best for tool-calling (MCP Agent)"

echo ""
echo -e "${BLUE}TIER 2: AGENTIC CODING${NC}"
echo "=================================="
install_model "qwen3-coder:30b" "BACKUP - Agentic workflows (if available)"

echo ""
echo -e "${BLUE}TIER 3: ALREADY INSTALLED${NC}"
echo "=================================="
model_exists "qwen2.5-coder:14b" && echo -e "${GREEN}✅${NC} qwen2.5-coder:14b - Quick fallback" || echo -e "${YELLOW}⚠️${NC} qwen2.5-coder:14b - Not found"
model_exists "mistral-nemo:latest" && echo -e "${GREEN}✅${NC} mistral-nemo:latest - Ultra-fast" || echo -e "${YELLOW}⚠️${NC} mistral-nemo:latest - Not found"
model_exists "phi4-mini:latest" && echo -e "${GREEN}✅${NC} phi4-mini:latest - Lightweight" || echo -e "${YELLOW}⚠️${NC} phi4-mini:latest - Not found"

echo ""
echo "======================================================================"
echo "Summary:"
ollama list 2>/dev/null | tail -n +2 | wc -l | xargs echo "Total models installed:"
echo "======================================================================"

