#!/usr/bin/env python3
"""
Analizzatore vendite per distributore sigarette
Analizza gli eventi di vendita e statistiche per motore
"""

import json
import sqlite3
import re
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import argparse

class SalesAnalyzer:
    def __init__(self, db_path="sales_data.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Inizializza il database SQLite per le vendite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabella vendite
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                motor_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                sale_datetime TEXT NOT NULL,
                event_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabella motori con info prodotto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motors (
                motor_id INTEGER PRIMARY KEY,
                product_name TEXT,
                price REAL,
                last_sale_datetime TEXT,
                total_sales INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')



        # Tabella stato sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_status (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabella eventi completa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_number TEXT NOT NULL,
                event_code TEXT,
                event_type TEXT NOT NULL,
                event_datetime TEXT NOT NULL,
                event_text TEXT NOT NULL,
                transaction_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(event_number, event_datetime)
            )
        ''')

        # Tabella transazioni
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT,
                payment_method TEXT,
                total_paid REAL DEFAULT 0,
                total_change REAL DEFAULT 0,
                net_revenue REAL DEFAULT 0,
                is_complete BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabella marche prodotti
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT UNIQUE NOT NULL,
                brand_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Aggiungi colonne alla tabella sales se non esistono
        try:
            cursor.execute('ALTER TABLE sales ADD COLUMN transaction_id INTEGER')
        except sqlite3.OperationalError:
            pass  # Colonna già esiste

        try:
            cursor.execute('ALTER TABLE sales ADD COLUMN brand_id INTEGER')
        except sqlite3.OperationalError:
            pass  # Colonna già esiste

        try:
            cursor.execute('ALTER TABLE sales ADD COLUMN payment_method TEXT')
        except sqlite3.OperationalError:
            pass  # Colonna già esiste

        # Aggiungi colonna is_complete alla tabella transactions se non esiste
        try:
            cursor.execute('ALTER TABLE transactions ADD COLUMN is_complete BOOLEAN DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Colonna già esiste

        # Rimuovi tabelle inutilizzate se esistono
        try:
            cursor.execute('DROP TABLE IF EXISTS daily_stats')
            cursor.execute('DROP TABLE IF EXISTS product_changes')
        except sqlite3.OperationalError:
            pass  # Tabelle già rimosse

        # Crea vista analytics per compatibilità con motor_analytics.py
        try:
            cursor.execute('DROP VIEW IF EXISTS sales_events')
            cursor.execute('''
                CREATE VIEW sales_events AS
                SELECT
                    id,
                    motor_id,
                    sale_datetime as timestamp,
                    1 as quantity,
                    price as amount,
                    'sale' as event_type
                FROM sales
                WHERE motor_id IS NOT NULL AND sale_datetime IS NOT NULL
            ''')

            # Aggiorna la tabella motors per includere position se non esiste
            cursor.execute('''
                SELECT sql FROM sqlite_master
                WHERE type='table' AND name='motors'
            ''')
            table_sql = cursor.fetchone()[0]

            if 'position' not in table_sql:
                cursor.execute('ALTER TABLE motors ADD COLUMN position TEXT')
                # Popola posizioni di default basate su motor_id
                cursor.execute('''
                    UPDATE motors
                    SET position = 'M' || motor_id
                    WHERE position IS NULL
                ''')

        except sqlite3.OperationalError as e:
            print(f"⚠️ Errore creazione vista analytics: {e}")

        conn.commit()
        conn.close()
        print(f"✅ Database inizializzato: {self.db_path}")

    def get_existing_event_keys(self):
        """Ottiene le chiavi (number, dateTime) di tutti gli eventi già presenti nel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT event_number, event_datetime FROM events')
        existing_keys = set(cursor.fetchall())

        conn.close()
        return existing_keys

    def import_new_events_only(self, events_data):
        """Importa solo gli eventi non ancora presenti nel database"""
        # Estrai lista eventi dal payload
        events_list = events_data if isinstance(events_data, list) else events_data.get('events_data', [])

        if not events_list:
            print("📝 Nessun evento trovato nel file")
            return []

        # Ottieni eventi già presenti
        existing_keys = self.get_existing_event_keys()

        # Filtra solo eventi nuovi
        new_events = []
        for event in events_list:
            event_key = (event.get('number', ''), event.get('dateTime', ''))
            if event_key not in existing_keys:
                new_events.append(event)

        # NON salviamo più gli eventi qui - li salveremo dopo aver costruito le transazioni
        # in modo da poter aggiungere il transaction_id corretto
        return new_events

    def get_last_incomplete_transaction(self):
        """Ottiene l'ultima transazione incompleta dal database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, start_datetime, payment_method, total_paid, total_change, net_revenue
            FROM transactions
            WHERE is_complete = 0
            ORDER BY start_datetime DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'id': result[0],
                'start_datetime': result[1],
                'payment_method': result[2],
                'total_paid': result[3] or 0,
                'total_change': result[4] or 0,
                'net_revenue': result[5] or 0,
                'events': [],
                'payments': [],
                'sales': []
            }
        return None

    def is_transaction_start(self, event):
        """Verifica se un evento è l'inizio di una transazione"""
        event_text = event.get('text', '')
        return 'IMPRONTA VALIDA' in event_text or 'TESSERA VALIDA' in event_text

    def build_transactions_from_new_events(self, new_events):
        """Costruisce transazioni dai nuovi eventi con linking a transazioni incomplete"""
        if not new_events:
            return [], {}

        # Cerca transazione incompleta esistente
        current_transaction = self.get_last_incomplete_transaction()

        completed_transactions = []
        event_transaction_map = {}  # Mapping (event_number, dateTime) -> transaction_id

        for event in new_events:
            event_key = (event.get('number', ''), event.get('dateTime', ''))

            if self.is_transaction_start(event):
                # Completa transazione precedente se esiste
                if current_transaction:
                    transaction_id = self.complete_transaction(current_transaction)
                    # Mappa tutti gli eventi della transazione al transaction_id
                    for tx_event in current_transaction['events']:
                        tx_event_key = (tx_event.get('number', ''), tx_event.get('dateTime', ''))
                        event_transaction_map[tx_event_key] = transaction_id
                    completed_transactions.append(current_transaction)

                # Inizia nuova transazione
                current_transaction = self.start_new_transaction(event)

            elif current_transaction:
                # Aggiungi evento alla transazione corrente
                self.add_event_to_transaction(current_transaction, event)

        # Se rimane una transazione aperta, salva quella parziale
        if current_transaction:
            if current_transaction.get('id') is None and current_transaction.get('sales'):
                # Solo se è una nuova transazione con vendite
                transaction_id = self.complete_transaction(current_transaction)
                for tx_event in current_transaction['events']:
                    tx_event_key = (tx_event.get('number', ''), tx_event.get('dateTime', ''))
                    event_transaction_map[tx_event_key] = transaction_id
                completed_transactions.append(current_transaction)

        return completed_transactions, event_transaction_map

    def start_new_transaction(self, start_event):
        """Inizia una nuova transazione"""
        return {
            'start_datetime': start_event.get('dateTime', ''),
            'events': [start_event],
            'payments': [],
            'total_paid': 0,
            'total_change': 0,
            'sales': []
        }

    def add_event_to_transaction(self, transaction, event):
        """Aggiunge un evento alla transazione corrente"""
        transaction['events'].append(event)

        event_type = event.get('type', '')
        event_text = event.get('text', '')

        # Eventi di pagamento
        if event_type in ['POS', 'MONETA', 'BANCONOTA']:
            payment_info = self.parse_payment_event(event)
            if payment_info:
                transaction['payments'].append(payment_info)
                transaction['total_paid'] += payment_info['amount']

        # Eventi di vendita
        elif event_type == 'EVENTO' and 'EROGAZIONE IN CORSO' in event_text:
            sale = self.parse_sale_event(event)
            if sale:
                transaction['sales'].append(sale)

        # Eventi di resto
        elif event_type == 'RESTO':
            resto_info = self.parse_resto_event(event)
            if resto_info:
                transaction['total_change'] += resto_info['amount']

    def complete_transaction(self, transaction):
        """Completa una transazione salvandola o aggiornandola nel database"""
        if not transaction['sales']:
            return None  # Salta transazioni senza vendite

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Determina metodo di pagamento e ricavo netto
        payment_method = self.determine_payment_method(transaction['payments'])
        net_revenue = transaction['total_paid'] - transaction['total_change']

        if transaction.get('id'):
            # Aggiorna transazione esistente
            cursor.execute('''
                UPDATE transactions
                SET end_datetime = ?, payment_method = ?, total_paid = ?,
                    total_change = ?, net_revenue = ?, is_complete = 1
                WHERE id = ?
            ''', (
                transaction.get('end_datetime', transaction['start_datetime']),
                payment_method,
                transaction['total_paid'],
                transaction['total_change'],
                net_revenue,
                transaction['id']
            ))
            transaction_id = transaction['id']
        else:
            # Crea nuova transazione
            cursor.execute('''
                INSERT INTO transactions
                (start_datetime, end_datetime, payment_method, total_paid, total_change, net_revenue, is_complete)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (
                transaction['start_datetime'],
                transaction.get('end_datetime', transaction['start_datetime']),
                payment_method,
                transaction['total_paid'],
                transaction['total_change'],
                net_revenue
            ))
            transaction_id = cursor.lastrowid

        # Salva vendite collegate
        new_sales = 0
        for sale in transaction['sales']:
            brand_name = self.extract_brand_from_product(sale['product_name'])
            brand_id = self.get_or_create_brand(brand_name, cursor)

            # Controlla se vendita già esiste
            cursor.execute('''
                SELECT COUNT(*) FROM sales
                WHERE motor_id = ? AND sale_datetime = ? AND event_number = ?
            ''', (sale['motor_id'], sale['sale_datetime'], sale['event_number']))

            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO sales
                    (motor_id, product_name, price, sale_datetime, event_number,
                     transaction_id, brand_id, payment_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sale['motor_id'], sale['product_name'], sale['price'],
                    sale['sale_datetime'], sale['event_number'],
                    transaction_id, brand_id, payment_method
                ))
                new_sales += 1

        conn.commit()
        conn.close()

        return transaction_id

    def parse_sale_event(self, event):
        """Estrae informazioni di vendita da un evento"""
        text = event.get('text', '')

        # Pattern: "EROGAZIONE IN CORSO - MOTORE: 80 - PREZZO: 6.20 euro (MARLBORO GOLD TOUCH KS)"
        pattern = r'MOTORE: (\d+) - PREZZO: ([\d.]+) euro \(([^)]+)\)'
        match = re.search(pattern, text)

        if not match:
            return None

        motor_id = int(match.group(1))
        price = float(match.group(2))
        product_name = match.group(3).strip()

        # Parse datetime (formato: "17/09/25 19:14:15")
        datetime_str = event.get('dateTime', '')
        try:
            # Converte formato YY in YYYY (assumendo 2000+)
            parts = datetime_str.split(' ')
            date_part = parts[0]  # "17/09/25"
            time_part = parts[1] if len(parts) > 1 else "00:00:00"

            day, month, year = date_part.split('/')
            year = "20" + year  # 25 -> 2025

            sale_datetime = f"{year}-{month}-{day} {time_part}"

        except:
            sale_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            'motor_id': motor_id,
            'product_name': product_name,
            'price': price,
            'sale_datetime': sale_datetime,
            'event_number': event.get('number', ''),
            'original_text': text
        }

    def store_sales(self, sales_events):
        """Salva gli eventi di vendita nel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        new_sales = 0

        for sale in sales_events:
            # Controlla se vendita già esiste (evita duplicati)
            cursor.execute('''
                SELECT COUNT(*) FROM sales
                WHERE motor_id = ? AND sale_datetime = ? AND event_number = ?
            ''', (sale['motor_id'], sale['sale_datetime'], sale['event_number']))

            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO sales (motor_id, product_name, price, sale_datetime, event_number)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sale['motor_id'], sale['product_name'], sale['price'],
                      sale['sale_datetime'], sale['event_number']))
                new_sales += 1

        conn.commit()
        conn.close()

        return new_sales

    def update_motor_stats(self):
        """Aggiorna le statistiche dei motori"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Aggiorna statistiche per ogni motore
        cursor.execute('''
            SELECT motor_id, product_name, price,
                   MAX(sale_datetime) as last_sale,
                   COUNT(*) as total_sales
            FROM sales
            GROUP BY motor_id, product_name, price
        ''')

        motors_data = cursor.fetchall()

        for motor_id, product_name, price, last_sale, total_sales in motors_data:
            cursor.execute('''
                INSERT OR REPLACE INTO motors
                (motor_id, product_name, price, last_sale_datetime, total_sales)
                VALUES (?, ?, ?, ?, ?)
            ''', (motor_id, product_name, price, last_sale, total_sales))

        conn.commit()
        conn.close()

    def update_system_status(self, key, value):
        """Aggiorna lo stato del sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO system_status (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))

        conn.commit()
        conn.close()

    def get_system_status(self, key):
        """Ottiene lo stato del sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT value, updated_at FROM system_status WHERE key = ?
        ''', (key,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {'value': result[0], 'updated_at': result[1]}
        return None


    def get_dashboard_data(self):
        """Restituisce dati formattati per la dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Dati motori
        cursor.execute('''
            SELECT motor_id, product_name, price, last_sale_datetime,
                   total_sales
            FROM motors
            ORDER BY motor_id
        ''')

        motors = []
        for row in cursor.fetchall():
            motor_id, product_name, price, last_sale, total_sales = row

            # Calcola ore dall'ultima vendita
            hours_since_sale = 0
            try:
                if last_sale:
                    last_sale_dt = datetime.strptime(last_sale, "%Y-%m-%d %H:%M:%S")
                    hours_since_sale = (datetime.now() - last_sale_dt).total_seconds() / 3600
            except:
                pass

            motors.append({
                'motor_id': motor_id,
                'product_name': product_name,
                'price': price,
                'last_sale_datetime': last_sale,
                'hours_since_last_sale': round(hours_since_sale, 1),
                'total_sales': total_sales
            })

        # Statistiche generali
        cursor.execute('SELECT COUNT(*) FROM sales WHERE DATE(sale_datetime) = DATE("now")')
        today_sales = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(price) FROM sales WHERE DATE(sale_datetime) = DATE("now")')
        today_revenue = cursor.fetchone()[0] or 0


        # Ottieni timestamp ultimo download
        last_download_info = self.get_system_status('last_download')
        if last_download_info:
            try:
                # Converte da ISO format a formato leggibile
                last_download_dt = datetime.fromisoformat(last_download_info['value'].replace('Z', '+00:00'))
                last_updated = last_download_dt.strftime("%d/%m/%Y, %H:%M:%S")
            except:
                last_updated = "Data non valida"
        else:
            last_updated = "mai"

        conn.close()

        return {
            'motors': motors,
            'summary': {
                'total_motors': len(motors),
                'today_sales': today_sales,
                'today_revenue': round(today_revenue, 2),
                'last_updated': last_updated
            }
        }


    def store_all_events(self, events_data, event_transaction_map=None):
        """Salva tutti gli eventi nel database con deduplicazione e transaction_id opzionale"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        new_events = 0
        events_list = events_data if isinstance(events_data, list) else events_data.get('events_data', [])

        for event in events_list:
            try:
                # Ottieni transaction_id dal mapping se disponibile
                transaction_id = None
                if event_transaction_map:
                    event_key = (event.get('number', ''), event.get('dateTime', ''))
                    transaction_id = event_transaction_map.get(event_key)

                cursor.execute('''
                    INSERT OR IGNORE INTO events
                    (event_number, event_code, event_type, event_datetime, event_text, transaction_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    event.get('number', ''),
                    event.get('code', ''),
                    event.get('type', ''),
                    event.get('dateTime', ''),
                    event.get('text', ''),
                    transaction_id
                ))
                if cursor.rowcount > 0:
                    new_events += 1
            except Exception as e:
                print(f"⚠️ Errore salvando evento {event.get('number', 'N/A')}: {e}")

        conn.commit()
        conn.close()
        return new_events

    def extract_brand_from_product(self, product_name):
        """Estrae la marca dal nome del prodotto"""
        if not product_name:
            return "UNKNOWN"

        product_upper = product_name.upper()

        # Mappatura marche principali
        brands = {
            'MARLBORO': ['MARLBORO'],
            'CAMEL': ['CAMEL'],
            'WINSTON': ['WINSTON'],
            'PHILIP MORRIS': ['PHILIP MORRIS'],
            'CHESTERFIELD': ['CHESTERFIELD'],
            'LUCKY STRIKE': ['LUCKY STRIKE'],
            'ROTHMANS': ['ROTHMANS'],
            'MERIT': ['MERIT'],
            'JPS': ['JPS'],
            'DIANA': ['DIANA'],
            'CHIARAVALLE': ['CHIARAVALLE']
        }

        for brand, keywords in brands.items():
            if any(keyword in product_upper for keyword in keywords):
                return brand

        return "OTHER"

    def get_or_create_brand(self, brand_name, cursor=None):
        """Ottiene o crea una marca nel database"""
        close_conn = False
        if cursor is None:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            close_conn = True

        cursor.execute('SELECT id FROM product_brands WHERE brand_name = ?', (brand_name,))
        result = cursor.fetchone()

        if result:
            brand_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO product_brands (brand_name, brand_category)
                VALUES (?, ?)
            ''', (brand_name, 'cigarettes'))
            brand_id = cursor.lastrowid

        if close_conn:
            conn.commit()
            conn.close()

        return brand_id

    def parse_all_events_and_build_transactions(self, events_data):
        """Analizza tutti gli eventi e costruisce le transazioni"""
        events_list = events_data if isinstance(events_data, list) else events_data.get('events_data', [])

        # Prima salva tutti gli eventi
        self.store_all_events(events_data)

        # Poi processa le transazioni
        transactions = []
        current_transaction = None

        for event in events_list:
            event_type = event.get('type', '')
            event_text = event.get('text', '')
            event_datetime = event.get('dateTime', '')

            # Inizio transazione
            if 'IMPRONTA VALIDA' in event_text or 'TESSERA VALIDA' in event_text:
                if current_transaction:
                    # Completa transazione precedente se non chiusa
                    transactions.append(current_transaction)

                current_transaction = {
                    'start_datetime': event_datetime,
                    'events': [event],
                    'payments': [],
                    'total_paid': 0,
                    'total_change': 0,
                    'sales': []
                }

            elif current_transaction:
                current_transaction['events'].append(event)

                # Eventi di pagamento
                if event_type in ['POS', 'MONETA', 'BANCONOTA']:
                    payment_info = self.parse_payment_event(event)
                    if payment_info:
                        current_transaction['payments'].append(payment_info)
                        current_transaction['total_paid'] += payment_info['amount']

                # Eventi di vendita
                elif event_type == 'EVENTO' and 'EROGAZIONE IN CORSO' in event_text:
                    sale = self.parse_sale_event(event)
                    if sale:
                        current_transaction['sales'].append(sale)

                # Eventi di resto
                elif event_type == 'RESTO':
                    resto_info = self.parse_resto_event(event)
                    if resto_info:
                        current_transaction['total_change'] += resto_info['amount']

        # Aggiungi ultima transazione se presente
        if current_transaction:
            transactions.append(current_transaction)

        return transactions

    def parse_payment_event(self, event):
        """Estrae informazioni da eventi di pagamento"""
        event_type = event.get('type', '')
        event_text = event.get('text', '')

        try:
            if event_type == 'POS':
                # CREDITO POS: 6.20 euro --- CREDITO: 6.20 euro
                import re
                match = re.search(r'CREDITO POS: ([\d.]+) euro', event_text)
                if match:
                    return {
                        'method': 'POS',
                        'amount': float(match.group(1)),
                        'credit': float(match.group(1))
                    }

            elif event_type in ['MONETA', 'BANCONOTA']:
                # MONETA: 2.00 euro --- CREDITO: 5.00 euro
                # BANCONOTA: 10.00 euro --- CREDITO: 10.00 euro
                import re
                match = re.search(r'(MONETA|BANCONOTA): ([\d.]+) euro --- CREDITO: ([\d.]+) euro', event_text)
                if match:
                    return {
                        'method': match.group(1),
                        'amount': float(match.group(2)),
                        'credit': float(match.group(3))
                    }
        except:
            pass

        return None

    def parse_resto_event(self, event):
        """Estrae informazioni da eventi di resto"""
        event_text = event.get('text', '')
        event_type = event.get('type', '')

        try:
            # Gli eventi RESTO hanno solo l'importo nel text: "1.50 euro"
            if event_type == 'RESTO':
                import re
                match = re.search(r'([\d.]+) euro', event_text)
                if match:
                    return {
                        'amount': float(match.group(1))
                    }
        except:
            pass

        return None

    def save_transactions_and_sales(self, transactions):
        """Salva transazioni e vendite collegate nel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        new_sales = 0

        for transaction in transactions:
            if not transaction['sales']:
                continue  # Salta transazioni senza vendite

            # Determina metodo di pagamento principale
            payment_method = self.determine_payment_method(transaction['payments'])

            # Calcola ricavo netto
            net_revenue = transaction['total_paid'] - transaction['total_change']

            # Salva transazione
            cursor.execute('''
                INSERT INTO transactions
                (start_datetime, end_datetime, payment_method, total_paid, total_change, net_revenue, is_complete)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction['start_datetime'],
                transaction.get('end_datetime', transaction['start_datetime']),
                payment_method,
                transaction['total_paid'],
                transaction['total_change'],
                net_revenue,
                1
            ))

            transaction_id = cursor.lastrowid

            # Salva vendite collegate
            for sale in transaction['sales']:
                brand_name = self.extract_brand_from_product(sale['product_name'])
                brand_id = self.get_or_create_brand(brand_name, cursor)

                # Controlla se vendita già esiste
                cursor.execute('''
                    SELECT COUNT(*) FROM sales
                    WHERE motor_id = ? AND sale_datetime = ? AND event_number = ?
                ''', (sale['motor_id'], sale['sale_datetime'], sale['event_number']))

                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO sales
                        (motor_id, product_name, price, sale_datetime, event_number,
                         transaction_id, brand_id, payment_method)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        sale['motor_id'], sale['product_name'], sale['price'],
                        sale['sale_datetime'], sale['event_number'],
                        transaction_id, brand_id, payment_method
                    ))
                    new_sales += 1

        conn.commit()
        conn.close()

        return new_sales

    def determine_payment_method(self, payments):
        """Determina il metodo di pagamento principale di una transazione"""
        if not payments:
            return "UNKNOWN"

        # Se c'è almeno un pagamento POS, è POS
        if any(p['method'] == 'POS' for p in payments):
            return "POS"

        # Altrimenti è contanti
        return "CASH"

    def get_statistics_overview(self, date_from=None, date_to=None):
        """Ottiene statistiche generali con filtri opzionali"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        where_clause = ""
        params = []

        if date_from or date_to:
            conditions = []
            if date_from:
                conditions.append("DATE(sale_datetime) >= ?")
                params.append(date_from)
            if date_to:
                conditions.append("DATE(sale_datetime) <= ?")
                params.append(date_to)
            where_clause = "WHERE " + " AND ".join(conditions)

        # Totali generali
        cursor.execute(f'SELECT COUNT(*), SUM(price) FROM sales {where_clause}', params)
        result = cursor.fetchone()
        total_sales = result[0] or 0
        total_revenue = result[1] or 0

        # Statistiche per metodo pagamento dalle transazioni
        trans_where = where_clause.replace('sale_datetime', 'start_datetime') if where_clause else ""
        cursor.execute(f'''
            SELECT payment_method, COUNT(*), SUM(net_revenue)
            FROM transactions
            {trans_where}
            GROUP BY payment_method
        ''', params)

        payment_stats = {}
        for row in cursor.fetchall():
            method = row[0] or 'UNKNOWN'
            payment_stats[method] = {
                'count': row[1],
                'revenue': row[2] or 0
            }

        conn.close()

        return {
            'total_sales': total_sales,
            'total_revenue': round(total_revenue, 2),
            'payment_methods': payment_stats
        }

    def get_statistics_by_brand(self, date_from=None, date_to=None):
        """Ottiene statistiche dettagliate per marca"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        where_clause = ""
        params = []

        if date_from or date_to:
            conditions = []
            if date_from:
                conditions.append("DATE(s.sale_datetime) >= ?")
                params.append(date_from)
            if date_to:
                conditions.append("DATE(s.sale_datetime) <= ?")
                params.append(date_to)
            where_clause = "WHERE " + " AND ".join(conditions)

        cursor.execute(f'''
            SELECT
                pb.brand_name,
                COUNT(*) as quantity,
                SUM(s.price) as revenue,
                AVG(s.price) as avg_price,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales s2 {where_clause.replace('s.', 's2.')}), 2) as sales_percentage,
                ROUND(SUM(s.price) * 100.0 / (SELECT SUM(price) FROM sales s3 {where_clause.replace('s.', 's3.')}), 2) as revenue_percentage
            FROM sales s
            LEFT JOIN product_brands pb ON s.brand_id = pb.id
            {where_clause}
            GROUP BY pb.brand_name
            ORDER BY revenue DESC
        ''', params + params + params)

        brands_stats = []
        for row in cursor.fetchall():
            brands_stats.append({
                'brand_name': row[0] or 'UNKNOWN',
                'quantity': row[1],
                'revenue': round(row[2] or 0, 2),
                'avg_price': round(row[3] or 0, 2),
                'sales_percentage': row[4] or 0,
                'revenue_percentage': row[5] or 0
            })

        conn.close()
        return brands_stats

    def get_statistics_by_package_type(self, date_from=None, date_to=None):
        """Ottiene statistiche dettagliate per tipologia di pacchetto (product_name)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        conditions = []
        params = []

        if date_from:
            conditions.append("DATE(s.sale_datetime) >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("DATE(s.sale_datetime) <= ?")
            params.append(date_to)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        cursor.execute(f'''
            SELECT
                TRIM(s.product_name) as package_type,
                COUNT(*) as quantity,
                SUM(s.price) as revenue,
                AVG(s.price) as avg_price,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sales s2 {where_clause.replace('s.', 's2.')}), 2) as sales_percentage,
                ROUND(SUM(s.price) * 100.0 / (SELECT SUM(price) FROM sales s3 {where_clause.replace('s.', 's3.')}), 2) as revenue_percentage
            FROM sales s
            {where_clause}
            GROUP BY TRIM(s.product_name)
            ORDER BY revenue DESC
        ''', params + params + params)

        package_stats = []
        for row in cursor.fetchall():
            package_stats.append({
                'package_type': row[0] or 'UNKNOWN',
                'quantity': row[1],
                'revenue': round(row[2] or 0, 2),
                'avg_price': round(row[3] or 0, 2),
                'sales_percentage': row[4] or 0,
                'revenue_percentage': row[5] or 0
            })

        conn.close()
        return package_stats

    def process_events_file(self, json_file):
        """Processa completamente un file di eventi con import efficiente"""

        if not os.path.exists(json_file):
            print(f"❌ File non trovato: {json_file}")
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)

        # NUOVO: Import solo eventi non presenti (deduplicazione efficiente)
        new_events = self.import_new_events_only(events_data)

        if not new_events:
            # Aggiorna sempre last_download anche se non ci sono eventi nuovi
            # Questo rappresenta l'ultima volta che il sistema ha verificato gli eventi
            self.update_system_status('last_download', datetime.now().isoformat())
            return

        # NUOVO: Costruisci transazioni dai nuovi eventi con linking
        transactions, event_transaction_map = self.build_transactions_from_new_events(new_events)

        # NUOVO: Salva eventi con transaction_id collegati
        if new_events:
            self.store_all_events(new_events, event_transaction_map)

        # Aggiorna statistiche motori se ci sono stati cambiamenti
        if transactions:
            self.update_motor_stats()

        # Aggiorna timestamp ultimo download SEMPRE quando processato un file
        # Questo rappresenta l'ultima sincronizzazione del sistema
        self.update_system_status('last_download', datetime.now().isoformat())

        # Aggiorna data ultimo evento importato
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(sale_datetime) FROM sales')
        last_event = cursor.fetchone()[0]
        if last_event:
            self.update_system_status('last_event_date', last_event)
        conn.close()

        print(f"✅ Processamento completato: {len(new_events)} nuovi eventi processati - sincronizzazione aggiornata")

    def update_existing_sales_brands(self):
        """Aggiorna le marche per le vendite esistenti che non le hanno"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trova vendite senza marca
        cursor.execute('SELECT id, product_name FROM sales WHERE brand_id IS NULL')
        sales_to_update = cursor.fetchall()

        updated_count = 0
        for sale_id, product_name in sales_to_update:
            brand_name = self.extract_brand_from_product(product_name)
            brand_id = self.get_or_create_brand(brand_name, cursor)

            cursor.execute('UPDATE sales SET brand_id = ? WHERE id = ?', (brand_id, sale_id))
            updated_count += 1

        conn.commit()
        conn.close()

        return updated_count

    def backfill_transaction_links(self):
        """Collega eventi esistenti alle transazioni esistenti retroattivamente"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Ottieni tutti gli eventi senza transaction_id, ordinati per data
        cursor.execute('''
            SELECT id, event_number, event_datetime, event_type, event_text
            FROM events
            WHERE transaction_id IS NULL
            ORDER BY event_datetime ASC
        ''')

        events_to_link = cursor.fetchall()

        if not events_to_link:
            conn.close()
            return 0

        # Ottieni tutte le transazioni ordinate per data
        cursor.execute('''
            SELECT id, start_datetime
            FROM transactions
            ORDER BY start_datetime ASC
        ''')

        transactions = cursor.fetchall()

        # Algoritmo di matching: associa eventi a transazioni basandosi sulla cronologia
        current_transaction_id = None
        linked_events = 0

        for event_id, event_number, event_datetime, event_type, event_text in events_to_link:
            # Converte datetime per confronto
            try:
                # Formato evento: "17/09/25 19:14:15"
                event_dt = datetime.strptime(event_datetime, "%d/%m/%y %H:%M:%S")
            except:
                continue

            # Se è un evento di inizio transazione, trova la transazione corrispondente
            if 'IMPRONTA VALIDA' in event_text or 'TESSERA VALIDA' in event_text:
                # Trova la transazione più vicina cronologicamente
                best_match = None
                min_diff = float('inf')

                for tx_id, tx_start in transactions:
                    try:
                        # Formato transazione: "17/09/25 19:14:15" (stesso degli eventi)
                        tx_dt = datetime.strptime(tx_start, "%d/%m/%y %H:%M:%S")
                        diff = abs((event_dt - tx_dt).total_seconds())
                        if diff < min_diff and diff < 300:  # Entro 5 minuti
                            min_diff = diff
                            best_match = tx_id
                    except:
                        continue

                current_transaction_id = best_match

            # Collega evento alla transazione corrente se disponibile
            if current_transaction_id:
                cursor.execute('''
                    UPDATE events
                    SET transaction_id = ?
                    WHERE id = ?
                ''', (current_transaction_id, event_id))
                linked_events += 1

        conn.commit()
        conn.close()
        return linked_events

def main():
    parser = argparse.ArgumentParser(description='Analizzatore vendite distributore sigarette')
    parser.add_argument('json_file', nargs='?', help='File JSON eventi da analizzare')
    parser.add_argument('--db', default='sales_data.db', help='Path database SQLite')
    parser.add_argument('--dashboard-data', action='store_true', help='Mostra dati dashboard')
    parser.add_argument('--stats', action='store_true', help='Mostra statistiche')
    parser.add_argument('--update-brands', action='store_true', help='Aggiorna marche per vendite esistenti')
    parser.add_argument('--backfill-links', action='store_true', help='Collega eventi esistenti alle transazioni')

    args = parser.parse_args()

    analyzer = SalesAnalyzer(args.db)

    if args.update_brands:
        analyzer.update_existing_sales_brands()

    if args.backfill_links:
        analyzer.backfill_transaction_links()

    if args.json_file:
        analyzer.process_events_file(args.json_file)

    if args.dashboard_data:
        data = analyzer.get_dashboard_data()
        print("\n📊 DATI DASHBOARD:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

    if args.stats:
        data = analyzer.get_dashboard_data()
        print(f"\n📈 STATISTICHE MOTORI:")
        print(f"Totale motori: {data['summary']['total_motors']}")
        print(f"Vendite oggi: {data['summary']['today_sales']}")
        print(f"Ricavi oggi: €{data['summary']['today_revenue']}")

if __name__ == "__main__":
    main()