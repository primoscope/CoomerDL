#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}CoomerDL Linux Installer${NC}"
echo "========================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed.${NC}"
    exit 1
fi

echo -e "${YELLOW}Checking system dependencies...${NC}"

# Check for apt (Debian/Ubuntu)
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu based system."

    echo "Updating package list..."
    sudo apt-get update -qq

    echo "Installing FFmpeg and core tools..."
    sudo apt-get install -y ffmpeg python3-pip python3-venv git

    # Ask for GUI support
    read -p "Do you want to install Desktop GUI support (requires X11/Wayland)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Tkinter..."
        sudo apt-get install -y python3-tk
    else
        echo "Skipping GUI dependencies. You can run the app in HEADLESS mode."
    fi
else
    echo -e "${YELLOW}Not a Debian/Ubuntu system. Please ensure FFmpeg and Python3-Tk (if using GUI) are installed manually.${NC}"
fi

# Setup Virtual Environment
echo -e "\n${YELLOW}Setting up Python Virtual Environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created venv."
else
    echo "venv already exists."
fi

source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo -e "\n${GREEN}Installation Complete!${NC}"
echo "-----------------------------------"
echo "To run the Desktop App:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "To run the Backend API (Headless):"
echo "  source venv/bin/activate"
echo "  export HEADLESS=true"
echo "  python main.py"
