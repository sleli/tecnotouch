#!/usr/bin/env python3
"""
Script di monitoraggio automatico per distributore sigarette
Scarica periodicamente gli eventi e aggiorna la dashboard
"""

import os
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from sales_analyzer import SalesAnalyzer

class SalesMonitor:
    def __init__(self, simulator_mode=False, download_interval=300, db_path="sales_data.db"):
        """
        Inizializza il monitor delle vendite

        Args:
            simulator_mode: Se True usa il simulatore invece del distributore reale
            download_interval: Intervallo in secondi tra i download (default: 5 minuti)
            db_path: Path del database SQLite
        """
        self.simulator_mode = simulator_mode
        self.download_interval = download_interval
        self.analyzer = SalesAnalyzer(db_path)
        self.last_processed_file = None

    def download_events(self):
        """Scarica gli eventi dal distributore"""
        try:
            # Genera nome file con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"events_{timestamp}.html"

            # Comando per scaricare eventi
            if self.simulator_mode:
                cmd = ["python3", "download_events.py", "--simulator", output_file, "1"]
                print(f"🎰 Scaricando eventi dal simulatore...")
            else:
                cmd = ["python3", "download_events.py", output_file, "1"]
                print(f"📡 Scaricando eventi dal distributore...")

            # Esegui il download
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                # Trova il file JSON degli eventi generato
                json_file = output_file.replace('.html', '_events_only.json')

                if os.path.exists(json_file):
                    print(f"✅ Download completato: {json_file}")
                    return json_file
                else:
                    print(f"⚠️  File JSON non trovato: {json_file}")
                    return None
            else:
                print(f"❌ Errore nel download: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("⏰ Timeout nel download degli eventi")
            return None
        except Exception as e:
            print(f"❌ Errore imprevisto nel download: {e}")
            return None

    def process_new_events(self, json_file):
        """Processa il nuovo file di eventi"""
        try:
            # Verifica se il file è diverso dall'ultimo processato
            if json_file == self.last_processed_file:
                print("📋 Nessun nuovo evento da processare")
                return False

            print(f"🔄 Processando eventi da: {json_file}")

            # Usa l'analyzer per processare gli eventi
            self.analyzer.process_events_file(json_file)

            self.last_processed_file = json_file
            return True

        except Exception as e:
            print(f"❌ Errore nel processamento eventi: {e}")
            return False

    def cleanup_old_files(self, keep_days=7):
        """Rimuove i file di eventi vecchi per liberare spazio"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)

            for filename in os.listdir('.'):
                if filename.startswith('events_') and (filename.endswith('.html') or filename.endswith('.json')):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filename))

                    if file_time < cutoff_date:
                        os.remove(filename)
                        print(f"🗑️  Rimosso file vecchio: {filename}")

        except Exception as e:
            print(f"⚠️  Errore nella pulizia file: {e}")


    def print_status_summary(self):
        """Stampa un riassunto dello stato attuale"""
        try:
            data = self.analyzer.get_dashboard_data()
            summary = data['summary']

            print("\n" + "="*60)
            print(f"📊 RIASSUNTO STATO DISTRIBUTORE")
            print("="*60)
            print(f"🎯 Totale motori: {summary['total_motors']}")
            print(f"💰 Vendite oggi: {summary['today_sales']} (€{summary['today_revenue']})")
            print(f"🕐 Ultimo aggiornamento: {summary['last_updated']}")


            print("="*60 + "\n")

        except Exception as e:
            print(f"❌ Errore nel riassunto stato: {e}")

    def run_monitoring_cycle(self):
        """Esegue un singolo ciclo di monitoraggio"""
        print(f"\n🔄 Avvio ciclo monitoraggio - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Scarica nuovi eventi
        json_file = self.download_events()

        if json_file:
            # 2. Processa gli eventi
            if self.process_new_events(json_file):
                print("✅ Nuovi eventi processati con successo")

                # 3. Mostra riassunto stato
                self.print_status_summary()

                # 4. Controlla alert

            # 5. Pulizia file vecchi (solo una volta al giorno)
            if datetime.now().hour == 2 and datetime.now().minute < 10:  # Alle 2 di notte
                self.cleanup_old_files()

        print(f"⏱️  Prossimo check tra {self.download_interval // 60} minuti...")

    def run_continuous(self):
        """Esegue il monitoraggio continuo"""
        mode_text = "SIMULATORE" if self.simulator_mode else "DISTRIBUTORE REALE"
        interval_text = f"{self.download_interval // 60} minuti"

        print("🚀 AVVIO MONITORAGGIO AUTOMATICO VENDITE")
        print("="*60)
        print(f"🎯 Modalità: {mode_text}")
        print(f"⏱️  Intervallo: {interval_text}")
        print(f"💾 Database: {self.analyzer.db_path}")
        print(f"🌐 Dashboard: http://localhost:3000")
        print("="*60)
        print("💡 Premi Ctrl+C per fermare il monitoraggio")
        print("="*60)

        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.download_interval)

        except KeyboardInterrupt:
            print("\n🛑 Monitoraggio arrestato dall'utente")
        except Exception as e:
            print(f"\n❌ Errore nel monitoraggio: {e}")

def main():
    parser = argparse.ArgumentParser(description='Monitor vendite distributore sigarette (solo modalità singola)')
    parser.add_argument('--simulator', action='store_true',
                        help='Usa il simulatore invece del distributore reale')
    parser.add_argument('--db', default='sales_data.db',
                        help='Path del database SQLite')

    args = parser.parse_args()

    print("⚠️  NOTA: La modalità di monitoraggio continuo è stata disabilitata.")
    print("   Usa la dashboard web per download manuali: http://localhost:3000")
    print("   Questo script eseguirà solo un singolo download.")
    print()

    # Verifica dipendenze
    if not os.path.exists('download_events.py'):
        print("❌ Script download_events.py non trovato nella directory corrente")
        return

    if args.simulator and not os.path.exists('cigarette_machine_simulator.py'):
        print("❌ Simulatore non trovato. Avvia prima: python3 cigarette_machine_simulator.py")
        return

    # Inizializza monitor
    monitor = SalesMonitor(
        simulator_mode=args.simulator,
        download_interval=300,  # Non usato in modalità singola
        db_path=args.db
    )

    # Esegui sempre un solo ciclo
    monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()