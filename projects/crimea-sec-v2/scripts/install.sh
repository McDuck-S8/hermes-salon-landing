#!/bin/bash
# Crimea Security Framework v2 — Installation Script
# Run from project root: ./scripts/install.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "========================================"
echo "Crimea Security Framework v2 - Installer"
echo "========================================"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.10"
if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION"

# Check/Install uv (fast pip alternative)
echo ""
echo "🔍 Checking uv..."
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo "✅ uv: $(uv --version)"

# Create virtual environment
echo ""
echo "🐍 Creating virtual environment..."
uv venv --python python3 .venv
source .venv/bin/activate

# Install package in development mode
echo ""
echo "📦 Installing Crimea Security Framework..."
uv pip install -e ".[dev,full]"

# Install external security tools
echo ""
echo "🔧 Installing external security tools..."

# Function to check/install tool
install_tool() {
    local tool=$1
    local check_cmd=$2
    local install_cmd=$3
    
    if eval "$check_cmd" &> /dev/null; then
        echo "  ✅ $tool already installed"
    else
        echo "  📦 Installing $tool..."
        eval "$install_cmd"
    fi
}

# OS detection
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt &> /dev/null; then
        PM="apt"
        UPDATE="apt update && apt install -y"
    elif command -v dnf &> /dev/null; then
        PM="dnf"
        UPDATE="dnf install -y"
    elif command -v pacman &> /dev/null; then
        PM="pacman"
        UPDATE="pacman -S --noconfirm"
    else
        PM="unknown"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PM="brew"
    UPDATE="brew install"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash / MSYS2)
    PM="choco"
    UPDATE="choco install -y"
else
    PM="unknown"
fi

echo "  Package manager: $PM"

# Install tools based on OS
case $PM in
    apt)
        install_tool "nmap" "nmap --version" "$UPDATE nmap"
        install_tool "nuclei" "nuclei -version" "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
        install_tool "ffuf" "ffuf -V" "go install -v github.com/ffuf/ffuf/v2@latest"
        install_tool "sqlmap" "sqlmap --version" "$UPDATE sqlmap"
        install_tool "amass" "amass -version" "go install -v github.com/owasp-amass/amass/v4/...@latest"
        install_tool "subfinder" "subfinder -version" "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        install_tool "httpx" "httpx -version" "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
        install_tool "dnsx" "dnsx -version" "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
        install_tool "naabu" "naabu -version" "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
        install_tool "katana" "katana -version" "go install -v github.com/projectdiscovery/katana/cmd/katana@latest"
        ;;
    brew)
        install_tool "nmap" "nmap --version" "$UPDATE nmap"
        install_tool "nuclei" "nuclei -version" "$UPDATE nuclei"
        install_tool "ffuf" "ffuf -V" "$UPDATE ffuf"
        install_tool "sqlmap" "sqlmap --version" "$UPDATE sqlmap"
        install_tool "amass" "amass -version" "$UPDATE amass"
        install_tool "subfinder" "subfinder -version" "$UPDATE subfinder"
        install_tool "httpx" "httpx -version" "$UPDATE httpx"
        install_tool "dnsx" "dnsx -version" "$UPDATE dnsx"
        install_tool "naabu" "naabu -version" "$UPDATE naabu"
        install_tool "katana" "katana -version" "$UPDATE katana"
        ;;
    choco)
        install_tool "nmap" "nmap --version" "$UPDATE nmap"
        install_tool "nuclei" "nuclei -version" "$UPDATE nuclei"
        install_tool "ffuf" "ffuf -V" "$UPDATE ffuf"
        install_tool "sqlmap" "sqlmap --version" "$UPDATE sqlmap"
        # Go tools need Go installed
        if command -v go &> /dev/null; then
            install_tool "amass" "amass -version" "go install -v github.com/owasp-amass/amass/v4/...@latest"
            install_tool "subfinder" "subfinder -version" "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
            install_tool "httpx" "httpx -version" "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
            install_tool "dnsx" "dnsx -version" "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
            install_tool "naabu" "naabu -version" "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
            install_tool "katana" "katana -version" "go install -v github.com/projectdiscovery/katana/cmd/katana@latest"
        else
            echo "  ⚠️  Go not installed - skipping Go-based tools (amass, subfinder, httpx, etc.)"
            echo "     Install Go from https://golang.org/dl/"
        fi
        ;;
    *)
        echo "  ⚠️  Unknown package manager - please install tools manually:"
        echo "     nmap, nuclei, ffuf, sqlmap, amass, subfinder, httpx, dnsx, naabu, katana"
        ;;
esac

# Download SecLists wordlists
echo ""
echo "📚 Setting up wordlists..."
WORDLIST_DIR="$PROJECT_ROOT/data/wordlists"
mkdir -p "$WORDLIST_DIR"

if [[ ! -d "$WORDLIST_DIR/SecLists" ]]; then
    echo "  Downloading SecLists..."
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git "$WORDLIST_DIR/SecLists" 2>/dev/null || \
        echo "  ⚠️  Could not clone SecLists (git not available or network issue)"
