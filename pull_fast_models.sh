#!/bin/bash
# ============================================================================
# pull_fast_models.sh
# Laden NUR schnelle, leichte Modelle
# Nutze wenn du schnelle Ergebnisse bevorzugst
# ============================================================================

set -e

echo "⚡ FAST-Tier Models Download (RTX 3090 - schnelle Iteration)"
echo "============================================================================"
echo ""
echo "📊 Modelle für schnelle Tests:"
echo "  1. mistral-nemo:latest ........... 7.1 GB (Super schnell, noch gut)"
echo "  2. phi4-mini:latest ............. 2.5 GB (Extrem schnell, leicht)"
echo "  3. neural-chat:latest ........... 4.1 GB (Chat-optimiert, schnell)"
echo ""
echo "✅ Vorteile:"
echo "  - Klein (2-7 GB)"
echo "  - Sehr schnelle Inference (1-3 Sek)"
echo "  - Gut für iteratives Arbeiten"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_model() {
    local model=$1
    if ollama list | grep -q "$model"; then
        echo -e "${GREEN}✅ $model bereits vorhanden${NC}"
        return 0
    else
        return 1
    fi
}

pull_model() {
    local model=$1
    local size=$2
    local desc=$3
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[PULLING] $desc${NC}"
    echo "Model: $model (Size: ~$size GB)"
    echo "⏱️ Download sollte schnell gehen (10-20 Minuten)"
    echo ""
    
    ollama pull "$model"
    
    echo -e "${GREEN}✅ $desc loaded!${NC}"
    echo ""
}

# Start
echo "🔄 Prüfe verfügbare Modelle..."
echo ""

# 1. Mistral Nemo (schnell + gut)
echo -e "${YELLOW}[1/3]${NC} Mistral Nemo 7B (Super schnell aber noch gut)"
if ! check_model "mistral-nemo"; then
    pull_model "mistral-nemo:latest" "7.1" "Mistral Nemo 7B"
else
    echo ""
fi

# 2. Phi Mini (extrem schnell)
echo -e "${YELLOW}[2/3]${NC} Phi Mini (Extrem schnell, leicht)"
if ! check_model "phi4-mini"; then
    pull_model "phi4-mini:latest" "2.5" "Phi4-Mini"
else
    echo ""
fi

# 3. Neural Chat (chat-optimiert)
echo -e "${YELLOW}[3/3]${NC} Neural Chat (Chat-optimiert + schnell)"
if ! check_model "neural-chat"; then
    pull_model "neural-chat:latest" "4.1" "Neural-Chat"
else
    echo ""
fi

echo ""
echo "============================================================================"
echo -e "${GREEN}✅ Fast-Tier Models geladen!${NC}"
echo ""
echo "⚡ Performance Sie Erwarten:"
echo "  - mistral-nemo:7b ......... ~1-2 Sek/Response (noch decent)"
echo "  - phi4-mini ............... ~0.5-1 Sek/Response (extrem schnell!)"
echo "  - neural-chat ............. ~1-2 Sek/Response (gut für chat)"
echo ""
echo "🚀 Zum Testen in Continue:"
echo "  1. Uncomment FAST-Tier Models in config-top-tier.yaml"
echo "  2. Nutze mistral-nemo für erste Tests"
echo "  3. Phi4-mini für Tab-Autocomplete"
echo ""
echo "💡 Wann nutzen:"
echo "  - Schnelle Codegen? → mistral-nemo"
echo "  - Tab-Autocomplete? → phi4-mini"
echo "  - Allgemein Chat? → neural-chat"
echo ""
