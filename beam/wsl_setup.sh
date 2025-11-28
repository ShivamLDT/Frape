#!/bin/sh
# WSL Setup Script for Beam
# Run this in WSL: sh wsl_setup.sh

set -e

echo "🔧 Setting up Beam in WSL..."
echo ""

# Check if Python is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python3 not found. Installing Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    echo "✅ Python installed"
else
    echo "✅ Python3 found: $(python3 --version)"
fi

# Navigate to beam directory
BEAM_DIR="/mnt/host/c/Users/LDT/frappe/beam"

# Try alternative path if the first doesn't work
if [ ! -d "$BEAM_DIR" ]; then
    BEAM_DIR="/mnt/c/Users/LDT/frappe/beam"
fi

if [ ! -d "$BEAM_DIR" ]; then
    echo "❌ Beam directory not found at expected location"
    echo "   Please navigate to beam directory manually and run:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -e ."
    exit 1
fi

echo "📁 Navigating to: $BEAM_DIR"
cd "$BEAM_DIR"

# Create virtual environment
echo "🔨 Creating virtual environment..."
python3 -m venv .venv

# Activate and install
echo "📦 Installing beam..."
.venv/bin/pip install -e .

# Add to PATH
BEAM_BIN="$BEAM_DIR/.venv/bin"
if ! grep -q "$BEAM_BIN" ~/.bashrc 2>/dev/null; then
    echo "📝 Adding beam to PATH..."
    echo "export PATH=\"\$PATH:$BEAM_BIN\"" >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
else
    echo "✅ Already in PATH"
fi

# Verify installation
echo ""
echo "✅ Installation complete!"
echo ""
echo "Testing beam..."
.venv/bin/beam --version

echo ""
echo "🎉 Beam is ready!"
echo ""
echo "To use beam from PowerShell:"
echo "  1. Close this WSL terminal"
echo "  2. Run: beam --version (in PowerShell)"
echo ""
echo "If beam doesn't work from PowerShell, run:"
echo "  source ~/.bashrc"
echo "  beam --version"

