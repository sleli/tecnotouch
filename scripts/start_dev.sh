#!/bin/bash

# Script di sviluppo per dashboard con cache busting automatico
# Avvia automaticamente API server e dashboard con reload

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Avvio Sistema di Sviluppo Dashboard${NC}"
echo "========================================"

# Controlla se i server sono già in esecuzione
if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Server API già in esecuzione sulla porta 8000${NC}"
    read -p "Vuoi terminarlo e riavviarlo? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}🛑 Terminando server esistente...${NC}"
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo -e "${YELLOW}⏭️  Mantenendo server esistente${NC}"
    fi
fi

if lsof -i :3000 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Server Dashboard già in esecuzione sulla porta 3000${NC}"
    read -p "Vuoi terminarlo e riavviarlo? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}🛑 Terminando server dashboard esistente...${NC}"
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo -e "${YELLOW}⏭️  Mantenendo server dashboard esistente${NC}"
    fi
fi

# Funzione per cleanup alla chiusura
cleanup() {
    echo -e "\n${RED}🛑 Terminando servers...${NC}"
    jobs -p | xargs kill -9 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Avvia API server
echo -e "${GREEN}🔧 Avvio API Server...${NC}"
python3 api_server.py --ip 0.0.0.0 --port 8000 &
API_PID=$!

# Attendi che l'API sia pronta
echo -e "${YELLOW}⏳ Attendo avvio API server...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API Server pronto${NC}"
        break
    fi
    sleep 1
done

# Avvia Dashboard server
echo -e "${GREEN}🌐 Avvio Dashboard Server...${NC}"
cd dashboard
python3 -m http.server 3000 &
DASHBOARD_PID=$!
cd ..

# Attendi che il dashboard sia pronto
echo -e "${YELLOW}⏳ Attendo avvio dashboard...${NC}"
for i in {1..5}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Dashboard pronto${NC}"
        break
    fi
    sleep 1
done

# Trova IP per accesso remoto
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

echo
echo -e "${GREEN}✅ Sistema Avviato con Successo!${NC}"
echo "========================================"
echo -e "${BLUE}📱 Accesso Locale:${NC}"
echo "   Dashboard: http://localhost:3000"
echo "   API:       http://localhost:8000"
echo
echo -e "${BLUE}🌐 Accesso Remoto:${NC}"
echo "   Dashboard: http://${LOCAL_IP}:3000"
echo "   API:       http://${LOCAL_IP}:8000"
echo
echo -e "${YELLOW}💡 Features Anti-Cache:${NC}"
echo "   ✅ Cache busting automatico con timestamp"
echo "   ✅ Meta tags no-cache attivi"
echo "   ✅ Refresh automatico ad ogni reload"
echo
echo -e "${GREEN}🎯 Pronto per lo sviluppo!${NC}"
echo -e "${YELLOW}Premi CTRL+C per terminare entrambi i server${NC}"

# Mantieni script attivo
wait $API_PID $DASHBOARD_PID