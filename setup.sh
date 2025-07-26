#!/bin/bash
"""
Setup script for Traveller Economics Analysis
============================================

Automated setup and installation script.
"""

set -e  # Exit on any error

echo "Traveller Economics Analysis - Setup Script"
echo "==========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Create virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    else
        print_warning "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
}

# Install dependencies
install_deps() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    
    if [ "$1" = "minimal" ]; then
        print_status "Installing minimal dependencies..."
        pip install requests pandas numpy tqdm
    else
        print_status "Installing all dependencies..."
        pip install -r requirements.txt
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    python3 -c "
from traveller_economics import EconomicCalculator
calc = EconomicCalculator()
print('✓ Core functionality working')
"
    
    if [ "$1" != "minimal" ]; then
        python3 -c "
import matplotlib
import seaborn
import plotly
import scipy
print('✓ All optional dependencies available')
" 2>/dev/null || print_warning "Some optional dependencies may not be available"
    fi
}

# Create necessary directories  
setup_dirs() {
    print_status "Creating directories..."
    mkdir -p cache output
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo
    
    # Parse arguments
    INSTALL_TYPE="full"
    if [ "$1" = "--minimal" ]; then
        INSTALL_TYPE="minimal"
        print_warning "Minimal installation selected (no visualizations)"
    fi
    
    # Check requirements
    if ! check_python; then
        exit 1
    fi
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_deps $INSTALL_TYPE
    
    # Create directories
    setup_dirs
    
    # Test installation
    test_installation $INSTALL_TYPE
    
    echo
    print_status "Setup complete!"
    echo
    echo "Next steps:"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Run a quick test: python3 quick_start.py"
    echo "  3. Run full analysis: python3 run_analysis.py --all"
    echo
    echo "For help: python3 run_analysis.py --help"
    echo
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "Usage: $0 [--minimal]"
        echo
        echo "Options:"
        echo "  --minimal    Install only core dependencies (no visualizations)"
        echo "  --help       Show this help message"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
