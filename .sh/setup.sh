#!/bin/bash
set -e

echo "=== Gemma Performance Test Setup ==="
echo ""

# Step 1: Update system
echo "[1/5] Updating system packages..."
sudo apt update -y && sudo apt upgrade -y > /dev/null 2>&1
echo "✓ System updated"

# Step 2: Install uv
echo "[2/5] Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
echo "✓ uv installed"

# Step 3: Verify Python 3.12
echo "[3/5] Checking Python 3.12..."
if ! command -v python3.12 &> /dev/null; then
    echo "Installing Python 3.12..."
    sudo apt install -y python3.12 python3.12-venv python3.12-dev > /dev/null 2>&1
fi
python3.12 --version
echo "✓ Python 3.12 available"

# Step 4: Create venv with uv
echo "[4/5] Creating Python environment with uv..."
$HOME/.local/bin/uv venv --python 3.12 .venv
source .venv/bin/activate
echo "✓ Virtual environment created"

# Step 5: Install dependencies
echo "[5/5] Installing dependencies..."
uv pip install vllm transformers torch pydantic python-dotenv psutil tqdm
echo "✓ Dependencies installed"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To verify installation:"
echo "  python -c 'import vllm, transformers; print(\"✓ All dependencies loaded\")'}"
echo ""
