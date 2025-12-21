#!/bin/bash
# Sistema di Avvio Unificato - Dashboard Distributore Sigarette
# Supporta modalità produzione e simulazione con gestione automatica processi

set -e  # Exit on error

# Configurazione
API_PORT=8000
DASHBOARD_PORT=3000
SIMULATOR_PORT=1500
DISTRIBUTORE_IP="192.168.1.65"

# Variabili globali per tracking processi
SIMULATOR_PID=""
API_PID=""
DASHBOARD_PID=""
LOG_FILE=""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               🚬 SISTEMA DISTRIBUTORE SIGARETTE              ║"
    echo "║                    Dashboard Manager v2.0                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Logging
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        "INFO")  echo -e "${GREEN}[INFO]${NC} $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" ;;
        "DEBUG") echo -e "${CYAN}[DEBUG]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
    esac

    if [[ -n "$LOG_FILE" ]]; then
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    fi
}

# Controlli sistema
check_dependencies() {
    log "INFO" "🔍 Controllo dipendenze sistema..."

    # Controlla Python3
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python3 non trovato. Installare Python 3.x"
        exit 1
    fi

    # Controlla moduli Python
    local missing_modules=()

    if ! python3 -c "import flask" 2>/dev/null; then
        missing_modules+=("flask")
    fi

    if ! python3 -c "import flask_cors" 2>/dev/null; then
        missing_modules+=("flask-cors")
    fi

    if [ ${#missing_modules[@]} -gt 0 ]; then
        log "WARN" "Moduli Python mancanti: ${missing_modules[*]}"
        log "INFO" "Installazione automatica..."

        for module in "${missing_modules[@]}"; do
            log "INFO" "Installando $module..."
            pip3 install "$module" || {
                log "ERROR" "Fallita installazione di $module"
                exit 1
            }
        done
        log "SUCCESS" "Dipendenze installate"
    else
        log "SUCCESS" "Tutte le dipendenze sono soddisfatte"
    fi
}

# Controllo porte
check_ports() {
    local ports=("$@")
    local occupied_ports=()

    for port in "${ports[@]}"; do
        if lsof -i ":$port" >/dev/null 2>&1; then
            occupied_ports+=($port)
        fi
    done

    if [ ${#occupied_ports[@]} -gt 0 ]; then
        log "WARN" "Porte occupate: ${occupied_ports[*]}"
        log "INFO" "Tentativo di terminazione processi..."

        for port in "${occupied_ports[@]}"; do
            local pids=$(lsof -t -i ":$port" 2>/dev/null || true)
            if [[ -n "$pids" ]]; then
                log "INFO" "Terminando processi sulla porta $port: $pids"
                echo "$pids" | xargs kill -TERM 2>/dev/null || true
                sleep 2
                # Force kill se necessario
                echo "$pids" | xargs kill -KILL 2>/dev/null || true
            fi
        done

        sleep 3

        # Ricontrolla
        for port in "${occupied_ports[@]}"; do
            if lsof -i ":$port" >/dev/null 2>&1; then
                log "ERROR" "Impossibile liberare porta $port"
                exit 1
            fi
        done
        log "SUCCESS" "Porte liberate"
    fi
}

# Controllo/inizializzazione database
check_database() {
    log "INFO" "🗄️  Controllo database..."

    if [[ ! -f "sales_data.db" ]]; then
        log "WARN" "Database non trovato"

        # Cerca file eventi per inizializzazione
        local events_files=($(ls events_*_events_only.json 2>/dev/null | head -1))

        if [[ ${#events_files[@]} -gt 0 ]]; then
            log "INFO" "Inizializzazione database con ${events_files[0]}..."
            python3 sales_analyzer.py "${events_files[0]}" --stats || {
                log "ERROR" "Fallita inizializzazione database"
                exit 1
            }
            log "SUCCESS" "Database inizializzato"
        else
            log "WARN" "Nessun file eventi trovato per inizializzazione"
            log "INFO" "Il database sarà creato vuoto"
        fi
    else
        log "SUCCESS" "Database esistente trovato"
    fi
}

# Avvio simulatore
start_simulator() {
    log "INFO" "🔧 Avvio simulatore distributore..."

    if [[ ! -f "simulator/vending_machine_simulator.py" ]]; then
        log "ERROR" "File simulatore non trovato"
        exit 1
    fi

    python3 simulator/vending_machine_simulator.py > /tmp/simulator.log 2>&1 &
    SIMULATOR_PID=$!

    # Attendi che il simulatore sia pronto
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        if curl -s "http://localhost:$SIMULATOR_PORT/login" >/dev/null 2>&1; then
            log "SUCCESS" "Simulatore avviato (PID: $SIMULATOR_PID)"
            return 0
        fi
        sleep 1
        ((attempts++))
    done

    log "ERROR" "Timeout avvio simulatore"
    return 1
}

# Avvio API server
start_api_server() {
    local mode=$1
    local ip=$2

    log "INFO" "🚀 Avvio API server modalità $mode..."

    if [[ ! -f "backend/api_server.py" ]]; then
        log "ERROR" "File api_server.py non trovato"
        exit 1
    fi

    python3 backend/api_server.py --ip "$ip" --port "$API_PORT" > /tmp/api_server.log 2>&1 &
    API_PID=$!

    # Attendi che l'API sia pronta
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        if curl -s "http://localhost:$API_PORT/api/health" >/dev/null 2>&1; then
            log "SUCCESS" "API server avviato (PID: $API_PID)"
            return 0
        fi
        sleep 1
        ((attempts++))
    done

    log "ERROR" "Timeout avvio API server"
    return 1
}

# Avvio dashboard
start_dashboard() {
    log "INFO" "🌐 Avvio dashboard statica..."

    if [[ ! -d "frontend" ]]; then
        log "ERROR" "Directory dashboard non trovata"
        exit 1
    fi

    cd frontend
    python3 -m http.server "$DASHBOARD_PORT" > /tmp/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    cd ..

    # Attendi che la dashboard sia pronta
    local attempts=0
    while [[ $attempts -lt 15 ]]; do
        if curl -s "http://localhost:$DASHBOARD_PORT" >/dev/null 2>&1; then
            log "SUCCESS" "Dashboard avviata (PID: $DASHBOARD_PID)"
            return 0
        fi
        sleep 1
        ((attempts++))
    done

    log "ERROR" "Timeout avvio dashboard"
    return 1
}

# Download eventi demo per simulatore
download_demo_events() {
    log "INFO" "📥 Download eventi demo..."

    if [[ ! -f "download_events.py" ]]; then
        log "WARN" "Script download_events.py non trovato"
        return 1
    fi

    python3 download_events.py --simulator eventi_demo.html 7 || {
        log "WARN" "Fallito download eventi demo"
        return 1
    }

    log "SUCCESS" "Eventi demo scaricati"
}

# Cleanup processi
cleanup() {
    log "INFO" "🧹 Cleanup processi..."

    local pids=()
    [[ -n "$SIMULATOR_PID" ]] && pids+=($SIMULATOR_PID)
    [[ -n "$API_PID" ]] && pids+=($API_PID)
    [[ -n "$DASHBOARD_PID" ]] && pids+=($DASHBOARD_PID)

    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            log "INFO" "Terminando processo $pid..."
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done

    # Attendi terminazione graceful
    sleep 3

    # Force kill se necessario
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            log "WARN" "Force kill processo $pid"
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done

    log "SUCCESS" "Cleanup completato"
    exit 0
}

# Health check
health_check() {
    local services=()

    # Controlla API
    if curl -s "http://localhost:$API_PORT/api/health" >/dev/null 2>&1; then
        services+=("✅ API Server")
    else
        services+=("❌ API Server")
    fi

    # Controlla Dashboard
    if curl -s "http://localhost:$DASHBOARD_PORT" >/dev/null 2>&1; then
        services+=("✅ Dashboard")
    else
        services+=("❌ Dashboard")
    fi

    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              STATO SERVIZI             ║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════╣${NC}"
    for service in "${services[@]}"; do
        echo -e "${BLUE}║${NC} $service"
    done
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
}

# Menu principale
show_menu() {
    echo ""
    echo -e "${PURPLE}Seleziona modalità di avvio:${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} 🏭 Produzione (distributore reale $DISTRIBUTORE_IP)"
    echo -e "${CYAN}2)${NC} 🧪 Simulazione (test offline)"
    echo -e "${CYAN}3)${NC} 🔍 Health Check"
    echo -e "${CYAN}4)${NC} 🛑 Esci"
    echo ""
    echo -n "Scelta [1-4]: "
}

# Modalità produzione
start_production() {
    log "INFO" "🏭 Avvio modalità PRODUZIONE"

    check_ports "$API_PORT" "$DASHBOARD_PORT"
    check_database

    if ! start_api_server "PRODUZIONE" "$DISTRIBUTORE_IP"; then
        log "ERROR" "Fallito avvio API server"
        exit 1
    fi

    if ! start_dashboard; then
        log "ERROR" "Fallito avvio dashboard"
        cleanup
        exit 1
    fi

    log "SUCCESS" "Sistema avviato in modalità PRODUZIONE"
    show_urls "produzione"
    show_production_info
}

# Modalità simulazione
start_simulation() {
    log "INFO" "🧪 Avvio modalità SIMULAZIONE"

    check_ports "$SIMULATOR_PORT" "$API_PORT" "$DASHBOARD_PORT"
    check_database

    if ! start_simulator; then
        log "ERROR" "Fallito avvio simulatore"
        exit 1
    fi

    if ! start_api_server "SIMULAZIONE" "localhost"; then
        log "ERROR" "Fallito avvio API server"
        cleanup
        exit 1
    fi

    if ! start_dashboard; then
        log "ERROR" "Fallito avvio dashboard"
        cleanup
        exit 1
    fi

    # Download eventi demo se database vuoto
    if [[ ! -s "sales_data.db" ]] || [[ $(sqlite3 sales_data.db "SELECT COUNT(*) FROM events;" 2>/dev/null || echo "0") -eq 0 ]]; then
        log "INFO" "Database vuoto, download eventi demo..."
        download_demo_events
    fi

    log "SUCCESS" "Sistema avviato in modalità SIMULAZIONE"
    show_urls "simulazione"
    show_simulation_info
}

# Mostra URLs
show_urls() {
    local mode=$1
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    SISTEMA ATTIVO ($mode)${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC} 🌐 Dashboard: ${CYAN}http://localhost:$DASHBOARD_PORT${NC}"
    echo -e "${GREEN}║${NC} 🔌 API:       ${CYAN}http://localhost:$API_PORT${NC}"
    if [[ "$mode" == "simulazione" ]]; then
        echo -e "${GREEN}║${NC} 🔧 Simulatore: ${CYAN}http://localhost:$SIMULATOR_PORT${NC}"
    fi
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
}

# Info produzione
show_production_info() {
    echo ""
    echo -e "${YELLOW}📋 COMANDI UTILI PRODUZIONE:${NC}"
    echo -e "   • Download eventi: ${CYAN}python3 download_events.py${NC}"
    echo -e "   • Processo eventi: ${CYAN}python3 sales_analyzer.py eventi_file.json${NC}"
    echo -e "   • Logs API:        ${CYAN}tail -f /tmp/api_server.log${NC}"
}

# Info simulazione
show_simulation_info() {
    echo ""
    echo -e "${YELLOW}📋 COMANDI UTILI SIMULAZIONE:${NC}"
    echo -e "   • Download demo:   ${CYAN}python3 download_events.py --simulator${NC}"
    echo -e "   • Logs simulatore: ${CYAN}tail -f /tmp/simulator.log${NC}"
    echo -e "   • Logs API:        ${CYAN}tail -f /tmp/api_server.log${NC}"
}

# Controllo parametri CLI
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick-sim)
                MODE="simulation"
                shift
                ;;
            --quick-prod)
                MODE="production"
                shift
                ;;
            --log-file)
                LOG_FILE="$2"
                shift 2
                ;;
            --api-port)
                API_PORT="$2"
                shift 2
                ;;
            --dashboard-port)
                DASHBOARD_PORT="$2"
                shift 2
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Parametro sconosciuto: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Help
show_help() {
    echo "Sistema di Avvio Unificato - Dashboard Distributore"
    echo ""
    echo "Uso: $0 [OPZIONI]"
    echo ""
    echo "Opzioni:"
    echo "  --quick-sim          Avvio rapido modalità simulazione"
    echo "  --quick-prod         Avvio rapido modalità produzione"
    echo "  --log-file FILE      File di log (opzionale)"
    echo "  --api-port PORT      Porta API server (default: 8000)"
    echo "  --dashboard-port PORT Porta dashboard (default: 3000)"
    echo "  --help, -h           Mostra questo help"
    echo ""
    echo "Esempi:"
    echo "  $0                   Menu interattivo"
    echo "  $0 --quick-sim       Avvio rapido simulazione"
    echo "  $0 --quick-prod      Avvio rapido produzione"
}

# MAIN
main() {
    # Setup signal handlers
    trap cleanup SIGINT SIGTERM

    # Parse arguments
    parse_args "$@"

    show_banner
    check_dependencies

    # Quick mode
    if [[ -n "$MODE" ]]; then
        case $MODE in
            "simulation")
                start_simulation
                ;;
            "production")
                start_production
                ;;
        esac

        # Wait indefinitely
        log "INFO" "Premi Ctrl+C per arrestare il sistema"
        while true; do
            sleep 60
            health_check
        done
    fi

    # Interactive mode
    while true; do
        show_menu
        read -r choice

        case $choice in
            1)
                start_production
                log "INFO" "Premi Ctrl+C per arrestare il sistema"
                while true; do
                    sleep 60
                    health_check
                done
                ;;
            2)
                start_simulation
                log "INFO" "Premi Ctrl+C per arrestare il sistema"
                while true; do
                    sleep 60
                    health_check
                done
                ;;
            3)
                health_check
                echo ""
                read -p "Premi ENTER per continuare..."
                ;;
            4)
                log "INFO" "Uscita..."
                exit 0
                ;;
            *)
                log "ERROR" "Scelta non valida"
                ;;
        esac
    done
}

# Avvia main
main "$@"