#!/usr/bin/env python3
"""
Simulatore del distributore di sigarette per test offline
Simula l'interfaccia web del distributore usando i dati JSON esistenti
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect
import json
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'simulator_secret_key_for_testing'

class CigaretteMachineSimulator:
    def __init__(self, events_file="sample_data.json"):
        self.events_file = events_file
        self.events_data = []
        self.date_range = None
        self.load_events()
        self.analyze_date_range()

    def load_events(self):
        """Carica gli eventi dal file JSON esistente"""
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    self.events_data = json.load(f)
                print(f"✅ Caricati {len(self.events_data)} eventi da {self.events_file}")
            except Exception as e:
                print(f"❌ Errore nel caricamento eventi: {e}")
                self.events_data = []
        else:
            # Cerca altri file eventi reali
            self.find_alternative_events_file()

    def find_alternative_events_file(self):
        """Cerca file eventi alternativi nella directory corrente"""
        import glob

        # Pattern per trovare file eventi
        patterns = [
            "events_*_events_only.json",
            "events_*_complete.json"
        ]

        found_files = []
        for pattern in patterns:
            found_files.extend(glob.glob(pattern))

        if found_files:
            # Usa il file più recente
            latest_file = max(found_files, key=lambda f: os.path.getmtime(f))
            print(f"📂 File specificato non trovato, uso file alternativo: {latest_file}")
            self.events_file = latest_file

            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    # Se è un file _complete.json, estrai solo gli eventi
                    data = json.load(f)
                    if isinstance(data, dict) and 'events_data' in data:
                        self.events_data = data['events_data']
                    else:
                        self.events_data = data

                print(f"✅ Caricati {len(self.events_data)} eventi da {latest_file}")

            except Exception as e:
                print(f"❌ Errore nel caricamento file alternativo: {e}")
                self.events_data = []
        else:
            print("❌ ERRORE: Nessun file eventi reale trovato!")
            print("   Per usare il simulatore, scarica prima degli eventi reali:")
            print("   python3 download_events.py --ip 192.168.1.65 eventi_reali.html 30")
            print("   oppure copia il file sample_data.json nella directory simulator/")
            self.events_data = []

    def analyze_date_range(self):
        """Analizza il range delle date negli eventi caricati"""
        if not self.events_data:
            return

        dates = []
        for event in self.events_data:
            try:
                event_datetime = datetime.strptime(event["dateTime"], "%d/%m/%y %H:%M:%S")
                dates.append(event_datetime.date())
            except (ValueError, KeyError):
                continue

        if dates:
            self.date_range = {
                'start': min(dates),
                'end': max(dates),
                'count': len(dates)
            }
            print(f"📅 Range eventi: {self.date_range['start'].strftime('%d/%m/%y')} - {self.date_range['end'].strftime('%d/%m/%y')}")

    def filter_events_by_date(self, start_date, end_date):
        """Filtra gli eventi per range di date"""
        filtered_events = []

        for event in self.events_data:
            try:
                # Parse della data dell'evento (formato: "17/09/25 19:14:15")
                event_datetime = datetime.strptime(event["dateTime"], "%d/%m/%y %H:%M:%S")
                event_date = event_datetime.date()

                if start_date <= event_date <= end_date:
                    filtered_events.append(event)
            except ValueError:
                continue

        return filtered_events

# Inizializza il simulatore
simulator = CigaretteMachineSimulator()

# Template HTML per la pagina di login
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>...::: TECNOTOUCH REMOTE SERVICE :::...</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
        .container { max-width: 400px; margin: 100px auto; padding: 20px; background: white; border-radius: 8px; }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .submit-btn { width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .submit-btn:hover { background-color: #0056b3; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>TECNOTOUCH SERVIZIO REMOTO</h2>
            <p>🎰 SIMULATORE - Modalità Test</p>
        </div>
        <form method="post" action="/login_check">
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" name="password" id="password" required>
            </div>
            <button type="submit" class="submit-btn">Accedi</button>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        </form>
        <div style="margin-top: 20px; font-size: 12px; color: #666;">
            <p>💡 Usa password: <strong>Andrea1976</strong></p>
        </div>
    </div>
</body>
</html>
"""

