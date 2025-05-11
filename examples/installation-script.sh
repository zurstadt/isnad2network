#!/bin/bash
# Installation script for isnad2network

# Exit on any error
set -e

# Print colored messages
function print_heading() {
    echo -e "\n\033[1;34m==== $1 ====\033[0m"
}

function print_success() {
    echo -e "\033[1;32m✓ $1\033[0m"
}

function print_error() {
    echo -e "\033[1;31m✗ $1\033[0m"
}

function print_info() {
    echo -e "\033[1;33m→ $1\033[0m"
}

# Header
print_heading "Isnad2Network Installation Script"
print_info "This script will install the isnad2network package and its dependencies."

# Check if we're in the right directory
if [ ! -d "src" ] || [ ! -f "setup.py" ]; then
    print_error "Please run this script from the root directory of the isnad2network project."
    exit 1
fi

# Check for Python
print_heading "Checking Python"
if command -v python3 &>/dev/null; then
    PYTHON="python3"
    print_success "Python 3 found"
else
    if command -v python &>/dev/null; then
        PYTHON="python"
        # Check if it's Python 3
        PY_VERSION=$($PYTHON --version 2>&1)
        if [[ $PY_VERSION == Python\ 3* ]]; then
            print_success "Python 3 found ($PY_VERSION)"
        else
            print_error "Python 3 is required, but $PY_VERSION was found."
            print_info "Please install Python 3 and try again."
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3 and try again."
        exit 1
    fi
fi

# Check pip
print_heading "Checking pip"
if command -v pip3 &>/dev/null; then
    PIP="pip3"
    print_success "pip3 found"
elif command -v pip &>/dev/null; then
    PIP="pip"
    print_success "pip found"
else
    print_error "pip not found. Attempting to install pip..."
    $PYTHON -m ensurepip --upgrade || {
        print_error "Failed to install pip. Please install pip manually and try again."
        exit 1
    }
    PIP="pip"
    print_success "pip installed"
fi

# Create virtual environment (optional)
print_heading "Virtual Environment"
read -p "Do you want to create a virtual environment? (recommended) [Y/n]: " CREATE_VENV
CREATE_VENV=${CREATE_VENV:-Y}
if [[ $CREATE_VENV =~ ^[Yy]$ ]]; then
    print_info "Installing virtualenv..."
    $PIP install --user virtualenv
    
    print_info "Creating virtual environment..."
    $PYTHON -m virtualenv venv || {
        print_error "Failed to create virtual environment. Continuing with system Python."
    }
    
    if [ -d "venv" ]; then
        print_success "Virtual environment created."
        print_info "Activating virtual environment..."
        source venv/bin/activate || {
            print_error "Failed to activate virtual environment. Please activate it manually."
            print_info "Run: source venv/bin/activate"
        }
    fi
else
    print_info "Skipping virtual environment creation."
fi

# Install dependencies
print_heading "Installing Dependencies"
$PIP install -r requirements.txt || {
    print_error "Failed to install dependencies. Please check requirements.txt and try again."
    exit 1
}
print_success "Dependencies installed."

# Install the package
print_heading "Installing Isnad2Network"
$PIP install -e . || {
    print_error "Failed to install isnad2network. Please check for errors and try again."
    exit 1
}
print_success "Isnad2Network installed in development mode."

# Test the installation
print_heading "Testing Installation"
if command -v isnad2network &>/dev/null; then
    print_success "isnad2network command is available."
    isnad2network --help | head -n 1
else
    print_error "isnad2network command not found. Installation may be incomplete."
    print_info "You can still use the package with 'python -m isnad2network' or by running the scripts directly."
fi

# Final message
print_heading "Installation Complete"
print_info "You can now use isnad2network to process isnad data."
print_info "Example usage:"
print_info "  isnad2network --help"
print_info "  python -m isnad2network --help"
print_info "  python examples/basic_pipeline.py"

if [ -d "venv" ]; then
    print_info "Note: Remember to activate the virtual environment with 'source venv/bin/activate' when using the package."
fi

print_success "Thank you for installing Isnad2Network!"
