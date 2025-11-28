#!/bin/bash
# Installation script for Beam

set -e

echo "Installing Beam CLI..."
echo "======================"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install beam in development mode
echo ""
echo "Installing beam in development mode..."
pip install -e .

# Check if bench is installed
if command -v bench &> /dev/null; then
    echo ""
    echo "✓ Bench is already installed"
    bench --version
else
    echo ""
    echo "Installing frappe-bench as dependency..."
    pip install frappe-bench
fi

echo ""
echo "======================"
echo "Installation complete!"
echo ""
echo "Test beam with:"
echo "  beam --version"
echo "  beam --help"
echo ""
echo "See TESTING.md for comprehensive testing instructions."

