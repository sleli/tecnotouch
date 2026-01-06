#!/usr/bin/env python3
"""
API Server minimale per sistema statistiche distributore sigarette
Server Flask leggero che espone solo endpoints REST per la dashboard
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import argparse
import os
import subprocess
import threading
import time
import shutil
import glob
import json
from datetime import datetime, timedelta
from data_processor import SalesAnalyzer
from motor_analytics import MotorAnalytics
import sys

# Add parent directory to path to import shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import Config

app = Flask(__name__)
CORS(app)  # Abilita CORS per dashboard statica

# Inizializza analyzer
analyzer = None
motor_analytics = None

# Variabile globale per stato download
download_status = {
    'is_running': False,
    'progress': 0,
    'message': '',
    'last_update': None,
    'error': None
}

# Variabile globale per IP distributore (verrà impostata da args.ip)
DISTRIBUTORE_IP = None

# Lista globale per gestire connessioni SSE
sse_clients = []

# Cache per ping distributore (evita ping ad ogni richiesta health)
distributore_ping_cache = {
    'last_check': None,
    'result': False,
    'cache_duration': 180  # 3 minuti
}

# === CORE API ENDPOINTS ===

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint per dati dashboard completa"""
    try:
        data = analyzer.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/motors')
def api_motors():
    """API endpoint per lista motori"""
    try:
        data = analyzer.get_dashboard_data()
        return jsonify(data['motors'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/motor/<int:motor_id>')
def api_motor_detail(motor_id):
    """API endpoint per dettagli specifici motore"""
    try:
        import sqlite3
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()

        # Dati motore
        cursor.execute('''
            SELECT motor_id, product_name, price, last_sale_datetime,
                   total_sales
            FROM motors WHERE motor_id = ?
        ''', (motor_id,))

        motor_data = cursor.fetchone()
        if not motor_data:
            return jsonify({"error": "Motore non trovato"}), 404

        # Vendite recenti (ultimi 7 giorni)
        cursor.execute('''
            SELECT sale_datetime, price
            FROM sales
            WHERE motor_id = ? AND DATE(sale_datetime) >= DATE('now', '-7 days')
            ORDER BY sale_datetime DESC
            LIMIT 50
        ''', (motor_id,))

        recent_sales = cursor.fetchall()
        conn.close()

        motor_info = {
            'motor_id': motor_data[0],
            'product_name': motor_data[1],
            'price': motor_data[2],
            'last_sale_datetime': motor_data[3],
            'total_sales': motor_data[4],
            'recent_sales': [{'datetime': sale[0], 'price': sale[1]} for sale in recent_sales]
        }

        return jsonify(motor_info)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === MOTOR ANALYTICS API ENDPOINTS ===

@app.route('/api/motors/<int:motor_id>/analytics')
def api_motor_analytics(motor_id):
    """API endpoint per analytics dettagliate di un motore specifico"""
    try:
        if not motor_analytics:
            return jsonify({"error": "Analytics engine not initialized"}), 500

        # Validate motor_id range
        if motor_id < 1 or motor_id > 70:
            return jsonify({"error": "NotFound", "message": f"Motor {motor_id} not found"}), 404

        analytics_data = motor_analytics.get_motor_analytics(motor_id)
        return jsonify(analytics_data)

    except ValueError as e:
        if "not found" in str(e):
            return jsonify({"error": "NotFound", "message": str(e)}), 404
        return jsonify({"error": "BadRequest", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "InternalServerError", "message": str(e)}), 500

@app.route('/api/motors/analytics/status')
def api_motors_status():
    """API endpoint per status indicators di tutti i motori"""
    try:
        if not motor_analytics:
            return jsonify({"error": "Analytics engine not initialized"}), 500

        status_data = motor_analytics.get_all_motor_status()
        return jsonify(status_data)

    except Exception as e:
        return jsonify({"error": "InternalServerError", "message": str(e)}), 500

@app.route('/api/analytics/refresh', methods=['POST'])
def api_analytics_refresh():
    """API endpoint per triggerare il refresh dei calcoli analytics"""
    try:
        if not motor_analytics:
            return jsonify({"error": "Analytics engine not initialized"}), 500

        # Esegui refresh in background (async)
        success = motor_analytics.refresh_analytics_cache()

        if success:
            estimated_completion = datetime.now() + timedelta(seconds=30)
            return jsonify({
                "message": "Analytics refresh initiated",
                "estimated_completion": estimated_completion.isoformat()
            }), 202
        else:
            return jsonify({"error": "InternalServerError", "message": "Failed to refresh analytics"}), 500

    except Exception as e:
        return jsonify({"error": "InternalServerError", "message": str(e)}), 500

@app.route('/api/analytics/cache/stats')
def api_analytics_cache_stats():
    """API endpoint per ottenere statistiche della cache analytics"""
    try:
        if not motor_analytics:
            return jsonify({"error": "Analytics engine not initialized"}), 500

        stats = motor_analytics.get_cache_stats()
        return jsonify(stats), 200

    except Exception as e:
        print(f"Errore cache stats: {e}")
        return jsonify({"error": "InternalServerError", "message": str(e)}), 500

@app.route('/api/analytics/cache/cleanup', methods=['POST'])
def api_analytics_cache_cleanup():
    """API endpoint per pulire le entry scadute dalla cache"""
    try:
        if not motor_analytics:
            return jsonify({"error": "Analytics engine not initialized"}), 500

        removed_count = motor_analytics.cleanup_expired_cache()
        return jsonify({
            "message": "Cache cleanup completed",
            "removed_entries": removed_count
        }), 200

    except Exception as e:
        print(f"Errore cache cleanup: {e}")
        return jsonify({"error": "InternalServerError", "message": str(e)}), 500

# === STATISTICS API ENDPOINTS ===

@app.route('/api/statistics/overview')
def api_statistics_overview():
    """API endpoint per statistiche generali con filtri opzionali"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        stats = analyzer.get_statistics_overview(date_from, date_to)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics/by-brand')
def api_statistics_by_brand():
    """API endpoint per statistiche dettagliate per marca"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        brands_stats = analyzer.get_statistics_by_brand(date_from, date_to)
        return jsonify(brands_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics/by-package-type')
def api_statistics_by_package_type():
    """API endpoint per statistiche dettagliate per tipologia di pacchetto"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        package_stats = analyzer.get_statistics_by_package_type(date_from, date_to)
        return jsonify(package_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics/transactions')
def api_statistics_transactions():
    """API endpoint per lista transazioni con filtri"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        payment_method = request.args.get('payment_method')
        limit = request.args.get('limit', 100, type=int)

        import sqlite3
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()

        where_conditions = []
        params = []

        if date_from:
            where_conditions.append("DATE(start_datetime) >= ?")
            params.append(date_from)
        if date_to:
            where_conditions.append("DATE(start_datetime) <= ?")
            params.append(date_to)
        if payment_method:
            where_conditions.append("payment_method = ?")
            params.append(payment_method)

        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

        cursor.execute(f'''
            SELECT id, start_datetime, payment_method, total_paid, total_change, net_revenue
            FROM transactions
            {where_clause}
            ORDER BY start_datetime DESC
            LIMIT ?
        ''', params + [limit])

        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'id': row[0],
                'start_datetime': row[1],
                'payment_method': row[2],
                'total_paid': row[3] or 0,
                'total_change': row[4] or 0,
                'net_revenue': row[5] or 0
            })

        conn.close()
        return jsonify(transactions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics/daily-summary')
def api_statistics_daily_summary():
    """API endpoint per riepilogo statistiche giornaliere"""
    try:
        days_back = request.args.get('days', 7, type=int)

        import sqlite3
        conn = sqlite3.connect(analyzer.db_path)
        cursor = conn.cursor()

        # Statistiche giornaliere aggregate
        cursor.execute('''
            SELECT
                DATE(sale_datetime) as date,
                COUNT(*) as sales_count,
                SUM(price) as revenue,
                payment_method,
                COUNT(DISTINCT motor_id) as motors_used
            FROM sales
            WHERE DATE(sale_datetime) >= DATE('now', ?)
            GROUP BY DATE(sale_datetime), payment_method
            ORDER BY date DESC, payment_method
        ''', (f'-{days_back} days',))

        daily_data = {}
        for row in cursor.fetchall():
            date = row[0]
            if date not in daily_data:
                daily_data[date] = {
                    'date': date,
                    'total_sales': 0,
                    'total_revenue': 0,
                    'motors_used': row[4],
                    'payment_methods': {}
                }

            payment_method = row[3] or 'UNKNOWN'
            daily_data[date]['total_sales'] += row[1]
            daily_data[date]['total_revenue'] += row[2] or 0
            daily_data[date]['payment_methods'][payment_method] = {
                'sales': row[1],
                'revenue': row[2] or 0
            }

        # Converti in lista ordinata per data
        result = list(daily_data.values())
        result.sort(key=lambda x: x['date'], reverse=True)

        conn.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === SSE FUNCTIONS ===

def send_sse_event(event_type, data):
    """Invia evento SSE a tutti i client connessi"""
    global sse_clients

    # Formatta messaggio SSE
    message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    # Invia a tutti i client connessi (rimuove quelli disconnessi)
    active_clients = []
    for client in sse_clients:
        try:
            client.put(message)
            active_clients.append(client)
        except:
            # Client disconnesso, rimuovi dalla lista
            pass

    sse_clients = active_clients

@app.route('/api/events')
def sse_events():
    """Endpoint SSE per eventi real-time"""
    import queue

    def event_stream():
        # Crea queue per questo client
        client_queue = queue.Queue()
        sse_clients.append(client_queue)

        try:
            # Invia evento di connessione
            yield f"event: connected\ndata: {json.dumps({'message': 'SSE connected'})}\n\n"

            # Loop per inviare eventi
            while True:
                try:
                    # Aspetta messaggi dalla queue (timeout 30s per mantenere connessione viva)
                    message = client_queue.get(timeout=30)
                    yield message
                except queue.Empty:
                    # Heartbeat per mantenere connessione viva
                    yield f"event: heartbeat\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
        except GeneratorExit:
            # Client disconnesso
            if client_queue in sse_clients:
                sse_clients.remove(client_queue)

    response = Response(event_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # Per nginx

    return response

# === DOWNLOAD API ENDPOINTS ===

def cleanup_old_events():
    """Rimuove file JSON più vecchi di 30 giorni dalla directory past_events"""
    past_events_dir = "past_events"
    if not os.path.exists(past_events_dir):
        return

    cutoff_date = datetime.now() - timedelta(days=30)
    removed_count = 0

    try:
        for filename in os.listdir(past_events_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(past_events_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                if file_time < cutoff_date:
                    os.remove(file_path)
                    removed_count += 1

    except Exception as e:
        print(f"❌ Errore durante cleanup: {e}")

def perform_download():
    """Funzione per eseguire il download in background"""
    global download_status, DISTRIBUTORE_IP

    try:
        download_status['is_running'] = True
        download_status['progress'] = 0
        download_status['message'] = 'Inizializzazione download...'
        download_status['error'] = None

        # Invia evento SSE di inizio download
        send_sse_event('download_started', {
            'message': 'Download iniziato',
            'progress': 0
        })

        # Esegui cleanup dei file vecchi
        cleanup_old_events()

        # Genera nome file con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"events_{timestamp}.html"

        # Assicurati che la directory past_events esista
        os.makedirs("past_events", exist_ok=True)

        # Comando per scaricare eventi
        cmd = ["python3", "download_events.py", "--ip", DISTRIBUTORE_IP, output_file, "30"]

        if DISTRIBUTORE_IP == 'localhost':
            download_status['message'] = 'Scaricando dal simulatore...'
        else:
            download_status['message'] = f'Scaricando dal distributore {DISTRIBUTORE_IP}...'

        download_status['progress'] = 20

        # Invia evento SSE di progresso
        send_sse_event('download_progress', {
            'message': download_status['message'],
            'progress': 20
        })

        # Esegui il download
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        download_status['progress'] = 60

        if result.returncode == 0:
            # Trova i file JSON degli eventi generati
            json_file = output_file.replace('.html', '_events_only.json')
            complete_file = output_file.replace('.html', '_complete.json')

            # Prova prima _complete.json, poi _events_only.json se il primo non esiste
            if os.path.exists(complete_file):
                target_file = complete_file
            elif os.path.exists(json_file):
                target_file = json_file
                download_status['message'] = 'Usando file events-only...'
            else:
                target_file = None

            if target_file:
                download_status['message'] = 'Processando eventi...'
                download_status['progress'] = 80

                # Sposta il file JSON nella directory past_events
                archived_file = os.path.join("past_events", os.path.basename(target_file))
                shutil.move(target_file, archived_file)

                # Rimuovi i file non necessari
                if os.path.exists(output_file):
                    os.remove(output_file)  # Rimuovi HTML

                # Rimuovi il file _events_only.json se abbiamo usato _complete.json
                if target_file == complete_file and os.path.exists(json_file):
                    os.remove(json_file)

                # Rimuovi il file _complete.json se abbiamo usato _events_only.json
                elif target_file == json_file and os.path.exists(complete_file):
                    os.remove(complete_file)

                # Processa gli eventi dal file archiviato
                analyzer.process_events_file(archived_file)

                # Aggiorna stato sistema (IP distributore)
                analyzer.update_system_status('distributore_ip', DISTRIBUTORE_IP)

                download_status['progress'] = 100
                download_status['message'] = f'Download completato! File archiviato: {archived_file}'

                # Invia evento SSE di completamento con successo
                send_sse_event('download_completed', {
                    'message': 'Download completato con successo!',
                    'progress': 100,
                    'success': True,
                    'last_download': datetime.now().isoformat()
                })

            else:
                download_status['error'] = f'Nessun file JSON trovato per {output_file}'
                # Invia evento SSE di errore
                send_sse_event('download_error', {
                    'message': 'Errore: Nessun file JSON trovato',
                    'error': download_status['error'],
                    'success': False
                })
        else:
            download_status['error'] = f'Errore download: {result.stderr}'
            # Invia evento SSE di errore
            send_sse_event('download_error', {
                'message': 'Errore durante il download',
                'error': download_status['error'],
                'success': False
            })

    except subprocess.TimeoutExpired:
        download_status['error'] = 'Timeout nel download (120s)'
        # Invia evento SSE di timeout
        send_sse_event('download_error', {
            'message': 'Timeout nel download',
            'error': 'Operazione interrotta per timeout (120s)',
            'success': False
        })
    except Exception as e:
        download_status['error'] = str(e)
        # Invia evento SSE di errore generico
        send_sse_event('download_error', {
            'message': 'Errore imprevisto',
            'error': str(e),
            'success': False
        })

    finally:
        download_status['is_running'] = False

@app.route('/api/download-events', methods=['POST'])
def api_download_events():
    """API endpoint per avviare download manuale eventi"""
    global download_status

    if download_status['is_running']:
        return jsonify({"error": "Download già in corso"}), 409

    try:
        # Avvia download in background
        thread = threading.Thread(target=perform_download)
        thread.daemon = True
        thread.start()

        return jsonify({"success": True, "message": "Download avviato"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download-status')
def api_download_status():
    """API endpoint per stato download corrente"""
    return jsonify(download_status)

@app.route('/api/download-info')
def api_download_info():
    """API endpoint per informazioni ultimo download"""
    try:
        last_download = analyzer.get_system_status('last_download')
        distributore_ip = analyzer.get_system_status('distributore_ip')
        last_event_date = analyzer.get_system_status('last_event_date')

        return jsonify({
            'last_download': last_download['value'] if last_download else None,
            'last_event_date': last_event_date['value'] if last_event_date else None,
            'distributore_ip': distributore_ip['value'] if distributore_ip else DISTRIBUTORE_IP,
            'is_simulator': (distributore_ip['value'] if distributore_ip else DISTRIBUTORE_IP) == 'localhost'
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === UTILITY ENDPOINTS ===

@app.route('/api/refresh')
def api_refresh():
    """API endpoint per aggiornare dati da nuovo file eventi"""
    try:
        # Cerca il file eventi più recente
        json_files = [f for f in os.listdir('.') if f.startswith('events_') and f.endswith('.json')]

        if not json_files:
            return jsonify({"error": "Nessun file eventi trovato"}), 404

        # Ordina per data di modifica e prendi il più recente
        latest_file = max(json_files, key=lambda f: os.path.getmtime(f))

        # Processa il file
        analyzer.process_events_file(latest_file)

        return jsonify({
            "success": True,
            "processed_file": latest_file,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-events', methods=['POST'])
def api_process_events():
    """API endpoint per processare eventi con sistema unificato"""
    try:
        data = request.get_json() or {}
        json_file = data.get('file')

        if not json_file:
            # Trova il file più recente se non specificato
            json_files = [f for f in os.listdir('.') if f.startswith('events_') and f.endswith('.json')]
            if not json_files:
                return jsonify({"error": "Nessun file eventi trovato"}), 404
            json_file = max(json_files, key=lambda f: os.path.getmtime(f))

        # Processa con il sistema unificato
        analyzer.process_events_file(json_file)

        return jsonify({
            "success": True,
            "processed_file": json_file,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === HEALTH CHECK ===

def check_distributore_ping():
    """Verifica connettività con distributore usando ping con cache"""
    global distributore_ping_cache, DISTRIBUTORE_IP

    now = datetime.now()

    # Controlla se cache è valida
    if (distributore_ping_cache['last_check'] and
        (now - distributore_ping_cache['last_check']).total_seconds() < distributore_ping_cache['cache_duration']):
        return distributore_ping_cache['result']

    # Esegui ping
    try:
        if DISTRIBUTORE_IP == 'localhost':
            # Per simulatore, controlla se porta 1500 è aperta
            result = subprocess.run(['nc', '-z', 'localhost', '1500'],
                                  capture_output=True, timeout=3)
            ping_success = result.returncode == 0
        else:
            # Ping reale per distributore
            result = subprocess.run(['ping', '-c', '1', '-W', '2000', DISTRIBUTORE_IP],
                                  capture_output=True, timeout=3)
            ping_success = result.returncode == 0

        # Aggiorna cache
        distributore_ping_cache['last_check'] = now
        distributore_ping_cache['result'] = ping_success

        return ping_success

    except Exception as e:
        print(f"❌ Errore ping distributore {DISTRIBUTORE_IP}: {e}")
        distributore_ping_cache['last_check'] = now
        distributore_ping_cache['result'] = False
        return False

@app.route('/api/health')
def api_health():
    """Health check endpoint con stato distributore"""
    distributore_reachable = check_distributore_ping()

    return jsonify({
        "status": "healthy",
        "api_reachable": True,
        "distributore_reachable": distributore_reachable,
        "distributore_ip": DISTRIBUTORE_IP,
        "api_base_url": request.host_url.rstrip('/'),
        "timestamp": datetime.now().isoformat(),
        "database": analyzer.db_path if analyzer else "not initialized"
    })

# === MAIN ===

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='API Server per sistema distributore sigarette')
    parser.add_argument('--ip', default=Config.DEFAULT_DISTRIBUTOR_IP,
                        help=f'Indirizzo IP del distributore (default: {Config.DEFAULT_DISTRIBUTOR_IP}, usa "localhost" per simulatore)')
    parser.add_argument('--port', type=int, default=Config.API_PORT,
                        help=f'Porta del server API (default: {Config.API_PORT})')
    parser.add_argument('--db', default=Config.DEFAULT_DB_PATH,
                        help=f'Path del database SQLite (default: {Config.DEFAULT_DB_PATH})')
    parser.add_argument('--host', default=Config.API_HOST,
                        help=f'Host per il server (default: {Config.API_HOST})')

    args = parser.parse_args()

    # Imposta IP distributore globale
    DISTRIBUTORE_IP = args.ip

    # Inizializza analyzer
    analyzer = SalesAnalyzer(args.db)

    # Inizializza motor analytics
    motor_analytics = MotorAnalytics(args.db)

    mode_text = "SIMULATORE" if args.ip == 'localhost' else f"DISTRIBUTORE {args.ip}"

    print("🚀 Avvio API Server")
    print("=" * 40)
    print(f"🎯 Modalità: {mode_text}")
    print(f"🌐 API disponibili su: http://{args.host}:{args.port}")
    print(f"💾 Database: {args.db}")
    print("📊 API endpoints:")
    print("  - GET /api/health - Health check")
    print("  - GET /api/dashboard - Dati dashboard completa")
    print("  - GET /api/motors - Lista motori")
    print("  - GET /api/motors/<id>/analytics - Analytics dettagliate motore")
    print("  - GET /api/motors/analytics/status - Status tutti i motori")
    print("  - POST /api/analytics/refresh - Refresh calcoli analytics")
    print("  - GET /api/analytics/cache/stats - Statistiche cache analytics")
    print("  - POST /api/analytics/cache/cleanup - Pulizia cache scaduta")
    print("  - GET /api/statistics/overview - Statistiche generali")
    print("  - GET /api/statistics/by-brand - Statistiche per marca")
    print("  - POST /api/download-events - Avvia download eventi")
    print("=" * 40)

    try:
        app.run(host=args.host, port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 API server arrestato")
    except Exception as e:
        print(f"\n❌ Errore nel server API: {e}")