# Template HTML per la pagina eventi
EVENTS_PAGE = """
<!DOCTYPE html>
<html><head>
<title>...::: TECNOTOUCH REMOTE SERVICE :::...</title>
<style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
    .tt_web_header { background-color: #333; color: white; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; }
    .tt_web_page_body { padding: 20px; }
    .tt_web_page_title { font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #333; }
    .simulator-notice { background-color: #e7f3ff; border: 1px solid #bee5eb; padding: 10px; margin-bottom: 20px; border-radius: 4px; }
    .events-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .event-stats { margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px; }
</style>
</head>
<body>
<div class='tt_web_header'>TECNOTOUCH SERVIZIO REMOTO</div>
<div class='tt_web_page_body'>

<div class='tt_web_page_title'>Eventi</div>

<div class="simulator-notice">
    🎰 <strong>MODALITÀ SIMULATORE</strong> - Eventi reali da distributore Tecnotouch.
    Eventi caricati: {{ total_events }} | Simulatore attivo su porta 1500
</div>

<div class="events-container">
    <div class="event-stats">
        <h3>Statistiche Eventi Reali Caricati</h3>
        <p>📊 <strong>Totale eventi:</strong> {{ total_events }}</p>
        <p>📅 <strong>Range temporale:</strong> {{ date_range }}</p>
        <p>📂 <strong>File sorgente:</strong> {{ events_file }}</p>
        <p>🔄 <strong>Ultimo aggiornamento:</strong> {{ current_time }}</p>
    </div>

    <div>
        <h3>Tipi di Eventi Disponibili</h3>
        <ul>
            <li><strong>PROGRAMMAZIONE</strong> - Eventi di configurazione sistema</li>
            <li><strong>EVENTO</strong> - Eventi generici del distributore</li>
            <li><strong>BANCONOTA</strong> - Transazioni con banconote</li>
            <li><strong>MONETA</strong> - Transazioni con monete</li>
            <li><strong>POS</strong> - Pagamenti con carta</li>
            <li><strong>RESTO</strong> - Operazioni di resto</li>
            <li><strong>SCONTRINO</strong> - Stampa scontrini</li>
            <li><strong>EMAIL</strong> - Notifiche email</li>
            <li><strong>ANOMALIA</strong> - Errori e anomalie</li>
            <li><strong>AGGIORNAMENTI</strong> - Aggiornamenti sistema</li>
        </ul>
    </div>

    <div style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
        <h4>💡 Come usare il simulatore</h4>
        <p>Il simulatore risponde alle stesse API del distributore reale:</p>
        <ul>
            <li><code>/events2_query?queryData=*|2025-09-01|2025-09-17</code> - API JSON per script</li>
            <li><code>/admin_index_back</code> - Uscita modalità programmazione</li>
        </ul>
    </div>
</div>

</div>
</body>
</html>
"""

@app.route('/login')
def login_page():
    """Pagina di login"""
    error = request.args.get('error')
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/login_check', methods=['POST'])
def login_check():
    """Gestisce l'autenticazione"""
    password = request.form.get('password')

    if password == 'Andrea1976':
        session['authenticated'] = True
        print(f"✅ Login simulato riuscito per password: {password}")
        return render_template_string("""
        <html><head><meta http-equiv="refresh" content="0;url=/events2"></head>
        <body>Login riuscito, reindirizzamento...</body></html>
        """)
    else:
        print(f"❌ Login simulato fallito per password: {password}")
        return render_template_string(LOGIN_PAGE, error="non sei connesso come amministratore")

