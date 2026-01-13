#!/bin/bash
# Installation script for gcs-public-share Gemini CLI extension

set -e

EXTENSION_NAME="gcs-public-share"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_SOURCE="$(dirname "$SCRIPT_DIR")"

echo "Installing $EXTENSION_NAME Gemini CLI extension..."
echo ""

# Check if Python 3.10+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "Python version: $PYTHON_VERSION"

# Check if gcloud is installed
if command -v gcloud &> /dev/null; then
    echo "Google Cloud SDK: installed"
else
    echo ""
    echo "Warning: Google Cloud SDK (gcloud) is not installed."
    echo "You will need to install it for authentication."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    echo ""
fi

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "Package manager: uv"
    echo ""
    echo "Installing Python dependencies with uv..."
    cd "$EXTENSION_SOURCE"
    uv sync
else
    echo "Package manager: pip"
    echo ""
    echo "Installing Python dependencies with pip..."
    cd "$EXTENSION_SOURCE"
    python3 -m pip install -r requirements.txt
fi

echo ""
echo "============================================"
echo "Installation complete!"
echo "============================================"
echo ""
echo "To use this extension with Gemini CLI, run:"
echo ""
echo "  gemini extensions link $EXTENSION_SOURCE"
echo ""
echo "Before using, authenticate with Google Cloud:"
echo ""
echo "  gcloud auth login"
echo "  gcloud auth application-default login"
echo ""
echo "Then restart Gemini CLI and try commands like:"
echo "  'Share this file publicly'"
echo "  'Upload document.pdf to my-bucket and make it public'"
echo ""
