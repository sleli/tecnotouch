#!/bin/bash

# Script per monitorare modifiche ai file e forzare reload automatico
# Monitora file JS/CSS e aggiorna timestamp per cache busting

set -e

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}👀 Monitoraggio File per Cache Busting${NC}"
echo "========================================"

# Controlla se fswatch è disponibile
if ! command -v fswatch &> /dev/null; then
    echo -e "${YELLOW}⚠️  fswatch non trovato. Installazione automatica...${NC}"

    # Prova installazione su macOS con Homebrew
    if command -v brew &> /dev/null; then
        echo -e "${BLUE}📦 Installando fswatch con Homebrew...${NC}"
        brew install fswatch
    else
        echo -e "${YELLOW}💡 Per installare fswatch:${NC}"
        echo "   macOS: brew install fswatch"
        echo "   Linux: sudo apt-get install fswatch"
        echo "   O usa polling mode con: ./watch_and_reload.sh --polling"
        exit 1
    fi
fi

# Funzione per aggiornare timestamp nel file HTML
update_cache_bust() {
    local file_changed="$1"
    echo -e "${GREEN}🔄 File modificato: ${file_changed}${NC}"
    echo -e "${YELLOW}⚡ Aggiornando cache busting...${NC}"

    # Trova e aggiorna la linea con timestamp nel file HTML
    if [[ -f "dashboard/index.html" ]]; then
        # Usa sed per aggiornare il timestamp
        local new_timestamp=$(date +%s%3N)  # timestamp in millisecondi

        # Backup del file originale
        cp dashboard/index.html dashboard/index.html.bak

        # Aggiorna il timestamp nel JavaScript
        sed -i.tmp "s/const timestamp = Date\.now();/const timestamp = ${new_timestamp};/" dashboard/index.html

        # Rimuovi file temporaneo
        rm dashboard/index.html.tmp 2>/dev/null || true

        echo -e "${GREEN}✅ Cache busting aggiornato (timestamp: ${new_timestamp})${NC}"
        echo -e "${BLUE}🌐 Ricarica la pagina nel browser per vedere le modifiche${NC}"
    else
        echo -e "${YELLOW}⚠️  File dashboard/index.html non trovato${NC}"
    fi
}

# Modalità polling se fswatch non è disponibile o richiesta
if [[ "$1" == "--polling" ]] || ! command -v fswatch &> /dev/null; then
    echo -e "${YELLOW}🔄 Usando modalità polling (controlla ogni 2 secondi)${NC}"

    # Salva i timestamp dei file
    declare -A file_times

    while true; do
        # Controlla file JS
        for file in dashboard/js/*.js; do
            if [[ -f "$file" ]]; then
                current_time=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null)
                if [[ "${file_times[$file]}" != "$current_time" ]]; then
                    file_times[$file]="$current_time"
                    update_cache_bust "$file"
                fi
            fi
        done

        # Controlla file CSS
        for file in dashboard/css/*.css dashboard/*.css; do
            if [[ -f "$file" ]]; then
                current_time=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null)
                if [[ "${file_times[$file]}" != "$current_time" ]]; then
                    file_times[$file]="$current_time"
                    update_cache_bust "$file"
                fi
            fi
        done

        sleep 2
    done
else
    echo -e "${GREEN}🎯 Monitoraggio attivo con fswatch${NC}"
    echo -e "${YELLOW}Premi CTRL+C per terminare${NC}"
    echo

    # Usa fswatch per monitorare modifiche in tempo reale
    fswatch -o dashboard/js/ dashboard/css/ 2>/dev/null | while read num; do
        update_cache_bust "file in dashboard/"
    done
fi