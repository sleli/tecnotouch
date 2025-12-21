#!/usr/bin/env python3
"""
Client per comunicare con il distributore di sigarette
Estratto e refactorizzato da download_events.py originale
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import Config


class CigaretteMachineClient:
    """Client per comunicare con il distributore di sigarette o simulatore"""

    def __init__(self, base_url=None, username=None):
        self.base_url = base_url or Config.get_distributor_url()
        self.username = username or Config.DEFAULT_USERNAME
        self.session = requests.Session()
        # User-Agent necessario - il distributore blocca richieste senza browser reale
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def login(self):
        """Effettua il login al sistema"""
        login_check_url = f"{self.base_url}/login_check"
        login_page_url = f"{self.base_url}/login"

        try:
            # Prima ottieni la pagina di login per stabilire la sessione
            print("🔗 Caricamento pagina di login...")
            response = self.session.get(login_page_url)
            response.raise_for_status()

            # Headers corretti come dal DevTools
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': login_page_url,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1'
            }

            # Dati di login corretti
            login_data = {
                'password': self.username
            }

            print("🔐 Effettuando login...")
            # Tentativo di login con URL corretto
            response = self.session.post(login_check_url, data=login_data, headers=headers)
            response.raise_for_status()

            print(f"📊 Response status: {response.status_code}")
            print(f"🍪 Cookie ricevuti: {len(self.session.cookies)} cookie")

            # Verifica se il login è riuscito controllando se non c'è il messaggio di errore
            if "non sei connesso come amministratore" in response.text:
                print("❌ Login fallito: credenziali errate")
                return False

            print(f"✅ Login effettuato con successo")
            return True

        except requests.RequestException as e:
            print(f"❌ Errore durante il login: {e}")
            return False

    def download_events_html(self, output_file=None):
        """Scarica la pagina degli eventi in formato HTML"""
        events_url = f"{self.base_url}/events2"

        try:
            response = self.session.get(events_url)
            response.raise_for_status()

            # Genera nome file se non specificato
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"events_{timestamp}.html"

            # Salva il contenuto
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"✅ Eventi scaricati in: {output_file}")
            print(f"📄 Dimensione file: {len(response.text)} caratteri")

            return output_file

        except requests.RequestException as e:
            print(f"❌ Errore durante il download: {e}")
            return None

    def download_events_data(self, days_back=30):
        """Scarica i dati degli eventi in formato JSON tramite API"""
        events_query_url = f"{self.base_url}/events2_query"

        try:
            # Calcola range di date (ultimi X giorni)
            today = datetime.now().date()
            start_date = today - timedelta(days=days_back)

            # Query per tutti gli eventi nel range
            query_data = f"*|{start_date}|{today}"

            # Headers per richiesta JSON (esatti come dal browser)
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Referer': f'{self.base_url}/events2'
            }

            print(f"🔍 Scaricamento dati eventi (ultimi {days_back} giorni)...")

            # Visita prima events2 per stabilire la sessione corretta
            self.session.get(f"{self.base_url}/events2", headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1'
            })

            # URL con encoding corretto (| = %7C)
            encoded_query = query_data.replace('|', '%7C')
            full_url = f"{events_query_url}?queryData={encoded_query}"

            response = self.session.get(full_url, headers=headers)
            response.raise_for_status()

            # Prova a parsare come JSON
            try:
                events_data = response.json()
                print(f"📊 Trovati {len(events_data)} eventi")
                return events_data
            except json.JSONDecodeError:
                print(f"⚠️  Risposta non JSON: {response.text[:100]}...")
                return []

        except requests.RequestException as e:
            print(f"❌ Errore durante il download dati JSON: {e}")
            return []

    def exit_programming_mode(self):
        """Esce dalla modalità programmazione del distributore"""
        try:
            print("🚪 Uscita dalla modalità programmazione...")
            response = self.session.get(f"{self.base_url}/admin_index_back")
            response.raise_for_status()
            print("✅ Uscita dalla modalità programmazione completata")
            return True
        except requests.RequestException as e:
            print(f"⚠️  Errore durante l'uscita dalla modalità programmazione: {e}")
            return False