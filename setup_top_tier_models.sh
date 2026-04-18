#!/bin/bash
# ============================================================================
# setup_top_tier_models.sh
# Laden ALLE Top-Tier Modelle für deine RTX 3090
# ============================================================================

set -e

echo "🚀 Starting Top-Tier Model Setup for RTX 3090..."
echo "============================================================================"
echo ""
echo "📊 Modelle die geladen werden:"
echo "  1. devstral-small-2:24b ............ 15 GB (✅ PRIMARY AGENT)"
echo "  2. qwen2.5-coder:14b .............. 9 GB (⚡ QUICK FALLBACK)"
echo "  3. qwen3-coder-next:latest ........ 51 GB (💪 POWER - mit CPU offload)"
echo "  4. glm-5.1:latest ................. ? GB (🚀 NEW - wenn verfügbar)"
echo "  5. nemotron-cascade-2:latest ...... 24 GB (🧠 MoE REASONING)"
echo ""
echo "⚙️ Dein System:"
echo "  - GPU: RTX 3090 (24GB VRAM)"
echo "  - CPU-Offload: ✅ Verfügbar"
echo ""
echo "💾 Gesamt Download: ~130 GB (mit CPU-offload machbar)"
echo ""

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Hilfsfunktion: Modell laden
pull_model() {
    local model=$1
    local size=$2
    local desc=$3
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[PULLING] $desc${NC}"
    echo -e "Model: $model (Size: ~$size GB)"
    echo ""
    
    ollama pull "$model"
    
    echo -e "${GREEN}✅ $desc loaded!${NC}"
    echo ""
}

# Hilfsfunktion: Modell existiert schon prüfen
check_model() {
    local model=$1
    if ollama list | grep -q "$model"; then
        echo -e "${GREEN}✅ $model bereits vorhanden - skipping${NC}"
        return 0
    else
        return 1
    fi
}

# Start Installation
echo "🔄 Prüfe welche Modelle schon vorhanden sind..."
echo ""

# 1. devstral-small-2:24b (PRIMARY)
echo -e "${YELLOW}1/5${NC} Devstral Small-2 24B (PRIMARY AGENT)"
if ! check_model "devstral-small-2"; then
    pull_model "devstral-small-2:24b" "15" "Devstral Small-2 (AGENT workflows)"
else
    echo ""
fi

# 2. qwen2.5-coder:14b (QUICK)
echo -e "${YELLOW}2/5${NC} Qwen 2.5 Coder 14B (QUICK FALLBACK)"
if ! check_model "qwen2.5-coder"; then
    pull_model "qwen2.5-coder:14b" "9" "Qwen 2.5 Coder (schnell)"
else
    echo ""
fi

# 3. nemotron-cascade-2 (REASONING)
echo -e "${YELLOW}3/5${NC} Nemotron Cascade-2 30B (MoE + REASONING)"
if ! check_model "nemotron-cascade-2"; then
    pull_model "nemotron-cascade-2:latest" "24" "Nemotron Cascade-2 (Reasoning)"
else
    echo ""
fi

# 4. qwen3-coder-next (POWER)
echo -e "${YELLOW}4/5${NC} Qwen3-Coder-Next 51B (POWER AGENT - mit CPU-offload)"
if ! check_model "qwen3-coder-next"; then
    echo -e "${YELLOW}⚠️ WARNING: Dieses Modell ist 51GB!${NC}"
    read -p "Fortfahren? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        pull_model "qwen3-coder-next:latest" "51" "Qwen3-Coder-Next (Power Agent)"
    else
        echo "⏭️ Übersprungen (kannst du später nachladen)"
    fi
else
    echo ""
fi

# 5. glm-5.1 (NEW - optional, wenn verfügbar)
echo -e "${YELLOW}5/5${NC} GLM-5.1 (NEW - Agentic Engineering)"
echo "⏳ Prüfe ob GLM-5.1 verfügbar ist..."
if ollama pull glm-5.1:latest 2>&1 | grep -q "not found\|No such file"; then
    echo -e "${YELLOW}ℹ️ GLM-5.1 noch nicht verfügbar auf ollama.com${NC}"
    echo "   Du kannst es später nachladen mit: ollama pull glm-5.1:latest"
    echo ""
else
    pull_model "glm-5.1:latest" "?" "GLM-5.1 (neue SOTA Agent Model)"
fi

echo ""
echo "============================================================================"
echo -e "${GREEN}✅ Model Setup abgeschlossen!${NC}"
echo ""
echo "📋 Nächste Schritte:"
echo "  1. Continue neustarten: continue dev"
echo "  2. In Continue Settings: Mode: AGENT"
echo "  3. Model: agent (= devstral-small-2:24b)"
echo ""
echo "🚀 Zum Testen verschiedener Modelle:"
echo "  - POWER: Nutze qwen3-coder-next oder nemotron-cascade-2"
echo "  - FAST: Nutze qwen2.5-coder:14b"
echo "  - BALANCED (empfohlen): devstral-small-2:24b"
echo ""
echo "💡 Tipp: Mit RTX 3090 + CPU-offload kannst du auch große Modelle testen!"
echo "   Gutes Reasoning (langsam) > Schnelle Average Ergebnisse"
echo ""
