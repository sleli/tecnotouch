# Dashboard Distributore - Startup Script for Windows
# PowerShell equivalent of start.sh

param(
    [string]$ip = $null
)

$ErrorActionPreference = "Stop"

# Determina la directory del progetto (parent di scripts/)
$ProjectPath = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectPath

# Load environment variables from .env if exists
$envFile = Join-Path $ProjectPath ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Colors for output
function Write-Header { Write-Host $args[0] -ForegroundColor Cyan }
function Write-Success { Write-Host $args[0] -ForegroundColor Green }
function Write-Warning { Write-Host $args[0] -ForegroundColor Yellow }
function Write-Error { Write-Host $args[0] -ForegroundColor Red }
function Write-Info { Write-Host $args[0] -ForegroundColor Blue }

# Configuration (with fallback to defaults if env vars not set)
$VUE_PROJECT_DIR = "frontend-vue"
$BACKEND_DIR = "backend"
$SIMULATOR_DIR = "simulator"
$API_PORT = if ($env:API_PORT) { $env:API_PORT } else { 8000 }
$FRONTEND_PORT = if ($env:FRONTEND_PORT) { $env:FRONTEND_PORT } else { 3000 }
$DISTRIBUTOR_IP = $env:DISTRIBUTOR_IP

Write-Header "🚀 Distributore Dashboard - Vue.js PWA"
Write-Host "==================================`n"

# Function to check if command exists
function Test-CommandExists {
    param($Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Function to check if port is in use
function Test-PortInUse {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Function to kill processes on port
function Stop-ProcessOnPort {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Warning "⚠️  Port $Port in use, killing existing process..."
        foreach ($conn in $connections) {
            try {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            } catch {}
        }
        Start-Sleep -Seconds 2
    }
}

# Function to clear development cache and rebuild
function Clear-CacheAndRebuild {
    Write-Host "🧹 Clearing cache and preparing fresh build...`n"

    # Clear Vite cache
    $viteCachePath = Join-Path $VUE_PROJECT_DIR "node_modules\.vite"
    if (Test-Path $viteCachePath) {
        Remove-Item -Path $viteCachePath -Recurse -Force
        Write-Success "✅ Vite cache cleared"
    }

    # Clear old dist for fresh build
    $distPath = Join-Path $VUE_PROJECT_DIR "dist"
    if (Test-Path $distPath) {
        Remove-Item -Path $distPath -Recurse -Force
        Write-Success "✅ Old dist removed"
    }

    Write-Success "✅ Cache clearing completed`n"
}

# Parse command line arguments
$API_TARGET = $null
$MODE = $null
$MODE_NAME = $null

if ($ip) {
    $API_TARGET = $ip

    if ($API_TARGET -eq "localhost" -or $API_TARGET -eq "127.0.0.1") {
        $MODE = 2
        $MODE_NAME = "Simulation"
    } else {
        $MODE = 1
        $MODE_NAME = "Production"
    }
}

# Check prerequisites
Write-Host "🔍 Checking prerequisites...`n"

if (-not (Test-CommandExists python)) {
    Write-Error "❌ Python not found. Please install Python 3"
    exit 1
}

if (-not (Test-CommandExists node)) {
    Write-Error "❌ Node.js not found. Please install Node.js"
    exit 1
}

if (-not (Test-CommandExists npm)) {
    Write-Error "❌ npm not found. Please install npm"
    exit 1
}

Write-Success "✅ Prerequisites OK`n"

# Always clear cache and rebuild
Clear-CacheAndRebuild

# Interactive mode selection if not provided via command line
if (-not $MODE) {
    Write-Host "📋 Select mode:"
    Write-Host "1) 🖥️  Production (connect to real vending machine at $DISTRIBUTOR_IP)"
    Write-Host "2) 🧪 Simulation (use local simulator)`n"

    $selection = Read-Host "Enter choice (1-2)"

    if ($selection -eq "1") {
        $API_TARGET = $DISTRIBUTOR_IP
        $MODE = 1
        $MODE_NAME = "Production"
        Write-Success "🏭 Production Mode Selected"
        Write-Host "   Target: http://${API_TARGET}:1500`n"
    } elseif ($selection -eq "2") {
        $API_TARGET = "localhost"
        $MODE = 2
        $MODE_NAME = "Simulation"
        Write-Info "🧪 Simulation Mode Selected"
        Write-Host "   Target: http://localhost:1500`n"
    } else {
        Write-Error "❌ Invalid selection"
        exit 1
    }
} else {
    Write-Success "🖥️  Command Line Mode: $MODE_NAME"
    Write-Host "   Target: http://${API_TARGET}:1500`n"
}

# Build Vue.js PWA
Write-Host "🏗️  Building Vue.js PWA...`n"

Set-Location $VUE_PROJECT_DIR

if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies...`n"
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ npm install failed"
        exit 1
    }
}

Write-Host "🔨 Building production bundle...`n"
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Build failed"
    exit 1
}

Set-Location $ProjectPath

if (-not (Test-Path (Join-Path $VUE_PROJECT_DIR "dist"))) {
    Write-Error "❌ Build failed - dist directory not found"
    exit 1
}

Write-Success "✅ Build completed`n"

# Kill existing processes
Stop-ProcessOnPort $API_PORT
Stop-ProcessOnPort $FRONTEND_PORT

if ($MODE -eq 2) {
    Stop-ProcessOnPort 1500  # Simulator port
}

# Start services
Write-Host "🚀 Starting services...`n"

# Array to track PIDs for cleanup
$global:ProcessPIDs = @()

# Cleanup function
function Stop-AllServices {
    Write-Host "`n"
    Write-Warning "🛑 Shutting down services..."

    foreach ($pid in $global:ProcessPIDs) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        } catch {}
    }

    # Additional cleanup by port
    Stop-ProcessOnPort $API_PORT
    Stop-ProcessOnPort $FRONTEND_PORT

    if ($MODE -eq 2) {
        Stop-ProcessOnPort 1500
    }

    # Remove PID file
    $pidFile = Join-Path $ProjectPath ".vue_pids"
    if (Test-Path $pidFile) {
        Remove-Item $pidFile -Force
    }

    Write-Success "✅ All services stopped"
}

