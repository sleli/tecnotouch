#!/bin/bash

# Vue.js PWA Dashboard Startup Script
# Simplified version with only Production and Simulation modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VUE_PROJECT_DIR="frontend-vue"
BACKEND_DIR="backend"
API_PORT=8000
FRONTEND_PORT=3000

echo -e "${BLUE}🚀 Distributore Dashboard - Vue.js PWA${NC}"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i ":$1" >/dev/null 2>&1
}

# Function to kill processes on port
kill_port() {
    local port=$1
    if port_in_use $port; then
        echo -e "${YELLOW}⚠️  Port $port in use, killing existing process...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to clear development cache and rebuild
clear_cache_and_rebuild() {
    echo "🧹 Clearing cache and preparing fresh build..."

    # Clear Vite cache
    if [ -d "$VUE_PROJECT_DIR/node_modules/.vite" ]; then
        rm -rf "$VUE_PROJECT_DIR/node_modules/.vite/"
        echo -e "${GREEN}✅ Vite cache cleared${NC}"
    fi

    # Clear old dist for fresh build
    if [ -d "$VUE_PROJECT_DIR/dist" ]; then
        rm -rf "$VUE_PROJECT_DIR/dist"
        echo -e "${GREEN}✅ Old dist removed${NC}"
    fi

    echo -e "${GREEN}✅ Cache clearing completed${NC}"
}

# Parse command line arguments
API_TARGET=""
COMMAND_LINE_MODE=""

if [ "$1" = "--ip" ] && [ ! -z "$2" ]; then
    API_TARGET="$2"
    COMMAND_LINE_MODE="true"

    if [ "$API_TARGET" = "localhost" ]; then
        MODE=2
        MODE_NAME="Simulation"
    else
        MODE=1
        MODE_NAME="Production"
    fi
elif [ ! -z "$1" ]; then
    echo -e "${RED}❌ Invalid parameter. Only --ip <IP_ADDRESS> is supported.${NC}"
    echo "Usage: $0 [--ip <IP_ADDRESS>]"
    echo "Examples:"
    echo "  $0                          # Interactive menu"
    echo "  $0 --ip 192.168.1.65       # Production mode with default IP"
    echo "  $0 --ip localhost           # Simulation mode"
    echo "  $0 --ip 192.168.1.100      # Production mode with custom IP"
    exit 1
fi

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"

# Always clear cache and rebuild
clear_cache_and_rebuild

# Interactive mode selection if not provided via command line
if [ "$COMMAND_LINE_MODE" != "true" ]; then
    echo ""
    echo "📋 Select mode:"
    echo "1) 🖥️  Production (connect to real vending machine at 192.168.1.65)"
    echo "2) 🧪 Simulation (use local simulator)"
    echo ""
    read -p "Enter choice (1-2): " MODE

    # Set API target based on selection
    if [ "$MODE" = "1" ]; then
        API_TARGET="192.168.1.65"
        MODE_NAME="Production"
        echo -e "${GREEN}🏭 Production Mode Selected${NC}"
        echo "   Target: http://192.168.1.65:1500"
    elif [ "$MODE" = "2" ]; then
        API_TARGET="localhost"
        MODE_NAME="Simulation"
        echo -e "${BLUE}🧪 Simulation Mode Selected${NC}"
        echo "   Target: http://localhost:1500"
    else
        echo -e "${RED}❌ Invalid selection${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}🖥️  Command Line Mode: $MODE_NAME${NC}"
    echo "   Target: http://$API_TARGET:1500"
fi

# Build Vue.js PWA (always build for production)
echo "🏗️  Building Vue.js PWA..."

cd "$VUE_PROJECT_DIR"

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔨 Building production bundle..."
npm run build

cd ..

if [ ! -d "$VUE_PROJECT_DIR/dist" ]; then
    echo -e "${RED}❌ Build failed - dist directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completed${NC}"

# Kill existing processes
kill_port $API_PORT
kill_port $FRONTEND_PORT

if [ "$MODE" = "2" ]; then
    kill_port 1500  # Simulator port
fi

# Start services
echo ""
echo "🚀 Starting services..."

# Start simulator if in simulation mode
if [ "$MODE" = "2" ]; then
    echo "🧪 Starting vending machine simulator..."
    cd simulator
    python3 vending_machine_simulator.py &
    SIMULATOR_PID=$!
    cd ..
    sleep 3
    echo -e "${GREEN}✅ Simulator started (PID: $SIMULATOR_PID)${NC}"
fi

# Start API server
echo "🔗 Starting API server..."
cd "$BACKEND_DIR"
python3 api_server.py --ip "$API_TARGET" --port $API_PORT &
API_PID=$!
cd ..
sleep 2
echo -e "${GREEN}✅ API server started (PID: $API_PID)${NC}"

# Start frontend (always production mode)
echo "🌐 Starting Vue.js frontend..."
cd "$VUE_PROJECT_DIR/dist"
python3 -m http.server $FRONTEND_PORT &
FRONTEND_PID=$!
cd ../..
sleep 2
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Service status
echo ""
echo -e "${GREEN}🎉 System started successfully!${NC}"
echo "=================================="
echo -e "📊 Dashboard:     ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "🔗 API Server:    ${BLUE}http://localhost:$API_PORT${NC}"

if [ "$MODE" = "2" ]; then
    echo -e "🧪 Simulator:     ${BLUE}http://localhost:1500${NC}"
fi

echo -e "⚙️  Mode:          ${YELLOW}$MODE_NAME${NC}"
echo -e "🎯 Target IP:      ${YELLOW}$API_TARGET${NC}"
echo ""
echo "📱 Mobile Access:"
echo "   - Open http://localhost:$FRONTEND_PORT on your phone"
echo "   - Install as PWA by tapping 'Add to Home Screen'"
echo ""
echo "🛑 To stop: Press Ctrl+C"
echo ""

# Create PID file for cleanup
cat > .vue_pids << EOF
API_PID=$API_PID
FRONTEND_PID=$FRONTEND_PID
EOF

if [ "$MODE" = "2" ]; then
    echo "SIMULATOR_PID=$SIMULATOR_PID" >> .vue_pids
fi

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"

    if [ -f .vue_pids ]; then
        source .vue_pids

        [ ! -z "$API_PID" ] && kill $API_PID 2>/dev/null || true
        [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
        [ ! -z "$SIMULATOR_PID" ] && kill $SIMULATOR_PID 2>/dev/null || true

        rm -f .vue_pids
    fi

    # Additional cleanup
    kill_port $API_PORT
    kill_port $FRONTEND_PORT

    if [ "$MODE" = "2" ]; then
        kill_port 1500
    fi

    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

trap cleanup INT TERM

# Wait for processes
wait