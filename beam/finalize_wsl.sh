#!/bin/bash
# Finalize beam installation in WSL
# Run this in Ubuntu WSL: bash finalize_wsl.sh

BEAM_DIR="/mnt/c/Users/LDT/frappe/beam"
BEAM_BIN="$BEAM_DIR/.venv/bin"

# Add to PATH if not already there
if ! grep -q "$BEAM_BIN" ~/.bashrc 2>/dev/null; then
    echo "export PATH=\"\$PATH:$BEAM_BIN\"" >> ~/.bashrc
    echo "✅ Added beam to PATH in ~/.bashrc"
else
    echo "✅ Beam already in PATH"
fi

# Test beam
export PATH="$PATH:$BEAM_BIN"
echo ""
echo "Testing beam..."
beam --version

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To use beam from PowerShell:"
echo "  1. Close this WSL terminal"
echo "  2. Run: beam --version (in PowerShell)"
echo ""
echo "Beam will automatically use WSL when you run commands from PowerShell."

