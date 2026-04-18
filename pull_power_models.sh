#!/bin/bash
# ============================================================================
# pull_power_models.sh
# Laden NUR die großen Power-Modelle für deine RTX 3090
# Nutze wenn du Zeit hast und beste Qualität brauchst
# ============================================================================

set -e

echo "💪 POWER-Tier Models Download (RTX 3090 + CPU-offload)"
echo "============================================================================"
echo ""
echo "📊 Modelle für dieses Script:"
echo "  1. qwen3-coder-next:latest ........ 51 GB (Multi-File Agent Expert)"
echo "  2. nemotron-cascade-2:latest ...... 24 GB (MoE Reasoning)"
echo "  3. glm-5.1:latest ................ ? GB (Neue SOTA - wenn verfügbar)"
echo ""
echo "⚠️ WARNUNG:"
echo "  - Großer Download (~80+ GB)"
echo "  - Benötigt CPU-offload"
echo "  - Inference wird langsamer (aber besser!)"
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Prüfe ob Modelle schon da sind
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
    echo "⏱️ Dieser Download kann 30-60 Minuten dauern..."
    echo ""
    
    ollama pull "$model"
    
    echo -e "${GREEN}✅ $desc loaded!${NC}"
    echo ""
}

# Start
echo "🔄 Prüfe verfügbare Modelle..."
echo ""

# 1. Qwen3-Coder-Next (POWER AGENT)
echo -e "${YELLOW}[1/3]${NC} Qwen3-Coder-Next 51B (Multi-File Agent)"
if ! check_model "qwen3-coder-next"; then
    read -p "⚠️ Download 51GB. Fortfahren? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        pull_model "qwen3-coder-next:latest" "51" "Qwen3-Coder-Next 51B"
    else
        echo "⏭️ Übersprungen"
    fi
else
    echo ""
fi

# 2. Nemotron Cascade-2 (MoE Reasoning)
echo -e "${YELLOW}[2/3]${NC} Nemotron Cascade-2 30B (MoE + Reasoning)"
if ! check_model "nemotron-cascade-2"; then
    pull_model "nemotron-cascade-2:latest" "24" "Nemotron Cascade-2 30B"
else
    echo ""
fi

# 3. GLM-5.1 (NEW)
echo -e "${YELLOW}[3/3]${NC} GLM-5.1 (Neue Agentic Engineering Model)"
echo "⏳ Prüfe Verfügbarkeit..."
if ! check_model "glm-5.1"; then
    if ollama pull glm-5.1:latest 2>&1 | grep -q "not found\|No such file"; then
        echo -e "${YELLOW}ℹ️ GLM-5.1 noch nicht verfügbar auf ollama.com${NC}"
        echo "   Versuche später: ollama pull glm-5.1:latest"
    else
        pull_model "glm-5.1:latest" "?" "GLM-5.1"
    fi
else
    echo ""
fi

echo ""
echo "============================================================================"
echo -e "${GREEN}✅ Power-Tier Models geladen!${NC}"
echo ""
echo "💻 CPU-Offload Konfiguration (für .bashrc oder Terminal):"
echo ""
echo "  # Aktiviere CPU-Offload für große Modelle:"
echo "  export OLLAMA_GPU_MEMORY=16384    # 16GB auf GPU"
echo "  export OLLAMA_NUM_THREAD=16       # 16 CPU-Threads"
echo ""
echo "  # Starte Ollama neu:"
echo "  pkill ollama"
echo "  sleep 2"
echo "  ollama serve"
echo ""
echo "🚀 Zum Testen in .continue/agents/config.yaml:"
echo "  1. Uncomment die POWER-Tier Models"
echo "  2. Reload Continue"
echo "  3. Nutze die neuen Modelle mit Continue Chat"
echo ""
echo "📊 Performance:"
echo "  - devstral-small-2:24b ... ~2-5 Sek/Response (aktuell)"
echo "  - qwen3-coder-next ....... ~30-60 Sek/Response (aber besser!)"
echo "  - nemotron-cascade-2 .... ~20-40 Sek/Response (gutes Reasoning)"
echo ""
echo "💡 Empfehlung: Teste einzelne Modelle und messe Qualität vs. Speed"
echo ""