else
    echo "  ✅ SecLists already present"
fi

# Create symlinks for common wordlists
mkdir -p "$PROJECT_ROOT/data/wordlists/raft"
if [[ -f "$WORDLIST_DIR/SecLists/Discovery/Web-Content/raft-small-directories.txt" ]]; then
    ln -sf "$WORDLIST_DIR/SecLists/Discovery/Web-Content/raft-small-directories.txt" "$PROJECT_ROOT/data/wordlists/raft/raft-small-directories.txt"
fi
if [[ -f "$WORDLIST_DIR/SecLists/Discovery/Web-Content/raft-medium-directories.txt" ]]; then
    ln -sf "$WORDLIST_DIR/SecLists/Discovery/Web-Content/raft-medium-directories.txt" "$PROJECT_ROOT/data/wordlists/raft/raft-medium-directories.txt"
fi
if [[ -f "$WORDLIST_DIR/SecLists/Discovery/Web-Content/raft-large-directories.txt" ]]; then
    ln -sf "$WORDLIST_DIR/SecLists/Discovery/Web-Content/raft-large-directories.txt" "$PROJECT_ROOT/data/wordlists/raft/raft-large-directories.txt"
fi
if [[ -f "$WORDLIST_DIR/SecLists/Discovery/Web-Content/common.txt" ]]; then
    ln -sf "$WORDLIST_DIR/SecLists/Discovery/Web-Content/common.txt" "$PROJECT_ROOT/data/wordlists/common.txt"
fi

# Download nuclei templates
echo ""
echo "☢️  Setting up Nuclei templates..."
NUCLEI_TEMPLATES_DIR="$HOME/nuclei-templates"
if [[ ! -d "$NUCLEI_TEMPLATES_DIR" ]]; then
    echo "  Downloading nuclei templates..."
    nuclei -update-templates 2>/dev/null || echo "  ⚠️  Could not update templates (run manually: nuclei -update-templates)"
else
    echo "  ✅ Nuclei templates present"
fi

# Initialize knowledge base
echo ""
echo "🧠 Initializing Knowledge Base..."
python3 -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from kb import create_kb
asyncio.run(create_kb())
print('  ✅ Knowledge base initialized')
"

# Create config from examples
echo ""
echo "⚙️  Setting up configuration..."
CONFIG_DIR="$PROJECT_ROOT/config"
for example in "$CONFIG_DIR"/*.example 2>/dev/null; do
    if [[ -f "$example" ]]; then
        target="${example%.example}"
        if [[ ! -f "$target" ]]; then
            cp "$example" "$target"
            echo "  Created: $target"
        fi
    fi
done

# Create .env template
ENV_FILE="$PROJECT_ROOT/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    cat > "$ENV_FILE" << 'EOF'
# Crimea Security Framework v2 - Environment Variables
# Copy to .env and fill in your values

# LLM Providers (at least one required)
OPENROUTER_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
VENICE_API_KEY=

# Local LLM (Ollama)
# OLLAMA_BASE_URL=http://localhost:11434

# Evidence encryption (generate with: python -c "import secrets; print(secrets.token_hex(32))")
EVIDENCE_ENCRYPTION_KEY=

# API Server token (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
CRIMEA_SEC_API_TOKEN=

# OPSEC Profile (silent, balanced, aggressive, apt, redteam)
CRIMEA_SEC_OPSEC_PROFILE=balanced

# Full Arsenal (enables opt-in tools like sqlmap, msfconsole)
# T3MP3ST_FULL_ARSENAL=false

# Debug
# LOG_LEVEL=DEBUG
EOF
    echo "  Created: .env (FILL IN YOUR API KEYS!)"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/evidence"
mkdir -p "$PROJECT_ROOT/reports"
mkdir -p "$PROJECT_ROOT/data/kb"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
source .venv/bin/activate
crimea-sec verify

echo ""
echo "========================================"
echo "✅ Installation complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (OpenRouter, Anthropic, etc.)"
echo "2. Edit config/crimea-targets.yaml - set authorized=true for your scopes"
echo "3. Add Scope Receipts for each authorized target"
echo "4. Run: crimea-sec mission create --name \"Test\" --desc \"Test mission\" --scope crimea-gov-main"
echo "5. Run: crimea-sec mission start <mission_id>"
echo ""
echo "MCP Integration:"
echo "  Add to Claude Desktop / Cursor / VS Code:"
echo "  {"
echo "    \"mcpServers\": {"
echo "      \"crimea-sec\": {"
echo "        \"command\": \"python\","
echo "        \"args\": [\"$(pwd)/src/mcp/server.py\"],"
echo "        \"env\": {"
echo "          \"CRIMEA_SEC_CONFIG\": \"$(pwd)/config/default.yaml\""
echo "        }"
echo "      }"
echo "    }"
echo "  }"
echo ""
echo "Documentation: docs/LEGAL_RU.md (READ BEFORE USE!)"
echo ""