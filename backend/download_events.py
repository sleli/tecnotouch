#!/usr/bin/env python3
"""
Script per scaricare gli eventi dal distributore di sigarette
Versione refactorizzata che usa CigaretteMachineClient
"""

import sys
import os
import json
from datetime import datetime
from cigarette_machine_client import CigaretteMachineClient

# Add parent directory to path to import shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import Config


def download_and_parse_events(client, output_file=None, days_back=30):
    """Scarica sia la pagina HTML che i dati JSON degli eventi"""
    # Scarica pagina HTML
    events_file = client.download_events_html(output_file)
    if not events_file:
        return None

    # Leggi il file HTML
    with open(events_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Scarica anche i dati JSON
    events_data = client.download_events_data(days_back)

    # Salva tutto in un file JSON completo
    json_file = events_file.replace('.html', '_complete.json')

    complete_data = {
        'download_info': {
            'timestamp': datetime.now().isoformat(),
            'source_url': f"{client.base_url}/events2",
            'html_file': events_file,
            'html_size': len(html_content),
            'days_searched': days_back
        },
        'events_data': events_data,
        'events_count': len(events_data)
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2, ensure_ascii=False)

    print(f"📋 Dati completi salvati in: {json_file}")

    # Salva anche solo gli eventi se ce ne sono
    if events_data:
        events_only_file = events_file.replace('.html', '_events_only.json')
        with open(events_only_file, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2, ensure_ascii=False)
        print(f"📋 Solo eventi salvati in: {events_only_file}")

    return events_file


def main():
    """Funzione principale"""
    # Parsing argomenti
    import argparse

    parser = argparse.ArgumentParser(description='Download eventi distributore sigarette')
    parser.add_argument('output_file', nargs='?', help='Nome file di output (opzionale)')
    parser.add_argument('days_back', nargs='?', type=int, default=30, help='Giorni di eventi da scaricare (default: 30)')
    parser.add_argument('--simulator', action='store_true', help='Usa simulatore localhost (deprecato, usa --ip localhost)')
    parser.add_argument('--ip', default=Config.DEFAULT_DISTRIBUTOR_IP, help=f'Indirizzo IP del distributore (default: {Config.DEFAULT_DISTRIBUTOR_IP})')

    args = parser.parse_args()

    # Gestione compatibilità --simulator
    if args.simulator:
        target_ip = 'localhost'
        print("🎰 Avvio download eventi dal SIMULATORE...")
    else:
        target_ip = args.ip
        if target_ip == 'localhost':
            print("🎰 Avvio download eventi dal SIMULATORE...")
        else:
            print(f"🔄 Avvio download eventi dal distributore ({target_ip})...")

    base_url = f"http://{target_ip}:1500"

    # Inizializza il client con URL appropriato
    client = CigaretteMachineClient(base_url=base_url)

    # Effettua il login
    if not client.login():
        if target_ip == 'localhost':
            print("❌ Login al simulatore fallito. Assicurati che il simulatore sia in esecuzione:")
            print("   cd simulator && python3 vending_machine_simulator.py")
        else:
            print(f"❌ Login fallito. Verifica le credenziali e la connessione al distributore {target_ip}.")
        # Tenta comunque di uscire dalla modalità programmazione se possibile
        client.exit_programming_mode()
        sys.exit(1)

    output_file = args.output_file
    days_back = args.days_back

    if target_ip == 'localhost':
        print(f"🎰 Cercando eventi dal simulatore (ultimi {days_back} giorni)...")
    else:
        print(f"📅 Cercando eventi dal distributore {target_ip} (ultimi {days_back} giorni)...")

    # Scarica gli eventi
    result = download_and_parse_events(client, output_file, days_back)

    # Esce sempre dalla modalità programmazione, anche in caso di errore
    client.exit_programming_mode()

    if result:
        mode_text = "simulatore" if target_ip == 'localhost' else f"distributore {target_ip}"
        print(f"✅ Download dal {mode_text} completato con successo!")
    else:
        print("❌ Download fallito.")
        sys.exit(1)


if __name__ == "__main__":
    main()