@app.route('/events2')
def events_page():
    """Pagina principale degli eventi"""
    if not session.get('authenticated'):
        return redirect('/login')

    # 🔄 NUOVO: Ricarica i dati anche per la pagina web per mostrare statistiche aggiornate
    print("🔄 Ricaricamento dati per pagina eventi...")
    simulator.load_events()
    simulator.analyze_date_range()

    total_events = len(simulator.events_data)
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Crea stringa range date
    if simulator.date_range:
        date_range = f"{simulator.date_range['start'].strftime('%d/%m/%y')} - {simulator.date_range['end'].strftime('%d/%m/%y')}"
    else:
        date_range = "Range non disponibile"

    return render_template_string(EVENTS_PAGE,
                                total_events=total_events,
                                current_time=current_time,
                                date_range=date_range,
                                events_file=simulator.events_file)

@app.route('/events2_query')
def events_query():
    """API JSON per gli eventi con filtro per data"""
    if not session.get('authenticated'):
        return jsonify({"error": "Non autenticato"}), 401

    query_data = request.args.get('queryData', '')
    print(f"📊 Richiesta eventi con query: {query_data}")

    # 🔄 NUOVO: Ricarica sempre il file ad ogni richiesta per aggiornamenti dinamici
    print("🔄 Ricaricamento dinamico sample_data.json...")
    simulator.load_events()
    simulator.analyze_date_range()
    print(f"✅ Ricaricati {len(simulator.events_data)} eventi")

    try:
        # Parse del formato: "*|2025-09-01|2025-09-17"
        if '|' in query_data:
            parts = query_data.split('|')
            if len(parts) >= 3:
                start_date_str = parts[1]
                end_date_str = parts[2]

                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

                filtered_events = simulator.filter_events_by_date(start_date, end_date)
                print(f"🔍 Filtrati {len(filtered_events)} eventi nel range {start_date} - {end_date}")

                return jsonify(filtered_events)

    except Exception as e:
        print(f"❌ Errore nel parsing query: {e}")

    # Fallback: restituisci tutti gli eventi
    print(f"📋 Restituisco tutti i {len(simulator.events_data)} eventi")
    return jsonify(simulator.events_data)

@app.route('/admin_index_back')
def admin_index_back():
    """Simula l'uscita dalla modalità programmazione"""
    print("🚪 Simulazione uscita dalla modalità programmazione")
    return """
    <html><head><title>Uscita modalità programmazione</title></head>
    <body><h2>Uscita dalla modalità programmazione completata</h2>
    <p>Simulatore: operazione completata con successo</p></body></html>
    """

@app.route('/')
def index():
    """Pagina principale - reindirizza al login"""
    return render_template_string("""
    <html><head><meta http-equiv="refresh" content="0;url=/login"></head>
    <body>Reindirizzamento al login...</body></html>
    """)

@app.route('/status')
def status():
    """Endpoint per verificare lo stato del simulatore"""
    return jsonify({
        "status": "running",
        "simulator": "cigarette_machine",
        "events_loaded": len(simulator.events_data),
        "events_file": simulator.events_file,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎰 Avvio Simulatore Distributore Sigarette")
    print("=" * 50)
    print(f"📊 Eventi caricati: {len(simulator.events_data)}")
    if simulator.date_range:
        print(f"📅 Range dati: {simulator.date_range['start'].strftime('%d/%m/%y')} - {simulator.date_range['end'].strftime('%d/%m/%y')}")
    print(f"📂 File sorgente: {simulator.events_file}")
    print("🌐 Server in ascolto su: http://localhost:1500")
    print("🔐 Credenziali test: password = Andrea1976")
    print("=" * 50)
    print("💡 Per testare con lo script:")
    print("   python3 download_events.py --ip localhost")
    print("=" * 50)

    try:
        app.run(host='0.0.0.0', port=1500, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Simulatore arrestato dall'utente")
    except Exception as e:
        print(f"\n❌ Errore nel simulatore: {e}")