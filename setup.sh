#!/bin/bash

# DariusAI Setup and Development Script
# This script sets up the development environment and starts both backend and frontend

echo "🤖 Welcome to DariusAI Setup!"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Found $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Found Node.js $NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f ".env" ]; then
        print_status "Creating environment file..."
        cp .env.example .env
        print_warning "Please edit backend/.env with your API keys and configuration"
    fi
    
    cd ..
    print_success "Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Copy environment file
    if [ ! -f ".env" ]; then
        print_status "Creating environment file..."
        cp .env.example .env
    fi
    
    cd ..
    print_success "Frontend setup complete!"
}

# Start development servers
start_dev() {
    print_status "Starting development servers..."
    
    # Start backend
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend
    print_status "Starting frontend server..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    print_success "🚀 DariusAI is starting up!"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/api/docs"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    
    # Wait for user to stop
    trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
}

# Main script
main() {
    echo ""
    print_status "Starting DariusAI setup process..."
    
    # Check prerequisites
    check_python
    check_node
    
    # Setup components
    setup_backend
    setup_frontend
    
    echo ""
    print_success "🎉 Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Edit backend/.env with your OpenAI API key and other settings"
    echo "2. Edit frontend/.env if needed"
    echo "3. Run './start-dev.sh' to start both servers"
    echo ""
    
    # Ask if user wants to start now
    read -p "Do you want to start the development servers now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_dev
    else
        print_status "You can start the servers later by running './start-dev.sh'"
    fi
}

# Run main function
main