# Register cleanup on exit
try {
    # Start simulator if in simulation mode
    if ($MODE -eq 2) {
        Write-Host "🧪 Starting vending machine simulator...`n"
        $simulatorScript = Join-Path $SIMULATOR_DIR "vending_machine_simulator.py"
        $simulatorProcess = Start-Process python -ArgumentList $simulatorScript -WorkingDirectory $SIMULATOR_DIR -PassThru -NoNewWindow -WindowStyle Hidden
        $global:ProcessPIDs += $simulatorProcess.Id
        Start-Sleep -Seconds 3
        Write-Success "✅ Simulator started (PID: $($simulatorProcess.Id))`n"
    }

    # Start API server
    Write-Host "🔗 Starting API server...`n"
    $apiArgs = @("api_server.py", "--ip", $API_TARGET, "--port", $API_PORT)
    $apiProcess = Start-Process python -ArgumentList $apiArgs -WorkingDirectory $BACKEND_DIR -PassThru -NoNewWindow -WindowStyle Hidden
    $global:ProcessPIDs += $apiProcess.Id
    Start-Sleep -Seconds 2
    Write-Success "✅ API server started (PID: $($apiProcess.Id))`n"

    # Start frontend
    Write-Host "🌐 Starting Vue.js frontend...`n"
    $frontendArgs = @("-m", "http.server", $FRONTEND_PORT)
    $frontendDir = Join-Path $VUE_PROJECT_DIR "dist"
    $frontendProcess = Start-Process python -ArgumentList $frontendArgs -WorkingDirectory $frontendDir -PassThru -NoNewWindow -WindowStyle Hidden
    $global:ProcessPIDs += $frontendProcess.Id
    Start-Sleep -Seconds 2
    Write-Success "✅ Frontend started (PID: $($frontendProcess.Id))`n"

    # Service status
    Write-Host ""
    Write-Success "🎉 System started successfully!"
    Write-Host "=================================="
    Write-Info "📊 Dashboard:     http://localhost:$FRONTEND_PORT"
    Write-Info "🔗 API Server:    http://localhost:$API_PORT"

    if ($MODE -eq 2) {
        Write-Info "🧪 Simulator:     http://localhost:1500"
    }

    Write-Warning "⚙️  Mode:          $MODE_NAME"
    Write-Warning "🎯 Target IP:      $API_TARGET"
    Write-Host ""
    Write-Host "📱 Mobile Access:"
    Write-Host "   - Open http://localhost:$FRONTEND_PORT on your phone"
    Write-Host "   - Install as PWA by tapping 'Add to Home Screen'`n"
    Write-Host "🛑 To stop: Press Ctrl+C`n"

    # Create PID file
    $pidFile = Join-Path $ProjectPath ".vue_pids"
    $global:ProcessPIDs | ForEach-Object { $_ } | Out-File $pidFile

    # Wait indefinitely (until Ctrl+C)
    Write-Host "Press Ctrl+C to stop all services..." -ForegroundColor Gray

    # Keep script running
    while ($true) {
        Start-Sleep -Seconds 1

        # Check if processes are still running
        $allRunning = $true
        foreach ($pid in $global:ProcessPIDs) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if (-not $proc) {
                $allRunning = $false
                break
            }
        }

        if (-not $allRunning) {
            Write-Warning "`n⚠️  One or more services stopped unexpectedly"
            break
        }
    }
} finally {
    # This runs on Ctrl+C or any error
    Stop-AllServices
}
